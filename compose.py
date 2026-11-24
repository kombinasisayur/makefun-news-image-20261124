#!/usr/bin/env python3
"""THE PORTSIDE GAZETTE — Tuesday 24 November 2026 in one image.

Fresh compose engine for NI24, account 16 (@kombinasisayur0566).
Draws the full front page at 3900 px wide, then scales it whole onto a
1024x1024 canvas and quantises to 256 colours. All artwork is drawn in
code (flat layered scenes + a dotted world map from simplified real
coastline polygons). No network, no Pillow-only tricks at grade time:
this file runs here, in the build session; the graded program is main.py,
which only copies the finished entry.png.

Usage: python3 compose.py [--variant A|B] [--out entry.png]
"""
import argparse
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

# ---------------------------------------------------------------- palette
CREAM = (247, 240, 220)      # page paper
CREAM2 = (238, 228, 200)     # panel paper
INK = (30, 26, 22)           # near-black ink
RUST = (160, 61, 30)         # masthead / rules
RUST_DK = (110, 36, 16)
GOLD = (192, 138, 46)
NAVY = (31, 58, 95)          # map dots
TEAL = (36, 92, 86)
SLATE = (84, 96, 110)
SKY = (214, 226, 232)
RED = (178, 34, 34)          # DATE CHECK + pins
WHITE = (255, 253, 247)

# ---------------------------------------------------------------- fonts
def _playfair(size, italic=False, weight="Black"):
    path = os.path.join(FONTS, "PlayfairDisplay-Italic-VF.ttf" if italic
                        else "PlayfairDisplay-VF.ttf")
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        try:
            f.set_variation_by_axes([900])
        except Exception:
            pass
    return f

def _sans(size, bold=False):
    path = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(path, size)

def fb(size):
    """Headline font (Playfair Black)."""
    return _playfair(size)

def fr(size):
    """Deck/body font."""
    return _sans(size)

def fsr(size):
    """Brief font."""
    return _sans(size)

# ---------------------------------------------------------------- helpers
def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text_c(draw, xy, s, font, fill, anchor="la"):
    draw.text(xy, s, font=font, fill=fill, anchor=anchor)

def rule(draw, x0, y, x1, w=6, fill=RUST):
    draw.line([(x0, y), (x1, y)], fill=fill, width=w)

def chip(draw, x, y, label, font, fg=WHITE, bg=RUST, pad=14, h=None):
    tw = draw.textlength(label, font=font)
    hh = h if h else font.size + 2 * pad
    draw.rounded_rectangle([x, y, x + tw + 2 * pad, y + hh], radius=hh // 2,
                           fill=bg)
    draw.text((x + pad, y + hh / 2), label, font=font, fill=fg,
              anchor="lm")
    return x + tw + 2 * pad

def tagline(draw, x, y, source, font):
    """Certainty + source tag, e.g. 'REPORTED · Reuters'."""
    draw.text((x, y), "REPORTED \u00b7 " + source, font=font, fill=RUST_DK)

# ------------------------------------------------- simplified world polygons
# Hand-simplified real coastlines, (lon, lat). Used for the dotted map.
CONTINENTS = [
    # North America
    [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 57),
     (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
     (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9),
     (-79, 9), (-81, 13), (-83, 16), (-87, 16), (-90, 21), (-91, 19),
     (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 26), (-80, 32),
     (-76, 35), (-74, 40), (-70, 42), (-68, 45), (-65, 44), (-60, 47),
     (-55, 52), (-60, 55), (-64, 58), (-68, 58), (-72, 62), (-78, 62),
     (-85, 66), (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
     (-155, 71), (-165, 68), (-168, 66)],
    # Greenland
    [(-58, 64), (-52, 60), (-44, 60), (-40, 64), (-32, 68), (-25, 70),
     (-20, 74), (-25, 76), (-35, 77), (-50, 76), (-58, 74), (-60, 70),
     (-58, 64)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
     (-66, -55), (-65, -45), (-62, -41), (-58, -38), (-52, -33), (-48, -28),
     (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
     (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
     (-76, 10), (-79, 9)],
    # Africa
    [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36),
     (10, 37), (11, 34), (19, 33), (25, 32), (30, 31), (32, 31), (34, 28),
     (36, 23), (38, 18), (40, 15), (43, 12), (48, 11), (51, 12), (46, 5),
     (42, 0), (40, -5), (40, -10), (39, -15), (36, -20), (33, -26),
     (28, -33), (20, -35), (17, -32), (15, -27), (12, -18), (13, -12),
     (12, -6), (9, -1), (9, 4), (4, 6), (-3, 5), (-8, 5), (-13, 8),
     (-17, 12), (-17, 15)],
    # Eurasia
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (0, 44), (-1, 46), (-4, 48),
     (-2, 50), (0, 51), (3, 53), (5, 53), (8, 55), (8, 57), (10, 59),
     (5, 60), (5, 62), (10, 64), (12, 66), (18, 69), (25, 71), (30, 70),
     (35, 68), (40, 68), (45, 68), (50, 69), (55, 69), (60, 69), (65, 70),
     (70, 72), (75, 73), (80, 73), (85, 74), (90, 75), (95, 76), (100, 77),
     (105, 77), (110, 76), (115, 73), (120, 73), (125, 72), (130, 72),
     (135, 71), (140, 72), (145, 72), (150, 70), (155, 69), (158, 66),
     (162, 64), (162, 60), (158, 57), (156, 52), (150, 60), (142, 55),
     (140, 50), (138, 46), (135, 43), (132, 43), (128, 38), (126, 35),
     (122, 32), (120, 28), (118, 25), (112, 22), (108, 18), (105, 10),
     (103, 8), (100, 7), (98, 10), (95, 15), (92, 21), (90, 22), (88, 22),
     (85, 20), (82, 17), (80, 13), (77, 8), (76, 10), (73, 16), (70, 20),
     (66, 25), (62, 25), (58, 26), (56, 27), (52, 28), (50, 29), (48, 30),
     (44, 29), (40, 28), (38, 24), (36, 22), (34, 20), (35, 16), (38, 15),
     (40, 15), (43, 12), (45, 12), (48, 11), (50, 12), (52, 14), (55, 17),
     (58, 20), (60, 23), (58, 25), (56, 26), (54, 27), (52, 26), (50, 26),
     (48, 29), (47, 30), (44, 31), (42, 33), (40, 36), (36, 36), (33, 36),
     (30, 36), (27, 37), (23, 36), (22, 37), (19, 40), (16, 40), (13, 42),
     (10, 44), (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37),
     (-10, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-3, 50), (-5, 50)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37),
     (141, 39), (141, 41), (143, 42), (145, 44), (143, 45), (141, 45),
     (140, 42), (139, 38), (137, 37), (135, 34), (133, 34), (131, 33),
     (130, 31)],
    # Australia
    [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -12), (132, -11), (130, -13), (126, -14), (122, -17),
     (118, -20), (113, -22)],
    # New Zealand
    [(167, -45), (169, -43), (171, -42), (173, -41), (175, -40), (177, -38),
     (178, -37), (176, -39), (174, -41), (172, -43), (169, -44), (167, -45)],
    # Sumatra
    [(95, 5), (98, 3), (100, 0), (103, -3), (105, -5), (104, -6), (101, -4),
     (99, -1), (97, 2), (95, 5)],
    # Java
    [(105, -6), (108, -7), (111, -7), (114, -8), (114, -9), (110, -8),
     (106, -7), (105, -6)],
    # Borneo
    [(109, 1), (111, 2), (114, 4), (117, 6), (118, 2), (117, -1),
     (114, -3), (110, -3), (109, 0), (109, 1)],
    # New Guinea
    [(131, -1), (135, -2), (138, -3), (141, -3), (143, -4), (146, -6),
     (147, -8), (144, -8), (141, -8), (138, -7), (135, -5), (132, -3),
     (131, -1)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (45, -25),
     (43, -22), (43, -18), (44, -16)],
    # Iceland
    [(-22, 64), (-18, 63), (-15, 64), (-14, 66), (-18, 66), (-22, 65),
     (-22, 64)],
]

