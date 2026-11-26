# Scientific Asset Reconstruction｜科研插图元素重建 · 安装与使用说明

版本 1.1.0 · 通用 Agent Skill 安装与使用说明

本技能根据科研插图元素拆解任务整理：参考图识别、最小粒度拆解、原图风格锁定、复杂图元独立重绘、简单图元小批量重绘、透明处理、逐图质量验收及打包。它是工作流说明与辅助脚本，不是独立的图像生成模型。

## 目录结构

```
scientific-asset-reconstruction/
├── SKILL.md                 # 技能入口（必须叫这个名字）
├── references/
│   ├── prompt-recipes.md    # 重绘提示模板（含负向清单、模型-语言建议）
│   ├── quality-gates.md     # 质量验收与交付规范
│   ├── hla-example.md       # HLA 案例与回归场景
│   ├── install-zh.md        # 本安装说明
│   └── CHANGELOG.md         # 变更记录
├── scripts/
│   ├── audit_assets.py      # 只读质检：CSV/JSON + 三背景预览 + manifest/quality_report 骨架
│   ├── crop_reference.py    # 参考图局部裁剪
│   └── trim_assets.py       # 裁透明留白 + 报有效尺寸
└── assets/
    └── manifest_template.csv
```

## 一、直接安装（推荐）

把 `scientific-asset-reconstruction.zip` 交给你的 Agent，或解压为 `scientific-asset-reconstruction/`。该目录遵循通用 Agent Skills 规范，入口 `SKILL.md` 带 YAML 元数据。**入口文件名必须是 `SKILL.md`，目录名必须与 `name` 一致（`scientific-asset-reconstruction`）**，否则部分客户端无法发现技能。不同 Agent 的实际安装位置和图像能力可能不同，请由 Agent 根据当前运行环境确认；不要假定所有客户端共享一个目录。

复制以下指令给 Agent：

> 请读取我提供的 scientific-asset-reconstruction.zip，并解压检查目录。使用当前环境的 Skill 安装/创建机制，将其中的 scientific-asset-reconstruction 作为可复用的用户级 Skill 注册，保留 SKILL.md、references/、scripts/ 和 assets/ 的相对路径。如果当前环境没有原生 Skill 注册功能，请把该目录放到当前 Agent 支持的持久化技能目录，或明确说明只能通过手动读取 SKILL.md 使用，不要假装已安装。不要删除或覆盖已有技能；如同名技能已存在，报告版本并使用非破坏性方式更新。检查 YAML 元数据、引用文件和脚本依赖，按 SKILL.md 的"能力探测"检查是否有参考图视觉读取、图像生成/编辑、真实透明 PNG 输出及本地文件处理能力。若缺少依赖或权限，说明并请求必要授权，不要编造可用能力。完成后告知真实安装路径、调用方式、检查结果和限制。

## 二、以后怎么调用

上传已经定稿或基本定稿的参考图，然后输入：

> 使用 Scientific Asset Reconstruction（科研插图元素重建）Skill，将本次参考图中所有具有独立使用价值的图形元素按最小粒度重绘。默认混合高清模式，保持原图比例与风格，不拉伸、不插值放大。最终提供独立透明 PNG、元素清单、预览及 ZIP 压缩包。

只需要复杂部件时：

> 使用 scientific-asset-reconstruction，仅重绘图中左侧的蛋白链、细胞膜和抗原肽，每个图元单独生成，保持原图比例，不使用素材板。

追求最高分辨率时：

> 使用 scientific-asset-reconstruction 的逐个重绘模式，禁止素材板分割替代单元素生成。让每个主体充满画面约 85%，重点素材有效内容长边尽可能达到 1024–2048 px 以上，保持真实透明背景，未达到目标的单独标记。

## 三、辅助脚本

依赖 Python 3 和 Pillow（可使用已存在的环境；缺失时经用户允许安装 `python -m pip install Pillow`）。

```bash
# 1) 从参考图裁出某个图元的局部（x0,y0,x1,y1 为像素坐标）
python scientific-asset-reconstruction/scripts/crop_reference.py ref.png --box 40,140,360,410 --out crops/hla1.png

# 2) 生成/编辑后，裁掉多余透明留白并报告有效尺寸
python scientific-asset-reconstruction/scripts/trim_assets.py ./output/png_raw --out ./output/png --target 1024

# 3) 只读质检（不改源素材）
python scientific-asset-reconstruction/scripts/audit_assets.py ./output/png --out ./output/audit_v1 --target 1024
```

`audit_assets.py` 输出 `audit.csv`、`audit.json`、三背景预览（白底/深灰底/棋盘格）、`manifest.csv` 与 `quality_report.md` 骨架；输入目录只读，质检输出必须为新目录且不在输入 PNG 目录内。报告的 `pass` 只表示机器检查无已定义警告；`review` 需要人工复核，`fail` 代表格式或透明度等硬性问题。此脚本不能证明原生高清、视觉忠实度、无光晕或生物学正确性，必须由 Agent 继续目视复核。

## 四、验收

用一张有 5–10 个图元的小参考图做首次端到端验证（需具备绘图能力），核对独立 PNG、透明度、有效分辨率、清单覆盖度、预览及压缩包；再用于正式论文图。没有图像生成工具的 Agent 无法仅通过安装此 Skill 获得该能力。

参考规范：https://agentskills.io/specification
