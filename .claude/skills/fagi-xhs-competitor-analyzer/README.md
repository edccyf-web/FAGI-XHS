# Fagi xhs competitor analyzer

通用小红书对标账号五维研究 Skill（指令型，无 API 密钥或爬虫依赖）。

## 使用方式

在 Mac 的解压目录执行 `bash install_codex.sh`，将本 Skill 安装到当前用户的全局目录 `~/.agents/skills/fagi-xhs-competitor-analyzer/`。该目录适用于所有本地 Codex 项目。旧版同名 Skill 会移到目录外的备份区，避免重复加载。

触发例：`启动小红书对标账号分析`。

首次无输入时会提示：

> 请把你想分析的 **小红书账号主页链接或截图** 发来，先看 **1–3 个**就够。
>
> 再补充两点：
> 1. **你现在做什么内容、卖什么产品或服务？** 还没开始的话，说想做的方向。
> 2. **这次主要想学什么？** 内容涨粉、获客成交，还是判断这个账号值不值得模仿？

支持任何赛道。报告覆盖行业赛道、粉丝数据、爆文数据、爆款逻辑、可借鉴内容点五维。

## 包含内容

- `SKILL.md`：触发条件、入口话术、采集与分析工作流。
- `references/analysis-method.md`：数据结构、统计口径和证据规则。
- `references/report-template.md`：五维报告模板与双/三账号对比。
- `tests/acceptance-cases.md`：10个验收场景。

## 特别提醒

本包是可供支持 Agent Skills 的助理执行的**工作流指令文件**，不包含可绕过小红书登录的采集器，也不自动赋予浏览器、网页登录或私人账号数据访问权限。用户只给主页截图也能获得“可见信息范围内”的五维初步报告；爆文TOP10等数据必须有真实可验证的笔记样本。


## V1.2 模拟验收

本发行包保留 `tests/fixtures/` 两张**虚构账号的模拟截图**，`tests/run_offline_checks.py`（无需额外 Python 包）以及 `tests/reports/` 两份示范报告。

请从发行包根目录运行 `bash install_codex.sh` 进行用户级安装；真正的 Codex 模型图像识别验收需在安装后由 Codex 执行。模拟测试通过不代表完成真人账号数据采集。

## 当前命名

- 显示名称：**Fagi xhs competitor analyzer**
- 触发标识：`$fagi-xhs-competitor-analyzer`
- `SKILL.md` frontmatter 名称：`fagi-xhs-competitor-analyzer`
- 用户级安装路径：`~/.agents/skills/fagi-xhs-competitor-analyzer/`

这是对原 `xhs-competitor-analyzer` 的更名升级；升级脚本备份旧版，不在可扫描的 skills 根目录留下重复 Skill。

## TOP榜明细与逐篇拆解

样本TOP榜每篇补核观看量、点赞、收藏、评论、转发五项，逐项附来源、时间和缺失原因，再分别拆解选题、标题、封面、结构、价值和互动设计。无法获取的观看/转发不补零、不估算；3–5篇代表作另作深入对照。
