#!/usr/bin/env python3
"""Offline contract/fixture checks, NOT a Codex LLM or screenshot OCR end-to-end test."""
import json, statistics, pathlib, sys, struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
F=ROOT/'tests'/'fixtures'
OUT=ROOT/'tests'/'reports'
OUT.mkdir(exist_ok=True)
fixture=json.loads((F/'fixture_data.json').read_text(encoding='utf-8'))
skill=(ROOT/'SKILL.md').read_text(encoding='utf-8')
required=['name: fagi-xhs-competitor-analyzer','小红书账号主页链接或截图','你现在做什么内容、卖什么产品或服务','这次主要想学什么','行业赛道','粉丝数据','爆文数据','爆款逻辑','值得借鉴的内容点','不足10','不可','截图']
for s in required:
    assert s in skill, f'缺少关键规则: {s}'
for pic in ['A_profile_only_mock.png','B_note_list_mock.png']:
    data=(F/pic).read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    w,h=struct.unpack('>II',data[16:24])
    assert w>=1000 and h>=1000

a=fixture['scenario_A'];b=fixture['scenario_B']
assert a['visible_note_likes'] is None
assert b['is_live_account'] is False
notes=b['notes']
assert len(notes)>=10
assert all(n['saves'] is None and n['comments'] is None and n['views'] is None and n['shares'] is None for n in notes)
ordered=sorted(notes,key=lambda n:n['likes'],reverse=True)
assert [n['likes'] for n in ordered[:3]]==[3400,2400,1800]
for n in notes:
    peers=[x['likes'] for x in notes if x is not n]
    n['R']=n['likes']/statistics.median(peers)
assert 6.5<ordered[0]['R']<6.6
assert sum(n['R']>=3 for n in notes)==3

A=f'''# 场景A｜仅主页截图：五维阶段性分析（模拟测试）

> **非真实账号研究：**本报告仅使用明确标记为模拟数据的测试截图。用于检验 Skill 的报告边界，不代表对任何真实小红书账号的评价。测试截图：`tests/fixtures/A_profile_only_mock.png`。

## 摘要
- 账号：{a['account']}（**测试虚构账号**；账号身份只来自截图），用户业务：{a['business']}，目标：{a['goal']}。
- 输入：仅主页截图；可见主页数字、简介和6个笔记封面标题；**未取得真实笔记互动、内容详情或历史快照**。
- 结论：可以初判定位与内容主题，但**不能**生成TOP10爆文、粉丝增长曲线或成交效果判断。

## 一、行业赛道
- **[截图可见]** 简介含「陶艺体验、周末手作、零基础课程」；显示杭州工作室体验。
- **[推断]** 细分定位为本地陶艺体验与初学者手作课程，潜在内容受众包括初学者和寻找周末体验的人。

## 二、粉丝数据
- **[截图可见]** 粉丝数约 **1.2万**；关注数 **88**；主页字段「获赞与收藏」**3.8万**（这些均为**测试虚构数据**）。
- **[缺失]** 粉丝历史变化、近期发文时间、单篇互动中位数；不能推断粉丝增长速度。

## 三、爆文数据
- 封面标题样本 **6条**，可见笔记互动样本 **0条**。**无法生成按互动排序的TOP榜单**，也不能计算R指数。

## 四、爆款逻辑
- **[仅封面标题可见]** 笔记涉及新手体验、零基础能否成功、约会场景、烧制对比、制作过程、避坑知识。
- **[待验证的假设]** 「第一次」「避坑」「前后变化」有可能分别对应新手焦虑、决策困难和结果展示；没有互动和视频详情，**不能判定它们实际爆款**。

## 五、值得借鉴的内容点（目标：获客成交）
1. 用「第一次体验完整流程」减少新客的不确定感；拍摄实际环节与成品，但不声称已证明能转化。
2. 制作「零基础常见疑问」选题，明确时长、难度、成品交付等可确认的信息。
3. 测试「预约前先知道」内容，说明适合人群、预约规则及必要的到店信息。

## 横向判断
仅有一个虚构测试账号，不能做多账号排名或真实对标价值判定。

## 数据质量
**通过预期：** 有五维结构、数字有截图来源、无伪造TOP10/转化率/涨粉曲线。此文件由模拟数据结构生成，不是图像识别模型运行结果。
'''
(OUT/'scenario_A_profile_only_report.md').write_text(A,encoding='utf-8')
rows=['|排名|笔记标题|观看量|点赞|收藏|评论|转发|R（点赞相对表现）|来源|','|---:|---|---|---:|---|---|---|---:|---|']
for i,n in enumerate(ordered[:10],1):
    rows.append(f"|{i}|{n['title']}|未获取|{n['likes']:,}|未获取|未获取|未获取|{n['R']:.2f}×|B_note_list_mock.png|")
