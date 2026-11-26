# Scientific Asset Reconstruction

> English | [中文](README.md)

**An Agent Skill that decomposes an existing scientific / medical figure into isolated, reusable,
high-resolution transparent PNG assets.**

It reads a finalized scientific figure, identifies every graphic element that is independently
reusable, redraws each one (individually or in small sheets) as a **true-alpha, high-resolution PNG**,
then audits and packages the results — so you can freely re-compose figures in PowerPoint, Illustrator
or Inkscape. It is **not** whole-figure redesign, and **not** low-res cropping or upscaling.

Works with any agent that can read images and call an image generation/editing tool (GPT-Image,
Qwen-Image, Gemini, etc.). The bundled scripts need only Python 3 + Pillow.

## Features

- **Minimum reusable granularity**: protein chains, nuclei, single phospholipids, exons, variant
  markers, single RNA strands, instruments, etc. become separate assets.
- **Style locking**: keeps silhouette, proportions, palette, gradients and shading of the original;
  never applies the example palette or turns icons into realistic 3D.
- **True transparent PNG**: requests and verifies real alpha; falls back to matting when needed.
- **Three redraw routes**: single-element, small-batch sheet, and vector reconstruction.
- **Machine QC + human review**: three-background previews, effective size, edge-contact and duplicate
  checks; emits `manifest.csv` and `quality_report.md` skeletons.
- **Deliverable ZIP**: PNG folder, manifest, previews and quality report packed together.
- **Honest boundaries**: no faked capabilities, no passing cropped originals off as redraws, no silent
  changes to scientific meaning.

## Structure

```
scientific-asset-reconstruction/      # the skill (drop into your agent's skills directory)
├── SKILL.md                          # entry (must be named exactly SKILL.md)
├── references/
│   ├── prompt-recipes.md             # redraw prompts, negative list, model/language tips
│   ├── quality-gates.md              # acceptance & delivery rules
│   ├── hla-example.md                # worked example + regression scenarios
│   ├── install-zh.md                 # Chinese install/usage notes
│   └── CHANGELOG.md
├── scripts/
│   ├── audit_assets.py               # read-only QC: CSV/JSON + 3-background previews + skeletons
│   ├── crop_reference.py             # crop reference regions
│   └── trim_assets.py                # trim transparent padding + report effective size
└── assets/
    └── manifest_template.csv
```

## Install

1. Download `scientific-asset-reconstruction.zip` and extract `scientific-asset-reconstruction/`.
2. Drop it into your agent's skills directory, or have the agent read `SKILL.md` manually.
   The entry file must be `SKILL.md` and the folder must be `scientific-asset-reconstruction`
   (matching `name`).
3. Ensure the agent has: image reading, image generation/editing, transparent output (or reliable
   matting), file writing, Python + Pillow.

## Quick start

Upload a finalized reference figure, then ask your agent:

> Use the Scientific Asset Reconstruction Skill to redraw every independently usable element at the
> minimal granularity, keep the original proportions and style, and output separate transparent PNGs,
> a manifest, a preview and a ZIP.

Complex parts only:

> Use scientific-asset-reconstruction to redraw only the left-side protein chain, membrane and peptide,
> each generated separately, without sheets.

## Scripts

```bash
python scientific-asset-reconstruction/scripts/crop_reference.py ref.png --box 40,140,360,410 --out crops/hla1.png
python scientific-asset-reconstruction/scripts/trim_assets.py ./out/png_raw --out ./out/png --target 1024
python scientific-asset-reconstruction/scripts/audit_assets.py ./out/png --out ./out/audit_v1 --target 1024
```

Requires `python -m pip install Pillow`.

## Example

See [`docs/examples/`](docs/examples/): an end-to-end demo (AI-generated original schematic →
decomposition → isolated transparent assets). The example image is AI-generated and contains no
third-party copyrighted material.

## Version

Current 1.1.0 — see [`references/CHANGELOG.md`](scientific-asset-reconstruction/references/CHANGELOG.md).

## Limitations

- Transparency depends on the image tool (some models need explicit `background="transparent"`);
  if true alpha is unavailable, regenerate or matte.
- Models/gateways often ignore `size`/ratio; trust the returned size, then `trim_assets.py` and verify
  the **effective** size before delivery.
- Machine QC checks file facts only; it does not certify visual fidelity or biological correctness —
  always do a human visual review.
- No automatic "sheet splitter" script; for batch (B) mode split by alpha projection / manual bounds.

## License

[MIT](LICENSE). This repository ships no third-party reference images or generated outputs; the
example is AI-generated. Confirm copyright/licensing before using others' figures.
