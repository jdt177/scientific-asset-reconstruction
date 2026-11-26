#!/usr/bin/env python3
"""Crop local reference regions from a source figure for use as per-element references.

Usage:
  python crop_reference.py SRC.png --box X0,Y0,X1,Y1 --out region.png [--scale-to WxH]
  python crop_reference.py SRC.png --regions regions.json --outdir crops/

regions.json: {"hla1": [40,140,360,410], "antibody": [1160,600,1360,760]}
Boxes are in pixels of the source image (x0,y0,x1,y1). Prints the saved path and size.
Depends on Pillow only. Read-only on the source; never overwrites it.
"""
import argparse, json, os
from PIL import Image

def crop_one(im, box, out_path):
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(im.width, x1), min(im.height, y1)
    if x1 <= x0 or y1 <= y0:
        raise ValueError(f"invalid box {box} for image {im.size}")
    c = im.crop((x0, y0, x1, y1))
    c.save(out_path)
    print(f"{out_path}\t{c.width}x{c.height}")

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src")
    ap.add_argument("--box")
    ap.add_argument("--out")
    ap.add_argument("--regions")
    ap.add_argument("--outdir", default="crops")
    a = ap.parse_args()
    im = Image.open(a.src)
    im.load()
    if a.regions:
        os.makedirs(a.outdir, exist_ok=True)
        data = json.load(open(a.regions, encoding="utf-8"))
        for name, box in data.items():
            crop_one(im, box, os.path.join(a.outdir, f"{name}.png"))
    elif a.box and a.out:
        crop_one(im, a.box.split(","), a.out)
    else:
        ap.error("provide --box/--out or --regions/--outdir")

if __name__ == "__main__":
    main()
