#!/usr/bin/env python3
"""Trim excess transparent padding from RGBA assets and keep a small safe margin.

Usage:
  python trim_assets.py INPUT_DIR --out NEW_DIR [--margin 0.04] [--target 1024]

For each PNG: crop to the alpha>=1 bounding box, add a margin of `margin * long_side`
transparent pixels, save RGBA to NEW_DIR, and report the *effective* content size
(the alpha>=16 long edge). Never upscales: if the native subject is below `target`,
it is flagged so you can regenerate it larger / ask the model to fill the frame.
Read-only on INPUT_DIR; writes only into NEW_DIR (must not already exist).
Requires Pillow.
"""
import argparse, os
from pathlib import Path
from PIL import Image, ImageOps

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input_dir", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--margin", type=float, default=0.04)
    ap.add_argument("--target", type=int, default=1024)
    a = ap.parse_args()
    if not a.input_dir.is_dir():
        ap.error("input_dir must be a directory")
    if a.out.exists():
        ap.error("out dir already exists; choose a new one")
    a.out.mkdir(parents=True)
    for p in sorted(a.input_dir.rglob("*.png")):
        im = Image.open(p).convert("RGBA")
        alpha = im.getchannel("A")
        b = alpha.getbbox()
        if not b:
            print(f"SKIP empty {p.name}")
            continue
        core = im.crop(b)
        m = int(round(max(core.width, core.height) * a.margin))
        canvas = Image.new("RGBA", (core.width + 2 * m, core.height + 2 * m), (0, 0, 0, 0))
        canvas.paste(core, (m, m))
        rel = p.relative_to(a.input_dir)
        dst = a.out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(dst)
        eff = alpha.crop(b).point(lambda v: 255 if v >= 16 else 0).getbbox()
        ew, eh = (eff[2]-eff[0], eff[3]-eff[1]) if eff else (0, 0)
        flag = "" if max(ew, eh) >= a.target else f"  -> BELOW target {a.target}, regenerate larger"
        print(f"{dst}\tcanvas {canvas.width}x{canvas.height}\teffective {ew}x{eh}{flag}")

if __name__ == "__main__":
    main()
