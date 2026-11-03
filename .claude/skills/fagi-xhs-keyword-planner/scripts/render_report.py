#!/usr/bin/env python3
"""词根请求去重、验证记录复用和双格式装配。搜索和语义判断不由脚本伪造。"""
import argparse
import json
import math
import unicodedata
from collections import Counter
from pathlib import Path


def normalize(text):
    return unicodedata.normalize('NFKC', text).strip().casefold()


def cell(value):
    return str(value if value is not None else '').replace('|', '\\|').replace('\n', '<br>')


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(map(cell, headers)) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(cell, row)) + ' |' for row in rows])


def prepare(data):
    queue = {}
    for item in data['keywords']:
        root = item.get('root')
        if not root:
            raise ValueError('每个候选词须提供已判断的 root，不用字符截断代替词根研究')
        key = normalize(root)
        queue.setdefault(key, {'root': root, 'keywords': []})['keywords'].append(item['keyword'])
    return list(queue.values())


def assemble(data):
    errors, seen = [], set()
    mode = data.get('mode', 'full')
    if mode not in ('full', 'keywords', 'competitive'):
        errors.append('mode 须为 full / keywords / competitive')
    if data.get('stage') not in ('新号起号期', '成长期', '成熟期'):
        errors.append('无效账号阶段')
    records = {normalize(x['root']): x for x in data.get('validation', [])}
    if len(records) != len(data.get('validation', [])):
        errors.append('同一词根存在重复验证记录，请确认采用的统计窗口和来源')
    keywords = []
    for original in data['keywords']:
        item = dict(original)
        key = normalize(item.get('keyword', ''))
        if key in seen:
            errors.append(f'关键词重复：{item.get("keyword")}')
        seen.add(key)
        for field in ('dim', 'seq', 'keyword', 'intent', 'value_rating', 'account_type', 'root'):
            if item.get(field) in (None, ''):
                errors.append(f'{item.get("keyword")} 缺 {field}')
        if item.get('dim') not in {f'D{i}' for i in range(1, 11)}:
            errors.append(f'无效维度：{item.get("dim")}')
        v = records.get(normalize(item.get('root', '')), {})
        volume = v.get('volume')
        unavailable = volume is None and v.get('status') == 'unavailable' and bool(v.get('reason'))
        valid_volume = isinstance(volume, (int, float)) and not isinstance(volume, bool) and math.isfinite(volume) and volume >= 0
        if mode != 'keywords' and (not v.get('source') or not v.get('checked_at') or not (valid_volume or unavailable)):
            errors.append(f'{item.get("root")} 缺有效搜索记录（volume/source/checked_at）')
            continue
        item.update(root_volume=volume, source=v.get('source'), checked_at=v.get('checked_at'))
        item['confidence'] = 'T1' if volume is not None and volume > 5000 and v.get('suggestion_confirmed') else 'T2' if volume is not None and 1000 <= volume <= 5000 else 'T3'
        if mode != 'keywords' and volume is not None and volume < 100:
            continue
        if mode != 'competitive' or item['dim'] == 'D7':
            keywords.append(item)
    dims = Counter(x['dim'] for x in keywords)
    if mode != 'competitive':
        for dim in (f'D{i}' for i in range(1, 11)):
            if dim == 'D7' and not data.get('competitors'):
                continue
            if dims[dim] < 6 or dims[dim] > 10:
                errors.append(f'{dim} 保留 {dims[dim]} 个词，需补齐或确认调整（原要求 6–10 个）')
    if any(x['dim'] == 'D7' for x in keywords) and not data.get('competitors'):
        errors.append('D7 须有用户提供的竞品名')
    if not keywords:
        errors.append('没有可交付关键词')
    if not data.get('stage'):
        errors.append('缺账号阶段')
    if mode == 'full' and not data.get('deployment'):
        errors.append('缺部署策略与执行日历')
    if mode in ('full', 'competitive') and not data.get('competitor_analysis'):
        errors.append('缺竞品分析报告或无竞品的明确说明')
    return keywords, errors


def render(data, keywords):
    from export_xlsx import DIM_NAMES, DIM_STRATEGY
    sections = ['# 小红书关键词矩阵报告', f'行业：{data.get("industry", "")}　账号阶段：{data["stage"]}',
                '## 搜索量验证结果', '下列数值是词根的搜索量，不是派生关键词的独立搜索量。',
                table(['词根', '月搜索量', '竞争度', '来源', '核验时间', '核验状态', '未完成原因'],
                [[x.get(k) for k in ('root', 'volume', 'competition', 'source', 'checked_at', 'status', 'reason')] for x in data.get('validation', [])]),
                '## 维度汇总']
    counts = Counter(x['dim'] for x in keywords)
    sections.append(table(['维度', '数量', 'T1', 'T2', 'T3', '策略定位'],
                   [[dim + ' ' + DIM_NAMES[dim], counts[dim]] + [sum(x['dim'] == dim and x['confidence'] == t for x in keywords) for t in ('T1', 'T2', 'T3')] + [DIM_STRATEGY[dim]] for dim in sorted(counts, key=lambda d: int(d[1:]))]))
    sections += ['## 关键词矩阵', table(['维度', '序号', '关键词', '搜索意图', '词根', '词根月搜索量', '策略价值', '置信度', '建议账号'],
                 [[x.get(k) for k in ('dim', 'seq', 'keyword', 'intent', 'root', 'root_volume', 'value_rating', 'confidence', 'account_type')] for x in keywords])]
    for key, title in [('competitor_analysis', '竞品分析'), ('deployment', '部署策略与执行日历'), ('pending', '待补充项')]:
        if data.get(key):
            sections += ['## ' + title, data[key]]
    return '\n\n'.join(sections) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('output')
    ap.add_argument('--prepare', action='store_true')
    ap.add_argument('--xlsx')
    args = ap.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    if args.prepare:
        Path(args.output).write_text(json.dumps(prepare(data), ensure_ascii=False, indent=2), encoding='utf-8')
        return
    keywords, errors = assemble(data)
    if errors:
        print(json.dumps({'status': 'needs_revision', 'errors': errors}, ensure_ascii=False))
        raise SystemExit(1)
    Path(args.output).write_text(render(data, keywords), encoding='utf-8')
    if args.xlsx:
        from export_xlsx import export_xlsx
        Path(args.xlsx).parent.mkdir(parents=True, exist_ok=True)
        export_xlsx(keywords, args.xlsx, data['stage'], data.get('brand', ''))
    print(json.dumps({'status': 'ok', 'keywords': len(keywords), 'markdown': args.output, 'xlsx': args.xlsx}, ensure_ascii=False))


if __name__ == '__main__':
    main()
