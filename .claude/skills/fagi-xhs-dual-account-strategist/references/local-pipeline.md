# 本地装配数据格式

沿用 `scripts/export_xlsx.py` 的字段：

- `meta`：`industry/category/pain_points/stage/month/brand_name/ip_name`，补充 `previous_month/supplementary` 保存上月依据和最终补充信息。
- `strategy`：`[{dim, ip_value, brand_value}]`，保留原有全部策略维度和账号简介参考。
- `ip_content_types`、`brand_content_types`：各 5 条 `{type,pct,desc,example}`。`pct` 为百分数 `40` 或 `"40%"`，不是小数 `0.4`。
- `ip_topics`：12 条 `{seq,week,type,title,core,visual,linkage}`。
- `brand_topics`：12 条 `{seq,week,type,title,core,visual,cta}`。
- `linkage`：`{core_idea,items:[{dim,ip_action,brand_action}]}`。
- `cta_strategy`：`[{stage,ip_cta,brand_cta}]`。
- `checklist`：`[{item,done}]`，只有实际完成的语义检查才写 `done:true`。

完整 Markdown 所需的新增字段（避免导出时遗漏原模板内容）：

- `stage_rhythm`：三阶段节奏的完整 Markdown，或 `[{stage,action}]`。
- `month_echo`：跨月呼应、系列延续、深化方向、阶段升级、下月预告的完整 Markdown；首次规划如实说明无上月数据。
- `search_keywords`：至少 15 个实际行业搜索词的字符串数组，用于检测标题及内容核心中的文字覆盖。文字覆盖不等于搜索量或语义有效性。
- `next_month`：下月使用提示。
- `summary`：一句话总结。

```bash
python3 scripts/render_report.py strategy_data.json 报告.md --xlsx 策略.xlsx
```

无 `--xlsx` 时只生成 Markdown；兼容原独立 Excel 命令。新增字段写入完整 Markdown，Excel 保留原有 6 个 Sheet 结构。策略 JSON 是交付的共同来源，不要分别改两份表造成内容分叉。脚本不推导选题、不调用模型。

## 买点信息的保存

不增加必填 JSON 字段：`strategy` 增加 `dim: "买点分析"`，两个账号值使用可读文本保存品类、人群、场景、价值、证据状态、限制及反馈；各选题 `core` 写买点编号及对应分析，不只写编号。`visual` 对应支撑材料，`cta/linkage` 对应真实目标，纯审美可写“纯审美展示，无转化引导”。`checklist` 追加实际完成的买点语义检查。原结构校验不会验证买点推理，脚本通过后仍需人工语义检查。
