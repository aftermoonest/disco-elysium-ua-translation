"""Repaint loading-panel-de / saving-panel-de in a COPY of images_dyslexic/german with Ukrainian text.

Usage: python -I tools/make_loading_panels.py <src images_dyslexic/german> <out bundle> [<preview dir>]

The originals are white pixels whose alpha carries the picture: thin text (alpha ~25/255) on the left and a
soft gradient block (alpha up to ~87) on the right where the spinner is drawn. We keep the right-hand block
pixels untouched and repaint only the text area, matching text alpha, baseline and left margin.
Font: Segoe UI Regular from the system (test only: check the font licence before shipping a release).
Never writes to the game folder.
"""
import sys
from pathlib import Path

import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
FONT = r"C:\Windows\Fonts\segoeui.ttf"
TEXTS = {"loading-panel-de": "ЗАВАНТАЖЕННЯ", "saving-panel-de": "ЗБЕРЕЖЕННЯ"}
LEFT, BASELINE, CAP_H, MIN_CAP = 4, 30, 16, 11
SS = 8  # supersampling


def block_start(a):
    """x of the block's left edge, read on a text-free row (y=8) above the letters."""
    return int(np.argmax(a[8] > 30))


def render(text, width_limit):
    cap = CAP_H
    while True:
        # Segoe cap height ~0.7 em
        size = cap / 0.70
        font = ImageFont.truetype(FONT, int(round(size * SS)))
        spacing = 0.06 * size * SS  # slightly wide tracking like the original
        w = sum(font.getlength(c) + spacing for c in text) - spacing
        if w / SS <= width_limit or cap <= MIN_CAP:
            return font, spacing, w / SS, cap
        cap -= 0.5


def paint(tex_img, text):
    im = np.array(tex_img.convert("RGBA"))
    a = im[..., 3]
    bx = block_start(a)
    text_a = a[:, : bx - 3]
    target = max(24.0, float(np.percentile(text_a[text_a > 3], 97)))  # original text peak alpha (floor: both panels share one material)
    font, spacing, w, cap = render(text, bx - 4 - LEFT)
    H, W = a.shape
    canvas = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(canvas)
    x = LEFT * SS
    for c in text:
        d.text((x, BASELINE * SS), c, font=font, fill=255, anchor="ls")
        x += font.getlength(c) + spacing
    cov = np.array(canvas.resize((W, H), Image.LANCZOS), dtype=np.float32) / 255.0
    new = im.copy()
    new[..., :3] = 255
    txt = np.clip(cov * target, 0, 255)
    xs = np.arange(W)[None, :]
    out = np.where(xs < bx, txt, a.astype(np.float32))
    # The old (longer) German text can run into the first block columns: rebuild rows 13..31 there from the
    # clean bottom row (y=30 is below the old text's body only in the block columns we copy).
    out[13:32, bx: bx + 10] = a[30, bx: bx + 10][None, :].astype(np.float32)
    new[..., 3] = np.clip(out, 0, 255).astype(np.uint8)
    return Image.fromarray(new, "RGBA"), dict(block_x=bx, target_alpha=round(target, 1), cap=cap, width=round(w, 1))


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    prev = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    env = UnityPy.load(str(src))
    done = 0
    for o in env.objects:
        if o.type.name != "Texture2D":
            continue
        d = o.read()
        if d.m_Name not in TEXTS:
            continue
        old = d.image
        new, info = paint(old, TEXTS[d.m_Name])
        print(d.m_Name, o.path_id, old.size, info)
        d.image = new
        d.save()
        done += 1
        if prev:
            prev.mkdir(parents=True, exist_ok=True)
            for tag, img in (("old", old), ("new", new)):
                bg = Image.new("RGBA", img.size, (60, 60, 60, 255))
                bg.alpha_composite(img.convert("RGBA"))
                bg.resize((img.width * 3, img.height * 3), Image.NEAREST).save(prev / f"dys_{d.m_Name}_{tag}.png")
    assert done == 2, done
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(env.file.save(packer="lz4"))
    print("written", dst, dst.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
