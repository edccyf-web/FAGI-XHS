# FAGI 小红书生态融合智能体

> **F**usion **A**gent **G**roup **I**ntelligence — 八位专家 agent 协作的小红书经营工具箱

FAGI 是小红书生态经营体系的统一入口。你不需要记住八个工具的名字，只需要把需求告诉 FAGI，它会自动路由到最合适的专家，完成后推荐下一步。

## 核心特性

- 🎯 **单入口路由**：用户只对 FAGI 说话，FAGI 自动识别意图并路由到最合适的专家
- 🔄 **完整闭环**：研究 → 规划 → 创作 → 审查 → 复盘，覆盖小红书经营全流程
- 🤝 **多 agent 协作**：八位专家各有专长，FAGI 负责协调衔接和结果流转
- 🧭 **动态导航**：每步完成后根据实际结论推荐下一步，不预设固定流程
- 🆕 **新手友好**：第一次使用有完整教程，用任务语言描述能力，不展示技术细节

## 八位专家 + 更新器

| 专家 | 擅长 | 闭环位置 |
|---|---|---|
| **对标分析师** | 1–3 个账号的五维研究 + 可借鉴内容 + 适配建议 | 研究 |
| **关键词研究员** | 10 维关键词矩阵 + 搜索量验证 + 账号阶段部署策略 | 研究 |
| **双账号策略师** | 双账号定位 + 月度 12 条选题 + 三阶段节奏 + 跨月迭代 | 规划 |
| **标题优化师** | 8 种框架 + 75 个爆款公式库 + ≤20 字标题 + 张力检查 | 创作 |
| **笔记作家** | 5 篇完整笔记 + AI 味修正 + 关键词密度 + 合规自检 | 创作 |
| **合规检测官** | 小红书违禁词 9 大章节 + 广告法增补 + 评分 + OCR | 审查 |
| **发布前审查官** | 多平台（抖音/小红书/视频号）审稿 + 保意修复 + 个人规则库 | 审查 |
| **数据复盘师** | 六层漏斗诊断 + 加码/砍掉判断 + 数据仪表盘 | 复盘 |
| **更新器** | 从 GitHub 同步最新 FAGI，保留用户个人数据 | 维护 |

## 快速开始

### 安装

将本仓库下载或 clone 到本地，然后把 `skills/` 目录下的内容复制到你的 WorkBuddy 项目中：

```bash
# 方式一：clone 仓库
git clone https://github.com/your-username/fagi.git

# 方式二：下载 zip 后解压
unzip fagi.zip
```

### 目录结构

```
fagi/
├── SKILL.md                          # FAGI 主入口（路由器 + 导航器）
├── fagi-xhs-competitor-analyzer/      # 对标分析师（链接或截图）
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   └── tests/
├── fagi-xhs-keyword-planner/         # 关键词研究员
│   ├── SKILL.md
│   └── scripts/
├── fagi-xhs-dual-account-strategist/  # 双账号策略师
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── data/
├── fagi-xhs-title-optimizer/          # 标题优化师
│   └── SKILL.md
├── fagi-xhs-note-writer/             # 笔记作家
│   └── SKILL.md
├── fagi-xhs-compliance-check/        # 合规检测官
│   ├── SKILL.md
│   └── scripts/
├── fagi-publish-precheck/       # 发布前审查官
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   ├── templates/
│   └── data/
├── fagi-xhs-data-review/             # 数据复盘师
│   └── SKILL.md
├── fagi-update/                      # 更新器（从 GitHub 同步最新 FAGI）
│   └── SKILL.md
├── LICENSE                           # MIT
├── README.md                         # 本文件
├── .gitignore
└── package.json
```

### 在 WorkBuddy 中使用

1. 把上述 skill 目录复制到你项目的 `skills/` 目录下
2. 在 `.workbuddy/skills/` 下创建符号链接（或直接复制）
3. 在对话中输入 `/fagi` 或直接描述你的小红书需求

```bash
# 示例：创建符号链接加载点
ln -sfn /path/to/your/project/skills/fagi /path/to/your/project/.workbuddy/skills/fagi
ln -sfn /path/to/your/project/skills/fagi-xhs-keyword-planner /path/to/your/project/.workbuddy/skills/fagi-xhs-keyword-planner
# ... 其余 7 个子 skill + fagi-update 同理
```

## 使用方式

### 触发 FAGI

输入 `/fagi` 或直接说你的需求。第一次使用输入 `/fagi 新手入门`。

### 对标账号分析

直接对 FAGI 说「分析这两个小红书账号，学习涨粉和获客」，附上 1–3 个账号主页链接或截图即可。FAGI 会自动调用对标分析师，沿用对话中的业务和研究目标；没有材料时一次询问，缺失数据明确标注。也可显式调用 `$fagi-xhs-competitor-analyzer`。

已安装用户说「更新 FAGI」即可通过更新器同步新增能力，个人 `data/` 与原有符号链接保留。

### 典型场景

**从 0 起号：**

```
用户：我在做功效护肤，小红书刚起步，不知道发什么
  → 关键词研究员：做 10 维关键词矩阵
  → 双账号策略师：基于关键词做月度选题
  → 标题优化师：给选题起标题
  → 笔记作家：写 5 篇笔记
  → 合规检测官：发布前合规检查
  → 发布后 → 数据复盘师：复盘优化
```

**已有内容要发布：**

```
用户：这段文案能不能发小红书？
  → 合规检测官：小红书违禁词检测 + 评分
  → 发布前审查官：保意修复（如需改稿）
```

