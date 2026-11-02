#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fagi-xhs-data-review · 可视化数据仪表盘生成器
============================================
读取小红书笔记数据（Excel / CSV / JSON），计算六层漏斗与全部指标，
生成「影视飓风科技风」深色自包含 HTML 仪表盘。

特性：
- 零外部依赖：纯内联 SVG + CSS，离线也能在浏览器/预览面板渲染
- 支持三种输入形态：Excel(.xlsx) / CSV / 已计算 JSON
- 自动识别中文列名（曝光/展现/浏览/阅读/观看 等混用）
- 严格遵守诚实边界：n<5 时标注「样本不足，仅描述」

用法：
  python3 generate_dashboard.py <输入文件> <输出HTML> [--title 标题]
输入文件支持 .xlsx / .csv / .json（JSON 为已规整的数据列表）
"""

import argparse
import json
import os
import sys
import statistics as st
from datetime import datetime

# ----------------------------------------------------------------------------
# 1. 列名映射（兼容小红书导出表的命名混乱）
# ----------------------------------------------------------------------------
COLUMN_ALIASES = {
    "title": ["笔记标题", "标题", "note_title", "title"],
    "date": ["首次发布时间", "发布时间", "发布日期", "日期", "date", "publish_time"],
    "fmt": ["体裁", "形式", "类型", "format", "note_type"],
    "exp": ["曝光", "曝光量", "展现量", "展现", "impression", "exposure"],
    "view": ["观看量", "观看", "阅读量", "阅读", "播放量", "播放", "views", "read"],
    "ctr": ["封面点击率", "点击率", "ctr", "click_rate"],
    "like": ["点赞", "赞", "likes", "like"],
    "cmt": ["评论", "评论数", "comments", "comment"],
    "fav": ["收藏", "藏", "favorites", "fav"],
    "fen": ["涨粉", "新增关注", "涨粉数", "followers_gain", "fen"],
    "share": ["分享", "转发", "shares", "share"],
    "dur": ["人均观看时长", "平均观看时长", "时长", "duration", "avg_duration"],
    "dm": ["弹幕", "danmu", "bullet"],
}

UNIT_FIELDS = {"ctr"}  # 这些字段可能是比率


def resolve_columns(headers):
    """把表头映射到标准字段名。返回 {std: col_index}。"""
    norm = {}
    for i, h in enumerate(headers):
        if h is None:
            continue
        norm[str(h).strip().lower()] = i
    mapping = {}
    for std, aliases in COLUMN_ALIASES.items():
        for a in aliases:
            if a.lower() in norm:
                mapping[std] = norm[a.lower()]
                break
    return mapping


# ----------------------------------------------------------------------------
# 2. 数据读取
# ----------------------------------------------------------------------------
def load_notes(path):
    from fast_input import load_table
    return load_table(path, COLUMN_ALIASES)[0]


# ----------------------------------------------------------------------------
# 3. 指标计算
# ----------------------------------------------------------------------------
def safe_div(a, b):
    return (a / b) if (a is not None and b not in (None, 0)) else None


def compute(notes):
    for n in notes:
        exp, view = n.get("exp"), n.get("view")
        like, cmt, fav, fen, share = (n.get(k) for k in ("like", "cmt", "fav", "fen", "share"))
        parts = (like, cmt, fav, share)
        inter = sum(parts) if all(v is not None for v in parts) else None
        n["_ctr_calc"] = safe_div(view, exp)
        n["_inter"] = inter
        n["_inter_rate"] = safe_div(inter, view)
        n["_zan"] = safe_div(like, view)
        n["_cang"] = safe_div(fav, view)
        n["_ping"] = safe_div(cmt, view)
        n["_fen_rate"] = safe_div(fen, view)
        n["_share_rate"] = safe_div(share, view)
        n["_ratio"] = safe_div(fav, like)
        # 漏斗定位：第一个明显掉链子的层
        n["_stage"] = locate_stage(n)
    return notes


def locate_stage(n):
    """单篇漏斗定位。

    设计要点（对齐技能诚实边界）：曝光 < 1000 时所有比率都是噪声，
    此时唯一可靠的结论就是「曝光不足」，统一归为 ① 曝光层——
    不能在样本太小/分发不足时假装内容没问题。
    """
    exp = n.get("exp")
    if exp is None:
        return -1
    ctr = n.get("ctr") if n.get("ctr") is not None else n.get("_ctr_calc")
    dur = n.get("dur")
    inter_rate = n.get("_inter_rate")
    fen_rate = n.get("_fen_rate")
    if exp < 1000:
        return 1
    if ctr is not None and ctr < 0.05:
        return 2
    if dur is not None and dur < 15:
        return 3
    if inter_rate is not None and inter_rate < 0.03:
        return 4
    if fen_rate is not None and fen_rate < 0.001:
        return 5
    return 0 if all(n.get(k) is not None for k in ("_ctr_calc", "dur", "_inter_rate", "_fen_rate")) else -1


def account_stage(notes):
    """账号级卡点：上游卡死时下游无意义，取最上游的系统性短板。"""
    exps = [n['exp'] for n in notes if n.get('exp') is not None]
    if not exps:
        return -1
    med_exp = st.median(exps) if exps else 0
    # 账号整体曝光中位 < 1000 → 系统性卡在 ① 曝光（分发/标签/权重问题）
    if med_exp < 1000:
        return 1
    total_exp = sum(exps)
    total_view = sum((n.get("view") or 0) for n in notes)
    total_inter = sum(n["_inter"] or 0 for n in notes)
    total_fen = sum((n.get("fen") or 0) for n in notes)
    agg_ctr = safe_div(total_view, total_exp)
    agg_ir = safe_div(total_inter, total_view)
    agg_fr = safe_div(total_fen, total_view)
    if any(n.get(k) is None for n in notes for k in ('exp', 'view')):
        agg_ctr = None
    if any(n.get(k) is None for n in notes for k in ('_inter', 'view')):
        agg_ir = None
    if any(n.get(k) is None for n in notes for k in ('fen', 'view')):
        agg_fr = None
    durs = [n.get("dur") for n in notes if n.get("dur") is not None]
    med_dur = st.median(durs) if durs else None
    if agg_ctr is not None and agg_ctr < 0.05:
        return 2
    if med_dur is not None and med_dur < 15:
        return 3
    if agg_ir is not None and agg_ir < 0.03:
        return 4
    if agg_fr is not None and agg_fr < 0.001:
        return 5
    return 0 if all(n.get(k) is not None for n in notes for k in ('exp', 'view', 'dur', '_inter', 'fen')) else -1


STAGE_LABEL = {-1: "字段不足，待核查", 0: "已提供指标无明显卡点", 1: "① 曝光层", 2: "② 点击层", 3: "③ 阅读完成层",
               4: "④ 互动层", 5: "⑤ 关注层", 6: "⑥ 转化层"}


# ----------------------------------------------------------------------------
# 4. SVG 图表（纯内联，无依赖）
# ----------------------------------------------------------------------------
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def funnel_svg(notes):
    """核心转化漏斗：曝光→观看→互动→涨粉 + 阅读完成/转化 辅助层。"""
    total_exp = sum((n.get("exp") or 0) for n in notes)
    total_view = sum((n.get("view") or 0) for n in notes)
    total_inter = sum(n["_inter"] or 0 for n in notes)
    total_fen = sum((n.get("fen") or 0) for n in notes)
    total_share = sum((n.get("share") or 0) for n in notes)
    durs = [n.get("dur") for n in notes if n.get("dur") is not None]
    med_dur = st.median(durs) if durs else 0

    layers = [
        ("① 曝光", total_exp, "#00e0ff", "系统愿不愿意推"),
        ("② 点击(观看)", total_view, "#2f7bff", "封面 + 标题"),
        ("③ 阅读完成", med_dur, "#7c5cff", f"时长中位 {med_dur:.0f}s（率指标）"),
        ("④ 互动", total_inter, "#36d39a", "赞藏评分评"),
        ("⑤ 关注(涨粉)", total_fen, "#ffb547", "人设记忆点"),
        ("⑥ 转化", 0, "#ff5e7a", "未提供转化数据，不用分享代替"),
    ]
    base = total_exp or 1
    W = 760
    H = 360
    top = 10
    lh = 56
    gap = 1
    colors = [c for _, _, c, _ in layers]
    vals = [v for _, v, _, _ in layers]
    # ③ 用相对值（时长/30s 上限1）
    rel = []
    for i, (_, v, _, _) in enumerate(layers):
        if i == 2:
            rel.append(min(v / 30.0, 1.0))
        else:
            rel.append(v / base if base else 0)
    svg = [f'<svg viewBox="0 0 {W} {H+20}" width="100%" preserveAspectRatio="xMidYMid meet" style="max-width:760px">']
    y = top
    for i, (name, val, color, desc) in enumerate(layers):
        w_top = W * (rel[i] if i == 0 else rel[i - 1]) if i > 0 else W * rel[0]
        w_bot = W * rel[i]
        cx = W / 2
        x1 = cx - w_top / 2
        x2 = cx + w_top / 2
        x3 = cx + w_bot / 2
        x4 = cx - w_bot / 2
        svg.append(f'<defs><linearGradient id="g{i}" x1="0" y1="0" x2="1" y2="0">'
                   f'<stop offset="0" stop-color="{color}" stop-opacity="0.35"/>'
                   f'<stop offset="1" stop-color="{color}" stop-opacity="0.85"/></linearGradient></defs>')
        svg.append(f'<polygon points="{x1:.1f},{y:.1f} {x2:.1f},{y:.1f} {x3:.1f},{y+lh:.1f} {x4:.1f},{y+lh:.1f}" '
                   f'fill="url(#g{i})" stroke="{color}" stroke-width="1.2"/>')
        # 标签
        pct = (val / base * 100) if i != 2 else (min(val / 30.0, 1.0) * 100)
        valstr = '未提供' if i == 5 or (i == 2 and not durs) else f"{int(val):,}" if i != 2 else f"{val:.0f}s"
        svg.append(f'<text x="14" y="{y+lh/2-4}" fill="#e8eefc" font-size="13" font-weight="600">{esc(name)}</text>')
        svg.append(f'<text x="14" y="{y+lh/2+13}" fill="#8a97b8" font-size="11">{esc(desc)}</text>')
        svg.append(f'<text x="{W-14}" y="{y+lh/2+4}" text-anchor="end" fill="#fff" font-size="15" font-weight="700">{valstr}</text>')
        # ③ 标注率
        if i == 2:
            svg.append(f'<text x="{W-14}" y="{y+lh/2+20}" text-anchor="end" fill="#7c5cff" font-size="10">率指标·时长</text>')
        y += lh + gap
    svg.append('</svg>')
    return "".join(svg)


def bars_svg(labels, values, color="#2f7bff", fmt="{:.0f}", unit=""):
    W, H = 760, 240
    pad_l, pad_r, pad_t, pad_b = 40, 20, 20, 46
    n = len(values)
    if n == 0:
        return '<svg></svg>'
    vmax = max(values) or 1
    bw = (W - pad_l - pad_r) / n * 0.6
    step = (W - pad_l - pad_r) / n
    svg = [f'<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" style="max-width:760px">']
    # 基线
    svg.append(f'<line x1="{pad_l}" y1="{H-pad_b}" x2="{W-pad_r}" y2="{H-pad_b}" stroke="#2a3556" stroke-width="1"/>')
    for i, (lab, v) in enumerate(zip(labels, values)):
        x = pad_l + step * i + (step - bw) / 2
        h = (v / vmax) * (H - pad_t - pad_b)
        y = H - pad_b - h
        svg.append(f'<defs><linearGradient id="b{i}" x1="0" y1="0" x2="0" y2="1">'
                   f'<stop offset="0" stop-color="{color}" stop-opacity="0.95"/>'
                   f'<stop offset="1" stop-color="{color}" stop-opacity="0.45"/></linearGradient></defs>')
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="4" fill="url(#b{i})"/>')
        svg.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" text-anchor="middle" fill="#e8eefc" font-size="11" font-weight="600">{fmt.format(v)}{unit}</text>')
        # x 标签（截断）
        lab_s = str(lab)
        if len(lab_s) > 8:
            lab_s = lab_s[:7] + "…"
        svg.append(f'<text x="{x+bw/2:.1f}" y="{H-pad_b+16}" text-anchor="middle" fill="#8a97b8" font-size="10">{esc(lab_s)}</text>')
    svg.append('</svg>')
    return "".join(svg)


def trend_svg(notes):
    """曝光随时间趋势（按发布日期排序）。"""
    pts = []
    for n in notes:
        d = n.get("date")
        if d is None:
            continue
        try:
            if isinstance(d, str):
                d = d.replace("年", "-").replace("月", "-").replace("日", " ").replace("时", ":").replace("分", ":").replace("秒", "")
                dt = datetime.strptime(d.strip(), "%Y-%m-%d %H:%M:%S")
            else:
                dt = d
            pts.append((dt, n.get("exp") or 0, n.get("_ctr_calc") or n.get("ctr") or 0))
        except Exception:
            continue
    pts.sort(key=lambda x: x[0])
    if len(pts) < 2:
        return '<div style="color:#8a97b8;font-size:12px;padding:8px">样本不足 2 个时间点，不绘制趋势线</div>'
    W, H = 760, 230
    pad_l, pad_r, pad_t, pad_b = 44, 20, 20, 40
    vmax = max(p[1] for p in pts) or 1
    n = len(pts)
    svg = [f'<svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="xMidYMid meet" style="max-width:760px">']
    svg.append(f'<line x1="{pad_l}" y1="{H-pad_b}" x2="{W-pad_r}" y2="{H-pad_b}" stroke="#2a3556" stroke-width="1"/>')
    coords = []
    for i, (dt, exp, ctr) in enumerate(pts):
        x = pad_l + (W - pad_l - pad_r) * (i / (n - 1))
        y = (H - pad_b) - (exp / vmax) * (H - pad_t - pad_b)
        coords.append((x, y, dt, exp, ctr))
    # 区域填充
    area = f'M {coords[0][0]:.1f},{H-pad_b} ' + " ".join(f"L {x:.1f},{y:.1f}" for x, y, _, _, _ in coords) + f' L {coords[-1][0]:.1f},{H-pad_b} Z'
    svg.append(f'<path d="{area}" fill="#00e0ff" fill-opacity="0.12"/>')
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _, _ in coords)
    svg.append(f'<polyline points="{poly}" fill="none" stroke="#00e0ff" stroke-width="2.2"/>')
    for x, y, dt, exp, ctr in coords:
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#00e0ff" stroke="#0a0e1a" stroke-width="1.5"/>')
        svg.append(f'<text x="{x:.1f}" y="{y-10:.1f}" text-anchor="middle" fill="#e8eefc" font-size="10">{int(exp)}</text>')
        svg.append(f'<text x="{x:.1f}" y="{H-pad_b+15}" text-anchor="middle" fill="#8a97b8" font-size="9">{dt.strftime("%m-%d")}</text>')
    svg.append('</svg>')
    return "".join(svg)


def pct(v):
    return f"{v*100:.1f}%" if v is not None else "—"


def number(v):
    return f'{int(v):,}' if v is not None else '—'


# ----------------------------------------------------------------------------
# 5. HTML 拼装
# ----------------------------------------------------------------------------
THEME_CSS = """
:root{
  --bg:#0a0e1a; --panel:rgba(19,26,46,.72); --panel-b:rgba(80,120,200,.18);
  --c1:#00e0ff; --c2:#2f7bff; --c3:#7c5cff; --c4:#36d39a; --c5:#ffb547; --c6:#ff5e7a;
  --txt:#e8eefc; --mut:#8a97b8; --line:#2a3556;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:radial-gradient(1200px 600px at 70% -10%,rgba(47,123,255,.18),transparent),var(--bg);
  color:var(--txt);font-family:-apple-system,"PingFang SC","Microsoft YaHei",Segoe UI,sans-serif;
  padding:22px;min-height:100vh}
