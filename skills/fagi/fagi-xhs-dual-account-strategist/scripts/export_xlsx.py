#!/usr/bin/env python3
"""
小红书双账号策略 → Excel 导出脚本
用法:
    python3 scripts/export_xlsx.py <data.json> <output.xlsx>

数据格式: JSON 对象，包含:
    meta: { industry, category, pain_points, stage, month, brand_name, ip_name }
    strategy: [ { dim, ip_value, brand_value } ]  # 策略总览
    ip_topics: [ { seq, week, type, title, core, visual, linkage } ]  # 个人号选题
    brand_topics: [ { seq, week, type, title, core, visual, cta } ]   # 品牌号选题
    ip_content_types: [ { type, pct, desc } ]  # 个人号内容类型
    brand_content_types: [ { type, pct, desc } ]  # 品牌号内容类型
    checklist: [ { item, done } ]  # 审查清单

依赖: pip3 install openpyxl --break-system-packages
"""

import json
import sys
import os


def export_xlsx(data, output_path):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        print(json.dumps({"error": "请先安装 openpyxl: pip3 install openpyxl --break-system-packages"}))
        sys.exit(1)

    wb = Workbook()
    hf = Font(bold=True, color="FFFFFF", size=11)
    hfill = PatternFill(start_color="4B3FE3", end_color="4B3FE3", fill_type="solid")
    ha = Alignment(horizontal="center", vertical="center", wrap_text=True)
    tb = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    sf = Font(bold=True, size=12, color="4B3FE3")
    bf = Font(size=10)
    meta = data.get("meta", {})

    # ====== Sheet 1: 策略总览 ======
    ws1 = wb.active
    ws1.title = "策略总览"
    
    # 标题行
    ws1.cell(row=1, column=1, value=f"小红书双账号策略 — {meta.get('industry','')} {meta.get('month','')}").font = Font(bold=True, size=14, color="4B3FE3")
    ws1.merge_cells('A1:D1')
    
    # 元信息
    meta_rows = [
        ("行业", meta.get("industry", "")),
        ("品类", meta.get("category", "")),
        ("核心痛点", meta.get("pain_points", "")),
        ("当前阶段", meta.get("stage", "")),
        ("月份", meta.get("month", "")),
        ("品牌名", meta.get("brand_name", "")),
        ("个人IP名", meta.get("ip_name", "")),
    ]
    for i, (k, v) in enumerate(meta_rows, 3):
        ws1.cell(row=i, column=1, value=k).font = Font(bold=True)
        ws1.cell(row=i, column=1).border = tb
        ws1.cell(row=i, column=2, value=v).border = tb
        ws1.merge_cells(f'B{i}:D{i}')
    
    # 策略总览表
    strategy_start = 3 + len(meta_rows) + 1
    ws1.cell(row=strategy_start, column=1, value="▎双账号策略总览").font = sf
    ws1.merge_cells(f'A{strategy_start}:D{strategy_start}')
    
    strategy_headers = ["维度", "个人IP号（建信任·建黏性）", "品牌号（留资·预约）"]
    for col, h in enumerate(strategy_headers, 1):
        cell = ws1.cell(row=strategy_start+1, column=col, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ha
        cell.border = tb
    
    for i, item in enumerate(data.get("strategy", []), strategy_start+2):
        ws1.cell(row=i, column=1, value=item.get("dim", "")).border = tb
        ws1.cell(row=i, column=1).font = Font(bold=True)
        ws1.cell(row=i, column=2, value=item.get("ip_value", "")).border = tb
        ws1.cell(row=i, column=2).font = bf
        ws1.cell(row=i, column=3, value=item.get("brand_value", "")).border = tb
        ws1.cell(row=i, column=3).font = bf
    
    ws1.column_dimensions['A'].width = 18
    ws1.column_dimensions['B'].width = 50
    ws1.column_dimensions['C'].width = 50
    ws1.column_dimensions['D'].width = 20

    # ====== Sheet 2: 内容类型体系 ======
    ws2 = wb.create_sheet("内容类型体系")
    
    ws2.cell(row=1, column=1, value="个人IP号 — 内容类型体系").font = sf
    ws2.merge_cells('A1:D1')
    
    ip_headers = ["类型", "占比", "作用", "行业化示例"]
    for col, h in enumerate(ip_headers, 1):
        cell = ws2.cell(row=2, column=col, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ha
        cell.border = tb
    
    for i, item in enumerate(data.get("ip_content_types", []), 3):
        ws2.cell(row=i, column=1, value=item.get("type", "")).border = tb
        ws2.cell(row=i, column=2, value=item.get("pct", "")).border = tb
        ws2.cell(row=i, column=2).alignment = Alignment(horizontal="center")
        ws2.cell(row=i, column=3, value=item.get("desc", "")).border = tb
        ws2.cell(row=i, column=3).font = bf
        ws2.cell(row=i, column=4, value=item.get("example", "")).border = tb
    
    offset = 3 + len(data.get("ip_content_types", [])) + 2
    ws2.cell(row=offset, column=1, value="品牌号 — 内容类型体系").font = sf
    ws2.merge_cells(f'A{offset}:D{offset}')
    
    for col, h in enumerate(ip_headers, 1):
        cell = ws2.cell(row=offset+1, column=col, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ha
        cell.border = tb
    
    for i, item in enumerate(data.get("brand_content_types", []), offset+2):
        ws2.cell(row=i, column=1, value=item.get("type", "")).border = tb
        ws2.cell(row=i, column=2, value=item.get("pct", "")).border = tb
        ws2.cell(row=i, column=2).alignment = Alignment(horizontal="center")
        ws2.cell(row=i, column=3, value=item.get("desc", "")).border = tb
        ws2.cell(row=i, column=3).font = bf
        ws2.cell(row=i, column=4, value=item.get("example", "")).border = tb
    
    ws2.column_dimensions['A'].width = 20
    ws2.column_dimensions['B'].width = 12
    ws2.column_dimensions['C'].width = 40
    ws2.column_dimensions['D'].width = 40

    # ====== Sheet 3: 个人号选题 ======
    ws3 = wb.create_sheet("个人号选题")
    
    ws3.cell(row=1, column=1, value=f"个人IP号 — {meta.get('month','')} 选题规划（12 条）").font = sf
    ws3.merge_cells('A1:G1')
    
    topic_headers = ["序号", "日期建议", "内容类型", "选题标题", "内容核心", "视觉方向", "联动"]
    for col, h in enumerate(topic_headers, 1):
        cell = ws3.cell(row=2, column=col, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ha
        cell.border = tb
    
    for i, item in enumerate(data.get("ip_topics", []), 3):
        ws3.cell(row=i, column=1, value=item.get("seq", "")).border = tb
        ws3.cell(row=i, column=1).alignment = Alignment(horizontal="center")
        ws3.cell(row=i, column=2, value=item.get("week", "")).border = tb
        ws3.cell(row=i, column=2).alignment = Alignment(horizontal="center")
        ws3.cell(row=i, column=3, value=item.get("type", "")).border = tb
        ws3.cell(row=i, column=4, value=item.get("title", "")).border = tb
        ws3.cell(row=i, column=4).font = bf
        ws3.cell(row=i, column=5, value=item.get("core", "")).border = tb
        ws3.cell(row=i, column=5).font = bf
        ws3.cell(row=i, column=6, value=item.get("visual", "")).border = tb
        ws3.cell(row=i, column=7, value=item.get("linkage", "")).border = tb
    
    ws3.column_dimensions['A'].width = 8
    ws3.column_dimensions['B'].width = 14
    ws3.column_dimensions['C'].width = 18
    ws3.column_dimensions['D'].width = 36
    ws3.column_dimensions['E'].width = 44
    ws3.column_dimensions['F'].width = 30
    ws3.column_dimensions['G'].width = 24

    # ====== Sheet 4: 品牌号选题 ======
    ws4 = wb.create_sheet("品牌号选题")
    
    ws4.cell(row=1, column=1, value=f"品牌号 — {meta.get('month','')} 选题规划（12 条）").font = sf
    ws4.merge_cells('A1:G1')
    
    brand_headers = ["序号", "日期建议", "内容类型", "选题标题", "内容核心", "视觉方向", "CTA"]
    for col, h in enumerate(brand_headers, 1):
        cell = ws4.cell(row=2, column=col, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ha
        cell.border = tb
    
    for i, item in enumerate(data.get("brand_topics", []), 3):
        ws4.cell(row=i, column=1, value=item.get("seq", "")).border = tb
        ws4.cell(row=i, column=1).alignment = Alignment(horizontal="center")
        ws4.cell(row=i, column=2, value=item.get("week", "")).border = tb
        ws4.cell(row=i, column=2).alignment = Alignment(horizontal="center")
        ws4.cell(row=i, column=3, value=item.get("type", "")).border = tb
        ws4.cell(row=i, column=4, value=item.get("title", "")).border = tb
        ws4.cell(row=i, column=4).font = bf
        ws4.cell(row=i, column=5, value=item.get("core", "")).border = tb
        ws4.cell(row=i, column=5).font = bf
        ws4.cell(row=i, column=6, value=item.get("visual", "")).border = tb
        ws4.cell(row=i, column=7, value=item.get("cta", "")).border = tb
    
    ws4.column_dimensions['A'].width = 8
    ws4.column_dimensions['B'].width = 14
    ws4.column_dimensions['C'].width = 18
    ws4.column_dimensions['D'].width = 36
    ws4.column_dimensions['E'].width = 44
    ws4.column_dimensions['F'].width = 30
    ws4.column_dimensions['G'].width = 24

    # ====== Sheet 5: CTA与联动 ======
    ws5 = wb.create_sheet("CTA与联动")
    
    ws5.cell(row=1, column=1, value="双号联动机制").font = sf
    ws5.merge_cells('A1:D1')
    
    linkage = data.get("linkage", {})
    ws5.cell(row=3, column=1, value="核心理念").font = Font(bold=True)
    ws5.cell(row=3, column=2, value=linkage.get("core_idea", "")).border = tb
    ws5.merge_cells(f'B3:D3')
    
    linkage_headers = ["维度", "个人IP号", "品牌号"]
    for col, h in enumerate(linkage_headers, 1):
        cell = ws5.cell(row=5, column=col, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ha
        cell.border = tb
    
    for i, item in enumerate(linkage.get("items", []), 6):
        ws5.cell(row=i, column=1, value=item.get("dim", "")).border = tb
        ws5.cell(row=i, column=1).font = Font(bold=True)
        ws5.cell(row=i, column=2, value=item.get("ip_action", "")).border = tb
        ws5.cell(row=i, column=2).font = bf
        ws5.cell(row=i, column=3, value=item.get("brand_action", "")).border = tb
        ws5.cell(row=i, column=3).font = bf
    
    # CTA策略
    cta_start = 6 + len(linkage.get("items", [])) + 2
    ws5.cell(row=cta_start, column=1, value="CTA 策略演变").font = sf
    ws5.merge_cells(f'A{cta_start}:D{cta_start}')
    
    cta_headers = ["阶段", "个人号 CTA", "品牌号 CTA"]
    for col, h in enumerate(cta_headers, 1):
        cell = ws5.cell(row=cta_start+1, column=col, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ha
        cell.border = tb
    
    for i, item in enumerate(data.get("cta_strategy", []), cta_start+2):
        ws5.cell(row=i, column=1, value=item.get("stage", "")).border = tb
        ws5.cell(row=i, column=2, value=item.get("ip_cta", "")).border = tb
        ws5.cell(row=i, column=2).font = bf
        ws5.cell(row=i, column=3, value=item.get("brand_cta", "")).border = tb
        ws5.cell(row=i, column=3).font = bf
    
    ws5.column_dimensions['A'].width = 18
    ws5.column_dimensions['B'].width = 50
    ws5.column_dimensions['C'].width = 50
    ws5.column_dimensions['D'].width = 20

    # ====== Sheet 6: 审查清单 ======
    ws6 = wb.create_sheet("审查清单")
    
    ws6.cell(row=1, column=1, value="质量审查清单").font = sf
    ws6.merge_cells('A1:C1')
    
    check_headers = ["序号", "检查项", "完成状态"]
    for col, h in enumerate(check_headers, 1):
        cell = ws6.cell(row=2, column=col, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ha
        cell.border = tb
    
    for i, item in enumerate(data.get("checklist", []), 3):
        ws6.cell(row=i, column=1, value=item.get("seq", i-2)).border = tb
        ws6.cell(row=i, column=1).alignment = Alignment(horizontal="center")
        ws6.cell(row=i, column=2, value=item.get("item", "")).border = tb
        ws6.cell(row=i, column=2).font = bf
        ws6.cell(row=i, column=3, value="☐" if item.get("done") is False else "✅" if item.get("done") else "☐").border = tb
        ws6.cell(row=i, column=3).alignment = Alignment(horizontal="center")
    
    ws6.column_dimensions['A'].width = 8
    ws6.column_dimensions['B'].width = 50
    ws6.column_dimensions['C'].width = 14

    wb.save(output_path)
    return {
        "status": "ok",
        "path": output_path,
        "sheets": 6,
        "ip_topics": len(data.get("ip_topics", [])),
        "brand_topics": len(data.get("brand_topics", [])),
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: export_xlsx.py <data.json> <output.xlsx>"}))
        sys.exit(1)
    
    data_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(data_path):
        print(json.dumps({"error": f"数据文件不存在: {data_path}"}))
        sys.exit(1)
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = export_xlsx(data, output_path)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
