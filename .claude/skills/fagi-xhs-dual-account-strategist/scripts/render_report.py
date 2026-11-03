#!/usr/bin/env python3
"""复用已确认的策略 JSON，校验结构并生成完整 Markdown；可同进程导出 Excel。"""
import argparse
import json
from collections import Counter
from pathlib import Path


def cell(value):
    return str(value if value is not None else '').replace('|', '\\|').replace('\r', '').replace('\n', '<br>')


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(map(cell, headers)) + ' |',
                      '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(cell, row)) + ' |' for row in rows])


def validate(data):
    errors = []
    for key in ('industry', 'category', 'pain_points', 'stage', 'month'):
        if not data.get('meta', {}).get(key):
            errors.append(f'缺行业参数：{key}')
    for account in ('ip', 'brand'):
        topics = data.get(account + '_topics', [])
        if len(topics) != 12:
            errors.append(f'{account} 选题须为 12 条，实际 {len(topics)}')
        if len({t.get('seq') for t in topics}) != len(topics):
            errors.append(f'{account} 选题序号重复')
        end = 'linkage' if account == 'ip' else 'cta'
        for i, topic in enumerate(topics, 1):
            for key in ('seq', 'week', 'type', 'title', 'core', 'visual', end):
                if topic.get(key) in (None, ''):
                    errors.append(f'{account} 第 {i} 条缺 {key}')
            if len(topic.get('title', '')) > 20:
                errors.append(f'{account} 第 {i} 条标题超过 20 字')
        types = data.get(account + '_content_types', [])
        if len(types) != 5:
            errors.append(f'{account} 须有 5 种内容类型')
        actual = Counter(t.get('type') for t in topics)
        if set(actual) - {t.get('type') for t in types}:
            errors.append(f'{account} 选题含未定义内容类型')
        total = 0
        for spec in types:
            try:
                pct = float(str(spec['pct']).rstrip('%'))
                total += pct
                if topics and abs(actual[spec['type']] / len(topics) * 100 - pct) > 5:
                    errors.append(f'{account} {spec["type"]} 占比偏差超过 5 个百分点')
            except (KeyError, ValueError, TypeError):
                errors.append(f'{account} 内容占比应为百分数，如 40 或 40%')
        if abs(total - 100) > .1:
            errors.append(f'{account} 内容类型占比合计应为 100%')
    for key in ('strategy', 'linkage', 'cta_strategy', 'checklist', 'stage_rhythm', 'month_echo', 'next_month', 'summary'):
        if not data.get(key):
            errors.append(f'缺少交付板块：{key}')
    # Search coverage is a literal coverage check, not a semantic relevance judgment.
    corpus = '\n'.join(str(t.get(k, '')) for a in ('ip_topics', 'brand_topics') for t in data.get(a, []) for k in ('title', 'core'))
    words = {w for w in data.get('search_keywords', []) if w and w in corpus}
    if len(words) < 15:
        errors.append(f'行业搜索词实际覆盖 {len(words)} 个，要求至少 15 个')
    return errors


def render(data):
    m = data.get('meta', {})
    sections = ['# 小红书双账号内容策略与选题规划', '## 板块 1：账号内容策略', '### 行业参数确认',
                table(['参数', '内容'], [(k, v) for k, v in m.items()]), '### 策略总览',
                table(['维度', '个人 IP 号', '品牌号'], [(x.get('dim'), x.get('ip_value'), x.get('brand_value')) for x in data['strategy']])]
    for a, title in [('ip', '个人 IP 号'), ('brand', '品牌号')]:
        sections += ['### ' + title + '内容类型体系', table(['类型', '占比', '作用', '行业化示例'],
                     [(x.get('type'), x.get('pct'), x.get('desc'), x.get('example')) for x in data[a + '_content_types']])]
    for key, title in [('stage_rhythm', '三阶段节奏'), ('month_echo', '跨月内容呼应说明')]:
        sections += ['### ' + title, data[key] if isinstance(data[key], str) else table(['阶段', '策略'], [(x['stage'], x['action']) for x in data[key]])]
    linkage = data['linkage']
    sections += ['### 双号联动', linkage.get('core_idea', ''), table(['维度', '个人 IP 号', '品牌号'],
                 [(x.get('dim'), x.get('ip_action'), x.get('brand_action')) for x in linkage.get('items', [])]),
                 '### CTA 策略', table(['阶段', '个人号 CTA', '品牌号 CTA'],
                 [(x.get('stage'), x.get('ip_cta'), x.get('brand_cta')) for x in data['cta_strategy']]), '## 板块 2：月度选题规划']
    for a, title in [('ip', '个人 IP 号'), ('brand', '品牌号')]:
        end = 'linkage' if a == 'ip' else 'cta'
        sections += ['### ' + title + '选题表', table(['序号', '日期建议', '内容类型', '选题标题', '内容核心', '视觉方向', '联动' if a == 'ip' else 'CTA'],
                     [[x.get(k) for k in ('seq', 'week', 'type', 'title', 'core', 'visual', end)] for x in data[a + '_topics']])]
    sections += ['## 板块 3：质量审查清单', table(['检查项', '状态'], [(x.get('item'), '已核验' if x.get('done') else '待核验') for x in data['checklist']]),
                 '### 下月使用提示', data['next_month'], '### 一句话总结', data['summary']]
    return '\n\n'.join(sections) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('markdown')
    ap.add_argument('--xlsx')
    args = ap.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    errors = validate(data)
    if errors:
        print(json.dumps({'status': 'needs_revision', 'errors': errors}, ensure_ascii=False))
        raise SystemExit(1)
    Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
    Path(args.markdown).write_text(render(data), encoding='utf-8')
    if args.xlsx:
        from export_xlsx import export_xlsx
        Path(args.xlsx).parent.mkdir(parents=True, exist_ok=True)
        export_xlsx(data, args.xlsx)
    print(json.dumps({'status': 'ok', 'markdown': args.markdown, 'xlsx': args.xlsx,
                      'manual_checks': ['原创角度', '视觉是否具体', '跨月递进', '至少 2 条真实跨号联动', '转化闭环与合规']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
