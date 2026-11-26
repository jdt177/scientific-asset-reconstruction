---
name: scientific-asset-reconstruction
description: Reconstruct independent scientific illustration assets from an existing reference figure. Use when the user requests 科研插图元素重建、拆分图形元素、逐个重绘、最小元素、透明背景PNG、科研素材库, or isolated reusable biological, medical, molecular, equipment, or workflow graphics in the original style. Produces separate high-resolution transparent assets, quality checks, preview and ZIP; not for designing a new full figure or merely cropping the original.
compatibility: Requires a reference image, visual inspection, and an image generation/editing capability; optional Python 3 + Pillow for auditing, cropping and trimming. Runs on Windows, macOS and Linux.
license: MIT
metadata:
  version: "1.1.0"
  display-name: "Scientific Asset Reconstruction｜科研插图元素重建"
  author: "Jiang Dongtao"
  keywords: "科研插图, 素材重建, 透明PNG, 元素拆分, scientific illustration, asset reconstruction, transparent PNG"
allowed-tools: Bash(python:*) Read Write
---

# Scientific Asset Reconstruction｜科研插图元素重建

## 目标与边界

将用户已确认的参考图重建成可在 PPT / Illustrator / Inkscape 自由组合的独立高清科研素材。默认处理全部独特且有独立使用价值的图形元素，输出真实透明背景 PNG；不是整图再设计，不是原图低分辨率抠图或插值放大。只重绘参考图实际存在的结构与状态，不自行扩展科学内容。若用户明确限制范围，优先遵守。

## 工具映射（运行前必读）

本 Skill 是"做什么"的规范，落地时按当前环境把下列动作映射到真实工具：

- **参考图局部裁剪**：`python scripts/crop_reference.py SRC.png --box x0,y0,x1,y1 --out crop.png`（或 `--regions regions.json --outdir crops/`）。主体外扩 10%–20%，保留完整轮廓，但不要把相邻文字/其他图元带进去；局部裁剪只作参考，不是最终素材。
- **图像生成/编辑**（按当前环境选其一）：
  - DSH 原生：`generate_image` / `edit_image`，用 `source_path` 或 `source_attachment_id` 传入参考，用 `aspect_ratio` / `size` 约束尺寸。
  - Magpie：`mcp__magpie-image__generate_image`，用 `reference_images`、`background="transparent"`、`size`、`resolution`、`model`（如 `codex/gpt-image`）。
- **透明背景**：必须**显式请求透明**（例如 `background="transparent"`）。生成后用脚本或代码校验 `alpha_min()==0` 且存在透明区；若拿到白底/棋盘底，先重生成或重新抠像，不能默认它有 alpha。
- **尺寸**：**以工具实际返回的尺寸为准**——很多模型/网关会忽略你传的 `size` 或比例。生成提示中要求"主体充满画面约 85%，四周留少量透明边"；生成后可等比例 `contain` 归一，再用 `python scripts/trim_assets.py <目录> --out <新目录>` 裁掉多余留白并重算有效尺寸。
- **质检**：`python scripts/audit_assets.py <PNG目录> --out <新目录> [--target 1024]`，输出 `audit.csv`、`audit.json`、三背景预览（白底/深灰底/棋盘格），并生成 `manifest.csv` 与 `quality_report.md` 骨架供人工填写。
- **能力探测（缺一不可）**：①能读到参考图内容；②有图像生成/编辑工具；③工具支持透明输出，或你能可靠抠像；④能写文件；⑤需要时能打包 ZIP、运行 Python/Pillow。任一项缺失按"能力降级"处理并如实说明，不编造能力。

## 执行顺序（必须完成而非仅描述）

### 1. 读取参考图，建立元素清单
- 使用最新且明确指定的参考图；多个参考图时按用户指示确定主图，不能擅自回到旧版。实际查看图像，不依赖文件名或历史概述。
- 分区域扫描，记录每个独特图元的 ID、类别、名称、原图位置、轮廓/朝向/比例、配色与透明状态、是否遮挡、组合关系、重绘路线、优先级。同步用 `scripts/crop_reference.py` 把关键图元的局部裁剪出来备用。
- 拆至最小**可独立复用**单元（如蛋白链、细胞核、单个磷脂、外显子、变异标记、单条 RNA）；不是每个像素或任意色块。相同图元去重，不同状态/颜色/形态分别保留。复杂结构同时保留独立部件与具有使用价值的完整组合版本。
- 默认不把正文文字、标题、装饰框列入素材；有意义的连接箭头、状态标记、图例符号需纳入。若图中结构被遮挡，仅在有合理依据时补全，并在清单注明推断。

### 2. 锁定原图样式与科学结构
- 提取原图的形态、长宽比、相对结构比例、描边、配色、渐变、光影、立体感、弯曲程度、方向和细节密度。原图是视觉基准，不沿用本 Skill 的案例配色到其他图。
- 保留原图示意图的表达层级，不把简化图标变成写实三维模型，不加无关高光、光晕、外阴影、纹理、文字或背景。
- 科学结构优先核对。发现明确错误时标注原图问题并提供建议；未经用户授权不静默改变含义。对于无法辨认的链或结构，采用中性名称并标记待核实，不将其冒充严格分子结构。

