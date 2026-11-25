#!/usr/bin/env python3
"""The World Today - front page summing up Wednesday 25 November 2026.

Draws one 1024x1024 newspaper front page with Pillow (stdlib + Pillow only,
no network, fully deterministic) and writes it to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png).
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)   # newsprint cream
INK = (18, 18, 18)        # near-black ink
RED = (178, 32, 44)       # headline red
NAVY = (24, 38, 64)       # markets band
SEA = (38, 84, 124)       # strait water
SEA_DARK = (22, 58, 92)
SAND = (214, 196, 158)    # coastline
GREY = (90, 86, 78)
RULE = (120, 112, 98)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit `width` pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, width, fill=INK, leading=None, max_lines=None):
    """Draw wrapped paragraph; returns y just below the last line."""
    if leading is None:
        leading = fnt.size + 5
    lines = wrap(draw, text, fnt, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def headline(draw, x, y, text, fnt, width, fill=INK, leading=None, max_lines=4):
    """Draw a wrapped headline; returns y below it."""
    if leading is None:
        leading = fnt.size + 7
    lines = wrap(draw, text, fnt, width)[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, x, y, text, fnt, width):
    draw.text((x, y), text, font=fnt, fill=RED)
    return y + fnt.size + 6


def hrule(draw, x0, x1, y, width=1, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vrule(draw, x, y0, y1, width=1, fill=RULE):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


# ---------------------------------------------------------------- pictograms

def draw_strait(draw, x, y, w, h):
    """Strait of Hormuz scene: sand coasts, blue water, two tankers, mines."""
    draw.rectangle([x, y, x + w, y + h], fill=SEA)
    # coastlines: Iran (top) and Oman (bottom)
    draw.polygon([(x, y), (x + w, y), (x + w, y + 16),
                  (x + int(w * 0.72), y + 26), (x + int(w * 0.45), y + 14),
                  (x + int(w * 0.18), y + 24), (x, y + 12)], fill=SAND)
    draw.polygon([(x, y + h), (x + w, y + h), (x + w, y + h - 14),
                  (x + int(w * 0.8), y + h - 26), (x + int(w * 0.5), y + h - 12),
                  (x + int(w * 0.2), y + h - 24), (x, y + h - 10)], fill=SAND)
    draw.text((x + 10, y + 2), "IRAN", font=font(SANS_B, 11), fill=(120, 96, 60))
    draw.text((x + w - 52, y + h - 15), "OMAN", font=font(SANS_B, 11), fill=(120, 96, 60))
    # tanker 1 (left, on fire)
    tx, ty = x + 90, y + h // 2 - 6
    draw.rectangle([tx, ty, tx + 150, ty + 18], fill=(24, 48, 72))
    draw.rectangle([tx, ty + 14, tx + 150, ty + 18], fill=(200, 40, 30))
    draw.rectangle([tx + 108, ty - 16, tx + 132, ty], fill=(24, 48, 72))
    draw.rectangle([tx + 128, ty - 26, tx + 136, ty - 16], fill=(200, 40, 30))
    draw.rectangle([tx + 20, ty - 10, tx + 96, ty], fill=(200, 40, 30))
    # explosion burst over tanker 1
    bx, by = tx + 60, ty - 26
    for dx, dy, r in [(-16, -8, 9), (0, -16, 11), (16, -8, 9), (-8, 4, 8),
                      (10, 4, 8), (0, 2, 12)]:
        draw.ellipse([bx + dx - r, by + dy - r, bx + dx + r, by + dy + r],
                     fill=(240, 140, 30))
    draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=(255, 210, 80))
    # tanker 2 (right, listing smoke)
    tx2, ty2 = x + 360, y + h // 2 + 8
    draw.rectangle([tx2, ty2, tx2 + 150, ty2 + 18], fill=(24, 48, 72))
    draw.rectangle([tx2, ty2 + 14, tx2 + 150, ty2 + 18], fill=(200, 40, 30))
    draw.rectangle([tx2 + 20, ty2 - 14, tx2 + 44, ty2], fill=(24, 48, 72))
    draw.rectangle([tx2 + 40, ty2 - 24, tx2 + 48, ty2 - 14], fill=(200, 40, 30))
    # small flame on tanker 2's deck
    draw.polygon([(tx2 + 60, ty2 - 2), (tx2 + 70, ty2 - 20), (tx2 + 80, ty2 - 2)],
                 fill=(240, 140, 30))
    for i, (sx, sy, r) in enumerate([(0, -34, 12), (14, -48, 15), (30, -62, 17)]):
        draw.ellipse([tx2 + 110 + sx - r, ty2 + sy - r,
                      tx2 + 110 + sx + r, ty2 + sy + r], fill=(70, 70, 74))
    # naval mines: spiked circles
    for mx, my in [(x + 300, y + 30), (x + 520, y + h - 34), (x + 250, y + h - 40)]:
        draw.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(12, 12, 14))
        for ang in range(0, 360, 45):
            import math
            ex = mx + int(11 * math.cos(math.radians(ang)))
            ey = my + int(11 * math.sin(math.radians(ang)))
            draw.line([(mx, my), (ex, ey)], fill=(12, 12, 14), width=2)
    # caption
    draw.text((x, y + h + 4), "THE STRAIT OF HORMUZ: TWO TANKERS STRUCK MINES AND CAUGHT FIRE",
              font=font(SANS_B, 11), fill=GREY)


def draw_courthouse(draw, x, y, w, h):
    """Small courthouse front for the Huawei story."""
    # steps
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=(150, 140, 122))
    draw.rectangle([x + 8, y + h - 16, x + w - 8, y + h - 8], fill=(170, 160, 140))
    # columns
    for i in range(4):
        cx = x + 22 + i * ((w - 44) // 3)
        draw.rectangle([cx, y + 34, cx + 14, y + h - 16], fill=(200, 190, 168))
        draw.rectangle([cx - 3, y + 30, cx + 17, y + 34], fill=(180, 170, 148))
    # pediment
    draw.polygon([(x, y + 32), (x + w, y + 32), (x + w // 2, y + 2)], fill=(150, 140, 122))
    draw.ellipse([x + w // 2 - 8, y + 12, x + w // 2 + 8, y + 28], fill=PAPER)
    # door
    draw.rectangle([x + w // 2 - 16, y + h - 44, x + w // 2 + 16, y + h - 16],
                   fill=(60, 52, 40))


def draw_tower(draw, x, y, w, h):
    pass  # (unused pictogram removed; mid-row columns are text-only)


# ------------------------------------------------------------------- page

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28                      # margin
    R = W - M                   # right edge

    # ---- masthead ------------------------------------------------------
    hrule(d, M, R, 18, 2)
    name = "THE WORLD TODAY"
    nf = font(SERIF_B, 74)
    d.text(((W - d.textlength(name, font=nf)) / 2, 26), name, font=nf, fill=INK)
    d.text((M, 108), "Vol. II  —  No. 329", font=font(SANS, 14), fill=GREY)
    date = "WEDNESDAY, 25 NOVEMBER 2026"
    df = font(SANS_B, 21)
    d.text(((W - d.textlength(date, font=df)) / 2, 106), date, font=df, fill=INK)
    d.text((R - d.textlength("WORLD EDITION", font=font(SANS, 14)), 108),
           "WORLD EDITION", font=font(SANS, 14), fill=GREY)
    hrule(d, M, R, 138, 3)
    hrule(d, M, R, 143, 1)

    # ---- lead story: Hormuz (left) --------------------------------------
    LX, LW = M, 636
    y = 156
    y = kicker(d, LX, y, "IRAN WAR  •  STRAIT OF HORMUZ", font(SANS_B, 15), LW)
    y = headline(d, LX, y, "Two oil tankers hit by naval mines in the Strait of Hormuz",
                 font(SERIF_B, 36), LW, leading=43, max_lines=3)
    y = para(d, LX, y + 2,
             "Iran's Revolutionary Guard said the tankers struck mines and caught "
             "fire on an unauthorised route through the strait, the chokepoint for "
             "a fifth of the world's oil.",
             font(SERIF, 15), LW, leading=20, max_lines=2)
    draw_strait(d, LX, 358, LW, 100)
    para(d, LX, 472,
         "Washington is weighing its response as the Iran war widens, with "
         "Houthi attacks now reaching deep into Saudi Arabia.",
         font(SERIF, 15), LW, leading=20, max_lines=2)

    # ---- Huawei (right) --------------------------------------------------
    RX, RW = 692, R - 692
    y = 156
    y = kicker(d, RX, y, "NEW YORK  •  TECHNOLOGY", font(SANS_B, 15), RW)
    y = headline(d, RX, y, "Huawei convicted of bank fraud and trade-secret theft",
                 font(SERIF_B, 27), RW, leading=33, max_lines=4)
    draw_courthouse(d, RX, 296, RW, 84)
    y = para(d, RX, 392,
             "A Brooklyn jury found the Chinese telecoms giant guilty on 10 of 12 "
             "counts, including bank fraud, wire fraud and sanctions violations — "
             "but cleared it of racketeering.",
             font(SERIF, 15), RW, leading=20, max_lines=5)

    hrule(d, M, R, 530, 1)

    # ---- second row: three columns ---------------------------------------
    cols = [
        (M, 312, "RUSSIA–UKRAINE WAR",
         "Ukrainian drones set two Russian refineries ablaze",
         "Strikes hit Rosneft's Syzran and Kuibyshev plants in Samara; one person "
         "was killed and 145 drones were downed. Leaked Russian data put the war's "
         "Russian death toll at about 490,000."),
        (352, 312, "ISRAEL–HAMAS WAR",
         "Israel kills Hamas security chief in Gaza strike",
         "Mohammad Abuelouf, who headed Hamas's interior security service, was "
         "killed with his wife and two children, Gaza medics said."),
        (676, 320, "YEMEN  •  SAUDI ARABIA",
         "Houthi strike on Riyadh tower injures 11",
         "A Houthi drone hit a tower in Riyadh's financial district; at least two "
         "of the injured are Indian. The Houthis also said they attacked Saudi "
         "Arabia's Ras Tanura oil refinery."),
    ]
    for cx, cw, kick, head, body in cols:
        y = 542
        y = kicker(d, cx, y, kick, font(SANS_B, 13), cw)
        y = headline(d, cx, y, head, font(SERIF_B, 20), cw, leading=24, max_lines=2)
        para(d, cx, y + 2, body, font(SERIF, 13), cw, leading=16, max_lines=5)
    vrule(d, 340, 542, 690)
    vrule(d, 664, 542, 690)

    # ---- markets strip ----------------------------------------------------
    d.rectangle([M, 700, R, 752], fill=NAVY)
    mf = font(SANS_B, 15)
    d.text((M + 12, 712), "MARKETS", font=mf, fill=(255, 210, 80))
    m1 = "KOSPI –6.16%   •   Samsung –9.9%   •   SK Hynix –11.1%   •   Nikkei –2.78%   •   SoftBank –14.8%"
    m2 = "Dow 50,018.70 — first close above 50,000   •   Nasdaq –1.5%   •   Oil down over 20% in November"
    d.text((M + 118, 712), m1, font=font(SANS, 14), fill=(235, 235, 235))
    d.text((M + 118, 732), m2, font=font(SANS, 14), fill=(235, 235, 235))

    # ---- briefs grid -------------------------------------------------------
    briefs = [
        ("SUDAN", "RSF drone strikes kill 19 civilians",
         "Paramilitary drone strikes killed 19 civilians and wounded 20 in two "
         "cities, Sudanese lawyers said."),
        ("CLIMATE", "Pope laments COP31 collapse",
         "Pope Leo XIV deplored the failure of the U.N. climate talks in Antalya, "
         "where oil states blocked a fossil-fuel phase-out."),
        ("PACIFIC", "Australia–Solomons sign security treaty",
         "The treaty bars any foreign military base on the Solomon Islands, a win "
         "for Canberra in the Pacific."),
        ("SPACE", "Shenzhou-24 docks; Pakistan's first astronaut in orbit",
         "China's Shenzhou-24 docked with the Tiangong station hours after launch, "
         "carrying Pakistan's first astronaut."),
        ("COLOMBIA", "All hostages freed in Cartagena siege",
         "Security forces stormed an Éxito supermarket and freed every hostage; "
         "one captor was killed."),
        ("INDONESIA", "Six dead, 20 miners trapped in Bogor",
         "Bodies were recovered from a flooded gold mine in West Java; about 20 "
         "miners remain trapped."),
        ("WASHINGTON", "Trump plans tariffs on 16 economies",
         "New U.S. tariffs are being prepared against 16 economies, including "
         "China, the EU and Japan, U.S. media reported."),
        ("TECH", "Nvidia slides; Dell posts record quarter",
         "Nvidia fell as Congress questioned Trump's role in Huang's return. Dell "
         "revenue hit $54.9bn, up 103%."),
    ]
    bw = (R - M - 3 * 16) // 4
    bh = 108
    for i, (kick, head, body) in enumerate(briefs):
        bx = M + (i % 4) * (bw + 16)
        by = 766 + (i // 4) * (bh + 12)
        kicker(d, bx, by, kick, font(SANS_B, 12), bw)
        y = headline(d, bx, by + 18, head, font(SANS_B, 14), bw, leading=18,
                     max_lines=2)
        para(d, bx, y + 1, body, font(SERIF, 12), bw, leading=16, max_lines=3)
        if i % 4 < 3:
            vrule(d, bx + bw + 8, by + 2, by + bh - 4)

    # ---- footer ------------------------------------------------------------
    hrule(d, M, R, 994, 1)
    foot = "Compiled from wire reports on Wednesday 25 November 2026  •  The World Today — one day's news in one page"
    ff = font(SANS, 12)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 1002), foot, font=ff, fill=GREY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG")
    print("wrote", path, img.size)


if __name__ == "__main__":
    main()
