# FAGI Personal

基于 [KcwStudio/FAGI](https://github.com/KcwStudio/FAGI) 的个人独立维护版本，完整保留原包的 10 个 Skill 及引用资源。保留 MIT 许可和原作者版权；不表示原作者维护此仓库。

## 安装

```bash
npx -y skills add edccyf-web/FAGI-XHS -g --all --full-depth
```

包含主入口、对标分析、关键词规划、双账号策略、标题、笔记、合规检查、发布前审查、数据复盘及更新器。安装会与同名的原版技能重合，请勿在未备份的情况下覆盖已有个人修改。当前交付不修改任何已安装技能。

## 修改与更新

日常只编辑 `skills/fagi/`。先阅读 `SOURCE_OF_TRUTH.md`，修改后检查差异、运行相关测试，在 `CHANGELOG.md` 记录变化，再提交和推送。不要重新解压旧包覆盖工作区。

```bash
git diff
git add skills/fagi CHANGELOG.md
git commit -m "Describe the change"
git push origin main
```

更新器仅从本仓库的 `skills/fagi/` 更新，并沿用原版个人数据保护逻辑。原作者新版本不会自动覆盖个人版本；先对照上游差异再选择合并。需要回退时优先用 `git revert <commit>`，避免覆盖未提交修改。

## 验证

```bash
python3 -m unittest discover -s skills/fagi/fagi-update/tests
```

部分功能需要网络、浏览器、表格处理或 OCR 等依赖，具体以各技能说明和脚本为准。本次复制不代表已验证真实平台业务效果。
