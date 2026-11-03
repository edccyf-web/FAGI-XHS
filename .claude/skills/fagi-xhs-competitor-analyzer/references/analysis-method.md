# 分析方法与数据口径（供 SKILL.md 引用）

## A. 原始信息记录

每个账号至少建立以下观察记录（没有数据保留 null，不填零）：

```
account_name: 用户提供名称或截图显示名称
account_id: 主页用户ID，可缺省
source_type: url | screenshot | mixed
source_refs: [主页URL或截图A-1等]
observed_at: 读取日期或未知
verification_status: verified | partial | unknown
profile:
  bio: null
  followers: null
  following: null
  profile_likes_or_likes_saves: null
  certifications: null
notes:
  - title: null
    url_or_screenshot_ref: null
    posted_at: null
    note_id: null
    views: null
    liked: null
    saved: null
    commented: null
    shared: null
    metrics: {} # views/liked/saved/commented/shared 各记录 value/raw/label/status/source/observed_at/reason
    detail_status: null
    breakdown: {} # 选题、标题、封面、结构、价值、互动设计，逐项记录证据与缺失
    visible_cover_features: null
    text_or_video_verified: false
limitations: []
```

## B. 计数和排名质量控制

- 识别小红书计数单位（万、千等），记录原显示形式和转换数值；模糊字形一律缺失。
- 日期、互动计数可能动态变化，快照不等同完整历史。
- 比较点赞与点赞，不要在A只有点赞、B有点赞收藏评论时直接比较两者所谓“总互动”。
- 分母数据缺失或不具可比性时不计算 R。样本篇数≥10是必要非充分条件。
- 如果笔记发布时间可见，尽量同窗口比较以减少发布时长带来的偏差。
- 在评论里找需求线索时，只据实际看到的评论，不伪造评论观点。
- 对账号粉丝的性别、年龄、地域不得凭页面风格声称掌握精确画像。

## C. 不同输入材料能回答什么

| 输入 | 可较可靠分析 | 不可直接确定 |
|---|---|---|
| 仅主页链接，页面可打开 | 公开简介、粉丝字段、可见笔记 | 后台曝光、转化、私密粉丝画像 |
| 仅主页截图 | 可见定位、数值、展示封面/标题 | 全量笔记排名、视频节奏、历史涨粉 |
| 主页+笔记列表截图 | 可见选题、发布节奏线索、部分互动 | 未显示的历史TOP10或真实完播率 |
| 主页+笔记详情截图 | 标题、正文、封面、可见互动与评论线索 | 不能仅凭静态截图断言视频前3秒 |
| 可合法观看的视频 | 视觉钩子、镜头推进、互动引导 | 后台曝光、用户转化、真实推荐算法原因 |

## D. 三种目标的解释标准

- 涨粉：用**可迁移的内容机制**给建议，不宣称对方的实际粉丝增长驱动被证实。
- 获客成交：区分内容呈现的“获客意图”和后台真实线索/成交数。
- 值不值得模仿：输出是否适合**目标人群、内容能力、商业路径、素材条件**，而不是看粉丝大就一律推荐。

## E. 借鉴建议模板

```
观察到的案例：[笔记标题/截图编号]
信号：[封面构图/用户提问/内容结构等]
机制推断：[待证实的解释]
适配判断：[为什么适合/不适合用户当前方向]
可执行改造：[可录制/可写的具体选题或结构]
难度：[低/中/高] + 依据
避免照搬：[原创、版权、过度承诺、平台规则等]
```

## F. TOP榜详情与数值核验

- 每篇使用稳定笔记ID或链接绑定列表值、详情值和拆解，不能串入另一篇笔记的数据。
- 五项字段 views、liked、saved、commented、shared 始终存在。单项记录 `value`（数值或 null）、`raw`（原显示）、`label`（平台原字段）、`status`（verified/missing/unreadable/not_applicable）、`source`、`observed_at` 和缺失原因 `reason`。仅确实显示0时填0。
- 视频播放量、图文阅读/浏览量保留原口径；曝光不等于观看，不跨类型混算观看互动率。计数带“万”保留近似性质；不将约数转换成精确实测值。
- 详情与列表快照冲突时保留两次观测及各自时间，不无声覆盖；报告所用快照和排序口径须明确。
- 不因某篇取得观看/转发而变更整组排序，不把缺失当0。计算赞藏评和、比率或R时要求相关数据齐全且同口径；缺失或分母为0不计算。
- TOP榜每篇附基础拆解卡，未取得正文或未观看视频时，结构、时点等对应项写无法核实。再选3–5篇深入对照，避免把部分深化误写成所有笔记已完整观看。
