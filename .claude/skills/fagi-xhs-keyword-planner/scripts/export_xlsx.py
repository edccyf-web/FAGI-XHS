#!/usr/bin/env python3
"""
小红书关键词矩阵 → Excel 导出脚本
用法:
    python3 scripts/export_xlsx.py <data.json> <output.xlsx> [--stage 新号起号期|成长期|成熟期] [--brand 品牌名]

数据格式: JSON 数组，每行包含: dim, seq, keyword, intent, value_rating, account_type
依赖: pip3 install openpyxl --break-system-packages
"""

import json
import sys
import os
import argparse

DIM_NAMES = {
    "D1": "品牌词", "D2": "空间/场景词", "D3": "痛点词",
    "D4": "方案需求词", "D5": "本地词", "D6": "风格词",
    "D7": "竞品拦截词", "D8": "长尾精准词", "D9": "属性词",
    "D10": "决策指南词"
}

DIM_STRATEGY = {
    "D1": "品牌搜索入口", "D2": "场景精准匹配", "D3": "流量获取",
    "D4": "高转化", "D5": "本地精准获客", "D6": "审美偏好匹配",
    "D7": "竞品流量拦截", "D8": "精准转化", "D9": "细分偏好匹配",
    "D10": "决策阶段拦截"
}

# 三个账号阶段的部署策略
STAGE_PLANS = {
    "新号起号期": {
        "label": "新号起号期（粉丝 < 1000）",
        "priority": [
            ("P0", "D8 长尾精准词", "主攻低竞争长尾词，标题前5字锁定长尾关键词", "3-4 篇/周", "快速获得初始搜索流量"),
            ("P1", "D9 属性词", "铺设材质/预算类属性词内容，拦截细分人群搜索", "2 篇/周", "拦截细分偏好流量"),
            ("P2", "D3 痛点词", "选择1-2个高共鸣痛点做爆款尝试", "1 篇/周", "培养账号辨识度"),
            ("❌ 避坑", "D1 品牌词", "新号期品牌词暂无搜索基础，暂不投入", "0", "避免无效内容"),
            ("❌ 避坑", "D7 竞品词", "新号期竞品拦截效果差，暂不投入", "0", "避免流量浪费"),
        ],
        "exec_checklist": [
            "优先发D8长尾词内容，标题前5字锁定核心长尾词",
            "正文自然嵌入同维度2-3个相关词",
            "评论区由作者主动置顶1条含关键词的引导评论",
            "发布后12小时检查笔记是否被收录（搜索完整标题）",
            "每周复盘数据，确定哪些长尾词效果好下周加量"
        ]
    },
    "成长期": {
        "label": "成长期（粉丝 1000-10000）",
        "priority": [
            ("P0", "D2 空间/场景词", "主力覆盖高频场景词，扩大流量入口", "2-3 篇/周", "扩大流量入口覆盖面"),
            ("P1", "D3 痛点词", "持续输出痛点内容形成系列，建立信任和共鸣", "2 篇/周", "建立账号信任度"),
            ("P2", "D6 风格词", "开始布局风格×空间组合内容，吸引审美偏好人群", "1 篇/周", "吸引审美圈层流量"),
            ("P2", "D10 决策指南词", "开始铺设选购指南类内容，拦截决策阶段流量", "1 篇/周", "拦截决策意向用户"),
        ],
        "exec_checklist": [
            "D2+D3为主力，每周至少4篇场景/痛点内容",
            "D6风格词做2-3篇爆款尝试，观察数据反馈",
            "关注评论区热门话题，作为下一条笔记选题来源",
            "定期检查搜索量数据，淘汰无效词根",
            "开始积累品牌词内容，为成熟期做准备"
        ]
    },
    "成熟期": {
        "label": "成熟期（粉丝 > 10000）",
        "priority": [
            ("P0", "D1 品牌词", "全力覆盖品牌词变体，锁定品牌搜索入口", "2 篇/周", "锁定品牌搜索流量"),
            ("P0", "D7 竞品拦截词", "大规模拦截竞品搜索流量", "2 篇/周", "抢夺竞品搜索份额"),
            ("P1", "D10 决策指南词", "深度攻略/排行榜类全覆盖，拦截最终决策流量", "2 篇/周", "转化高意向用户"),
            ("P2", "D4 方案需求词", "持续输出方案类内容，挂商品链接直接转化", "1 篇/周", "直接获取转化"),
        ],
        "exec_checklist": [
            "D1+D7为主力，每周至少4篇品牌/竞品内容",
            "D10深度内容可作为系列连载，持续吸引搜索流量",
            "D4方案词内容直接挂商品链接，追求转化",
            "定期复盘关键词排名变化，调整部署优先级",
            "建立评论区UGC运营机制，丰富关键词密度"
        ]
    }
}


