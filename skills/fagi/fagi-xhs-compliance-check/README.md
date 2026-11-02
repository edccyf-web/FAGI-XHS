# xhs-compliance-check

**小红书内容合规检测专家 · Xiaohongshu Compliance Checker**

> 对笔记标题、正文、图片文字、视频字幕等进行全方位违禁词检测。两阶段检测流程（手册知识库筛查 + 广告法增补检测），支持上传图片自动 OCR 提取文字。输出风险等级总览 + 逐条检测结果 + 综合评分 + 发布前自查清单。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 功能概述

| 能力 | 说明 |
|------|------|
| 🔍 **两阶段检测** | 手册知识库筛查（9 大章节）+ 广告法增补检测 |
| 🖼️ **图片 OCR** | 上传图片自动识别文字后检测 |
| 📊 **风险评级** | 🔴高/🟠中/🟡低/✅合规 四级风险 |
| ✏️ **优化建议** | 每个违规点提供具体替换词或改写方案 |
| 📋 **自查清单** | 发布前 10 项逐项检查 |
| 📝 **合规改写版** | 将优化建议应用到原文后的完整版本 |

## 安装

```bash
# TRAE / Claude Code / Codex
git clone https://github.com/your-username/xhs-compliance-check.git ~/.trae/skills/xhs-compliance-check
```

## 触发关键词

违禁词检测、合规检查、小红书检测、敏感词检测、发布前检查、帮我查违禁词、审稿、广告法检测

## 使用示例

> "帮我检测这段文案有没有违禁词：【文案内容】"
> "帮我查查这篇笔记封面有没有违规词"（可上传图片）
> "标题和正文都写好了，帮我来一次全面合规检查"