breakdowns='\n'.join(f"- 样本{i}：{n['title']}。仅有模拟标题与点赞，其余四项数值未显示；正文和视频未取得，结构与互动设计无法核实。标题含义仅作待验证假设，不宣称已观看或已证实因果。" for i,n in enumerate(ordered[:10],1))
B=f'''# 场景B｜主页链接 + 笔记列表截图：五维阶段性分析（模拟测试）

> **非真实账号研究：**测试链接 `https://www.xiaohongshu.com/user/profile/000000000000000000000001` 只是**虚构ID占位符**，不访问、不代表真实账号。数值来自人为构造的模拟截图，不是实际采集。截图：`A_profile_only_mock.png`、`B_note_list_mock.png`。

## 摘要
- 账号：{b['account']}（虚构）。用户业务：{b['business']}；目标：{b['goal']}。
- 输入：模拟主页链接 + 主页截图 + 12篇模拟笔记的列表截图。仅可比字段是**点赞数**。
- 关键结论：可计算**样本点赞TOP10**和基于点赞的相对表现，不可声称这是该账号全量历史TOP10，也不得把点赞当成阅读、收藏、评论或成交。

## 一、行业赛道
- **[截图可见]** 陶艺体验、周末手作和零基础课程；杭州工作室体验。
- **[推断]** 初学者与周末体验型客群可能是重要目标群体，需评论/访谈验证。

## 二、粉丝数据
- **[模拟主页截图可见]** 粉丝约 **1.2万**，主页「获赞与收藏」**3.8万**，仅是单次快照。
- **[缺失]** 历史涨粉、笔记发布时间、频率、曝光量、转化率。

## 三、爆文数据｜当前可见12篇样本，点赞TOP10
- 排序口径：**仅点赞**。观看量、收藏、评论、转发没有显示，均保持缺失并记原因“模拟截图未显示”；**不**计算「赞+藏+评」。
- R = 单篇点赞 / 另外11篇点赞中位数（样本≥10，按其他笔记比较）。这是内部相对表现指标，**不是**小红书官方爆款标准。

{chr(10).join(rows)}

- 其中样本R≥3的有 **3篇**，只能称为「样本内相对高点赞候选」，不是平台爆款因果结论。

## 四、爆款逻辑

{breakdowns}

- **[截图可见]** TOP3标题分别涉及「第一次成果」、「约会反差」、「新手避坑」。
- **[推断]** 三种可能的内容利益分别是成果惊喜、体验差异和决策风险降低。
- **[无法验证]** 封面图像细节、正文内容、视频前三秒、评论反馈以及成交效果，不能据此宣称已验证爆款原因。

## 五、值得借鉴的内容点（目标：获客成交）
1. **新手结果展示**：做真实第一次体验案例，以前后过程提升理解。来自模拟样本TOP1；注意不保证人人做出同样作品。
2. **场景化决策内容**：解释陶艺约会与其他周末活动在流程上的具体区别。来自模拟TOP2；避免夸大。
3. **避坑/FAQ系列**：整理课时、烧制、取件、预算等实际规则，降低预约前疑问。来自模拟TOP3；所有信息必须与真实服务一致。

## 横向结论
只有一个虚构账号，不做账号间比较。不能据此推断真实的获客ROI。

## 数据质量与测试边界
所有数据均为**模拟**，本报告由结构化测试基准生成，测试了同口径排序及R计算规则；**没有进行Codex模型执行，也未进行截图OCR/真实网页采集**。
'''
(OUT/'scenario_B_link_plus_note_screenshot_report.md').write_text(B,encoding='utf-8')
print('PASS: SKILL 结构/字段规则检查')
print('PASS: 两张模拟截图可读取')
print('PASS: 场景A禁止无互动时的TOP榜单')
print('PASS: 场景B点赞TOP10与R指数计算；R>=3计数=3')
print('WARN: 未执行Codex模型、截图视觉解析和真实网络采集')