### 3. 重绘策略（默认混合高清模式）
- **A 单元素独立重绘**：复杂或关键素材（蛋白质/分子复合体、独立链、细胞/细胞核、仪器）及特别要求高清的图元。每次图像任务明确只生成指定图元，使用原图局部作为形态参考。按自然长宽比生成，不强迫所有图元填满正方形。若工具不支持目标比例，留白后等比例裁剪。
- **B 小批量素材板重绘**：简单且风格相近的元素（DNA/RNA、染色体、外显子、箭头等）可分组生成，优先每板 4–8 个，必要时减少数量。固定网格、充足透明间距、不重叠、无编号和文字；每个图元必须有足够原生像素。素材板只是中间产物，最终拆成独立文件。
- **C 矢量重建**：若工具支持，适合规则箭头、波形、外显子、染色体、膜等图元。保持原样式，用真实可编辑路径、形状或渐变；不得把内嵌 PNG 伪称为矢量。可由真实 SVG 直接渲染高清透明 PNG。
- **提示词**统一参考 [重绘提示模板](references/prompt-recipes.md)，含负向清单与模型-语言建议。
- **批量节奏（重要）**：一张图常含几十个图元，不要一次性全发。先列清单与数量，按优先级分批（建议每批 ≤8 个，单批失败不阻塞后续）；元素总数超过阈值（如 12 个）时先向用户确认范围与优先级，避免超时/超预算。
- **重试上限**：同一元素连续失败 ≥3 次即记为"未通过"并继续下一个，不无限重试；最终如实报告。
- **防跑偏**：若你只要单元素，却收到多个元素、整图或整张素材板，丢弃并只保留指定图元重画，不得拿素材板切图冒充逐张生成。
- 高质量目标：复杂重点图元的有效内容长边尽量达到 1024–2048 px 或更高；简单图元按用途和原生能力确定。不得通过插值制造虚假的高清。真实记录有效像素尺寸，未达到目标时标记并优先重绘或让主体填满画面后重生成。

### 4. 独立分割与透明处理
- 优先使用图像生成工具的真实透明输出；**必须先确认输出了真 alpha**，而不是默认它有。检查实际 Alpha，而非仅凭预览或扩展名。必要时对重绘图进行精细抠像，保留主体、内部空隙、真实的半透明部分；不能用简单阈值破坏浅色/虚线元素或边缘抗锯齿。
- 素材板按布局或人工边界拆分；避免把多部件组合（如剪接图、虚线图元）错误拆断。保留完整结构，移除相邻残留。不能通过强制清除所有低 Alpha 像素来处理正常渐变。
- 每个 PNG 只包含对应的一个独立单元（或清单中明确命名的完整组合），使用 RGBA，真实透明背景。交付前运行 `python scripts/trim_assets.py` 裁掉过多透明留白，保留每边约 3%–5% 的透明安全边；**不要裁到满画布**（否则质检会判"无透明像素"）。不做非等比缩放，不覆盖参考图或已有结果。

### 5. 质量验收与返工
- 先运行机器检查（如有 Python），再逐个在白底、深灰底和透明棋盘背景上目视对照参考图。详细标准见 [质量验收](references/quality-gates.md)。
- 运行 `python scripts/audit_assets.py <PNG目录> --out <新质检目录> --target 1024`；依赖 Pillow。输出机器检查 CSV/JSON、三背景预览、`manifest.csv` 骨架与 `quality_report.md` 骨架，脚本不修改源素材。机器检查不是生物学或视觉忠实度认证。
- 清单逐项映射真实输出；检查状态变体、关键独立部件、组合版是否齐全。修复或重新生成未达标的素材，不能以不相关素材凑数。将仍不合格、科学性存疑或缺失的条目标注，不能报告全量通过。

### 6. 交付（默认直接执行至可用结果）
- 新建独立输出目录，推荐 `scientific_assets_<figure>_<version>/`。采用稳定编号、类别与英文语义文件名，如 `001_genome_dna_normal.png`，按类别分目录；可提供中文名称映射。
- 交付 PNG 目录、可选真实 SVG 目录、元素清单 `manifest.csv`（UTF-8 BOM 便于 Excel；可用 `assets/manifest_template.csv` 起手）、编号+名称预览图、质量检查报告、ZIP 压缩包。ZIP 包含清单、预览、质量报告与素材；仅打包实际存在且检查过的文件。将失败候选放在交付目录之外或明确标为未通过。
- 清单至少记录 `id,category,name_zh,name_en,source_region,variant,parent_id,method,filename,width_px,height_px,effective_width_px,effective_height_px,alpha_status,visual_status,science_status,notes`。`method` 区分 `individual_generation`、`sheet_reconstruction`、`vector_reconstruction`；不将裁剪原图标为重绘。不能确定的字段写 unknown，不伪造数据。
- 最终说明实际完成数量、未完成项、是否存在素材板分割、有效分辨率限制和科学结构疑问。输出链接须对应真实文件；不保证当前工具无法验证的结果。

## 能力降级

先按"工具映射"里的能力探测清单核对。无图像生成能力时，规则图元可采用真实矢量重建并说明；复杂图元仅提供可执行重绘任务清单/提示词并报告缺失，不假装已生成。若只有图像生成没有文件系统，交付当前能生成的独立图并说明无法打包。若工具不支持透明输出也抠不好像，如实说明该限制。不要擅自把私有参考图上传至外部服务；使用外部工具须遵循环境授权。

## 案例（非固定清单）

可参考 [HLA 示例与回归验收](references/hla-example.md) 理解最小拆解粒度。不要将案例元素强加到其他参考图。默认不需要用户逐项确认，除非歧义会造成不可逆或重大的科学含义变更（或元素数量超过批量阈值）；否则采用合理假设并记录。

## 版本与维护

当前版本 1.1.0，变更见 [CHANGELOG](references/CHANGELOG.md)；中文安装与调用说明见 [install-zh](references/install-zh.md)。