def export_xlsx(data, output_path, account_stage="新号起号期", brand=""):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        print(json.dumps({"error": "请先安装 openpyxl: pip3 install openpyxl --break-system-packages"}))
        sys.exit(1)

    wb = Workbook()
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4B3FE3", end_color="4B3FE3", fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    section_font = Font(bold=True, size=12, color="4B3FE3")
    body_font = Font(size=10)

    # ====== Sheet 1: 维度汇总 ======
    ws_summary = wb.active
    ws_summary.title = "维度汇总"
    
    headers = ["维度编号", "维度名称", "关键词数量", "策略定位"]
    for col, h in enumerate(headers, 1):
        cell = ws_summary.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border
    
    dim_counts = {}
    for item in data:
        d = item.get("dim", "D0")
        dim_counts[d] = dim_counts.get(d, 0) + 1
    
    row = 2
    for d in sorted(dim_counts.keys()):
        ws_summary.cell(row=row, column=1, value=d).border = thin_border
        ws_summary.cell(row=row, column=2, value=DIM_NAMES.get(d, d)).border = thin_border
        c3 = ws_summary.cell(row=row, column=3, value=dim_counts[d])
        c3.border = thin_border
        c3.alignment = Alignment(horizontal="center")
        ws_summary.cell(row=row, column=4, value=DIM_STRATEGY.get(d, "")).border = thin_border
        row += 1
    
    # 总计行
    total = sum(dim_counts.values())
    ws_summary.cell(row=row, column=1, value="合计").border = thin_border
    ws_summary.cell(row=row, column=1).font = Font(bold=True)
    ws_summary.cell(row=row, column=2).border = thin_border
    c_t = ws_summary.cell(row=row, column=3, value=total)
    c_t.border = thin_border
    c_t.font = Font(bold=True)
    c_t.alignment = Alignment(horizontal="center")
    ws_summary.cell(row=row, column=4).border = thin_border
    
    ws_summary.column_dimensions['A'].width = 12
    ws_summary.column_dimensions['B'].width = 16
    ws_summary.column_dimensions['C'].width = 14
    ws_summary.column_dimensions['D'].width = 20

    # ====== Sheet 2: 关键词矩阵 ======
    ws_matrix = wb.create_sheet("关键词矩阵")
    matrix_headers = ["维度", "序号", "关键词", "搜索意图", "策略价值", "建议账号", "词根", "词根月搜索量", "置信度", "来源", "核验时间"]
    for col, h in enumerate(matrix_headers, 1):
        cell = ws_matrix.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border
    
    current_dim = ""
    row_idx = 2
    # 按维度排序后写入
    sorted_data = sorted(data, key=lambda x: (x.get("dim",""), x.get("seq",0)))
    for item in sorted_data:
        dim = item.get("dim", "")
        if dim != current_dim:
            current_dim = dim
            # 维度分隔行
            for col in range(1, 7):
                cell = ws_matrix.cell(row=row_idx, column=col)
                cell.fill = PatternFill(start_color="E8E6FB", end_color="E8E6FB", fill_type="solid")
                cell.border = thin_border
            ws_matrix.cell(row=row_idx, column=1, value=DIM_NAMES.get(dim, dim)).font = Font(bold=True)
            row_idx += 1
        
        ws_matrix.cell(row=row_idx, column=1, value=DIM_NAMES.get(dim, dim)).border = thin_border
        ws_matrix.cell(row=row_idx, column=1).font = body_font
        ws_matrix.cell(row=row_idx, column=2, value=item.get("seq", "")).border = thin_border
        ws_matrix.cell(row=row_idx, column=2).alignment = Alignment(horizontal="center")
        ws_matrix.cell(row=row_idx, column=3, value=item.get("keyword", "")).border = thin_border
        ws_matrix.cell(row=row_idx, column=3).font = body_font
        ws_matrix.cell(row=row_idx, column=4, value=item.get("intent", "")).border = thin_border
        ws_matrix.cell(row=row_idx, column=4).font = body_font
        ws_matrix.cell(row=row_idx, column=5, value=item.get("value_rating", "")).border = thin_border
        ws_matrix.cell(row=row_idx, column=5).alignment = Alignment(horizontal="center")
        ws_matrix.cell(row=row_idx, column=6, value=item.get("account_type", "")).border = thin_border
        ws_matrix.cell(row=row_idx, column=6).alignment = Alignment(horizontal="center")
        for col, key in enumerate(("root", "root_volume", "confidence", "source", "checked_at"), 7):
            c = ws_matrix.cell(row=row_idx, column=col, value=item.get(key))
            c.border = thin_border
            c.font = body_font
            c.alignment = Alignment(vertical="top", wrap_text=True)
        row_idx += 1
    for col in ("G", "H", "I", "J", "K"):
        ws_matrix.column_dimensions[col].width = 22 if col != "J" else 44
    
    ws_matrix.column_dimensions['A'].width = 14
    ws_matrix.column_dimensions['B'].width = 8
    ws_matrix.column_dimensions['C'].width = 36
    ws_matrix.column_dimensions['D'].width = 44
    ws_matrix.column_dimensions['E'].width = 12
    ws_matrix.column_dimensions['F'].width = 14

    # ====== Sheet 3: 部署策略 ======
    ws_deploy = wb.create_sheet("部署策略")
    plan = STAGE_PLANS.get(account_stage, STAGE_PLANS["新号起号期"])
    
    # 标题行
    ws_deploy.cell(row=1, column=1, value=f"账号阶段：{plan['label']}").font = Font(bold=True, size=14, color="4B3FE3")
    ws_deploy.merge_cells('A1:E1')
    
    # 策略说明
    ws_deploy.cell(row=2, column=1, value="策略说明：基于账号阶段定制的关键词发布优先级和部署动作，帮助有条不紊地执行关键词策略。").font = Font(size=10, color="666666")
    ws_deploy.merge_cells('A2:E2')
    
    # ===== 3a: 优先级表 =====
    ws_deploy.cell(row=4, column=1, value="▎优先级执行计划").font = section_font
    ws_deploy.merge_cells('A4:E4')
    
    priority_headers = ["优先级", "推荐维度", "部署动作", "每周发布频率", "预期效果"]
    for col, h in enumerate(priority_headers, 1):
        cell = ws_deploy.cell(row=5, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border
    
    for i, (pri, dim, action, freq, effect) in enumerate(plan["priority"], 6):
        ws_deploy.cell(row=i, column=1, value=pri).border = thin_border
        ws_deploy.cell(row=i, column=1).font = Font(bold=True)
        ws_deploy.cell(row=i, column=1).alignment = Alignment(horizontal="center")
        ws_deploy.cell(row=i, column=2, value=dim).border = thin_border
        ws_deploy.cell(row=i, column=3, value=action).border = thin_border
        ws_deploy.cell(row=i, column=3).font = body_font
        ws_deploy.cell(row=i, column=4, value=freq).border = thin_border
        ws_deploy.cell(row=i, column=4).alignment = Alignment(horizontal="center")
        ws_deploy.cell(row=i, column=5, value=effect).border = thin_border
        ws_deploy.cell(row=i, column=5).font = body_font
        
        # 颜色标记优先级
        if pri == "P0":
            fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
        elif pri == "P1":
            fill = PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid")
        elif pri == "P2":
            fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
        elif pri == "❌ 避坑":
            fill = PatternFill(start_color="FFEBEE", end_color="FFEBEE", fill_type="solid")
        else:
            fill = PatternFill()
        
        for col in range(1, 6):
            ws_deploy.cell(row=i, column=col).fill = fill
    
    # ===== 3b: 执行清单 =====
    checklist_start = 6 + len(plan["priority"]) + 2
    ws_deploy.cell(row=checklist_start, column=1, value="▎执行检查清单").font = section_font
    ws_deploy.merge_cells(f'A{checklist_start}:E{checklist_start}')
    
    checklist_headers = ["序号", "待办事项", "完成状态", "备注"]
    for col, h in enumerate(checklist_headers, 1):
        cell = ws_deploy.cell(row=checklist_start+1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border
    
    for i, task in enumerate(plan["exec_checklist"], 1):
        r = checklist_start + 1 + i
        ws_deploy.cell(row=r, column=1, value=i).border = thin_border
        ws_deploy.cell(row=r, column=1).alignment = Alignment(horizontal="center")
        ws_deploy.cell(row=r, column=2, value=f"☐ {task}").border = thin_border
        ws_deploy.cell(row=r, column=2).font = body_font
        ws_deploy.cell(row=r, column=3, value="").border = thin_border
        ws_deploy.cell(row=r, column=3).alignment = Alignment(horizontal="center")
        ws_deploy.cell(row=r, column=4, value="").border = thin_border
    
    # ===== 3c: 月度日历 =====
    calendar_start = checklist_start + 1 + len(plan["exec_checklist"]) + 2
    ws_deploy.cell(row=calendar_start, column=1, value="▎月度执行日历（参考模板）").font = section_font
    ws_deploy.merge_cells(f'A{calendar_start}:E{calendar_start}')
    
    cal_headers = ["周次", "主题方向", "目标关键词", "内容类型", "发布账号"]
    for col, h in enumerate(cal_headers, 1):
        cell = ws_deploy.cell(row=calendar_start+1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border
    
    cal_rows = [
        ("第1周", "", "", "图文/视频", "IP号/蓝V号"),
        ("第2周", "", "", "图文/视频", "IP号/蓝V号"),
        ("第3周", "", "", "图文/视频", "IP号/蓝V号"),
        ("第4周", "", "", "图文/视频", "IP号/蓝V号"),
    ]
    for i, (week, topic, kw, ctype, account) in enumerate(cal_rows, 1):
        r = calendar_start + 1 + i
        ws_deploy.cell(row=r, column=1, value=week).border = thin_border
        ws_deploy.cell(row=r, column=2, value=topic).border = thin_border
        ws_deploy.cell(row=r, column=3, value=kw).border = thin_border
        ws_deploy.cell(row=r, column=4, value=ctype).border = thin_border
        ws_deploy.cell(row=r, column=4).alignment = Alignment(horizontal="center")
        ws_deploy.cell(row=r, column=5, value=account).border = thin_border
    
    # 列宽
    ws_deploy.column_dimensions['A'].width = 18
    ws_deploy.column_dimensions['B'].width = 22
    ws_deploy.column_dimensions['C'].width = 44
    ws_deploy.column_dimensions['D'].width = 18
    ws_deploy.column_dimensions['E'].width = 30

    wb.save(output_path)
    return {
        "status": "ok",
        "path": output_path,
        "sheets": 3,
        "keywords": len(data),
        "account_stage": account_stage
    }


def main():
    parser = argparse.ArgumentParser(description='导出关键词矩阵 Excel')
    parser.add_argument('data_path', help='关键词数据 JSON 文件路径')
    parser.add_argument('output_path', help='输出 Excel 文件路径')
    parser.add_argument('--stage', default='新号起号期', choices=['新号起号期', '成长期', '成熟期'],
                        help='账号阶段，决定部署策略内容')
    parser.add_argument('--brand', default='', help='品牌名')
    parser.add_argument('--mode', default='full', choices=['full', 'keywords', 'competitive'],
                        help='输出模式：full=全流程含部署策略, keywords=只要关键词矩阵, competitive=只要竞品分析')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_path):
        print(json.dumps({"error": f"数据文件不存在: {args.data_path}"}))
        sys.exit(1)
    
    with open(args.data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 根据模式过滤数据
    if args.mode == 'competitive':
        # 竞品分析模式：只保留 D7 维度
        data = [item for item in data if item.get('dim') == 'D7']
    
    result = export_xlsx(data, args.output_path, args.stage, args.brand)
    result['mode'] = args.mode
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
