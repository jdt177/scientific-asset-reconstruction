# 重绘提示模板

使用当前参考图及必要的局部参考。下列方括号为 Agent 填写字段，不是硬编码的生成参数。优先用工具真实支持的透明参数、尺寸和参考图输入；不编造接口。不要把整个元素清单附在单元素生成任务中，避免模型误生成整张素材板。

## 通用负向清单（每个提示都带上）

> 不出现：整张参考图、多个元素/素材板、文字与编号、图例、边框、外阴影、光晕、白底或棋盘纹理、写实照片感、与参考无关的装饰。不要拉伸或非等比变形。

## 模型-语言建议

- GPT-Image 系列（含本地 codex/gpt-image 网关）：英文提示更稳，先英文后中文注释。
- 千问 / Qwen-Image：中文提示可用，术语可中文。
- Gemini 图像：中文英文均可，注意它更"听话"但可能把元素画得更写实，强调"保持示意图风格"。
- 若某模型反复忽略透明或尺寸：改用该模型支持的显式参数（如 `background=transparent`、`size`），并生成后统一裁剪归一。

## 裁剪上下文量（经验值）

- 局部参考在主体外扩约 10%–20%，确保含完整轮廓和少量背景以锁定风格；
- 不要把相邻文字、其他图元、面板边框带进参考，否则模型会复现它们。

## A. 单元素（复杂结构优先）

> 仅重绘参考图中 [位置/元素名称] 这一个图元。保持原始轮廓、朝向、自然长宽比、各结构比例、[实际配色]、描边、渐变与光影风格。细节和结构关系以局部参考图为准；被遮挡部分仅按已知形态合理补全。高清、边缘清楚、抗锯齿。主体充满画面约 85%、四周留少量透明边；单个元素独立居中，真实 Alpha 透明背景。不拉伸、不变形，不加文字、图例、边框、阴影、光晕、其他元素或背景。不要重画整张参考图，也不要生成多元素素材板。

英文辅助（工具对英文更稳定时）：

> Reconstruct only the specified element [element] from the provided reference crop. Match the exact silhouette, orientation, natural aspect ratio, relative domain proportions, palette, outline weight, gradients and scientific illustration style. One isolated asset only, filling about 85% of the frame with a small clear margin, high native detail, clean anti-aliased edges, true alpha transparency. No labels, frame, other objects, glow, external shadow, checkerboard texture or stretching. Do not reproduce the whole figure.

## B. 小批量素材板（仅在用户允许批量方式时）

> 参考同一图的 [区域]，重绘以下 [4–8] 个简单图元：[明确编号的元素清单]。采用彼此独立且足够宽松的网格单元；无文字和可见编号，按清单顺序排列，互不接触或重叠。保留各元素原比例，不统一拉伸。真实 Alpha 透明背景；每个元素尽可能占据其单元的有效面积，保持原图统一风格。不得增加清单以外的元素。该图仅是中间素材板，随后逐一分割为独立 PNG。

若图元较细、近似或很长，减少每板数量以避免有效分辨率过低。发现漏项或错位时重新生成对应项。素材板切分需按 alpha 投影或人工边界进行，不要盲目按网格坐标硬切。

## C. 可编辑矢量

依原图测定形状比例、曲线、描边、渐变。采用 viewBox 和真实 SVG 路径/形状；渲染 PNG 时保持比例，背景透明；用渲染图对照参考确认视觉效果。复杂蛋白不要用粗糙几何图形强行代替。矢量版如与原图存在明显风格差异，应注明或不交付。

## D. 跑偏补救

若返回的是整图、多个元素或素材板而你只要单元素：丢弃该结果，重新用更小的任务范围（只描述一个图元）生成，或改用矢量重建；不得把素材板切图冒充逐张生成，并在报告里如实记录。