.wrap{max-width:1180px;margin:0 auto}
header{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;
  padding:18px 22px;border:1px solid var(--panel-b);border-radius:16px;
  background:linear-gradient(120deg,rgba(0,224,255,.08),rgba(124,92,255,.08)),var(--panel);
  backdrop-filter:blur(8px);margin-bottom:18px}
header h1{font-size:20px;font-weight:700;letter-spacing:.5px}
header h1 .dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--c1);
  box-shadow:0 0 12px var(--c1);margin-right:9px;vertical-align:middle}
header .sub{color:var(--mut);font-size:12px;margin-top:4px}
.badge{font-size:11px;color:var(--mut);border:1px solid var(--line);padding:5px 11px;border-radius:20px}
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:18px}
.kpi{background:var(--panel);border:1px solid var(--panel-b);border-radius:14px;padding:14px 14px 12px;
  position:relative;overflow:hidden}
.kpi::before{content:"";position:absolute;left:0;top:0;width:3px;height:100%;background:var(--c2)}
.kpi .l{color:var(--mut);font-size:11px}
.kpi .v{font-size:22px;font-weight:700;margin-top:6px;font-variant-numeric:tabular-nums}
.kpi .s{color:var(--mut);font-size:10px;margin-top:3px}
.alert{display:flex;align-items:center;gap:14px;border:1px solid rgba(255,94,122,.45);
  background:linear-gradient(120deg,rgba(255,94,122,.12),rgba(255,181,71,.06));
  border-radius:14px;padding:16px 20px;margin-bottom:18px}