**数据不好要优化：**

```
用户：最近 3 篇笔记数据都不好
  → 数据复盘师：六层漏斗诊断
  → 根据结论路由到 标题优化师 / 笔记作家 / 关键词研究员
```

## 架构设计

### 三模式架构（参照 dbskill）

- **模式 C 新手教程**：第一次使用时介绍能力，带用户完成首次实际使用
- **模式 A 任务前路由**：识别用户意图，路由到最合适的专家
- **模式 B 任务后导航**：根据上一位专家的结论，推荐当前最值得处理的下一步

### 单步路由原则

每次只决定当前一位专家。不预设「先 A 再 B 再 C」的长链，因为实际结果可能改变方向。FAGI 的导航地图定义了每种结论下的推荐下一步，但最终路由由当前对话上下文决定。

### 路由边界

用户明确指定优先；否则按当前交付物、对象和材料选择。账号定位/笔记/内容做法研究归对标分析师，竞品搜索词/D7/SEO 词包归关键词研究员。新号的明确标题或写作请求不强制改做定位；多平台只有在请求审查时才选择发布前审查官。复盘导航按曝光、点击、阅读完成、互动、关注、转化六层区分，依据证据选择下一步。

### 两位审查官的区分

合规检测官和发布前审查官都做合规检查，但定位不同：

| 场景 | 路由到 | 理由 |
|---|---|---|
| 仅小红书的一般审稿、能不能发、敏感词、评分或 OCR | 合规检测官 | 默认处理一般检测 |
| 多平台/其他国内平台/平台未指定的审查 | 发布前审查官 | 按需要确认平台 |
| 完整保意修复、交易导流专项、处罚归因或个人规则 | 发布前审查官 | 按专项需求选择 |
| 明确指定某个 skill | 用户指定的 skill | 在该 skill 的边界内执行，不静默改换 |

## 技术栈

- **运行环境**：WorkBuddy（支持 Skill 机制的 AI 助手平台）
- **脚本语言**：Python 3（关键词研究员、双账号策略师、合规检测官、发布前审查官的数据处理脚本）
- **数据格式**：Markdown + Excel（.xlsx）
- **架构参考**：[dbskill](https://github.com/dontbesilent2025/dbskill)（dontbesilent 商业工具箱）的三模式路由 + 导航地图设计

## 子 skill 说明

| skill 目录 | 角色名 | 核心能力 |
|---|---|---|
| `fagi-xhs-competitor-analyzer` | 对标分析师 | 赛道、粉丝、爆文、内容逻辑、可借鉴内容五维分析；无数据不编造 |
| `fagi-xhs-keyword-planner` | 关键词研究员 | 10 维关键词矩阵 + DSO100 搜索量验证 + 账号阶段部署策略 |
| `fagi-xhs-dual-account-strategist` | 双账号策略师 | 3 轮对话 + 双账号策略 + 12 条月度选题 + Excel 导出 |
| `fagi-xhs-title-optimizer` | 标题优化师 | 8 框架首轮 + 75 公式库重试 + Top 3 推荐 |
| `fagi-xhs-note-writer` | 笔记作家 | 5 篇笔记 + 6 类 AI 味清洗 + 关键词密度 + 合规自检 |
| `fagi-xhs-compliance-check` | 合规检测官 | 9 大章节违禁词 + 广告法增补 + 评分 + OCR 图片识别 |
| `fagi-publish-precheck` | 发布前审查官 | 多平台逐条判定 + 保意修复 + 个人规则库沉淀 |
| `fagi-xhs-data-review` | 数据复盘师 | 六层漏斗诊断 + 加码/砍掉判断 + HTML 数据仪表盘 |
| `fagi-update` | 更新器 | 从 GitHub 同步最新 FAGI，保留用户个人数据 |

## 许可证

[MIT License](./LICENSE)

各子 skill 保留各自的许可证声明。如子 skill 未单独声明，适用本仓库的 MIT 许可证。

## 贡献

欢迎提交 Issue 和 PR。提交前请阅读 [CONTRIBUTING](#)（如有）。

## 致谢

- **架构参考**：[dbskill](https://github.com/dontbesilent2025/dbskill) — dontbesilent 商业工具箱
- **子 skill 来源**：小红书生态专家团 8 个独立 skill 包
- **命名释义**：FAGI = Fusion Agent Group Intelligence（融合智能体群）

## TOP榜数值与更新去重（1.3.0）

对标分析对样本TOP榜每篇核验观看量、点赞、收藏、评论、转发，逐项附来源、时间、缺失原因，并逐篇拆解内容；无法取得的数值不补零、不估算。平台显示约数时保留约数。

更新器提供 `fagi-update/scripts/sync_skills.py`：默认只输出计划，加 `--apply` 执行用户已授权的更新。按同一安装目录的技能身份和版本去重，将确认旧版移到加载目录外的可恢复备份；不同宿主各自安装不算重复，更高版本、同版不同内容、数据冲突或链接依赖会阻止自动删除。个人数据和原有链接保留。

FAGI 1.4.0：选题策划、标题优化师、笔记生产专家加入买点执行规则。先按赛道品类、具体消费人群与使用/决策场景分析选择价值，再连接产品事实、可信依据和适用条件，贯穿选题、标题与正文。支持信息决策与视觉审美，区分需求证据和待验证假设，不强造痛点或效果承诺。保留现有导出及 AI 味质检。本次分发仅包含执行规则，不附理论原文。
