# Scientific Asset Reconstruction

> 中文 | [English](README.en.md)

**把一张科研 / 医学插图按最小粒度拆解成独立、可复用、高清透明 PNG 素材的 Agent Skill。**

一个可复用的 Agent Skill：读取一张已定稿的科研插图，识别其中每一个有独立使用价值的图形元素，
逐个（或小批量）重绘为**真透明背景的高清 PNG**，再做机器质检与打包，方便后续在 PPT / Illustrator /
Inkscape 里自由组图。它不是"整图再设计"，也不是"低清抠图 / 插值放大"。

适用于任何"能读图 + 能调用图像生成/编辑工具"的 Agent（GPT-Image、Qwen-Image、Gemini 等）。
附带脚本只需 Python 3 + Pillow。

## 特性

- **最小可复用粒度拆解**：蛋白链、细胞核、单个磷脂、外显子、变异标记、单条 RNA、仪器等分别成图。
- **原图风格锁定**：保留轮廓、比例、配色、渐变、光影，不套用案例配色、不写实化。
- **真透明 PNG**：要求并校验真 alpha；支持抠像兜底。
- **单元素 / 小批量素材板 / 矢量重建** 三种重绘路线，可按需切换。
- **机器质检 + 人工复核**：三背景预览、有效尺寸、贴边与重复检测，输出 `manifest.csv` / `quality_report.md` 骨架。
- **可交付 ZIP**：PNG 目录、清单、预览、质量报告一并打包。
- **诚实边界**：不伪造能力、不把裁剪原图冒充重绘、不静默修改科学含义。

## 目录结构

```
scientific-asset-reconstruction/      # 技能目录（放入你的 Agent 技能目录）
├── SKILL.md                          # 入口（必须命名为 SKILL.md）
├── references/
│   ├── prompt-recipes.md             # 重绘提示模板（负向清单、模型-语言建议）
│   ├── quality-gates.md              # 质量验收与交付规范
│   ├── hla-example.md                # 案例与回归场景
│   ├── install-zh.md                 # 中文安装与调用说明
│   └── CHANGELOG.md
├── scripts/
│   ├── audit_assets.py               # 只读质检：CSV/JSON + 三背景预览 + manifest/report 骨架
│   ├── crop_reference.py             # 参考图局部裁剪
│   └── trim_assets.py                # 裁透明留白 + 报有效尺寸
└── assets/
    └── manifest_template.csv
```

## 安装

1. 下载 `scientific-asset-reconstruction.zip`，解压得到 `scientific-asset-reconstruction/` 目录。
2. 放入你的 Agent 支持的技能目录；或让 Agent 直接读取 `SKILL.md` 手动使用。
   入口文件必须叫 `SKILL.md`，目录名必须是 `scientific-asset-reconstruction`（与 `name` 一致）。
3. 确认 Agent 具备：读图、图像生成/编辑、透明输出（或可靠抠像）、写文件、Python + Pillow。

## 快速使用

上传已定稿的参考图，然后对 Agent 说：

> 使用 Scientific Asset Reconstruction（科研插图元素重建）Skill，把参考图中所有有独立使用价值的图元按最小粒度重绘，
> 保持原图比例与风格，输出独立透明 PNG、元素清单、预览与 ZIP。

只要复杂部件时：

> 使用 scientific-asset-reconstruction，仅重绘图中左侧的蛋白链、细胞膜和抗原肽，每个图元单独生成，不使用素材板。

## 脚本

```bash
python scientific-asset-reconstruction/scripts/crop_reference.py ref.png --box 40,140,360,410 --out crops/hla1.png
python scientific-asset-reconstruction/scripts/trim_assets.py ./out/png_raw --out ./out/png --target 1024
python scientific-asset-reconstruction/scripts/audit_assets.py ./out/png --out ./out/audit_v1 --target 1024
```

需要 `python -m pip install Pillow`。

## 示例

见 [`docs/examples/`](docs/examples/)：用 AI 生成的原创示意图演示"参考图 → 拆解 → 独立透明素材"的完整过程
（示例图由 AI 生成，不含第三方版权素材）。

## 版本

当前 1.1.0，变更见 [`references/CHANGELOG.md`](scientific-asset-reconstruction/references/CHANGELOG.md)。

## 已知限制

- 透明输出依赖图像工具能力（部分模型需显式 `background="transparent"`）；拿不到真 alpha 时需重生成或抠像。
- 模型/网关常忽略 `size`/比例，实际尺寸以返回为准；交付前用 `trim_assets.py` 裁留白并核对**有效尺寸**。
- 机器质检只查文件事实，不代表视觉忠实度或生物学正确性，必须人工目视复核。
- 未内置"素材板自动切分"脚本；批量（B）路线请按 alpha 投影 / 人工边界切分。

## 许可

[MIT](LICENSE)。本仓库不附带任何第三方参考图或成品；示例图由 AI 生成。使用他人插图请自行确认版权与授权。
