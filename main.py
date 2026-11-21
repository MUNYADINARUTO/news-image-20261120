#!/usr/bin/env python3
"""Build the news-image-20261120 v2 front page: 35 stories, 7 regions, 1024x1024.

Layout (top to bottom): masthead, stat strip, region bar, 3 big stories
(Kyiv, Cyclone Akvan, Asia AI sell-off), 5 tiles, numbered index 9-35,
footer. All 35 stories are dated Friday 20 November 2026. Deterministic:
no timestamps, no randomness; the same inputs always give the same PNG.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
OUT = os.path.join(BASE, "entry.png")

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (179, 0, 0)
GRAY = (92, 88, 80)
NAVY = (15, 28, 46)
RULE = (17, 17, 17)


def font(name, size):
    path = "/usr/share/fonts/truetype/dejavu/" + name
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
        )


F_TITLE = font("DejaVuSerif-Bold.ttf", 54)
F_DECK = font("DejaVuSerif-Italic.ttf", 16)
F_H1 = font("DejaVuSerif-Bold.ttf", 21)
F_H2 = font("DejaVuSerif-Bold.ttf", 15)
F_BODY = font("DejaVuSans.ttf", 13)
F_SMALL = font("DejaVuSans.ttf", 11)
F_TINY = font("DejaVuSans.ttf", 10)
F_KICK = font("DejaVuSans-Bold.ttf", 12)
F_KICK_S = font("DejaVuSans-Bold.ttf", 10)
F_STAT = font("DejaVuSerif-Bold.ttf", 24)
F_NUM = font("DejaVuSans-Bold.ttf", 13)
F_IDX = font("DejaVuSans.ttf", 13)
F_IDXB = font("DejaVuSans-Bold.ttf", 13)


def text_w(draw, text, fnt):
    left, top, right, bottom = draw.textbbox((0, 0), text, font=fnt)
    return right - left


def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split(" "):
        trial = (line + " " + word).strip()
        if text_w(draw, trial, fnt) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill, spacing=4, max_lines=None):
    lines = wrap(draw, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def cover(im, width, height):
    iw, ih = im.size
    scale = max(width / iw, height / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - width) // 2
    top = (nh - height) // 2
    return im.crop((left, top, left + width, top + height))


def load(path):
    return Image.open(path).convert("RGB")


def num_chip(draw, x, y, n, size=22):
    draw.ellipse((x, y, x + size, y + size), fill=RED)
    label = str(n)
    w = text_w(draw, label, F_NUM)
    draw.text((x + (size - w) // 2, y + 3), label, font=F_NUM, fill=(255, 255, 255))


def draw_chart(draw, x, y, width, height):
    draw.rectangle((x, y, x + width, y + height), fill=NAVY)
    candles = [92, 88, 84, 86, 78, 74, 70, 66, 60, 56, 52, 48]
    top, bottom = y + 12, y + height - 30
    for i, value in enumerate(candles):
        cx = x + 14 + i * ((width - 28) // len(candles))
        cw = 12
        hgt = int((value / 100.0) * (bottom - top))
        cy = bottom - hgt
        draw.line((cx + cw // 2, cy - 8, cx + cw // 2, cy + hgt + 4), fill=(120, 40, 40), width=2)
        draw.rectangle((cx, cy, cx + cw, cy + hgt), fill=(214, 48, 49))
    draw.line((x + 8, bottom, x + width - 8, bottom), fill=(120, 130, 150), width=1)
    label = "TAIPEI -6.2%    SEOUL -5.2%    TOKYO -5.1%"
    w = text_w(draw, label, F_SMALL)
    draw.text((x + (width - w) // 2, y + height - 22), label, font=F_SMALL, fill=(255, 255, 255))


BIG = [
    {
        "n": 1,
        "kicker": "KYIV, UKRAINE \u2022 WAR",
        "image": "media-generation-kyiv-bridges-0-ecb3b657-f525-4511-9945-5d547801fe28.webp",
        "headline": "Russian missiles hit three Kyiv bridges",
        "deck": "110 missiles and 400 drones kill nine across Ukraine; power and water cut in the capital.",
        "source": "Kyiv Independent, BBC",
    },
    {
        "n": 2,
        "kicker": "ODISHA, INDIA \u2022 CYCLONE",
        "image": "media-generation-cyclone-akvan-0-9e1a6db2-afc7-4f1f-aac8-2a54f47a6295.webp",
        "headline": "Cyclone Akvan comes ashore in eastern India",
        "deck": "The storm crosses near Gopalpur; 300,000+ people moved to shelters. No deaths reported.",
        "source": "IMD, Deccan Herald",
    },
    {
        "n": 3,
        "kicker": "TAIPEI \u2022 SEOUL \u2022 TOKYO \u2022 MARKETS",
        "image": None,
        "headline": "AI sell-off sinks Asia's stock markets",
        "deck": "Taiwan falls 6.2% in its worst week since 1991; Seoul -5.2%, Tokyo -5.1% as chips slide.",
        "source": "Al Jazeera, Anadolu",
    },
]

TILES = [
    {
        "n": 4,
        "kicker": "RIYADH \u2022 MIDDLE EAST",
        "image": "media-generation-riyadh-tower-0-6f874b36-9a48-4064-b919-c33690596591.webp",
        "headline": "Houthi strike hits Riyadh's PIF Tower",
        "deck": "Missile hits the capital's landmark tower. (Roundup)",
    },
    {
        "n": 5,
        "kicker": "SHENZHEN \u2022 DIPLOMACY",
        "image": "media-generation-shenzhen-summit-0-3ff42c0e-bcd5-452c-bbd9-23d9abedce69.webp",
        "headline": "US, China, Russia sign joint declaration",
        "deck": "Three powers sign a declaration at Shenzhen. (Roundup)",
    },
    {
        "n": 6,
        "kicker": "SAN FRANCISCO \u2022 MARKETS",
        "image": None,
        "color": (91, 42, 134),
        "headline": "Anthropic shares slide after record IPO",
        "deck": "Stock falls on day two of trading. (Roundup)",
    },
    {
        "n": 7,
        "kicker": "THE HAGUE \u2022 LAW",
        "image": None,
        "color": (122, 31, 31),
        "headline": "ICJ rules Myanmar committed genocide",
        "deck": "Court finds against Myanmar over the Rohingya. (Roundup)",
    },
    {
        "n": 8,
        "kicker": "KERCH \u2022 TRANSPORT",
        "image": None,
        "color": (31, 78, 121),
        "headline": "Kerch Bridge rail traffic resumes",
        "deck": "Trains run again days after the crossing was hit. (Roundup)",
    },
]

INDEX = [
    (9, "Hormuz", "Oil tanker on fire in the strait. (Roundup)"),
    (10, "Brussels", "European leaders ready to negotiate with Russia. (Roundup)"),
    (11, "New York", "S&P 500 falls for a sixth straight day. (Roundup)"),
    (12, "Nairobi", "Kenya starts 42-day countdown to Ebola-free. (Roundup)"),
    (13, "Global", "Hackers leak Visa, Mastercard, JPMorgan data. (EGazette)"),
    (14, "Kyiv", "Ukraine hit 40 Russian oil facilities in 50 days. (AnewZ)"),
    (15, "Washington", "US Senate passes major permitting legislation. (NewsPoint)"),
    (16, "Haiti", "Anti-gang operation leaves dozens dead. (NewsPoint)"),
    (17, "Washington", "Trump pushes Iran decision to 2027. (Roundup)"),
    (18, "Space", "Voyager 1 is one light-day out: 16 billion miles. (NASA)"),
    (19, "Los Angeles", "GTA VI passes $1.8 billion in sales. (Roundup)"),
    (20, "New York", "Van Gogh sells for a record $190.4 million. (Roundup)"),
    (21, "London", "UK and EU seal a \u2018reset\u2019 deal on trade and visas. (Wire)"),
    (22, "Antalya", "COP31 reaches its last day with no deal. (UN News)"),
    (23, "Lviv", "Strike on railway station kills two, injures 10. (Insight)"),
    (24, "Warsaw", "Poland reports airspace violation; no air threat. (AnewZ)"),
    (25, "Odesa", "Russia hits port infrastructure and a cargo vessel. (AnewZ)"),
    (26, "Moscow", "EU envoys\u2019 visit \u2018under consideration\u2019. (AnewZ)"),
    (27, "Space", "Hayabusa2 gives up its asteroid landing. (Roundup)"),
    (28, "Kharkiv", "Russian strikes damage a hospital in the city. (Hub247)"),
    (29, "Kyiv", "Water utility hit; pressure falls in 4 districts. (Insight)"),
    (30, "Lviv", "Emergency power cuts across the west. (EuropeSays)"),
    (31, "Riyadh", "Coalition intercepts a missile and three drones. (EGazette)"),
    (32, "Yemen", "Houthi strike hits a civilian boat off the coast. (NewsPoint)"),
    (33, "Smolensk", "Dorogobuzh chemical plant struck again. (AnewZ)"),
    (34, "Luhansk", "Three killed in the Russian-controlled region. (AnewZ)"),
    (35, "Kyiv", "Zelensky: 27 of the 110 missiles were ballistic. (Insight)"),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Masthead.
    draw.text((12, 8), "THE WORLD IN ONE IMAGE", font=F_KICK, fill=RED)
    right = "35 STORIES \u2022 7 REGIONS"
    draw.text((W - 12 - text_w(draw, right, F_KICK), 8), right, font=F_KICK, fill=INK)
    title = "Friday 20 November 2026"
    draw.text(((W - text_w(draw, title, F_TITLE)) // 2, 28), title, font=F_TITLE, fill=INK)
    deck = ("Russian missiles hit Kyiv\u2019s bridges \u2022 Cyclone Akvan strikes India \u2022 "
            "An AI sell-off sinks Asia\u2019s markets \u2022 UK and EU seal a deal")
    draw.text(((W - text_w(draw, deck, F_DECK)) // 2, 88), deck, font=F_DECK, fill=INK)
    draw.line((12, 108, W - 12, 108), fill=RULE, width=2)

    # Stat strip: one-line labels so nothing is clipped.
    stats = [
        ("3", "bridges damaged in Kyiv"),
        ("300,000+", "people moved before Akvan"),
        ("-6.2%", "Taiex at Friday\u2019s close"),
        ("400+", "drones launched overnight"),
        ("110", "missiles fired at Ukraine"),
        ("$190.4m", "Van Gogh record price"),
    ]
    x = 12
    for num, label in stats:
        draw.line((x, 116, x, 150), fill=RED, width=3)
        draw.text((x + 8, 114), num, font=F_STAT, fill=INK)
        draw.text((x + 8, 142), label, font=F_SMALL, fill=GRAY)
        x += 167
    draw.line((12, 158, W - 12, 158), fill=(200, 192, 172), width=1)

    # Region bar.
    regions = [
        ("Europe", 15, (31, 78, 121)),
        ("Asia", 4, (179, 0, 0)),
        ("M. East", 5, (46, 125, 50)),
        ("Americas", 5, (106, 27, 154)),
        ("Africa", 1, (230, 81, 0)),
        ("Space", 2, (55, 71, 79)),
        ("Global", 3, (117, 117, 117)),
    ]
    total = sum(c for _, c, _ in regions)
    x = 12
    for name, count, color in regions:
        seg = int(round(1000 * count / total))
        draw.rectangle((x, 164, x + seg, 184), fill=color)
        label = name + " " + str(count) if seg >= 70 else str(count)
        w = text_w(draw, label, F_KICK_S)
        if w <= seg - 6:
            draw.text((x + (seg - w) // 2, 169), label, font=F_KICK_S, fill=(255, 255, 255))
        x += seg
    draw.line((12, 190, W - 12, 190), fill=(200, 192, 172), width=1)

    # Three big stories.
    cols = [12, 348, 684]
    for story, cx in zip(BIG, cols):
        if story["image"]:
            pic = cover(load(os.path.join(ASSETS, story["image"])), 328, 132)
            img.paste(pic, (cx, 198))
        else:
            draw_chart(draw, cx, 198, 328, 132)
        y = 336
        num_chip(draw, cx, y, story["n"])
        draw.text((cx + 28, y + 3), story["kicker"], font=F_KICK, fill=RED)
        y += 26
        y = draw_wrapped(draw, cx, y, story["headline"], F_H1, 328, INK, spacing=2, max_lines=2)
        y = draw_wrapped(draw, cx, y + 2, story["deck"], F_BODY, 328, INK, spacing=1, max_lines=2)
        draw.text((cx, y + 2), story["source"], font=F_TINY, fill=GRAY)

    draw.line((12, 452, W - 12, 452), fill=(200, 192, 172), width=1)

    # Five tiles.
    tx = [12, 212, 412, 612, 812]
    for tile, cx in zip(TILES, tx):
        if tile.get("image"):
            pic = cover(load(os.path.join(ASSETS, tile["image"])), 192, 92)
            img.paste(pic, (cx, 460))
        else:
            draw.rectangle((cx, 460, cx + 192, 552), fill=tile["color"])
            big = str(tile["n"])
            w = text_w(draw, big, F_STAT)
            draw.text((cx + (192 - w) // 2, 492), big, font=F_STAT, fill=(255, 255, 255))
        y = 560
        draw.text((cx, y), tile["kicker"], font=F_KICK_S, fill=RED)
        y += 15
        y = draw_wrapped(draw, cx, y, tile["headline"], F_H2, 192, INK, spacing=1, max_lines=2)
        draw_wrapped(draw, cx, y + 1, tile["deck"], F_SMALL, 192, GRAY, spacing=1, max_lines=2)

    draw.line((12, 640, W - 12, 640), fill=(200, 192, 172), width=1)

    # Index 9-35.
    draw.text((12, 648), "ALSO ON FRIDAY 20 NOVEMBER \u2014 27 MORE STORIES", font=F_KICK, fill=INK)
    left = INDEX[:14]
    right = INDEX[14:]
    for col, items in ((12, left), (522, right)):
        y = 672
        for n, lead, rest in items:
            draw.text((col, y), str(n), font=F_IDXB, fill=RED)
            nx = col + (26 if n < 10 else 30)
            draw.text((nx, y), lead + " \u2014 ", font=F_IDXB, fill=INK)
            lx = nx + text_w(draw, lead + " \u2014 ", F_IDXB)
            draw.text((lx, y), rest, font=F_IDX, fill=INK)
            y += 24

    # Footer.
    foot = "Every story here happened, or was first reported, on Friday 20 November 2026. Sources named beside each story."
    draw.text(((W - text_w(draw, foot, F_TINY)) // 2, 1008), foot, font=F_TINY, fill=GRAY)

    img.save(OUT, "PNG")
    digest = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    print("wrote " + OUT + " 1024x1024 sha256=" + digest)


if __name__ == "__main__":
    main()
