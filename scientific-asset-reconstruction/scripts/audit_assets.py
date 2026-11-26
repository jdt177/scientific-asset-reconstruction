#!/usr/bin/env python3
"""Read-only PNG audit; writes new CSV, JSON, three-background previews, and
manifest.csv / quality_report.md skeletons. Never alters the source images.

Usage:
  python audit_assets.py INPUT_DIR --out NEW_REPORT_DIR [--target 1024]
Requires Python 3 and Pillow. Machine checks are not a visual or scientific
certification.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps


def load_font(size=14):
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in candidates:
        try:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def checkerboard(w, h, s=14):
    im = Image.new("RGB", (w, h), "#ffffff")
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if ((x // s) + (y // s)) % 2 == 0:
                d.rectangle((x, y, x + s - 1, y + s - 1), fill="#d0d0d0")
    return im


def inspect(path, root, target, seen):
    row = {'file': path.relative_to(root).as_posix(), 'mode': '', 'width_px': '',
           'height_px': '', 'effective_width_px': '', 'effective_height_px': '',
           'alpha_min': '', 'alpha_max': '', 'transparent_border': '',
           'duplicate_of': '', 'machine_status': '', 'warnings': ''}
    warnings, failures = [], []
    try:
        with Image.open(path) as im:
            im.load()
            if im.format != 'PNG':
                failures.append('not_png_format')
            row.update(mode=im.mode, width_px=im.width, height_px=im.height)
            if im.mode != 'RGBA':
                failures.append('not_RGBA')
            rgba = im.convert('RGBA')
            a = rgba.getchannel('A')
            lo, hi = a.getextrema()
            row.update(alpha_min=lo, alpha_max=hi)
            if lo != 0:
                failures.append('no_fully_transparent_pixels')
            if hi == 0:
                failures.append('empty_image')
            if 0 < hi < 255:
                warnings.append('entire_subject_semitransparent_review')
            b = a.getbbox()
            border_ok = bool(b and b[0] > 0 and b[1] > 0 and b[2] < im.width and b[3] < im.height)
            row['transparent_border'] = border_ok
            if not border_ok and b:
                sides = []
                if b[0] <= 0:
                    sides.append('left')
                if b[1] <= 0:
                    sides.append('top')
                if b[2] >= im.width:
                    sides.append('right')
                if b[3] >= im.height:
                    sides.append('bottom')
                warnings.append('edge_contact_review(' + '/'.join(sides) + ')')
            eff = a.point(lambda v: 255 if v >= 16 else 0).getbbox()
            if eff:
                w, h = eff[2] - eff[0], eff[3] - eff[1]
                row.update(effective_width_px=w, effective_height_px=h)
                if max(w, h) < target:
                    warnings.append('effective_long_edge_below_target_review')
            elif hi > 0:
                warnings.append('very_faint_asset_review')
            normalized = rgba.copy()
            normalized.paste((0, 0, 0, 0), mask=a.point(lambda v: 255 if v == 0 else 0))
            key = hashlib.sha256(f'{im.width}x{im.height}:'.encode() + normalized.tobytes()).hexdigest()
            if key in seen:
                row['duplicate_of'] = seen[key]
                warnings.append('exact_pixel_duplicate_review')
            else:
                seen[key] = row['file']
    except Exception as exc:
        failures.append(f'unreadable: {type(exc).__name__}: {exc}')
    row['machine_status'] = 'fail' if failures else ('review' if warnings else 'pass')
    row['warnings'] = '; '.join(failures + warnings)
    return row


def make_previews(paths, rows, out):
    font = load_font(14)
    small = load_font(12)
    cols, per_page, cw, ch = 2, 10, 620, 215
    colors = [('#ffffff', '白底'), ('#333333', '深灰底'), ('checker', '棋盘格')]
    for start in range(0, len(paths), per_page):
        subset = paths[start:start + per_page]
        nr = (len(subset) + cols - 1) // cols
        canvas = Image.new('RGB', (cols * cw, nr * ch), '#e5e7eb')
        d = ImageDraw.Draw(canvas)
        for j, path in enumerate(subset):
            x, y = j % cols * cw, j // cols * ch
            d.rectangle((x + 4, y + 4, x + cw - 4, y + ch - 4), fill='white')
            r = rows[start + j]
            label = f'{start + j + 1:03d} {path.stem}'[:56]
            d.text((x + 10, y + 8), label, fill='#172033', font=font)
            tw, th, gap = 188, 122, 6
            for k, (color, cname) in enumerate(colors):
                bx = x + 10 + k * (tw + gap)
                by = y + 30
                tile = checkerboard(tw, th) if color == 'checker' else Image.new('RGB', (tw, th), color)
                try:
                    with Image.open(path) as im:
                        rgba = im.convert('RGBA')
                        bb = rgba.getchannel('A').getbbox()
                        if bb:
                            thumb = ImageOps.contain(rgba.crop(bb), (tw - 10, th - 10), Image.Resampling.LANCZOS)
                            tile.paste(thumb, ((tw - thumb.width) // 2, (th - thumb.height) // 2), thumb)
                except Exception:
                    ImageDraw.Draw(tile).text((8, 50), 'unreadable', fill='#cc4444', font=small)
                canvas.paste(tile.convert('RGB'), (bx, by))
                d.rectangle((bx, by, bx + tw - 1, by + th - 1), outline='#b0b0b0')
                d.text((bx + 4, by + th + 2), cname, fill='#666666', font=small)
            d.text((x + 10, y + ch - 26),
                   f"{r['effective_width_px']} x {r['effective_height_px']} px | {r['machine_status']} | {r['warnings'][:70]}",
                   fill='#333333', font=small)
        canvas.save(out / f'preview_{start // per_page + 1:02d}.png')


def write_manifest(rows, out):
    fields = ['id', 'category', 'name_zh', 'name_en', 'source_region', 'variant',
              'parent_id', 'method', 'filename', 'width_px', 'height_px',
              'effective_width_px', 'effective_height_px', 'alpha_status',
              'visual_status', 'science_status', 'notes']
    with (out / 'manifest.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            stem = Path(r['file']).stem
            w.writerow({
                'id': f'{i:03d}', 'category': '', 'name_zh': '', 'name_en': stem,
                'source_region': '', 'variant': '', 'parent_id': '',
                'method': 'individual_generation', 'filename': r['file'],
                'width_px': r['width_px'], 'height_px': r['height_px'],
                'effective_width_px': r['effective_width_px'],
                'effective_height_px': r['effective_height_px'],
                'alpha_status': 'pass' if 'no_fully_transparent_pixels' not in r['warnings'] and r['mode'] == 'RGBA' else 'fail',
                'visual_status': 'review', 'science_status': 'unknown', 'notes': '',
            })


def write_quality_report(rows, counts, out, target):
    lines = ['# 质量检查报告（骨架，需人工补全）', '',
             f'- 素材总数：{len(rows)}',
             f'- 机器判定：pass={counts["pass"]} / review={counts["review"]} / fail={counts["fail"]}',
             f'- 有效长边目标：{target} px',
             '- 机器检查不等于视觉/科学认证，以下需人工填写。', '',
             '## 逐图机器结果', '',
             '| 文件 | 有效尺寸 | 判定 | 警告 |', '|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['file']} | {r['effective_width_px']}x{r['effective_height_px']} | {r['machine_status']} | {r['warnings']} |")
    lines += ['', '## 人工复核（待填）', '',
              '- [ ] 视觉忠实度（轮廓/配色/比例/风格）',
              '- [ ] 科学结构（含义/标注语义/疑问记录）',
              '- [ ] 半透明与虚线细节',
              '- [ ] 有效分辨率是否满足排版', '',
              '## 未完成 / 未通过项（待填）', '', '- ', '',
              '## 限制与备注（待填）', '', '- ']
    (out / 'quality_report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input_dir', type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--target', type=int, default=1024, help='effective long-edge review threshold, not a hard fail')
    args = p.parse_args()
    root = args.input_dir.resolve()
    out = args.out.resolve()
    if not root.is_dir():
        p.error('input_dir must be an existing directory')
    if args.target < 1:
        p.error('--target must be positive')
    if out == root or root in out.parents:
        p.error('report directory must be outside input directory')
    paths = sorted((f for f in root.rglob('*') if f.is_file() and f.suffix.lower() == '.png'),
                   key=lambda f: f.relative_to(root).as_posix())
    if not paths:
        p.error('no PNG files found')
    if out.exists():
        p.error('report directory already exists; choose a new directory')
    out.mkdir(parents=True)
    seen = {}
    rows = [inspect(f, root, args.target, seen) for f in paths]
    with (out / 'audit.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    counts = {s: sum(r['machine_status'] == s for r in rows) for s in ('pass', 'review', 'fail')}
    report = {'total': len(rows), 'counts': counts, 'effective_long_edge_target': args.target,
              'visual_and_scientific_review': 'not performed by script', 'files': rows}
    (out / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    make_previews(paths, rows, out)
    write_manifest(rows, out)
    write_quality_report(rows, counts, out, args.target)
    print(json.dumps({'total': len(rows), **counts, 'report_dir': str(out)}, ensure_ascii=False))
    return 1 if counts['fail'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
