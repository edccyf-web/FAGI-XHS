# 本地装配数据格式

`render_report.py` 使用 JSON 对象，原有 Excel 数组接口不变：

```json
{
  "industry": "行业", "brand": "品牌", "stage": "成长期",
  "mode": "full", "competitors": ["用户提供的竞品"],
  "keywords": [{"dim":"D1","seq":1,"keyword":"候选词","intent":"搜索意图","value_rating":"★★★★","account_type":"品牌号","root":"词根"}],
  "validation": [{"root":"词根","volume":1300,"competition":"低","source":"真实来源 URL","checked_at":"2026-10-11","suggestion_confirmed":false}],
  "competitor_analysis": "完整竞品分析 Markdown（无竞品则明确说明）",
  "deployment": "完整部署策略、执行清单与月度日历 Markdown",
  "pending": "待补充项、适用边界和未验证项"
}
```

- `mode` 为 `full` / `keywords` / `competitive`。全流程/矩阵保留原要求每维 6–10 个词；缺竞品时不生成 D7 并在报告说明。竞品模式仅交付 D7。
- 搜索数值单位为词根月搜索量。`keywords` 模式允许不验证，标 T3；其余模式不能把缺记录当 0。低于 100 的词根保留在验证表中，对应派生词不进入最终矩阵；按缺项提示补齐候选词。
- 已实际尝试但因配额等原因未取得结果时，验证记录保留真实 `source/checked_at`，填 `volume:null,status:"unavailable",reason:"具体原因"`。可以输出明确标 T3 的待验证词及未完成原因，不把无法获取伪装成已验证，也不因外部配额丢掉已有交付。
- 词根语义、评级、账号分配由研究判断提供；脚本仅按已有记录装配，不调用模型或网络。
- `--prepare` 在填验证结果前使用，输出去重词根队列。完整运行读取同一 JSON，输出 Markdown；加 `--xlsx` 调用既有导出器并保留原配色和 3 个 Sheet。
- 遇到结构错误只修报错项；语义、来源、阶段适配、部署可执行性仍按主 skill 核验。