.alert .ic{font-size:26px}
.alert .t{font-size:15px;font-weight:700;color:#ffd0d8}
.alert .d{color:var(--mut);font-size:12px;margin-top:3px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
.card{background:var(--panel);border:1px solid var(--panel-b);border-radius:14px;padding:16px}
.card h3{font-size:13px;font-weight:600;color:var(--txt);margin-bottom:12px;display:flex;align-items:center;gap:8px}
.card h3 .tag{font-size:10px;color:var(--mut);font-weight:400}
.legend{display:flex;gap:18px;flex-wrap:wrap;color:var(--mut);font-size:11px;margin-top:10px}
.legend i{font-style:normal;margin-right:5px}
.note{color:var(--mut);font-size:11px;line-height:1.7;margin-top:10px;padding:10px 12px;
  border-left:2px solid var(--c3);background:rgba(124,92,255,.07);border-radius:0 8px 8px 0}
table{width:100%;border-collapse:collapse;font-size:11px;margin-top:6px}
th,td{padding:8px 7px;text-align:right;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}
th{color:var(--mut);font-weight:500;text-align:right}
th:first-child,td:first-child{text-align:left;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
tr:hover td{background:rgba(47,123,255,.06)}
.stage-pill{font-size:10px;padding:2px 8px;border-radius:10px;font-weight:600}
.footer{color:var(--mut);font-size:10px;text-align:center;margin-top:20px;line-height:1.8}
@media(max-width:860px){.kpis{grid-template-columns:repeat(3,1fr)}.grid2{grid-template-columns:1fr}}
"""


def build_html(notes, title="小红书笔记数据复盘 · 数据仪表盘", window="未提供，待确认", prepared=False):
    if not prepared:
        notes = compute(notes)
    n = len(notes)
    total_exp = sum((x.get("exp") or 0) for x in notes)
    total_view = sum((x.get("view") or 0) for x in notes)
    total_inter = sum(x["_inter"] or 0 for x in notes)
    total_fen = sum((x.get("fen") or 0) for x in notes)
    agg_ctr = safe_div(total_view, total_exp)
    agg_ir = safe_div(total_inter, total_view)
    if any(x.get(k) is None for x in notes for k in ('exp', 'view')):
        agg_ctr = None
    if any(x.get(k) is None for x in notes for k in ('_inter', 'view')):
        agg_ir = None
    # 中位
    def med(key):
        vs = [x[key] for x in notes if x.get(key) is not None]
        return st.median(vs) if vs else None
    med_ctr = med("_ctr_calc")

    # 卡点统计（单篇分布，用于表格）
    stage_count = {}
    for x in notes:
        s = x["_stage"]
        stage_count[s] = stage_count.get(s, 0) + 1
    # 头条结论：账号级卡点（上游卡死时下游无意义）
    stuck = account_stage(notes)
    stuck_desc = STAGE_LABEL.get(stuck, "—")
    med_exp = st.median([(x.get("exp") or 0) for x in notes]) if notes else 0
    stuck_detail = (f"账号曝光中位仅 {int(med_exp):,}，系统性卡在 ① 曝光层——"
                    f"比率样本不足，原因需结合内容与账号信息核验。"
                    f"不能据此判断内容方向正确或被限流。") if stuck == 1 else \
                   (f"账号未卡在曝光，按聚合指标定位到 {stuck_desc}。")

    missing = {k: sum(x.get(k) is None for x in notes) for k in ("exp", "view", "like", "cmt", "fav", "share", "fen")}
    quality_note = "；".join(f"{k} 缺失 {v}/{n}" for k, v in missing.items() if v)
    if quality_note:
        stuck_detail += " 已知值合计（非完整总量）：" + quality_note
    # KPI
    kpis = [
        ("笔记数", str(n), "样本量", "--c2"),
        ("总曝光", f"{int(total_exp):,}", "全部笔记累计", "--c1"),
        ("总观看", f"{int(total_view):,}", "点击合计", "--c2"),
        ("汇总观看÷曝光", pct(agg_ctr), f"逐篇计算值中位 {pct(med_ctr)}", "--c1"),
        ("总互动", f"{int(total_inter):,}", f"互动率 {pct(agg_ir)}", "--c4"),
        ("总涨粉", f"{int(total_fen):,}", "关注合计", "--c5"),
    ]

    labels = [str(x.get("title"))[:10] if x.get("title") else f"笔记{i+1}" for i, x in enumerate(notes)]
    exp_vals = [x.get("exp") or 0 for x in notes]
    ctr_vals = [(x.get("ctr") if x.get("ctr") is not None else (x.get("_ctr_calc") or 0)) * 100 for x in notes]
    ir_vals = [(x.get("_inter_rate") or 0) * 100 for x in notes]

    # 数据表
    rows = ""
    stage_colors = {0: "#36d39a", 1: "#ff5e7a", 2: "#ffb547", 3: "#7c5cff", 4: "#2f7bff", 5: "#00e0ff"}
    for i, x in enumerate(notes):
        sc = stage_colors.get(x["_stage"], "#8a97b8")
        ratio_cell = f"{x.get('_ratio'):.2f}" if x.get('_ratio') is not None else "—"
        title_cell = esc(str(x.get('title'))[:24]) if x.get('title') else f"笔记{i+1}"
        rows += (f"<tr><td>{title_cell}</td>"
                 f"<td>{number(x.get('exp'))}</td>"
                 f"<td>{number(x.get('view'))}</td>"
                 f"<td>{pct(x.get('ctr') if x.get('ctr') is not None else x.get('_ctr_calc'))}</td>"
                 f"<td>{pct(x.get('_inter_rate'))}</td>"
                 f"<td>{number(x.get('fen'))}</td>"
                 f"<td>{pct(x.get('_fen_rate'))}</td>"
                 f"<td>{ratio_cell}</td>"
                 f"<td><span class='stage-pill' style='background:{sc}22;color:{sc}'>{STAGE_LABEL.get(x['_stage'],'—')}</span></td></tr>")

    sample_note = (f"样本量 n={n}，{'低于 5 篇红线，仅逐篇诊断、不给规律结论' if n < 5 else '达到 ≥5 篇阈值，可识别极值与假设（不断言因果）'}。"
                   f"曝光<1000 的笔记比率 {sum(1 for x in notes if (x.get('exp') or 0) < 1000)/max(n,1)*100:.0f}%。")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><style>{THEME_CSS}</style></head>
<body><div class="wrap">
<header>
  <div><h1><span class="dot"></span>{esc(title)}</h1>
  <div class="sub">FAGI · 数据复盘师 · 影视飓风科技风看板 · 生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}</div></div>
  <div class="badge">数据口径：{esc(window)}</div>
</header>

<div class="kpis">{"".join(f'<div class="kpi" style="--c2:var({c})"><div class="l">{l}</div><div class="v">{v}</div><div class="s">{s}</div></div>' for l,v,s,c in kpis)}</div>

<div class="alert">
  <div class="ic">⚠️</div>
  <div><div class="t">卡点定位：{esc(stuck_desc)}</div>
  <div class="d">{esc(stuck_detail)} 单篇明细见下方数据表；深度归因与下一步动作见 Markdown 报告。</div></div>
</div>

<div class="grid2">
  <div class="card"><h3>核心转化漏斗 <span class="tag">曝光→观看→互动→涨粉（③⑥为率指标）</span></h3>
    {funnel_svg(notes)}</div>
  <div class="card"><h3>曝光对比 <span class="tag">每篇绝对量</span></h3>
    {bars_svg(labels, exp_vals, color="#00e0ff", fmt="{:.0f}")}
    <div class="legend"><span><i style="color:#00e0ff">●</i>曝光量</span></div></div>
</div>

<div class="grid2">
  <div class="card"><h3>点击率 CTR 对比 <span class="tag">封面+标题唯一考卷</span></h3>
    {bars_svg(labels, ctr_vals, color="#2f7bff", fmt="{:.1f}", unit="%")}
    <div class="legend"><span><i style="color:#2f7bff">●</i>CTR(%)</span><span>经验区间 5–10% 正常</span></div></div>
  <div class="card"><h3>互动率对比 <span class="tag">赞藏评分评 ÷ 观看</span></h3>
    {bars_svg(labels, ir_vals, color="#36d39a", fmt="{:.1f}", unit="%")}
    <div class="legend"><span><i style="color:#36d39a">●</i>互动率(%)</span><span>经验区间 3–8% 正常</span></div></div>
</div>

<div class="card" style="margin-bottom:16px"><h3>曝光时间趋势 <span class="tag">按发布日期排序</span></h3>
  {trend_svg(notes)}</div>

<div class="card"><h3>逐篇明细 <span class="tag">含漏斗卡点标注</span></h3>
  <table><thead><tr><th>笔记标题</th><th>曝光</th><th>观看</th><th>CTR</th><th>互动率</th><th>涨粉</th><th>涨粉率</th><th>藏收比</th><th>卡点</th></tr></thead>
  <tbody>{rows}</tbody></table>
</div>

<div class="note">📊 可信度图例：🟢 口径确定（公式决定）｜🟡 行业经验值·中（方向可信，数值非标准）｜🔴 经验值·低（仅粗筛，受赛道/粉丝量影响大）。
<br>🧱 诚实边界：{esc(sample_note)} 本看板所有比率在曝光&lt;1000 或点赞&lt;20 时为噪声，仅描述不解读。平台「封面点击率」与「观看÷曝光」口径可能不一致，以平台列为准。</div>

<div class="footer">FAGI · fagi-xhs-data-review 数据仪表盘 ｜ 自包含 HTML · 无外部依赖 ｜ 配合 Markdown 报告使用，深度归因与下一步动作见报告正文</div>
</div></body></html>"""
    return html


# ----------------------------------------------------------------------------
# 6. 入口
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Excel(.xlsx) / CSV / JSON 数据文件")
    ap.add_argument("output", help="输出的 HTML 仪表盘路径")
    ap.add_argument("--title", default="小红书笔记数据复盘 · 数据仪表盘", help="仪表盘标题")
    args = ap.parse_args()

    notes = load_notes(args.input)
    if not notes:
        print("⚠️ 未解析到任何笔记数据，请检查文件列名或内容。", file=sys.stderr)
        sys.exit(1)
    html = build_html(notes, title=args.title)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 已生成仪表盘：{args.output}（{len(notes)} 篇笔记）")


if __name__ == "__main__":
    main()
