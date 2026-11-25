#!/usr/bin/env python3
"""news-image-20261124 v6 — "One day, hour by hour".

38 stories (15 illustrated hero cards + 23 numbered ALSO ON briefs),
8 regions, organised on a 24-hour spine: every story carries its UTC
hour, the timeline strip at the top is the spine (00:00 -> 24:00), and
the briefs run in chronological order. Heroes are ORIGINAL flat-vector
illustrations depicting the event, each with a big stat/banner — no
place-postcard photos, no empty boxes. DATE CHECK box names what was
LEFT OUT with dates. Pin map: heroes 1-15, colour-coded by region.
Input: items6.json + ../lockup-on-dark.png + land-110m.geojson
Output: ../news24/entry-v6.png (1024x1024, palette-quantized <= 1 MiB).
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news24")
OUT = os.path.join(BASE, "entry-v6.png")
ITEMS = os.path.join(BASE, "items6.json")
LOCKUP = os.path.join(os.path.dirname(BASE), "lockup-on-dark.png")
W = H = 1024
Image.MAX_IMAGE_PIXELS = 400_000_000

PAPER = (246, 241, 229)
INK = (26, 26, 26)
NAVY = (16, 38, 63)
CREAM = (247, 242, 231)
AMBER = (217, 138, 31)
CARD_BG = (255, 255, 255)
BORDER = (206, 198, 178)
MUTED = (90, 84, 70)
RED = (183, 28, 28)
TAGC = {"CONFIRMED": (30, 125, 50), "OFFICIAL": (21, 101, 192),
        "REPORTED": (178, 106, 0), "CLAIM": (183, 28, 28),
        "ONGOING": (106, 90, 205)}
BANNERC = {"RED": (183, 28, 28), "AMBER": (217, 138, 31),
           "TEAL": (0, 128, 128), "PURPLE": (106, 90, 205),
           "NAVY": (16, 38, 63), "GREEN": (30, 125, 50)}
REGIONC = {"EUROPE": (31, 119, 180), "MIDDLE EAST": (180, 106, 0),
           "ASIA": (0, 140, 140), "AFRICA": (46, 160, 67),
           "N. AMERICA": (128, 0, 128), "OCEANIA": (0, 150, 180),
           "LATIN AMERICA": (220, 60, 140), "WORLD": (110, 110, 110)}


def font(size, bold=False, serif=False, italic=False):
    if serif:
        name = "DejaVuSerif%s.ttf" % ("-Bold" if bold else
                                      "-Italic" if italic else "")
    else:
        name = "DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + name, size)
    except Exception:
        return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def trunc(draw, text, fnt, width):
    if draw.textlength(text, font=fnt) <= width:
        return text
    while text and draw.textlength(text + "…", font=fnt) > width:
        text = text[:-1]
    if " " in text:
        text = text.rsplit(" ", 1)[0]
    return text + "…"


def pill(draw, x, y, text, color, fnt, h=16, pad=7):
    w = int(draw.textlength(text, font=fnt)) + pad * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=color)
    draw.text((x + pad, y + (h - fnt.size) // 2 - 1), text, font=fnt,
              fill=(255, 255, 255))
    return w


def num_badge(draw, cx, cy, n, r=9):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER,
                 outline=(255, 255, 255), width=1)
    f = font(10, bold=True)
    t = str(n)
    draw.text((cx - draw.textlength(t, font=f) / 2, cy - 6), t, font=f,
              fill=(26, 26, 26))


# ---------------------------------------------------------------- scenes
# Original flat-vector illustrations, one per hero. Each draws inside
# the box (x, y, w, h) on the given ImageDraw. No photos anywhere.

def _sky(d, x, y, w, h, top, bot=None):
    d.rectangle([x, y, x + w, y + h], fill=top)
    if bot:
        d.rectangle([x, y + h * 2 // 3, x + w, y + h], fill=bot)


def _building(d, x, y, w, h, col, win=(255, 220, 130)):
    d.rectangle([x, y, x + w, y + h], fill=col)
    for wy in range(y + 5, y + h - 4, 8):
        for wx in range(x + 4, x + w - 4, 8):
            d.rectangle([wx, wy, wx + 3, wy + 4], fill=win)


def _smoke(d, cx, cy, col=(120, 120, 120)):
    for dx, dy, r in [(-8, 0, 6), (0, -7, 7), (8, -1, 6), (2, -14, 6)]:
        d.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r],
                  fill=col)


def _flame(d, cx, cy, s=1.0):
    d.polygon([(cx - 9 * s, cy + 8 * s), (cx, cy - 14 * s),
               (cx + 9 * s, cy + 8 * s)], fill=(230, 90, 20))
    d.polygon([(cx - 5 * s, cy + 8 * s), (cx, cy - 6 * s),
               (cx + 5 * s, cy + 8 * s)], fill=(255, 200, 40))


def scene(d, kind, x, y, w, h):
    if kind == "hormuz":
        _sky(d, x, y, w, h, (176, 214, 232), (31, 110, 160))
        for sx in (6, w // 2 - 14, w - 52):
            d.rectangle([x + sx, y + h - 26, x + sx + 44, y + h - 18],
                        fill=(30, 30, 30))
            d.rectangle([x + sx + 16, y + h - 34, x + sx + 26, y + h - 26],
                        fill=(30, 30, 30))
            d.rectangle([x + sx + 8, y + h - 22, x + sx + 36, y + h - 20],
                        fill=(200, 60, 40))
        for px, py in [(x + w // 3, y + 8), (x + 2 * w // 3, y + 14)]:
            d.line([px, py, px - 12, py + 12], fill=(183, 28, 28), width=2)
            d.ellipse([px - 14, py + 10, px - 10, py + 14], fill=(255, 200, 40))
        d.ellipse([x + w - 22, y + 6, x + w - 8, y + 20], fill=(255, 220, 120))
    elif kind == "nepal":
        _sky(d, x, y, w, h, (210, 228, 240), (140, 170, 150))
        d.polygon([(x, y + h), (x + w * 0.28, y + 6), (x + w * 0.55, y + h)],
                  fill=(90, 110, 140))
        d.polygon([(x + w * 0.35, y + h), (x + w * 0.62, y + 2),
                   (x + w * 0.9, y + h)], fill=(70, 95, 125))
        d.polygon([(x + w * 0.55, y + 10), (x + w * 0.62, y + 2),
                   (x + w * 0.69, y + 10)], fill=(255, 255, 255))
        pts = [(x + 4 + i * 7, y + h - 16 + (0 if i % 2 else -8))
               for i in range(9)]
        d.line(pts, fill=(183, 28, 28), width=2)
    elif kind == "zaporizhzhia":
        _sky(d, x, y, w, h, (52, 58, 84), (90, 80, 70))
        _building(d, x + 8, y + h - 34, 34, 34, (150, 140, 130))
        d.polygon([(x + 8, y + h - 34), (x + 25, y + h - 44),
                   (x + 42, y + h - 34)], fill=(120, 110, 100))
        _building(d, x + w - 52, y + h - 28, 40, 28, (110, 105, 95))
        _smoke(d, x + w // 2, y + 16)
        for dx in (-14, 0, 14):
            d.line([x + w // 2 + dx, y + 6, x + w // 2 + dx + 6, y + 12],
                   fill=(255, 255, 255), width=1)
        d.ellipse([x + w - 20, y + 4, x + w - 8, y + 16], fill=(255, 200, 90))
    elif kind == "solomons":
        _sky(d, x, y, w, h, (200, 230, 240), (0, 150, 160))
        d.ellipse([x + w * 0.18, y + h - 26, x + w * 0.82, y + h - 6],
                  fill=(60, 160, 90))
        d.polygon([(x + w * 0.42, y + h - 22), (x + w * 0.5, y + 8),
                   (x + w * 0.58, y + h - 22)], fill=(40, 130, 70))
        d.rectangle([x + w * 0.5 - 1, y + 4, x + w * 0.5 + 1, y + 22],
                    fill=(90, 70, 40))
        d.polygon([(x + w * 0.5 + 1, y + 4), (x + w * 0.5 + 22, y + 10),
                   (x + w * 0.5 + 1, y + 16)], fill=(0, 120, 80))
        d.ellipse([x + w - 24, y + 4, x + w - 10, y + 18], fill=(255, 220, 120))
    elif kind == "sanofi":
        _sky(d, x, y, w, h, (247, 242, 231))
        d.rounded_rectangle([x + w * 0.2, y + h * 0.32, x + w * 0.8,
                             y + h * 0.68], radius=10, fill=(120, 60, 160))
        d.rounded_rectangle([x + w * 0.5, y + h * 0.32, x + w * 0.8,
                             y + h * 0.68], radius=10, fill=(240, 240, 240))
        d.ellipse([x + w * 0.12, y + h * 0.6, x + w * 0.2, y + h * 0.72],
                  fill=(120, 60, 160))
        d.ellipse([x + w * 0.8, y + h * 0.28, x + w * 0.88, y + h * 0.4],
                  fill=(240, 240, 240))
        d.text((x + 6, y + 4), "$", font=font(16, bold=True),
               fill=(120, 60, 160))
    elif kind == "chen":
        _sky(d, x, y, w, h, (240, 220, 200), (180, 170, 150))
        _building(d, x + 6, y + h - 30, 16, 30, (90, 90, 100))
        _building(d, x + 26, y + h - 40, 14, 40, (70, 75, 90))
        d.polygon([(x + 33, y + h - 40), (x + 33, y + h - 52),
                   (x + 40, y + h - 40)], fill=(70, 75, 90))
        _building(d, x + 44, y + h - 24, 18, 24, (110, 105, 100))
        cx, cy = x + w - 26, y + 18
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=(183, 28, 28),
                  width=3)
        d.line([cx + 8, cy + 8, cx + 18, cy + 18], fill=(183, 28, 28), width=3)
        d.text((cx - 4, cy - 7), "?", font=font(12, bold=True),
               fill=(183, 28, 28))
    elif kind == "korea":
        _sky(d, x, y, w, h, (180, 200, 230), (120, 150, 170))
        cx, cy = x + w // 2, y + h - 14
        for r in (18, 12, 6):
            d.ellipse([cx - r, cy - r, cx + r, cy + r],
                      outline=(30, 125, 50), width=1)
        d.line([cx, cy, cx + 12, cy - 12], fill=(30, 125, 50), width=2)
        for jx in (x + 12, x + w - 30):
            d.polygon([(jx, y + 10), (jx + 18, y + 14), (jx, y + 18)],
                      fill=(60, 60, 60))
        d.text((x + 4, y + 2), "07:52", font=font(9, bold=True),
               fill=(183, 28, 28))
    elif kind == "england":
        _sky(d, x, y, w, h, (255, 230, 160), (240, 200, 120))
        d.ellipse([x + 10, y + 4, x + 34, y + 28], fill=(255, 180, 40))
        for a in range(0, 360, 45):
            import math as _m
            x1 = x + 22 + 16 * _m.cos(_m.radians(a))
            y1 = y + 16 + 16 * _m.sin(_m.radians(a))
            x2 = x + 22 + 21 * _m.cos(_m.radians(a))
            y2 = y + 16 + 21 * _m.sin(_m.radians(a))
            d.line([x1, y1, x2, y2], fill=(255, 180, 40), width=2)
        tx = x + w - 22
        d.rounded_rectangle([tx, y + 8, tx + 10, y + h - 8], radius=5,
                            fill=(255, 255, 255), outline=(183, 28, 28), width=1)
        d.rectangle([tx + 3, y + h - 16, tx + 7, y + h - 10], fill=(183, 28, 28))
        d.ellipse([tx - 2, y + h - 12, tx + 12, y + h - 2], fill=(183, 28, 28))
        d.rectangle([x + 8, y + h - 10, x + w - 30, y + h - 6],
                    fill=(200, 140, 60))
    elif kind == "gaza":
        _sky(d, x, y, w, h, (230, 210, 190), (170, 150, 130))
        _building(d, x + 6, y + h - 32, 22, 32, (140, 130, 115))
        _building(d, x + 32, y + h - 24, 18, 24, (120, 110, 95))
        _building(d, x + w - 30, y + h - 36, 24, 36, (150, 140, 125))
        _smoke(d, x + w // 2 + 6, y + 14, col=(90, 90, 90))
        d.polygon([(x + w // 2 - 2, y + 22), (x + w // 2 + 10, y + 16),
                   (x + w // 2 + 22, y + 22), (x + w // 2 + 10, y + 28)],
                  fill=(255, 200, 40))
    elif kind == "ariane":
        _sky(d, x, y, w, h, (16, 38, 63))
        for sx, sy in [(x + 12, y + 10), (x + w - 16, y + 6),
                       (x + w // 2 + 20, y + 4), (x + 30, y + 26)]:
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        cx = x + w // 2
        d.polygon([(cx - 6, y + 8), (cx, y - 2), (cx + 6, y + 8)],
                  fill=(255, 255, 255))
        d.rectangle([cx - 6, y + 8, cx + 6, y + h - 18], fill=(240, 240, 240))
        d.rectangle([cx - 6, y + h // 2, cx + 6, y + h // 2 + 6],
                    fill=(220, 60, 40))
        _flame(d, cx, y + h - 14, s=0.9)
        d.rectangle([x + 8, y + h - 6, x + w - 8, y + h - 2], fill=(60, 160, 90))
    elif kind == "cikande":
        _sky(d, x, y, w, h, (240, 200, 170), (150, 140, 130))
        d.rectangle([x + 10, y + h - 26, x + w - 34, y + h - 6],
                    fill=(120, 110, 100))
        d.rectangle([x + w - 30, y + h - 40, x + w - 22, y + h - 6],
                    fill=(100, 95, 90))
        _flame(d, x + w // 2 - 8, y + h - 30, s=1.1)
        _flame(d, x + w // 2 + 12, y + h - 26, s=0.8)
        _smoke(d, x + w // 2, y + 10)
        d.rectangle([x + 14, y + h - 20, x + 22, y + h - 12], fill=(255, 220, 130))
        d.rectangle([x + 26, y + h - 20, x + 34, y + h - 12], fill=(255, 220, 130))
    elif kind == "senegal":
        _sky(d, x, y, w, h, (240, 235, 200))
        d.rectangle([x, y, x + w // 3, y + h], fill=(0, 130, 60))
        d.rectangle([x + w // 3, y, x + 2 * w // 3, y + h], fill=(255, 220, 60))
        d.rectangle([x + 2 * w // 3, y, x + w, y + h], fill=(220, 40, 40))
        cx, cy = x + w // 2, y + h // 2 + 2
        d.polygon([(cx - 12, cy - 12), (cx + 12, cy - 12), (cx + 8, cy + 2),
                   (cx - 8, cy + 2)], fill=(255, 200, 40),
                  outline=(180, 130, 0))
        d.rectangle([cx - 3, cy + 2, cx + 3, cy + 10], fill=(255, 200, 40))
        d.rectangle([cx - 9, cy + 10, cx + 9, cy + 14], fill=(255, 200, 40))
        d.ellipse([cx - 16, cy - 14, cx - 8, cy - 2], outline=(255, 200, 40),
                  width=2)
        d.ellipse([cx + 8, cy - 14, cx + 16, cy - 2], outline=(255, 200, 40),
                  width=2)
    elif kind == "riyadh":
        _sky(d, x, y, w, h, (250, 220, 180), (200, 180, 150))
        _building(d, x + 8, y + h - 26, 14, 26, (140, 135, 125))
        tx = x + w // 2 - 8
        d.polygon([(tx, y + h - 6), (tx, y + 4), (tx + 5, y + 2),
                   (tx + 10, y + 2), (tx + 16, y + 4), (tx + 16, y + h - 6)],
                  fill=(90, 110, 140))
        for wy in range(y + 10, y + h - 10, 7):
            d.line([tx + 3, wy, tx + 13, wy], fill=(255, 220, 130), width=1)
        _smoke(d, tx + 8, y + 12, col=(100, 100, 100))
        d.polygon([(x + w - 26, y + 8), (x + w - 12, y + 12),
                   (x + w - 26, y + 16)], fill=(60, 60, 60))
        d.ellipse([x + w - 30, y + 4, x + w - 8, y + 20],
                  outline=(183, 28, 28), width=1)
    elif kind == "huawei":
        _sky(d, x, y, w, h, (235, 228, 210))
        d.polygon([(x + w // 2 - 34, y + 8), (x + w // 2 + 34, y + 8),
                   (x + w // 2, y + 22)], fill=(120, 110, 95))
        for cx in (x + w // 2 - 26, x + w // 2, x + w // 2 + 26):
            d.rectangle([cx - 3, y + 22, cx + 3, y + h - 10], fill=(200, 190, 170))
        d.rectangle([x + w // 2 - 36, y + h - 10, x + w // 2 + 36, y + h - 6],
                    fill=(120, 110, 95))
        gx = x + w - 26
        d.line([gx - 10, y + 12, gx + 10, y + 12], fill=(60, 60, 60), width=2)
        d.line([gx, y + 12, gx, y + 26], fill=(60, 60, 60), width=2)
        d.line([gx - 10, y + 26, gx + 10, y + 26], fill=(60, 60, 60), width=2)
        d.ellipse([gx - 14, y + 8, gx - 6, y + 16], fill=(217, 138, 31))
        d.ellipse([gx + 6, y + 8, gx + 14, y + 16], fill=(217, 138, 31))
    elif kind == "dow":
        _sky(d, x, y, w, h, (16, 38, 63))
        for gy in range(y + 10, y + h - 4, 10):
            d.line([x + 4, gy, x + w - 4, gy], fill=(40, 70, 105), width=1)
        pts = [(x + 6, y + h - 14), (x + w * 0.25, y + h - 22),
               (x + w * 0.45, y + h - 18), (x + w * 0.65, y + h - 30),
               (x + w * 0.85, y + h - 34), (x + w - 6, y + 10)]
        d.line(pts, fill=(60, 200, 90), width=3)
        d.polygon([(x + w - 14, y + 8), (x + w - 4, y + 8), (x + w - 6, y + 18)],
                  fill=(60, 200, 90))
        d.text((x + 6, y + 4), "DOW", font=font(10, bold=True),
               fill=(120, 170, 220))


def main():
    data = json.load(open(ITEMS))
    cards = data["cards"]
    also = data["also_on"]
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead band: make.fun lockup + title ----
    d.rectangle([0, 0, W, 44], fill=NAVY)
    lk0 = Image.open(LOCKUP).convert("RGBA")
    lk0.thumbnail((170, 34), Image.LANCZOS)
    img.paste(lk0, (14, (44 - lk0.height) // 2), lk0)
    tx0 = 14 + lk0.width + 14
    d.text((tx0, 9), data["masthead"], font=font(24, bold=True), fill=CREAM)
    dt = data["dateline"]
    fdt = font(12, bold=True)
    d.text((W - 14 - d.textlength(dt, font=fdt), 14), dt, font=fdt,
           fill=(232, 178, 90))

    # ---- giant serif date masthead ----
    d.text((16, 50), "Tuesday 24 November 2026",
           font=font(40, bold=True, serif=True), fill=INK)
    cnt = "38 STORIES · 8 REGIONS · 15 HEROES"
    fc = font(12, bold=True)
    d.text((W - 16 - d.textlength(cnt, font=fc), 52), cnt, font=fc, fill=RED)
    d.text((W - 16 - d.textlength("ONE DAY, HOUR BY HOUR", font=font(10, bold=True)), 68),
           "ONE DAY, HOUR BY HOUR", font=font(10, bold=True), fill=MUTED)
    d.text((16, 92), "China probes Shanghai's party chief  ·  US jury finds Huawei guilty  ·  Dow closes back above 50,000",
           font=font(13, serif=True, italic=True), fill=(90, 30, 30))

    # ---- region chips ----
    cx = 16
    for name, n in data["regions"]:
        lab = "%s %s" % (name, n)
        f = font(9, bold=True)
        wch = int(d.textlength(lab, font=f)) + 14
        d.rounded_rectangle([cx, 110, cx + wch, 126], radius=8,
                            fill=REGIONC[name])
        d.text((cx + 7, 113), lab, font=f, fill=(255, 255, 255))
        cx += wch + 5
    d.text((cx + 2, 113), "= 38 stories", font=font(9, bold=True), fill=MUTED)

    # ---- THE DAY IN UTC — the 24-hour spine ----
    # Title row, then the line; beat labels sit ABOVE the line in two
    # staggered rows (even beats high, odd beats low) so neighbours
    # never collide; hour ticks sit below the line only.
    ty = 126
    d.text((16, ty), "THE DAY IN UTC — THE 24-HOUR SPINE",
           font=font(10, bold=True), fill=NAVY)
    d.text((W - 16 - d.textlength("* 07:52 is local time (KST)", font=font(8)), ty + 1),
           "* 07:52 is local time (KST)", font=font(8), fill=MUTED)
    lx0, lx1, ly = 30, 1000, 166
    d.line([lx0, ly, lx1, ly], fill=NAVY, width=2)
    for hh in range(0, 25, 3):
        xx = lx0 + (lx1 - lx0) * hh / 24
        d.line([xx, ly - 4, xx, ly + 4], fill=NAVY, width=1)
        lab = "%02d:00" % hh
        d.text((xx - d.textlength(lab, font=font(7)) / 2, ly + 6), lab,
               font=font(7), fill=MUTED)
    for i, (tm, lab) in enumerate(data["timeline"]):
        hh, mm = map(int, tm.split(":"))
        xx = lx0 + (lx1 - lx0) * (hh + mm / 60) / 24
        d.ellipse([xx - 5, ly - 5, xx + 5, ly + 5], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = tm + " " + lab
        f7 = font(7, bold=True)
        tw = d.textlength(t, font=f7)
        txp = max(16, min(W - 16 - tw, xx - tw / 2))
        d.text((txp, ly - 22 if i % 2 == 0 else ly - 12), t, font=f7,
               fill=RED if i % 2 == 0 else NAVY)

    # ---- IN NUMBERS strip ----
    ny, nh = 184, 32
    d.rectangle([16, ny, 1008, ny + nh], fill=CARD_BG, outline=BORDER, width=1)
    cw = 992 / 6
    for i, (num, lab) in enumerate(data["numbers"]):
        x = 16 + i * cw
        if i:
            d.line([x, ny + 5, x, ny + nh - 5], fill=BORDER, width=1)
        d.text((x + cw / 2 - d.textlength(num, font=font(16, bold=True)) / 2, ny + 2),
               num, font=font(16, bold=True), fill=NAVY)
        for j, ln in enumerate(wrap(d, lab, font(7), cw - 10)):
            d.text((x + cw / 2 - d.textlength(ln, font=font(7)) / 2, ny + 21 + j * 8),
                   ln, font=font(7), fill=MUTED)

    # ---- vertical spine rail (left edge of the story area) ----
    d.line([8, 218, 8, 702], fill=AMBER, width=3)
    for yy in (218, 283, 409, 527, 645, 702):
        d.ellipse([4, yy - 4, 12, yy + 4], fill=AMBER, outline=(255, 255, 255),
                  width=1)

    # ---- hero cards ----
    # Row A: 3 big cards; rows B-D: 4 cards each. Chronological order.
    def hero(c, x, y, w, h, big):
        d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=BORDER, width=1)
        ih = 50 if big else 44
        scene(d, c["scene"], x + 1, y + 1, w - 2, ih)
        num_badge(d, x + 14, y + 14, c["n"], r=9)
        bf = font(9 if big else 8, bold=True)
        bt = c["banner"]
        bw = int(d.textlength(bt, font=bf)) + 12
        bc = BANNERC[c["banner_color"]]
        d.rounded_rectangle([x + w - bw - 5, y + ih - 17, x + w - 5, y + ih - 3],
                            radius=6, fill=bc)
        d.text((x + w - bw + 1, y + ih - 16), bt, font=bf, fill=(255, 255, 255))
        yy = y + ih + 4
        tlab = c["time"] + (" " + c["time_note"] if "time_note" in c else " UTC")
        cat = tlab + " · " + c["place"] + " · " + c["field"]
        tf = font(7, bold=True)
        tw = int(d.textlength(c["tag"], font=tf)) + 10
        d.text((x + 5, yy), trunc(d, cat, font(7, bold=True), w - tw - 12),
               font=font(7, bold=True), fill=REGIONC[c["region"]])
        d.rounded_rectangle([x + w - tw - 4, yy, x + w - 4, yy + 12], radius=6,
                            fill=TAGC[c["tag"]])
        d.text((x + w - tw + 1, yy + 1), c["tag"], font=tf, fill=(255, 255, 255))
        yy += 14
        hs = 12 if big else 10
        for ln in wrap(d, c["headline"], font(hs, bold=True), w - 10)[:2]:
            d.text((x + 5, yy), ln, font=font(hs, bold=True), fill=INK)
            yy += hs + 2
        ds = 9 if big else 8
        dl = wrap(d, c["deck"], font(ds), w - 10)
        for ln in dl[:2 if big else 1]:
            d.text((x + 5, yy), ln, font=font(ds), fill=(60, 56, 48))
            yy += ds + 2
        d.text((x + 5, y + h - 10), "Source: " + c["source"],
               font=font(7), fill=MUTED)

    gx, gy = 16, 218
    bigw, gap = 328, 5
    for i, c in enumerate(cards[:3]):
        hero(c, gx + i * (bigw + gap), gy, bigw, 130, True)
    smw = 244
    rows = [cards[3:7], cards[7:11], cards[11:15]]
    for r, row in enumerate(rows):
        for i, c in enumerate(row):
            hero(c, gx + i * (smw + gap), gy + 134 + r * 118, smw, 114, False)

    # ---- ALSO ON (chronological briefs) ----
    ay = 708
    d.text((16, ay), "ALSO ON — the day in brief, hour by hour",
           font=font(13, bold=True), fill=NAVY)
    d.line([16, ay + 19, 1008, ay + 19], fill=NAVY, width=1)
    by = ay + 25
    d.line([512, by - 2, 512, by + 12 * 12 - 2], fill=BORDER, width=1)
    for i, b in enumerate(also):
        col, row = divmod(i, 12)
        x = 16 + col * 500
        y = by + row * 12
        f8, f8b = font(8), font(8, bold=True)
        tf = font(7, bold=True)
        tw = int(d.textlength(b["tag"], font=tf)) + 8
        nx = x
        num = "%d · " % b["n"]
        d.text((nx, y), num, font=f8b, fill=(178, 106, 0))
        nx += d.textlength(num, font=f8b)
        tm = b["time"] + " "
        d.text((nx, y), tm, font=f8, fill=MUTED)
        nx += d.textlength(tm, font=f8)
        pl = b["place"] + " — "
        d.text((nx, y), pl, font=f8b, fill=INK)
        nx += d.textlength(pl, font=f8b)
        d.text((nx, y), trunc(d, b["headline"], f8, x + 492 - tw - 6 - nx),
               font=f8, fill=INK)
        d.rounded_rectangle([x + 492 - tw, y, x + 492, y + 11], radius=5,
                            fill=TAGC[b["tag"]])
        d.text((x + 492 - tw + 4, y + 1), b["tag"], font=tf, fill=(255, 255, 255))

    # ---- DATE CHECK strip ----
    dy = 881
    d.rectangle([16, dy, 1008, dy + 30], fill=(255, 248, 235),
                outline=RED, width=1)
    d.text((22, dy + 9), "DATE CHECK", font=font(9, bold=True), fill=RED)
    for j, ln in enumerate(wrap(d, data["datecheck"].split("— ", 1)[1],
                                font(8), 1008 - 16 - 92)):
        d.text((108, dy + 4 + j * 11), ln, font=font(8), fill=INK)

    # ---- bottom band: sources + legend | pin map ----
    byy = 917
    d.line([16, byy, 1008, byy], fill=NAVY, width=1)
    sy = byy + 7
    for ln in wrap(d, data["sources"], font(8), 568):
        d.text((16, sy), ln, font=font(8), fill=(60, 56, 48))
        sy += 11
    sy += 3
    d.text((16, sy), "HOW SURE ARE WE?", font=font(8, bold=True), fill=NAVY)
    sy += 12
    for ln in wrap(d, data["legend"], font(8), 568):
        d.text((16, sy), ln, font=font(8), fill=(60, 56, 48))
        sy += 11
    sy += 3
    for ln in ["All 15 hero illustrations are original flat-vector drawings — no photos.",
               "Korea alert 07:52 Tue local (22:52 UTC Mon 23 Nov) · Hormuz incident 23 Nov 20:25 UTC, reported Tue 24 Nov."]:
        d.text((16, sy), ln, font=font(8), fill=MUTED)
        sy += 11

    mx, my, mw, mh = 600, byy, 408, 102
    map_img = Image.new("RGB", (mw, mh), (198, 220, 238))
    md = ImageDraw.Draw(map_img)
    mapx, mapy, mapw, maph = 4, 16, mw - 8, mh - 20
    lon0, lon1, lat0, lat1 = -130, 175, -10, 75

    def mxy(lon, lat):
        return (mapx + (lon - lon0) / (lon1 - lon0) * mapw,
                mapy + (lat1 - lat) / (lat1 - lat0) * maph)

    land = json.load(open(os.path.join(BASE, "land-110m.geojson")))
    for feat in land["features"]:
        geom = feat["geometry"]
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        for poly in polys:
            for ring in poly:
                pts, prev = [], None
                for lon, lat in ring:
                    if prev is not None and abs(lon - prev) > 180:
                        lon += 360 if lon < prev else -360
                    prev = lon
                    x, y = mxy(lon, lat)
                    pts.append((x, y))
                if len(pts) >= 3:
                    md.polygon(pts, fill=(208, 222, 196), outline=(150, 170, 140))
    for lon in range(-120, 151, 30):
        xx = mapx + (lon - lon0) / (lon1 - lon0) * mapw
        md.line([xx, mapy, xx, mapy + maph], fill=(170, 196, 216), width=1)
    for lat in range(0, 76, 15):
        yy = mapy + (lat1 - lat) / (lat1 - lat0) * maph
        md.line([mapx, yy, mapx + mapw, yy], fill=(170, 196, 216), width=1)

    pins = []
    for c in cards:
        x, y = mxy(c["lon"], c["lat"])
        pins.append([x, y, x, y, c["n"], REGIONC[c["region"]]])
    MIN_D = 18.0
    for _ in range(10):
        for i in range(len(pins)):
            for j in range(i + 1, len(pins)):
                dx = pins[j][0] - pins[i][0]
                dy = pins[j][1] - pins[i][1]
                dist = math.hypot(dx, dy)
                if dist >= MIN_D:
                    continue
                if dist < 0.01:
                    ang = pins[j][4] * 2.399963
                    dx, dy, dist = math.cos(ang), math.sin(ang), 1.0
                push = (MIN_D - dist) / 2
                ux, uy = dx / dist, dy / dist
                pins[i][0] -= ux * push
                pins[i][1] -= uy * push
                pins[j][0] += ux * push
                pins[j][1] += uy * push
        for p in pins:
            for k in (0, 1):
                p[k] = max(p[k + 2] - 16, min(p[k + 2] + 16, p[k]))
            p[0] = max(mapx + 8, min(mapx + mapw - 8, p[0]))
            p[1] = max(mapy + 8, min(mapy + maph - 8, p[1]))
    for x, y, _tx, _ty, n, col in pins:
        r = 7
        md.ellipse([x - r, y - r, x + r, y + r], fill=col,
                   outline=(255, 255, 255), width=1)
        f = font(7, bold=True)
        t = str(n)
        md.text((x - md.textlength(t, font=f) / 2, y - 5), t, font=f,
                fill=(255, 255, 255))
    img.paste(map_img, (mx, my))
    d.rectangle([mx, my, mx + mw, my + mh], outline=NAVY, width=2)
    d.text((mx + 8, my + 3), "WHERE IT HAPPENED — PINS = HEROES 1–15, BY REGION",
           font=font(9, bold=True), fill=NAVY)

    img.save(OUT)
    q = img.convert("P", palette=Image.ADAPTIVE, colors=256)
    q.save(OUT, optimize=True)
    print("saved", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
