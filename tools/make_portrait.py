#!/usr/bin/env python3
"""Convert a profile photo into ASCII rows for the banner portrait.

Requires: pip install pillow numpy "rembg[cpu]"
Usage:    python3 tools/make_portrait.py photo.jpeg

Writes tools/portrait.json with two character grids:
  "dark"  - dense characters = bright pixels (light glyphs on a dark canvas)
  "light" - dense characters = dark pixels   (dark glyphs on a light canvas)
The original photo is never embedded in the SVG output.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

COLS = 100
CHAR_ASPECT = 0.6          # monospace advance / line height
RAMP = " .,:;-=+*#%@"      # no XML-special characters
CROP_TOP = 24              # trims the decorative strip above the head in the source photo
CROP_BOTTOM = 990          # trims the dark frame below the shoulders


def cutout(path):
    from rembg import new_session, remove
    img = Image.open(path).convert("RGB")
    return remove(img, session=new_session("u2net_human_seg"))


def grid(img):
    img = img.crop((0, CROP_TOP, img.width, min(CROP_BOTTOM, img.height)))
    rows = round(COLS * img.height / img.width * CHAR_ASPECT)
    rgba = np.asarray(img).astype(float) / 255
    lum = 0.2126 * rgba[..., 0] + 0.7152 * rgba[..., 1] + 0.0722 * rgba[..., 2]

    # local contrast: keeps glasses, beard and hair edges readable
    blur = np.asarray(Image.fromarray((lum * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(28))).astype(float) / 255
    detail = np.clip((lum - blur) * 2.2 + 0.5, 0, 1)

    def down(x):
        return np.asarray(Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8))
                          .resize((COLS, rows), Image.BOX)).astype(float) / 255

    mask = down(rgba[..., 3]) > 0.5
    base = down(lum)
    lo, hi = np.percentile(base[mask], [3, 97])
    base = np.clip((base - lo) / (hi - lo), 0, 1)
    v = np.clip(0.62 * base + 0.38 * (0.5 + (down(detail) - 0.5) * 2.0), 0, 1)
    v = np.clip(0.75 * v + 0.25 * base, 0, 1)

    def render(dense, floor=0.1):
        lines = []
        for y in range(rows):
            row = ""
            for x in range(COLS):
                if not mask[y, x]:
                    row += " "
                    continue
                d = floor + (1 - floor) * dense[y, x]
                row += RAMP[max(1, min(len(RAMP) - 1, int(d * (len(RAMP) - 1) + 0.5)))]
            lines.append(row.rstrip())
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        return lines

    return {"cols": COLS, "dark": render(v ** 1.0), "light": render((1 - v) ** 1.1)}


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "photo.jpeg"
    data = grid(cutout(src))
    out = Path(__file__).with_name("portrait.json")
    out.write_text(json.dumps(data, indent=1))
    print(f"wrote {out} ({len(data['dark'])} rows x {data['cols']} cols)")
