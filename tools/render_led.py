#!/usr/bin/env python3
"""Renders 32x8 frames as LED-matrix images for the docs, all in one style.

Frames come from three places, read back to their exact 32x8 pixels:
  - the test suite's previews (test_mtafeed with MTA_PREVIEW_DIR set): <name>.ppm, 408x120
  - tools/preview_clock.cpp (stock Time/Date apps): clock_time.ppm / clock_date.ppm, 408x120
  - a real clock: GET http://CLOCK/api/v1/display/screen saved as JSON, or a 640x160 capture

Usage:
  tools/render_led.py FRAMES_DIR            writes preview/*.png and docs/images/*

FRAMES_DIR holds the raw frames; preview/ only ever receives output (never read back).
"""

import glob
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
W, H = 32, 8
CELL = 16            # pixels per LED in the output
OFF = (26, 26, 30)   # an unlit LED
PANEL = (10, 10, 12)


def grid_from_image(path):
    """32x8 RGB grid from a preview image (408x120, 12-px cells, 1-cell margin) or a 640x160
    capture (20-px cells, no margin). Unlit cells come back as None."""
    im = Image.open(path).convert("RGB")
    if im.size == (408, 120):
        cell, off = 12, 12
    elif im.size == (640, 160):
        cell, off = 20, 0
    else:
        raise ValueError(f"{path}: unknown frame size {im.size}")
    g = []
    for y in range(H):
        row = []
        for x in range(W):
            c = im.getpixel((off + x * cell + cell // 2, off + y * cell + cell // 2))
            row.append(None if max(c) <= 0x18 else c)
        g.append(row)
    return g


def grid_from_json(path):
    d = json.load(open(path))
    p = d["pixels"]
    return [[(lambda v: None if not v else ((v >> 16) & 255, (v >> 8) & 255, v & 255))(p[y * W + x])
             for x in range(W)] for y in range(H)]


def load(path):
    return grid_from_json(path) if path.endswith(".json") else grid_from_image(path)


def render(grid, cell=CELL, margin=None):
    """The matrix alone: round LEDs, unlit ones faintly visible, a soft glow around lit ones."""
    m = cell if margin is None else margin
    size = (W * cell + 2 * m, H * cell + 2 * m)
    base = Image.new("RGB", size, PANEL)
    lit = Image.new("RGB", size, (0, 0, 0))
    db, dl = ImageDraw.Draw(base), ImageDraw.Draw(lit)
    r = cell * 0.40
    for y in range(H):
        for x in range(W):
            cx, cy = m + x * cell + cell / 2, m + y * cell + cell / 2
            box = [cx - r, cy - r, cx + r, cy + r]
            c = grid[y][x]
            db.ellipse(box, fill=c or OFF)
            if c:
                dl.ellipse(box, fill=c)
    glow = lit.filter(ImageFilter.GaussianBlur(cell * 0.45))
    # the glow goes on top of the panel; a screen blend keeps the lit LEDs crisp
    return ImageChops.screen(base, Image.eval(glow, lambda v: int(v * 0.55)))


def device(grid, scale=1.0):
    """The matrix in a TC001-like body: a dark rounded case with the display behind a smoked front."""
    cell = int(22 * scale)
    mat = render(grid, cell=cell, margin=cell // 2)
    pad_x, pad_y = int(46 * scale), int(34 * scale)
    bw, bh = mat.width + 2 * pad_x, mat.height + 2 * pad_y
    shadow = int(40 * scale)
    out = Image.new("RGBA", (bw + 2 * shadow, bh + 2 * shadow), (0, 0, 0, 0))
    sh = Image.new("L", out.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle([shadow, shadow + 10, shadow + bw, shadow + bh + 10],
                                         radius=int(34 * scale), fill=150)
    out.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(18 * scale)))
    body = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=int(34 * scale), fill=(28, 28, 32, 255))
    bd.rounded_rectangle([6, 6, bw - 7, bh - 7], radius=int(30 * scale), fill=(17, 17, 20, 255))
    body.paste(mat, (pad_x, pad_y))
    # a faint highlight across the top of the front glass
    hl = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(hl).rounded_rectangle([10, 10, bw - 11, bh // 3], radius=int(26 * scale), fill=18)
    body = Image.composite(Image.new("RGBA", (bw, bh), (255, 255, 255, 255)), body,
                           hl.filter(ImageFilter.GaussianBlur(8)))
    out.alpha_composite(body, (shadow, shadow))
    # three buttons on top
    bt = ImageDraw.Draw(out)
    for i in (-1, 0, 1):
        cx = shadow + bw // 2 + i * int(70 * scale)
        bt.rounded_rectangle([cx - int(22 * scale), shadow - int(7 * scale), cx + int(22 * scale), shadow + 2],
                             radius=int(4 * scale), fill=(40, 40, 46, 255))
    return out


def font(size):
    for f in ("/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def sheet(items, cols=2, bg=(255, 255, 255), fg=(36, 36, 40)):
    """Captioned grid of matrices."""
    tiles = [(render(g, cell=14), t) for g, t in items]
    tw, th = tiles[0][0].size
    cap, gap = 40, 28
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * tw + (cols + 1) * gap, rows * (th + cap + gap) + gap), bg)
    d, f = ImageDraw.Draw(out), font(22)
    for i, (im, t) in enumerate(tiles):
        x = gap + (i % cols) * (tw + gap)
        y = gap + (i // cols) * (th + cap + gap)
        d.text((x, y + 4), t, fill=fg, font=f)
        out.paste(im, (x, y + cap))
    return out


def main():
    frames = sys.argv[1] if len(sys.argv) > 1 else None
    if not frames:
        sys.exit(__doc__)
    src = {}
    for p in glob.glob(os.path.join(frames, "*.ppm")):
        src[os.path.splitext(os.path.basename(p))[0]] = p
    for name in ("clock_time", "clock_date"):
        for ext in (".ppm", ".png"):
            p = os.path.join(frames, name + ext)
            if name not in src and os.path.exists(p):
                src[name] = p
    grids = {k: load(v) for k, v in src.items()}

    # the overnight A, captured on a real clock
    cap = os.path.join(ROOT, "preview", "device", "after-left-aligned.png")
    if os.path.exists(cap) and Image.open(cap).size == (640, 160):
        grids["device_overnight_a"] = grid_from_image(cap)

    os.makedirs(os.path.join(ROOT, "docs", "images"), exist_ok=True)
    for k, g in grids.items():
        if not k.startswith("device_"):
            render(g).save(os.path.join(ROOT, "preview", k + ".png"), optimize=True)

    hero = grids["bc_3_7_12_25"]
    device(hero).save(os.path.join(ROOT, "docs", "images", "hero.png"), optimize=True)

    items = [("bc_3_7_12_25", "B (orange) and C (blue), soonest first"),
             ("device_overnight_a", "Overnight: only the A (a real clock)"),
             ("bc_alert_3_7_12_25", "Red dot: an MTA disruption"),
             ("bc_now_4_9_14", "N: arriving now"),
             ("bc_bullets_3_7", "Layout: bullets"),
             ("bc_turns_b_3_25", "Layout: turns"),
             ("live_4_11", "A single line"),
             ("bc_offline", "No live data: never an old number")]
    sheet([(grids[k], t) for k, t in items if k in grids]).save(
        os.path.join(ROOT, "docs", "images", "screens.png"), optimize=True)

    # a short loop: the clock, then the trains, the way the rotation goes
    seq = [("clock_time", 2200), ("bc_3_7_12_25", 2600), ("clock_time", 1400),
           ("bc_turns_b_3_25", 1600), ("bc_turns_c_7_12", 1600), ("bc_alert_3_7_12_25", 2200)]
    gif = [device(grids[k], scale=0.62).convert("RGBA") for k, _ in seq if k in grids]
    bg = Image.new("RGBA", gif[0].size, (255, 255, 255, 255))
    gif = [Image.alpha_composite(bg, f).convert("RGB").quantize(colors=256, method=Image.Quantize.FASTOCTREE)
           for f in gif]
    gif[0].save(os.path.join(ROOT, "docs", "images", "demo.gif"), save_all=True, append_images=gif[1:],
                duration=[d for k, d in seq if k in grids], loop=0, optimize=True)
    print("rendered", len(grids), "frames")


if __name__ == "__main__":
    main()
