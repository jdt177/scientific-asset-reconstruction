# Changelog

## 1.1.0 — 2026-11-26
- 新增 `## 工具映射（运行前必读）`：透明必须显式 `background=transparent`；尺寸以工具实际返回为准；生成后裁剪归一。
- 新增批量节奏与重试上限：分批（建议每批 ≤8）、元素数超阈值先确认、单元素失败 ≤3 次不再重试。
- 新增防跑偏：若返回多元素/整图，丢弃重画，不得用素材板切图冒充逐张生成。
- 新增脚本 `scripts/crop_reference.py`（参考局部裁剪）与 `scripts/trim_assets.py`（裁留白 + 报有效尺寸）。
- `audit_assets.py`：修复中文预览显示为 `?`（跨平台字体加载）；预览升级为白底/深灰底/真棋盘三背景；增加贴边具体边方向提示；自动生成 `manifest.csv` 与 `quality_report.md` 骨架。
- 新增 `assets/manifest_template.csv` 起手模板；补 `README.md`、`LICENSE`（MIT）、`.gitignore`。
- 修正文档"三背景 / 双背景"不一致；补充"画布尺寸≠有效尺寸"说明。

## 1.0.0
- 初版：元素清单、原图风格锁定、A/B/C 重绘策略、透明处理、质量验收、交付打包。