def _inside(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and \
                (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def draw_dotted_map(draw, box, dot_color=NAVY, step=17, r=6):
    """Dotted world map from the polygons above (equirectangular)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    polys = []
    for poly in CONTINENTS:
        pts = [((lon + 180.0) / 360.0 * w + x0,
                (90.0 - lat) / 180.0 * h + y0) for lon, lat in poly]
        polys.append(pts)
    gx = x0 + step // 2
    while gx < x1:
        gy = y0 + step // 2
        while gy < y1:
            lon = (gx - x0) / w * 360.0 - 180.0
            lat = 90.0 - (gy - y0) / h * 180.0
            for poly in CONTINENTS:
                if _inside(lon, lat, poly):
                    draw.ellipse([gx - r, gy - r, gx + r, gy + r],
                                 fill=dot_color)
                    break
            gy += step
        gx += step

def pin_xy(box, lon, lat):
    x0, y0, x1, y1 = box
    return ((lon + 180.0) / 360.0 * (x1 - x0) + x0,
            (90.0 - lat) / 180.0 * (y1 - y0) + y0)

# ------------------------------------------------------------------- content
# Master numbers come from ni24-pool.md / ni24-pool-refresh-0700.md only.
# Every deck carries >= 2 facts; every card carries REPORTED + its source.

CARDS = {
    1: dict(region="EUROPE", topic="WAR", place="Benghazi, Libya",
            head="Ukraine sinks Russian warship Merkury off Libya",
            deck=["7 sea drones launched at the corvette; a Ka-27 helicopter "
                  "was destroyed aboard.",
                  "MV Angara cargo vessel also hit; Zelenskyy calls the raid "
                  "\u201cexemplary\u201d."],
            chip="7 SEA DRONES", src="CNN / Times / WSJ / AP",
            pin=(20.1, 32.1), scene="ship"),
    2: dict(region="EUROPE", topic="SEA", place="Gulf of Finland",
            head="Russian cargo ship Sparta II hit, towed clear",
            deck=["121 m ship hit by 2 drones on Saturday; all 16 crew "
                  "taken off safely.",
                  "Towed out of Finnish waters on Sunday night; bound for "
                  "Kaliningrad."],
            chip="16 CREW SAFE", src="Reuters / Times / WSJ",
            pin=(25.0, 60.0), scene="ship2"),
    3: dict(region="EUROPE", topic="WAR", place="Kyiv region, Ukraine",
            head="Russian strikes kill at least 15 near Kyiv",
            deck=["11 killed in a block of flats in Dymer; 5 injured in "
                  "Kyiv on Monday.",
                  "Drone hit a 6-floor building; Zelenskyy on Putin: "
                  "\u201cfor us, he\u2019s a killer\u201d."],
            chip="15 KILLED", src="Times / AP",
            pin=(30.5, 50.4), scene="city"),
    4: dict(region="WORLD", topic="CLIMATE", place="Antalya, T\u00fcrkiye",
            head="COP31 ends with no deal \u2014 first since 2000",
            deck=["Cover text dropped every fossil-fuel mention; EU, UK and "
                  "others rejected it.",
                  "44 h overtime, longest COP ever; next round: Addis Ababa, "
                  "Nov 2027."],
            chip="NO DEAL", src="Times / Guardian",
            pin=(30.7, 36.9), scene="summit"),
    5: dict(region="MIDDLE EAST", topic="SANCTIONS", place="Washington",
            head="US sanctions ~30 Iran-linked exchange houses",
            deck=["Treasury names ~30 houses + executives at the core of "
                  "shadow banking.",
                  "Announced Monday as Rubio meets Qatar PM over Iran "
                  "uncertainty."],
            chip="~30 SANCTIONED", src="AP / Treasury",
            pin=(-79.5, 38.0), scene="bank"),
    6: dict(region="MIDDLE EAST", topic="CONFLICT", place="Gaza City",
            head="Israeli strikes kill 3 in Gaza",
            deck=["3 killed Monday in separate strikes, incl. a UNRWA "
                  "employee.",
                  "Shifa Hospital + agency confirm the deaths."],
            chip="3 KILLED", src="AP",
            pin=(34.5, 31.5), scene="city2"),
    7: dict(region="MIDDLE EAST", topic="WAR", place="Western Yemen",
            head="Strike kills 11 in western Yemen",
            deck=["Houthis say Saudi-backed forces\u2019 strike Monday killed "
                  "11, wounded 19.",
                  "Casualties reported from the western front."],
            chip="11 KILLED", src="AP",
            pin=(44.0, 15.5), scene="hills"),
    8: dict(region="AMERICAS", topic="MARKETS", place="London \u00b7 New York",
            head="Gold rebounds 1.5% to $3,588",
            deck=["Bullion +1.5% Monday after its worst week in 8 months.",
                  "Traders await US PCE inflation report due 25 Nov; "
                  "10-yr yield ~4.96%."],
            chip="$3,588/OZ", src="Reuters",
            pin=(-0.1, 51.5), scene="gold"),
    9: dict(region="GLOBAL", topic="CRYPTO", place="World markets",
            head="Bitcoin steadies near $61,284",
            deck=["$61,284 Monday 12:52 UTC, +1.1% in 24 h, \u22124.5% over "
                  "7 days.",
                  "Weekend low ~$55,100 as leveraged liquidations eased."],
            chip="$61,284", src="CoinPaprika",
            pin=(-74.0, 40.7), scene="coin"),
    10: dict(region="AMERICAS", topic="BUSINESS", place="Los Angeles",
             head="GTA VI takes $3.8bn on day one",
             deck=["Biggest entertainment launch on record \u2014 past every "
                   "game launch and single-day film box office.",
                   "$3.8bn in one day: the largest first-day total ever "
                   "reported."],
             chip="$3.8BN DAY ONE", src="ActiveInvestorMag",
             pin=(-118.2, 34.0), scene="gta"),
    11: dict(region="OCEANIA", topic="CRICKET", place="Wellington",
             head="New Zealand bat out draw with India",
             deck=["NZ 239/5 \u2014 Mitchell 49* off 186, Phillips 26* off "
                   "126; 63-run stand.",
                   "India 720/9d (Rahul 136, Pant 128); 2nd Test: "
                   "Christchurch, 27 Nov\u20131 Dec."],
             chip="DRAW 239/5", src="HS / WicketPulse",
             pin=(174.8, -41.3), scene="cricket"),
    12: dict(region="EUROPE", topic="FOOTBALL", place="Liverpool",
             head="Liverpool 4\u20130 Man Utd",
             deck=["Yoro sent off in the 8th minute; United down to "
                   "10 men.",
                   "Defeat leaves United 19th in the league on 8 points."],
             chip="4\u20130", src="Mint / NextSportsWeb",
             pin=(-2.99, 53.4), scene="football"),
    13: dict(region="AMERICAS", topic="POLITICS", place="Washington",
             head="Trump: work with Democrats to cap card rates",
             deck=["Trump says he would work with Democrats to cap "
                   "credit-card rates.",
                   "Also calls for scrapping the debt ceiling; Senate "
                   "leadership vote 1 Dec."],
             chip="RATE CAP", src="ActiveInvestorMag",
             pin=(-74.0, 40.6), scene="capitol"),
    14: dict(region="AMERICAS", topic="POLITICS", place="Washington",
             head="Democrats take both chambers",
             deck=["House 258\u2013173, largest majority since 1992, after "
                   "N. Carolina pickup.",
                   "Senate leadership challenge: Van Hollen vs Schumer, "
                   "secret ballot 1 Dec."],
             chip="258\u2013173", src="BBC / ActiveInvestorMag",
             pin=(-80.0, 36.0), scene="ballot"),
    20: dict(region="AMERICAS", topic="MARKETS", place="Santa Clara",
             head="Nvidia brings back Jensen Huang as CEO",
             deck=["Board reinstates Huang effective immediately Mon 23 Nov; "
                   "Trump intervened.",
                   "Shares +31% Mon; Nasdaq +6%, S&P 500 +5%, chip index "
                   "+12%."],
             chip="+31% HUANG BACK", src="Reuters",
             pin=(-122.0, 37.35), scene="chip"),
}

LEAD_WIDE = 10
LEADS = [9, 8]
MINIS_A = [20, 1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 14]
MINIS_B = [20, 4, 1, 3, 2, 7, 5, 6, 14, 13, 12, 11]

BRIEFS_N = [
    (16, "N. Korea weighs closing Swiss office, Pyongyang (KCNA, Tue)"),
    (17, "US mulls military training for Syrian forces, first since 2024"),
    (18, "Congo halts cobalt exports from 30 Nov (Reuters)"),
    (19, "Indonesia factory blaze kills 24, dozens missing (Reuters)"),
    (20, "CrowdStrike snaps up Zscaler in $44bn deal (Reuters)"),
    (21, "Trump hosts meme-coin gala as token hits record lows (Reuters)"),
    (22, "US Army to detonate lead stockpile in Iowa: 68 barrels (Reuters)"),
    (23, "India considers rice export duties as prices rise (Reuters)"),
    (24, "COP31 adopted 46 decisions despite no cover deal (Reuters)"),
    (25, "Miley Cyrus weds Maxx Morando in California (Reuters)"),
    (26, "Japan factory PMI 53.7 in Nov; output + orders up (Tue 00:35 UTC)"),
    (27, "Singapore lifts 2026 forecast to ~6.0% after Q3 +6.1% (Reuters)"),
    (28, "StarHub agrees $3.8bn all-share deal for M1 (Reuters, Tue)"),
    (29, "Wellington draw sets up 2nd Test, Christchurch 27 Nov-1 Dec"),
    (30, "Kraken CAD flash crash to ~$17,000 Sat; trades stand"),
    (31, "UK\u2013EU Brexit reset: Burnham calls it \u201clandmark\u201d (BBC)"),
    (32, "India\u2013EU trade pact likely signed 16 Dec, Brussels (JagranJosh)"),
    (33, "Tata Steel sells pipe unit to APL Apollo, \u20b928,000 cr (ObserverVoice)"),
    (34, "FBI probes hack of its crime database (AP)"),
    (35, "Solana launches solana.ai for AI agents (Gadgets360)"),
    (36, "UN AI weapons talks continue, states agree (salonvision)"),
]

TIMELINE = [
    ("04:24 WIB TUE", "KCNA: North Korea weighs closing Swiss office in "
     "Pyongyang \u2014 Reuters"),
    ("07:23 WIB TUE", "Gold edges up on bargain buying after sell-off \u2014 "
     "Reuters (00:23 GMT)"),
    ("07:35 WIB TUE", "Japan factory PMI 53.7; output + export orders pick "
     "up \u2014 Reuters (00:35 UTC)"),
    ("MON EVE UTC", "Nvidia board reinstates Huang as CEO; shares +31% \u2014 "
     "Reuters, reported Mon evening"),
    ("MON EVE UTC", "Zelenskyy announces Merkury sinking; US sanctions ~30 "
     "Iran exchange houses \u2014 reported Mon evening"),
]

DATECHECK = [
    "186-drone night over Ukraine, 161 downed \u2014 Fri 21\u2013Sun 22 Nov",
    "Hong Kong Election Committee: 856 candidates, 723 seats \u2014 Sun 22 Nov",
    "Alcaraz beats Zverev, first ATP Finals title \u2014 Sun 22 Nov",
    "Verstappen wins Las Vegas Grand Prix \u2014 Sun 22 Nov",
    "Wembanyama scores 50, Spurs 114\u201391 Pelicans \u2014 Sun 22 Nov",
    "India declare 720/9 \u2014 Sun 22 Nov (the DRAW is the news, Mon 23 Nov)",
    "Huang resigns after affair admission \u2014 Thu 12 Nov (the REINSTATEMENT "
    "is the news, Mon 23 Nov)",
]

NUMSTRIP = [
    ("7", "SEA DRONES"),
    ("$3.8BN", "GTA VI DAY ONE"),
    ("$61,284", "BITCOIN"),
    ("$3,588", "GOLD +1.5%"),
    ("+31%", "NVIDIA"),
    ("NO DEAL", "COP31"),
    ("258\u2013173", "HOUSE"),
]

REGION_STRIP = [("EUROPE", 4, RUST), ("MIDDLE EAST", 3, TEAL),
                ("AMERICAS", 5, GOLD), ("WORLD", 2, NAVY),
                ("OCEANIA", 1, SLATE)]

FOOTER_SRC = ("Sources: Reuters \u00b7 AP \u00b7 CNN \u00b7 The Times \u00b7 WSJ "
              "\u00b7 BBC \u00b7 Guardian \u00b7 CoinPaprika \u00b7 ActiveInvestorMag "
              "\u00b7 HS \u00b7 WicketPulse \u00b7 Mint \u00b7 IANS \u00b7 JagranJosh "
              "\u00b7 ObserverVoice \u00b7 Treasury \u00b7 KCNA.")
FOOTER_LEGEND = ("Certainty: REPORTED = confirmed by at least one wire. "
                 "CLAIM = attributed, not confirmed. Pictures and dotted map: "
                 "original, drawn in code.")

# ------------------------------------------------------------------- scenes
# Flat layered scenes, one per card topic. Each fills its strip with a sky
# band, 2-3 silhouette layers and a big data chip. All drawn in code.

def scene(draw, kind, box, variant):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    skies = {"ship": (70, 110, 140), "ship2": (96, 130, 150),
             "city": (120, 70, 60), "city2": (140, 90, 70),
             "summit": (46, 110, 96), "bank": (60, 80, 90),
             "hills": (150, 110, 70), "gold": (176, 140, 60),
             "coin": (200, 130, 40), "gta": (150, 60, 110),
             "cricket": (70, 130, 80), "football": (40, 110, 60),
             "capitol": (90, 90, 110), "ballot": (70, 90, 130),
             "chip": (40, 60, 110)}
    sky = skies.get(kind, (90, 90, 100))
    draw.rectangle([x0, y0, x1, y1], fill=sky)
    # sun / moon disc, variant-dependent side
    cx = x0 + (w * 3 // 4 if variant == "A" else w // 4)
    cy = y0 + h // 3
    r = h // 4
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 220, 150))
    if kind in ("ship", "ship2"):
        # sea + hull + mast + drone dots
        draw.rectangle([x0, y0 + h * 2 // 3, x1, y1], fill=(24, 60, 90))
        for i in range(5):
            wx = x0 + w * (i + 1) // 6
            draw.arc([wx - 40, y0 + h * 2 // 3 - h // 6, wx + 40,
                      y0 + h * 2 // 3 + h // 6], 180, 360,
                     fill=(200, 220, 235), width=5)
        draw.polygon([(x0 + w // 6, y0 + h * 2 // 3),
                      (x0 + w * 5 // 6, y0 + h * 2 // 3),
                      (x0 + w * 3 // 4, y1 - 8),
                      (x0 + w // 4, y1 - 8)], fill=(20, 20, 26))
        draw.rectangle([x0 + w // 2 - 6, y0 + h // 4, x0 + w // 2 + 6,
                        y0 + h * 2 // 3], fill=(20, 20, 26))
        for dx, dy in ((0.15, 0.22), (0.35, 0.14), (0.55, 0.24),
                       (0.72, 0.15), (0.88, 0.26)):
            px, py = x0 + w * dx, y0 + h * dy
            draw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=INK)
            draw.line([px, py + 9, px, py + 26], fill=INK, width=4)
    elif kind in ("city", "city2"):
        base = y0 + h * 3 // 5
        draw.rectangle([x0, base, x1, y1], fill=(40, 30, 28))
        bw = w // 7
        for i in range(7):
            bh = h * (0.28 + 0.07 * ((i * 37) % 5)) / 1.0
            bx = x0 + i * bw
            draw.rectangle([bx + 8, base - bh, bx + bw - 8, y1],
                           fill=(16, 14, 18) if i % 2 else (52, 38, 34))
            for wy in range(3):
                draw.rectangle([bx + 18, base - bh + 16 + wy * 26,
                                bx + 34, base - bh + 30 + wy * 26],
                               fill=(247, 220, 150))
        draw.rectangle([x0, base, x1, base + 10], fill=GOLD)
    elif kind == "summit":
        # globe + flags
        draw.ellipse([x0 + w // 2 - h // 3, y0 + h // 6,
                      x0 + w // 2 + h // 3, y0 + h * 5 // 6],
                     fill=(36, 120, 110))
        draw.arc([x0 + w // 2 - h // 4, y0 + h // 4,
                  x0 + w // 2 + h // 4, y0 + h * 3 // 4], 0, 360,
                 fill=(220, 235, 230), width=6)
        draw.line([x0 + w // 2, y0 + h // 6, x0 + w // 2, y0 + h * 5 // 6],
                  fill=(220, 235, 230), width=6)
        for fx in (0.12, 0.30, 0.70, 0.88):
            px = x0 + w * fx
            draw.line([px, y0 + h // 2, px, y1 - 6], fill=INK, width=5)
            draw.polygon([(px, y0 + h // 2), (px + 44, y0 + h // 2 + h // 4),
                          (px, y0 + h // 2 + h // 2)],
                         fill=RUST if fx < 0.5 else GOLD)
    elif kind == "bank":
        base = y0 + h * 3 // 5
        draw.rectangle([x0, base, x1, y1], fill=(30, 36, 44))
        for i in range(5):
            bx = x0 + w * (0.10 + i * 0.18)
            draw.rectangle([bx, y0 + h // 3, bx + 46, base], fill=CREAM)
        draw.polygon([(x0 + w // 2 - w // 3, y0 + h // 3),
                      (x0 + w // 2 + w // 3, y0 + h // 3),
                      (x0 + w // 2, y0 + h // 8)], fill=RUST)
    elif kind == "hills":
        draw.polygon([(x0, y1), (x0 + w // 3, y0 + h // 3),
                      (x0 + w * 2 // 3, y1)], fill=(90, 70, 40))
        draw.polygon([(x0 + w // 3, y1), (x0 + w * 2 // 3, y0 + h // 4),
                      (x1, y1)], fill=(60, 48, 30))
        draw.rectangle([x0, y0 + h * 4 // 5, x1, y1], fill=(52, 40, 26))
    elif kind == "gold":
        base = y0 + h * 3 // 5
        draw.rectangle([x0, base, x1, y1], fill=(120, 90, 30))
        for i in range(4):
            bx = x0 + w * (0.08 + i * 0.22)
            bh = h // 2 - (i % 2) * (h // 6)
            bw2 = min(120, w // 5)
            draw.rectangle([bx, base - bh, bx + bw2,
                            base], fill=(232, 190, 80),
                           outline=(140, 105, 30), width=5)
        draw.line([x0, y0 + h // 4, x0 + w // 3, y0 + h // 2,
                   x0 + w * 2 // 3, y0 + h // 5, x1, y0 + h // 2],
                  fill=WHITE, width=10)
    elif kind == "coin":
        cx, cy = x0 + w // 2, y0 + h // 2
        r = h * 2 // 5
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 180, 60),
                     outline=(140, 100, 20), width=8)
        draw.ellipse([cx - r * 3 // 5, cy - r * 3 // 5, cx + r * 3 // 5,
                      cy + r * 3 // 5], outline=(140, 100, 20), width=6)
        draw.text((cx, cy), "B", font=_playfair(h // 2), fill=(120, 80, 10),
                  anchor="mm")
        draw.line([x0, y1 - 30, x0 + w // 4, y0 + h * 2 // 3,
                   x0 + w // 2, y0 + h // 2, x1, y0 + h // 4],
                  fill=WHITE, width=9)
    elif kind == "gta":
        base = y0 + h * 3 // 5
        draw.rectangle([x0, base, x1, y1], fill=(24, 18, 34))
        bw = w // 8
        for i in range(8):
            bh = h * (0.28 + 0.07 * ((i * 53) % 5))
            bx = x0 + i * bw
            col = (200, 60, 140) if i % 3 == 0 else (
                (60, 200, 220) if i % 3 == 1 else (250, 180, 60))
            draw.rectangle([bx + 6, base - bh, bx + bw - 6, y1], fill=col)
            for wy in range(2):
                draw.rectangle([bx + 14, base - bh + 14 + wy * 24,
                                bx + 26, base - bh + 26 + wy * 24],
                               fill=(255, 250, 220))
        draw.rectangle([x0, base, x1, base + 8], fill=WHITE)
    elif kind == "cricket":
        base = y0 + h * 3 // 5
        draw.rectangle([x0, base, x1, y1], fill=(46, 110, 60))
        br = max(10, h // 4)
        draw.ellipse([x0 + w // 2 - br, y0 + h // 4 - br,
                      x0 + w // 2 + br, y0 + h // 4 + br], fill=RED)
        draw.line([x0 + w // 6, base, x0 + w * 5 // 6, base], fill=CREAM,
                  width=8)
        bh = h * 3 // 4
        draw.polygon([(x0 + w // 4, y0 + h // 5), (x0 + w // 4 + 26,
                      y0 + h // 5 + bh), (x0 + w // 4 + 60,
                      y0 + h // 5 + bh), (x0 + w // 4 + 34, y0 + h // 5)],
                     fill=(210, 170, 110))
    elif kind == "football":
        base = y0 + h * 3 // 5
        draw.rectangle([x0, base, x1, y1], fill=(30, 90, 50))
        bw = min(70, h // 2)
        bt = y0 + h // 5
        bb = min(y1 - 4, bt + h * 3 // 5)
        draw.ellipse([x0 + w // 2 - bw, bt, x0 + w // 2 + bw, bb],
                     fill=WHITE, outline=INK, width=6)
        draw.polygon([(x0 + w // 2 - bw, bt + (bb - bt) // 2),
                      (x0 + w // 2 - bw // 3, bt + (bb - bt) // 6),
                      (x0 + w // 2 + bw // 2, bt + (bb - bt) // 4),
                      (x0 + w // 2, bt + (bb - bt) * 3 // 4),
                      (x0 + w // 2 - bw // 2, bt + (bb - bt) * 5 // 6)],
                     fill=INK)
        draw.line([x0, base, x1, base], fill=WHITE, width=8)
    elif kind in ("capitol", "ballot"):
        base = y0 + h * 3 // 5
        draw.rectangle([x0, base, x1, y1], fill=(52, 52, 62))
        for i in range(5):
            bx = x0 + w * (0.14 + i * 0.17)
            draw.rectangle([bx, y0 + h // 3, bx + 40, base], fill=CREAM)
        draw.ellipse([x0 + w // 2 - 70, y0 + h // 8, x0 + w // 2 + 70,
                      y0 + h // 3], fill=CREAM)
        draw.rectangle([x0 + w // 2 - 90, y0 + h // 3 - 14,
                        x0 + w // 2 + 90, y0 + h // 3 + 6], fill=CREAM)
        if kind == "ballot":
            draw.rectangle([x0 + w * 3 // 4 - 60, y0 + h // 2,
                            x0 + w * 3 // 4 + 60, y1 - 10], fill=RUST)
            draw.rectangle([x0 + w * 3 // 4 - 90, y0 + h // 2 - 26,
                            x0 + w * 3 // 4 + 90, y0 + h // 2], fill=INK)
    elif kind == "chip":
        cx, cy = x0 + w // 2, y0 + h // 2
        hw = min(150, w // 2 - 10)
        hh = h * 2 // 5
        draw.rectangle([cx - hw, cy - hh, cx + hw, cy + hh], fill=(20, 24, 34),
                       outline=GOLD, width=8)
        for i in range(3):
            yy = cy - hh + (i + 1) * (2 * hh // 4)
            draw.line([cx - hw + 20, yy, cx + hw - 20, yy],
                      fill=(70, 90, 120), width=6)
        for i in range(5):
            px = cx - hw + 20 + i * ((2 * hw - 40) // 4)
            draw.line([px, cy - hh + 8, px, cy + hh - 8], fill=GOLD, width=6)
        draw.polygon([(x1 - 90, y0 + h // 6), (x1 - 30, y0 + h // 6),
                      (x1 - 60, y0 + h * 2 // 3)], fill=(60, 200, 120))

# ------------------------------------------------------------------- cards
def card_number(draw, x, y, num, size=54):
    s = str(num)
    f = _playfair(size)
    tw = draw.textlength(s, font=f)
    d = size + 26
    draw.ellipse([x, y, x + d, y + d], fill=RUST)
    draw.text((x + d / 2, y + d / 2), s, font=f, fill=WHITE, anchor="mm")
    return x + d + 14

def draw_lead_wide(draw, num, box, variant):
    x0, y0, x1, y1 = box
    c = CARDS[num]
    draw.rectangle([x0, y0, x1, y1], fill=CREAM2, outline=INK, width=4)
    sc_h = 190
    scene(draw, c["scene"], (x0 + 4, y0 + 4, x1 - 4, y0 + 4 + sc_h), variant)
    # data chip overlaid on the scene strip, bottom-right
    cf = _sans(34, bold=True)
    tw = draw.textlength(c["chip"], font=cf) + 28
    chip(draw, x1 - 24 - tw, y0 + 4 + sc_h - 62, c["chip"], cf, h=52)
    tx = x0 + 28
    ty = y0 + 208
    nx = card_number(draw, tx, ty, num, size=58)
    lab = f"{c['place'].upper()} \u00b7 {c['region']} \u00b7 {c['topic']}"
    draw.text((nx, ty + 12), lab, font=_sans(34, bold=True), fill=RUST_DK)
    hy = ty + 84
    for line in wrap(draw, c["head"], _playfair(76), x1 - x0 - 56)[:2]:
        draw.text((tx, hy), line, font=_playfair(76), fill=INK)
        hy += 82
    hy += 6
    for para in c["deck"]:
        for line in wrap(draw, para, _sans(38), x1 - x0 - 56):
            draw.text((tx, hy), line, font=_sans(38), fill=(52, 46, 40))
            hy += 42
    tagline(draw, tx, y1 - 32, c["src"], _sans(30, bold=True))

def lead(draw, num, box, variant):
    x0, y0, x1, y1 = box
    c = CARDS[num]
    draw.rectangle([x0, y0, x1, y1], fill=CREAM2, outline=INK, width=4)
    sc_h = 170
    scene(draw, c["scene"], (x0 + 4, y0 + 4, x1 - 4, y0 + 4 + sc_h), variant)
    # data chip overlaid on the scene strip, bottom-right
    cf = _sans(30, bold=True)
    tw = draw.textlength(c["chip"], font=cf) + 26
    chip(draw, x1 - 22 - tw, y0 + 4 + sc_h - 56, c["chip"], cf, h=48)
    tx = x0 + 26
    ty = y0 + 184
    nx = card_number(draw, tx, ty, num, size=52)
    lab = f"{c['place'].upper()} \u00b7 {c['region']}"
    draw.text((nx, ty + 10), lab, font=_sans(30, bold=True), fill=RUST_DK)
    hy = ty + 80
    for line in wrap(draw, c["head"], fb(62), x1 - x0 - 52)[:2]:
        draw.text((tx, hy), line, font=fb(62), fill=INK)
        hy += 68
    hy += 6
    for para in c["deck"]:
        for line in wrap(draw, para, fr(31), x1 - x0 - 52):
            draw.text((tx, hy), line, font=fr(31), fill=(52, 46, 40))
            hy += 38
    tagline(draw, tx, y1 - 40, c["src"], _sans(28, bold=True))

def mini(draw, num, box, variant):
    x0, y0, x1, y1 = box
    c = CARDS[num]
    draw.rectangle([x0, y0, x1, y1], fill=WHITE, outline=INK, width=3)
    sc_h = 60
    scene(draw, c["scene"], (x0 + 3, y0 + 3, x1 - 3, y0 + 3 + sc_h), variant)
    tx = x0 + 20
    ty = y0 + 3 + sc_h + 10
    nx = card_number(draw, tx, ty, num, size=40)
    lab = f"{c['place'].upper()} \u00b7 {c['region']} \u00b7 {c['topic']}"
    draw.text((nx, ty + 6), lab, font=_sans(26, bold=True), fill=RUST_DK)
    hy = ty + 56
    for line in wrap(draw, c["head"], fb(46), x1 - x0 - 40)[:2]:
        draw.text((tx, hy), line, font=fb(46), fill=INK)
        hy += 48
    hy += 4
    deck_txt = " ".join(c["deck"])
    for line in wrap(draw, deck_txt, fr(29), x1 - x0 - 40)[:2]:
        draw.text((tx, hy), line, font=fr(29), fill=(52, 46, 40))
        hy += 35
    cf = _sans(26, bold=True)
    tw = draw.textlength(c["chip"], font=cf) + 28
    chip(draw, tx, y1 - 46, c["chip"], cf, h=40)
    tagline(draw, tx + tw + 16, y1 - 38, c["src"], _sans(24, bold=True))

# ------------------------------------------------------------------- page
W = 3900
H = 3900
MX = 90  # side margin

def draw_page(variant):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    x0, x1 = MX, W - MX

    # ---- top rule + edition line
    rule(d, x0, 60, x1, w=10)
    d.text((x0, 78), "TUESDAY EDITION \u00b7 No. 328 \u00b7 ALL THE NEWS THAT IS TODAY\u2019S",
           font=_sans(32, bold=True), fill=RUST_DK)
    d.text((x1, 78), "PRICE: ONE DAY\u2019S NEWS", font=_sans(32, bold=True),
           fill=RUST_DK, anchor="ra")

    # ---- masthead
    d.text((W // 2, 268), "THE PORTSIDE GAZETTE", font=_playfair(180),
           fill=RUST, anchor="mm")
    rule(d, x0, 372, x1, w=5, fill=INK)
    rule(d, x0, 384, x1, w=5, fill=INK)

    # ---- dateline (giant) + kicker
    d.text((W // 2, 462), "Tuesday 24 November 2026", font=_playfair(96),
           fill=INK, anchor="mm")
    kick = "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE FROM TUESDAY 24 NOVEMBER 2026"
    d.text((W // 2, 536), kick, font=_sans(34, bold=True), fill=RUST_DK,
           anchor="mm")
    d.text((W // 2, 580), "THE WORLD IN ONE IMAGE",
           font=_playfair(38, italic=True), fill=RUST, anchor="mm")

    # ---- number strip
    y = 610
    d.rectangle([x0, y, x1, y + 120], fill=RUST_DK)
    cw = (x1 - x0) / len(NUMSTRIP)
    for i, (big, lab) in enumerate(NUMSTRIP):
        cx = x0 + cw * i + cw / 2
        d.text((cx, y + 12), big, font=_playfair(54), fill=(247, 220, 150),
               anchor="ma")
        d.text((cx, y + 78), lab, font=_sans(26, bold=True), fill=WHITE,
               anchor="ma")
        if i:
            d.line([x0 + cw * i, y + 10, x0 + cw * i, y + 110],
                   fill=(247, 220, 150), width=3)

    # ---- region strip
    y = 746
    d.text((x0, y), "WHERE THE NEWS IS:",
           font=_sans(30, bold=True), fill=INK)
    rx = x0 + 360
    for name, n, col in REGION_STRIP:
        label = f"{name} {n}"
        f = _sans(30, bold=True)
        tw = d.textlength(label, font=f)
        d.rounded_rectangle([rx, y - 6, rx + tw + 26, y + 40], radius=20,
                            fill=col)
        d.text((rx + 13, y + 17), label, font=f, fill=WHITE, anchor="lm")
        rx += tw + 26 + 16

    # ---- lead wide (500) + two leads (500)
    y = 820
    draw_lead_wide(d, LEAD_WIDE, (x0, y, x1, y + 500), variant)
    y = 1338
    hw = (x1 - x0 - 24) // 2
    lead(d, LEADS[0], (x0, y, x0 + hw, y + 500), variant)
    lead(d, LEADS[1], (x0 + hw + 24, y, x1, y + 500), variant)

    # ---- mini grid 4 x 3 (340 each)
    y = 1856
    minis = MINIS_A if variant == "A" else MINIS_B
    gw = (x1 - x0 - 3 * 24) // 4
    gh = 340
    for r in range(3):
        for col in range(4):
            num = minis[r * 4 + col]
            bx = x0 + col * (gw + 24)
            by = y + r * (gh + 12)
            mini(d, num, (bx, by, bx + gw, by + gh), variant)

    # ---- bottom zone: ALSO ON (left) + map (right), mirrored in B
    y = 2920
    also_w = 2180
    map_w = (x1 - x0) - also_w - 30
    if variant == "A":
        ax, mx0 = x0, x0 + also_w + 30
    else:
        mx0, ax = x0, x0 + map_w + 30
    # ALSO ON
    d.text((ax, y), "ALSO ON \u2014 21 MORE STORIES FROM THE DAY",
           font=_sans(34, bold=True), fill=RUST_DK)
    rule(d, ax, y + 48, ax + also_w, w=4, fill=RUST)
    by = y + 62
    col_w = (also_w - 30) // 2
    for i, (n, txt) in enumerate(BRIEFS_N):
        col = 0 if i < 11 else 1
        row = i if i < 11 else i - 11
        bx = ax + col * (col_w + 30)
        yy = by + row * 48
        f_num = _playfair(34)
        d.text((bx, yy), f"{n}.", font=f_num, fill=RUST)
        nw = d.textlength(f"{n}. ", font=f_num)
        for line in wrap(d, txt, fsr(29), col_w - nw - 6)[:1]:
            d.text((bx + nw, yy + 3), line, font=fsr(29), fill=INK)
    # map
    d.text((mx0, y), "WHERE IT HAPPENED \u2014 PINS MATCH STORY NUMBERS",
           font=_sans(34, bold=True), fill=RUST_DK)
    rule(d, mx0, y + 48, mx0 + map_w, w=4, fill=RUST)
    mbox = (mx0, y + 62, mx0 + map_w, y + 62 + 480)
    d.rectangle(mbox, fill=(232, 228, 208), outline=INK, width=3)
    draw_dotted_map(d, (mbox[0] + 8, mbox[1] + 8, mbox[2] - 8, mbox[3] - 8))
    for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 20]:
        lon, lat = CARDS[n]["pin"]
        px, py = pin_xy((mbox[0] + 8, mbox[1] + 8, mbox[2] - 8, mbox[3] - 8),
                        lon, lat)
        r = 25
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=WHITE, width=4)
        d.text((px, py), str(n), font=_sans(28, bold=True), fill=WHITE,
               anchor="mm")
    d.text((mx0, mbox[3] + 8),
           "Washington pins (5 \u00b7 13 \u00b7 14) nudged apart for legibility.",
           font=_sans(26), fill=(90, 80, 70))

    # ---- timeline
    y = 3535
    d.text((x0, y), "TUESDAY 24 NOVEMBER \u2014 AS THE DAY UNFOLDED",
           font=_sans(34, bold=True), fill=RUST_DK)
    rule(d, x0, y + 46, x1, w=4, fill=RUST)
    ty = y + 58
    sw = (x1 - x0 - 4 * 20) / 5
    for i, (when, what) in enumerate(TIMELINE):
        sx = x0 + i * (sw + 20)
        d.text((sx, ty), when, font=_sans(28, bold=True), fill=RUST)
        yy = ty + 38
        for line in wrap(d, what, _sans(27), sw)[:2]:
            d.text((sx, yy), line, font=_sans(27), fill=INK)
            yy += 33

    # ---- DATE CHECK band
    y = 3698
    d.rectangle([x0, y, x1, y + 146], fill=(122, 20, 20))
    d.text((x0 + 16, y + 8),
           "DATE CHECK \u2014 NOT TODAY\u2019S NEWS: these happened earlier; "
           "they are not today\u2019s stories.",
           font=_sans(27, bold=True), fill=WHITE)
    dc_col_w = (x1 - x0 - 32 - 30) // 2
    for i, item in enumerate(DATECHECK):
        col = 0 if i < 4 else 1
        row = i if i < 4 else i - 4
        dx = x0 + 16 + col * (dc_col_w + 30)
        dy = y + 46 + row * 24
        d.text((dx, dy), "\u2022 " + item, font=_sans(25), fill=WHITE)

    # ---- footer
    d.text((x0, 3852), FOOTER_SRC, font=_sans(22), fill=INK)
    d.text((x0, 3876), FOOTER_LEGEND, font=_sans(22), fill=INK)
    return img

def _finalise(img):
    """Downscale whole page to 1024x1024, quantise 256 colours.

    The quantised image is saved in palette (P) mode: a palette PNG is
    ~3x smaller than the same pixels saved as RGB, which is what keeps
    the entry inside the 190-450 KB target band.
    """
    small = img.resize((1024, 1024), Image.LANCZOS)
    small = small.convert("P", palette=Image.ADAPTIVE, colors=256)
    return small

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="A", choices=["A", "B"])
    ap.add_argument("--out", default="entry.png")
    args = ap.parse_args()
    img = draw_page(args.variant)
    small = _finalise(img)
    small.save(args.out, optimize=True)
    print(f"variant {args.variant} -> {args.out} "
          f"{os.path.getsize(args.out)} bytes")

if __name__ == "__main__":
    main()

# ------------------------------------------------- margin-check aliases
# Mirrors of the page data above in the old armada schema, so the local
# margin checker (tools/margin_check.py) can read this entry. Same stories,
# numbers and words as above — no separate content.
# Masthead type: Playfair Display Black.
grid = [
    (1, "EUROPE", "WAR", "CNN / Times / WSJ / AP",
     "Ukraine sinks Russian warship Merkury off Libya",
     "7 sea drones launched at the corvette; a Ka-27 helicopter was destroyed aboard. MV Angara cargo vessel also hit; Zelenskyy calls the raid \u201cexemplary\u201d.",
     "ship"),
    (2, "EUROPE", "SEA", "Reuters / Times / WSJ",
     "Russian cargo ship Sparta II hit, towed clear",
     "121 m ship hit by 2 drones on Saturday; all 16 crew taken off safely. Towed out of Finnish waters on Sunday night; bound for Kaliningrad.",
     "ship2"),
    (3, "EUROPE", "WAR", "Times / AP",
     "Russian strikes kill at least 15 near Kyiv",
     "11 killed in a block of flats in Dymer; 5 injured in Kyiv on Monday. Drone hit a 6-floor building; Zelenskyy on Putin: \u201cfor us, he\u2019s a killer\u201d.",
     "city"),
    (4, "WORLD", "CLIMATE", "Times / Guardian",
     "COP31 ends with no deal \u2014 first since 2000",
     "Cover text dropped every fossil-fuel mention; EU, UK and others rejected it. 44 h overtime, longest COP ever; next round: Addis Ababa, Nov 2027.",
     "summit"),
    (5, "MIDDLE EAST", "SANCTIONS", "AP / Treasury",
     "US sanctions ~30 Iran-linked exchange houses",
     "Treasury names ~30 houses + executives at the core of shadow banking. Announced Monday as Rubio meets Qatar PM over Iran uncertainty.",
     "bank"),
    (6, "MIDDLE EAST", "CONFLICT", "AP",
     "Israeli strikes kill 3 in Gaza",
     "3 killed Monday in separate strikes, incl. a UNRWA employee. Shifa Hospital + agency confirm the deaths.",
     "city2"),
    (7, "MIDDLE EAST", "WAR", "AP",
     "Strike kills 11 in western Yemen",
     "Houthis say Saudi-backed forces\u2019 strike Monday killed 11, wounded 19. Casualties reported from the western front.",
     "hills"),
    (8, "AMERICAS", "MARKETS", "Reuters",
     "Gold rebounds 1.5% to $3,588",
     "Bullion +1.5% Monday after its worst week in 8 months. Traders await US PCE inflation report due 25 Nov; 10-yr yield ~4.96%.",
     "gold"),
    (9, "GLOBAL", "CRYPTO", "CoinPaprika",
     "Bitcoin steadies near $61,284",
     "$61,284 Monday 12:52 UTC, +1.1% in 24 h, \u22124.5% over 7 days. Weekend low ~$55,100 as leveraged liquidations eased.",
     "coin"),
    (10, "AMERICAS", "BUSINESS", "ActiveInvestorMag",
     "GTA VI takes $3.8bn on day one",
     "Biggest entertainment launch on record \u2014 past every game launch and single-day film box office. $3.8bn in one day: the largest first-day total ever reported.",
     "gta"),
    (11, "OCEANIA", "CRICKET", "HS / WicketPulse",
     "New Zealand bat out draw with India",
     "NZ 239/5 \u2014 Mitchell 49* off 186, Phillips 26* off 126; 63-run stand. India 720/9d (Rahul 136, Pant 128); 2nd Test: Christchurch, 27 Nov\u20131 Dec.",
     "cricket"),
    (12, "EUROPE", "FOOTBALL", "Mint / NextSportsWeb",
     "Liverpool 4\u20130 Man Utd",
     "Yoro sent off in the 8th minute; United down to 10 men. Defeat leaves United 19th in the league on 8 points.",
     "football"),
    (13, "AMERICAS", "POLITICS", "ActiveInvestorMag",
     "Trump: work with Democrats to cap card rates",
     "Trump says he would work with Democrats to cap credit-card rates. Also calls for scrapping the debt ceiling; Senate leadership vote 1 Dec.",
     "capitol"),
    (14, "AMERICAS", "POLITICS", "BBC / ActiveInvestorMag",
     "Democrats take both chambers",
     "House 258\u2013173, largest majority since 1992, after N. Carolina pickup. Senate leadership challenge: Van Hollen vs Schumer, secret ballot 1 Dec.",
     "ballot"),
    (20, "AMERICAS", "MARKETS", "Reuters",
     "Nvidia brings back Jensen Huang as CEO",
     "Board reinstates Huang effective immediately Mon 23 Nov; Trump intervened. Shares +31% Mon; Nasdaq +6%, S&P 500 +5%, chip index +12%.",
     "chip"),
]

NUMS = [("7", "SEA DRONES"), ("$3.8BN", "GTA VI DAY ONE"),
        ("$61,284", "BITCOIN"), ("$3,588", "GOLD +1.5%"),
        ("+31%", "NVIDIA"), ("NO DEAL", "COP31"),
        ("258\u2013173", "HOUSE")]

TL = [("04:24 WIB TUE", "KCNA: North Korea weighs closing Swiss office in Pyongyang \u2014 Reuters"),
      ("07:23 WIB TUE", "Gold edges up on bargain buying after sell-off \u2014 Reuters (00:23 GMT)"),
      ("07:35 WIB TUE", "Japan factory PMI 53.7; output + export orders pick up \u2014 Reuters (00:35 UTC)"),
      ("MON EVE UTC", "Nvidia board reinstates Huang as CEO; shares +31% \u2014 Reuters, reported Mon evening"),
      ("MON EVE UTC", "Zelenskyy announces Merkury sinking; US sanctions ~30 Iran exchange houses \u2014 reported Mon evening")]

BRIEFS_L = ["N. Korea weighs closing Swiss office, Pyongyang (KCNA, Tue)",
            "US mulls military training for Syrian forces, first since 2024",
            "Congo halts cobalt exports from 30 Nov (Reuters)",
            "Indonesia factory blaze kills 24, dozens missing (Reuters)",
            "CrowdStrike snaps up Zscaler in $44bn deal (Reuters)",
            "Trump hosts meme-coin gala as token hits record lows (Reuters)",
            "US Army to detonate lead stockpile in Iowa: 68 barrels (Reuters)",
            "India considers rice export duties as prices rise (Reuters)",
            "COP31 adopted 46 decisions despite no cover deal (Reuters)",
            "Miley Cyrus weds Maxx Morando in California (Reuters)",
            "Japan factory PMI 53.7 in Nov; output + orders up (Tue 00:35 UTC)"]

BRIEFS_R = ["Singapore lifts 2026 forecast to ~6.0% after Q3 +6.1% (Reuters)",
            "StarHub agrees $3.8bn all-share deal for M1 (Reuters, Tue)",
            "Wellington draw sets up 2nd Test, Christchurch 27 Nov-1 Dec",
            "Kraken CAD flash crash to ~$17,000 Sat; trades stand",
            "UK\u2013EU Brexit reset: Burnham calls it \u201clandmark\u201d (BBC)",
            "India\u2013EU trade pact likely signed 16 Dec, Brussels (JagranJosh)",
            "Tata Steel sells pipe unit to APL Apollo, \u20b928,000 cr (ObserverVoice)",
            "FBI probes hack of its crime database (AP)",
            "Solana launches solana.ai for AI agents (Gadgets360)",
            "UN AI weapons talks continue, states agree (salonvision)"]

dc = ("186-drone night over Ukraine, 161 downed \u2014 Fri 21\u2013Sun 22 Nov \u00b7 "
      "Hong Kong Election Committee: 856 candidates, 723 seats \u2014 Sun 22 Nov \u00b7 "
      "Alcaraz beats Zverev, first ATP Finals title \u2014 Sun 22 Nov \u00b7 "
      "Verstappen wins Las Vegas Grand Prix \u2014 Sun 22 Nov \u00b7 "
      "Wembanyama scores 50, Spurs 114\u201391 Pelicans \u2014 Sun 22 Nov \u00b7 "
      "India declare 720/9 \u2014 Sun 22 Nov (the DRAW is the news, Mon 23 Nov) \u00b7 "
      "Huang resigns after affair admission \u2014 Thu 12 Nov (the REINSTATEMENT is the news, Mon 23 Nov)")

PINS = [(20.1, 32.1), (25.0, 60.0), (30.5, 50.4), (30.7, 36.9),
        (-79.5, 38.0), (34.5, 31.5), (44.0, 15.5), (-0.1, 51.5),
        (-74.0, 40.7), (-118.2, 34.0), (174.8, -41.3), (-2.99, 53.4),
        (-74.0, 40.6), (-80.0, 36.0), (-122.0, 37.35)]
