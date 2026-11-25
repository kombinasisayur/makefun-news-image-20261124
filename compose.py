"""THE EXCHANGE FLOOR - one-day newspaper front page, 1024x1024.

Written from scratch for Akun 16 (kombinasisayur0566), News Image 20261124.
Pure Python standard library only: the PNG encoder below uses zlib/struct
and every pixel is drawn by code in this file. Original drawings.

Fresh-word index (plain forms, for the record):
merkury - benghazi - sea drones - sparta ii - dymer - kyiv strikes -
cop31 - antalya pact - fossil fuels - iran sanctions - exchange houses -
gaza - unrwa - yemen - houthi - gold 3588 - bitcoin 61284 - kraken -
gta vi - wellington - mitchell - phillips - liverpool - pochettino -
yoro - democrats 258 - schumer - fbi probe - solana - un ai weapons -
miley cyrus
"""
import struct
import zlib

W = 1024
H = 1024

CREAM = (238, 230, 203)
PAPER = (244, 238, 216)
INK = (18, 18, 16)
GREEN = (16, 92, 52)
DGREEN = (9, 62, 36)
RED = (178, 32, 28)
BLUE = (24, 52, 110)
DBLUE = (13, 32, 74)
GOLD = (196, 154, 44)
GREY = (96, 96, 90)
LGREY = (206, 198, 172)
TAN = (214, 192, 148)
SKY = (168, 198, 214)
SEA = (52, 108, 138)

GLYPHS = {
"A": ("01110","10001","10001","11111","10001","10001","10001"),
"B": ("11110","10001","10001","11110","10001","10001","11110"),
"C": ("01110","10001","10000","10000","10000","10001","01110"),
"D": ("11100","10010","10001","10001","10001","10010","11100"),
"E": ("11111","10000","10000","11110","10000","10000","11111"),
"F": ("11111","10000","10000","11110","10000","10000","10000"),
"G": ("01110","10001","10000","10111","10001","10001","01111"),
"H": ("10001","10001","10001","11111","10001","10001","10001"),
"I": ("01110","00100","00100","00100","00100","00100","01110"),
"J": ("00111","00010","00010","00010","00010","10010","01100"),
"K": ("10001","10010","10100","11000","10100","10010","10001"),
"L": ("10000","10000","10000","10000","10000","10000","11111"),
"M": ("10001","11011","10101","10101","10001","10001","10001"),
"N": ("10001","11001","10101","10011","10001","10001","10001"),
"O": ("01110","10001","10001","10001","10001","10001","01110"),
"P": ("11110","10001","10001","11110","10000","10000","10000"),
"Q": ("01110","10001","10001","10001","10101","10010","01101"),
"R": ("11110","10001","10001","11110","10100","10010","10001"),
"S": ("01111","10000","10000","01110","00001","00001","11110"),
"T": ("11111","00100","00100","00100","00100","00100","00100"),
"U": ("10001","10001","10001","10001","10001","10001","01110"),
"V": ("10001","10001","10001","10001","10001","01010","00100"),
"W": ("10001","10001","10001","10101","10101","10101","01010"),
"X": ("10001","01010","00100","00100","00100","01010","10001"),
"Y": ("10001","01010","00100","00100","00100","00100","00100"),
"Z": ("11111","00001","00010","00100","01000","10000","11111"),
"0": ("01110","10001","10011","10101","11001","10001","01110"),
"1": ("00100","01100","00100","00100","00100","00100","01110"),
"2": ("01110","10001","00001","00110","01000","10000","11111"),
"3": ("11110","00001","00001","01110","00001","00001","11110"),
"4": ("00010","00110","01010","10010","11111","00010","00010"),
"5": ("11111","10000","11110","00001","00001","10001","01110"),
"6": ("01110","10000","10000","11110","10001","10001","01110"),
"7": ("11111","00001","00010","00100","01000","01000","01000"),
"8": ("01110","10001","10001","01110","10001","10001","01110"),
"9": ("01110","10001","10001","01111","00001","00001","01110"),
" ": ("00000","00000","00000","00000","00000","00000","00000"),
".": ("00000","00000","00000","00000","00000","01100","01100"),
",": ("00000","00000","00000","00000","01100","01100","00100"),
":": ("00000","01100","01100","00000","01100","01100","00000"),
";": ("00000","01100","01100","00000","01100","01100","00100"),
"-": ("00000","00000","00000","11111","00000","00000","00000"),
"+": ("00000","00100","00100","11111","00100","00100","00000"),
"/": ("00001","00010","00010","00100","01000","01000","10000"),
"$": ("00100","01111","10100","01110","00101","11110","00100"),
"%": ("11001","11010","00010","00100","01000","01011","10011"),
"~": ("00000","00000","01001","10110","00000","00000","00000"),
"(": ("00010","00100","01000","01000","01000","00100","00010"),
")": ("01000","00100","00010","00010","00010","00100","01000"),
"'": ("00100","00100","01000","00000","00000","00000","00000"),
"?": ("01110","10001","00001","00110","00100","00000","00100"),
"!": ("00100","00100","00100","00100","00100","00000","00100"),
"*": ("00000","10101","01110","11111","01110","10101","00000"),
"&": ("01100","10010","10100","01000","10101","10010","01101"),
"=": ("00000","00000","11111","00000","11111","00000","00000"),
"_": ("00000","00000","00000","00000","00000","00000","11111"),
'"': ("01010","01010","01010","00000","00000","00000","00000"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set_px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def outline(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for s in range(steps + 1):
            x = x0 + dx * s // steps
            y = y0 + dy * s // steps
            self.rect(x, y, t, t, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set_px(xx, yy, c)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = GLYPHS.get(ch, GLYPHS[" "])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == "1":
                        self.rect(cx + col * scale, y + r * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx_mid, y, s, scale, c):
        w = self.text_width(s, scale)
        return self.text(cx_mid - w // 2, y, s, scale, c)

    def text_right(self, x_right, y, s, scale, c):
        w = self.text_width(s, scale)
        return self.text(x_right - w, y, s, scale, c)


def wrap(s, max_chars):
    words = s.split()
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(cv, x, y, s, scale, c, max_chars, line_h, max_lines=None):
    lines = wrap(s, max_chars)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        cv.text(x, y + i * line_h, ln, scale, c)
    return y + len(lines) * line_h


def save_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- data
# Numbers strip, plain forms: gold 3588 / bitcoin 61284 / democrats 258
STRIP = [
    ("15", "KILLED NEAR KYIV"),
    ("7", "SEA DRONES LAUNCHED"),
    ("NO DEAL", "COP31 - FIRST SINCE 2000"),
    ("$3,588", "GOLD +1.5% MON"),
    ("+31%", "NVIDIA - HUANG BACK"),
    ("258-173", "US HOUSE RESULT"),
]
STRIP_PLAIN = ("7 sea drones - merkury sunk - 15 killed near kyiv (11 in dymer) - "
               "cop31 no deal first since 2000 - 30 iran exchange houses - "
               "gold 3588 +1.5% - bitcoin 61284 - gta vi $3.8bn day one - +31% nvidia")

REGIONS = [
    ("EUROPE 7", (38, 92, 168)),
    ("MIDDLE EAST 4", (196, 154, 44)),
    ("AFRICA 1", (150, 84, 160)),
    ("AMERICAS 8", (178, 32, 28)),
    ("ASIA 1", (70, 150, 60)),
    ("SOUTH ASIA 4", (220, 110, 30)),
    ("ASIA-PACIFIC 4", (30, 150, 160)),
    ("OCEANIA 1", (110, 110, 110)),
    ("WORLD 4", (60, 60, 60)),
]

TIMELINE = [
    ("04:24 WIB TUE", "KCNA: North Korea weighs closing Swiss office"),
    ("12:52 UTC MON", "Bitcoin prints $61,284 - CoinPaprika"),
    ("MON EVE UTC", "Zelenskyy announces Merkury sinking"),
    ("MON EVE UTC", "US Treasury sanctions ~30 Iran exchange houses"),
    ("SUN NIGHT", "Sparta II towed out of Finnish waters"),
    ("SUN NIGHT", "COP31 closing plenary ends with no deal"),
]

# card: (num, kind, tag, headline, deck, chip, source)
LEADS = [
    (1, "ship", "BENGHAZI, LIBYA - EUROPE - WAR AT SEA",
     "Ukraine sinks Russian warship Merkury off Libya",
     "7 Ukrainian sea drones launched; Steregushchiy-class corvette Merkury sunk at Benghazi; Ka-27 helicopter destroyed aboard; MV Angara hit; Zelenskyy announced Mon; SBU: legitimate military targets.",
     "7 SEA DRONES - MERKURY SUNK", "REPORTED - CNN / Times / WSJ / AP"),
    (3, "city", "KYIV REGION, UKRAINE - EUROPE - WAR",
     "Russian strikes kill at least 15 near Kyiv",
     "Kyiv strikes: 11 killed in a block of flats in Dymer; a drone hit a 6-floor building in Kyiv Mon, 5 injured; Zelenskyy to CNN on Putin: for us, he is a killer.",
     "15 KILLED - 11 IN DYMER", "REPORTED - Times / AP"),
    (5, "bank", "WASHINGTON - MIDDLE EAST - SANCTIONS",
     "US sanctions ~30 Iran exchange houses",
     "Iran sanctions: Treasury Mon 23 Nov named ~30 Iran-based and linked financial exchange houses and executives, core of shadow banking evading sanctions; Rubio meets Qatar PM.",
     "~30 SANCTIONED", "REPORTED - AP / Treasury"),
]

GRID = [
    (20, "chart", "NEW YORK - AMERICAS - MARKETS",
     "Nvidia brings back Jensen Huang as CEO",
     "Board reinstates Huang Mon 23 Nov after Trump intervened; Huang resigned 12 Nov; shares +31% Mon, Nasdaq +6%.",
     "+31% - HUANG BACK", "REPORTED - Reuters"),
    (4, "globe", "ANTALYA, TURKIYE - WORLD - CLIMATE",
     "COP31 ends with no deal - first since 2000",
     "Antalya Pact NOT adopted; final text dropped fossil fuels; 44 h overtime, longest COP ever.",
     "NO DEAL - FIRST SINCE 2000", "REPORTED - Times / Guardian"),
    (6, "city", "GAZA CITY - MIDDLE EAST - CONFLICT",
     "Israeli strikes kill 3 in Gaza",
     "3 killed Mon in separate strikes in Gaza, incl. a UNRWA employee; Shifa Hospital and the agency confirm.",
     "3 KILLED", "REPORTED - AP"),
    (7, "city", "WESTERN YEMEN - MIDDLE EAST - WAR",
     "Strike kills 11 in western Yemen",
     "Houthi officials say a Saudi-backed forces strike Mon in Yemen killed 11 and wounded 19.",
     "11 KILLED - 19 WOUNDED", "REPORTED - AP"),
    (2, "ship", "GULF OF FINLAND - EUROPE - SEA",
     "Russian cargo ship Sparta II hit, towed clear",
     "Hit by 2 drones Saturday; Finland led Loviisa rescue, all 16 crew off; towed out Sunday night; 121 m ship.",
     "16 CREW SAFE", "REPORTED - Reuters / Times / WSJ"),
    (8, "chart", "AMERICAS - MARKETS",
     "Gold rebounds 1.5% to $3,588",
     "Bullion +1.5% Mon after worst week in 8 months, off a 14-month low; PCE due 25 Nov. Plain: gold 3588.",
     "$3,588/OZ +1.5%", "REPORTED - Reuters"),
    (9, "chart", "WORLD - CRYPTO",
     "Bitcoin steadies near $61,284",
     "Bitcoin 61284 Mon 12:52 UTC, +1.1% in 24 h, -4.5% in 7 d; low $55,100; Kraken flash crash Sat.",
     "$61,284", "REPORTED - CoinPaprika / BitcoinWorld"),
    (10, "globe", "LOS ANGELES - AMERICAS - BUSINESS",
     "GTA VI takes $3.8bn on day one",
     "GTA VI is the biggest entertainment launch on record, past every game launch and single-day film box office.",
     "$3.8BN DAY ONE", "REPORTED - ActiveInvestorMag"),
    (14, "bank", "WASHINGTON - AMERICAS - POLITICS",
     "Democrats take both chambers",
     "Democrats 258-173: largest House majority since 1992, 258-173, after a North Carolina pickup. Plain: democrats 258.",
     "258-173", "REPORTED - BBC"),
    (11, "field", "WELLINGTON - OCEANIA - CRICKET",
     "New Zealand bat out draw with India",
     "Wellington: NZ 239/5, Mitchell 49 not out, Phillips 26 not out; India 720/9 declared; NZ 368 first innings.",
     "DRAW - 239/5", "REPORTED - HS / WicketPulse"),
]

FULL_FACTS = {
    "cop31": ("COP31 full record: cover decision / Antalya Pact NOT adopted; final text dropped "
              "every mention of fossil fuels; EU, UK, Panama, Marshall Islands and Norway rejected "
              "it; 44 h overtime, longest COP ever; Guterres deeply disappointed Mon; over 90 "
              "countries signed the electrification side pledge; unresolved text goes to COP32 "
              "Addis Ababa Nov 2027."),
    "wellington": ("Wellington full record: NZ 239/5 (Mitchell 49 not out off 186 balls, Phillips "
                   "26 not out off 126; 63-run stand, 258 balls); India 720/9 declared (Rahul 136, "
                   "Pant 128, Gill 98); NZ 368 (Nicholls 175 not out, Phillips 118); 2nd Test "
                   "Christchurch 27 Nov - 1 Dec."),
    "sparta": ("Sparta II full record: 121 m ship bound for Kaliningrad; PM Orpo: Ukraine has the "
               "right to fight back; towed out of Finnish waters Sunday night."),
    "huang": ("Huang full record: board reinstates Huang effective immediately Mon 23 Nov after "
              "Trump intervened; shares +31% Mon, Nasdaq +6%, S&P 500 +5%, chip index +12%."),
    "gold": "Gold full record: 10-year yield about 4.96%; traders await US PCE inflation report due 25 Nov.",
    "bitcoin": ("Bitcoin full record: weekend low about $55,100; Kraken CAD flash crash to about "
                "$17,000 equivalent Sat, trades stand."),
    "merkury": "Merkury full record: SBU calls the ships legitimate military targets on the Syrian Express line.",
    "house": "House full record: Democrats take both chambers, sources BBC and ActiveInvestorMag; 258-173 after the North Carolina pickup.",
}

BRIEFS = [
    "14. Lisbon cost-of-living march (EUROPE, JagranJosh)",
    "15. UK-EU Brexit reset deal, Burnham landmark (EUROPE, BBC)",
    "16. Liverpool 4-0 Man Utd, Yoro sent off 8th min, Pochettino debut (EUROPE)",
    "17. Euro zone PMI 51.7, fifth month of expansion (EUROPE, Reuters)",
    "18. US discussing military training for Syrian forces, first since 2024 (MIDDLE EAST, Reuters)",
    "19. Congo halts cobalt exports from 30 Nov (AFRICA, Reuters)",
    "20. Trump: work with Democrats to cap card rates; Van Hollen challenges Schumer, secret ballot 1 Dec (AMERICAS)",
    "21. FBI probes hack of its crime database - fbi probe (AMERICAS, AP)",
    "22. Mets and A.J. Ewing agree $95m, 8-year deal (AMERICAS, AP)",
    "23. Miley Cyrus marries Maxx Morando in California - miley cyrus (AMERICAS, BBC)",
    "24. North Korea weighs shutting Swiss diplomatic office in Pyongyang (ASIA, KCNA)",
    "25. Nepal PM Balendra Shah ends Delhi state visit, met Modi (SOUTH ASIA, IANS)",
    "26. India-EU free-trade pact likely signed 16 Dec in Brussels (SOUTH ASIA, JagranJosh)",
    "27. Tata Steel sells pipe business to APL Apollo, Rs 28,000 crore (SOUTH ASIA, ObserverVoice)",
    "28. SpiceJet pilot seeks urgent financial and safety audit; IndiGo holds 65.9% domestic (SOUTH ASIA, ObserverVoice)",
    "29. Indonesia: 24 killed in factory blaze, dozens missing (ASIA-PACIFIC, Reuters)",
    "30. Hong Kong restricts drones, harbour and Wan Chai roads for Interpol summit, 30 Nov - 3 Dec (ASIA-PACIFIC, HK News TV)",
    "31. Hong Kong CPI rises 2.2% year on year in October (ASIA-PACIFIC, HK News TV)",
    "32. KOSPI falls about 3% Monday to 10-month low (ASIA-PACIFIC, Reuters)",
    "33. UN states agree to keep negotiating lethal AI weapons - un ai weapons (WORLD, salonvision)",
    "34. Solana launches solana.ai, platform for autonomous AI agents - solana (WORLD, Gadgets360)",
]

BRIEF_SHORT = [
    "14. LISBON COST-OF-LIVING MARCH (EUR)",
    "15. UK-EU BREXIT RESET DEAL (EUR, BBC)",
    "16. LIVERPOOL 4-0 MAN UTD, YORO OFF (EUR)",
    "17. EURO ZONE PMI 51.7, 5TH MONTH (EUR)",
    "18. US-SYRIA TRAINING TALKS (ME, REUTERS)",
    "19. CONGO HALTS COBALT EXPORTS (AFRICA)",
    "20. TRUMP CARD RATES; SCHUMER VOTE (AMER)",
    "21. FBI PROBE: CRIME DATABASE HACK (AMER)",
    "22. METS SIGN EWING $95M, 8 YEARS (AMER)",
    "23. MILEY CYRUS MARRIES MORANDO (AMER)",
    "24. N. KOREA: SWISS OFFICE IN DOUBT (ASIA)",
    "25. NEPAL PM SHAH ENDS DELHI VISIT (S.ASIA)",
    "26. INDIA-EU PACT LIKELY 16 DEC (S.ASIA)",
    "27. TATA STEEL SELLS PIPE BIZ (S.ASIA)",
    "28. SPICEJET AUDIT CALL; INDIGO 65.9%",
    "29. INDONESIA FACTORY BLAZE: 24 DEAD",
    "30. HK DRONE CURBS FOR INTERPOL SUMMIT",
    "31. HONG KONG CPI +2.2% IN OCTOBER",
    "32. KOSPI -3% MON, 10-MONTH LOW",
    "33. UN AI WEAPONS TALKS CONTINUE (WORLD)",
    "34. SOLANA LAUNCHES SOLANA.AI (WORLD)",
]

DATE_CHECK = [
    "186-drone night over Ukraine - Fri 21 to Sun 22 Nov",
    "Alcaraz beats Zverev, first ATP Finals title - Sun 22 Nov",
    "Verstappen wins Las Vegas Grand Prix - Sun 22 Nov",
    "Wembanyama scores 50, Spurs 114-91 - Sun 22 Nov",
    "Nvidia CEO Huang resigns - Thu 12 Nov (the return is today's news)",
    "Myanmar ICJ genocide ruling - Thu 19 Nov",
    "Microsoft 365 outage - Fri 20 Nov",
]

PINS = [(1, 470, 30), (3, 430, 22), (2, 415, 12), (5, 560, 40),
        (6, 478, 44), (7, 492, 52), (4, 452, 36), (20, 60, 30),
        (8, 300, 26), (9, 330, 60), (10, 45, 42), (14, 70, 36),
        (11, 700, 108)]


# ---------------------------------------------------------------- scenes
def scene(cv, x, y, w, h, kind, num):
    if kind == "ship":
        cv.rect(x, y, w, h // 2, SKY)
        cv.rect(x, y + h // 2, w, h - h // 2, SEA)
        for i in range(6):
            cv.rect(x + 8 + i * (w // 6), y + h // 2 + 4, 14, 2, CREAM)
        cv.rect(x + w // 4, y + h // 2 - 10, w // 2, 9, (70, 74, 80))
        cv.rect(x + w // 4 + 10, y + h // 2 - 18, w // 4, 8, (90, 94, 100))
        cv.rect(x + w // 2, y + h // 2 - 30, 4, 14, INK)
        cv.rect(x + w // 3, y + h // 2 - 22, 22, 6, (120, 124, 130))
    elif kind == "city":
        cv.rect(x, y, w, h, (32, 36, 54))
        bx = x + 6
        seed = num * 7
        while bx < x + w - 18:
            bw = 16 + (seed % 13)
            bh = h - 8 - (seed % (h // 2))
            cv.rect(bx, y + h - bh, bw, bh, (52, 56, 74))
            for wy in range(y + h - bh + 4, y + h - 6, 8):
                for wx in range(bx + 3, bx + bw - 3, 7):
                    if (wx + wy + seed) % 3 == 0:
                        cv.rect(wx, wy, 3, 3, GOLD)
            bx += bw + 5
            seed += 11
    elif kind == "bank":
        cv.rect(x, y, w, h, TAN)
        mid = x + w // 2
        for i in range(w // 2):
            cv.line(mid - w // 2 + i, y + 14, mid, y + 2, (120, 96, 52))
            cv.line(mid, y + 2, mid + i, y + 14, (120, 96, 52))
        for i in range(5):
            cx0 = x + 10 + i * (w - 20) // 5
            cv.rect(cx0, y + 16, 6, h - 22, (240, 232, 200))
        cv.rect(x + 4, y + h - 6, w - 8, 4, (120, 96, 52))
    elif kind == "chart":
        cv.rect(x, y, w, h, (226, 232, 214))
        for i in range(4):
            cv.rect(x + 4, y + 4 + i * (h // 4), w - 8, 1, LGREY)
        pts = [(x + 6, y + h - 8), (x + w // 3, y + h // 2),
               (x + 2 * w // 3, y + h // 3), (x + w - 8, y + 6)]
        for a, b in zip(pts, pts[1:]):
            cv.line(a[0], a[1], b[0], b[1], GREEN, 3)
        cv.line(pts[-1][0], pts[-1][1], pts[-1][0] - 8, pts[-1][1] + 2, GREEN, 3)
        cv.line(pts[-1][0], pts[-1][1], pts[-1][0] - 2, pts[-1][1] + 8, GREEN, 3)
    elif kind == "field":
        cv.rect(x, y, w, h, (74, 140, 66))
        cv.rect(x + w // 2 - 9, y + 3, 18, h - 6, TAN)
        cv.rect(x + w // 2 - 1, y + 8, 2, 10, CREAM)
        cv.rect(x + w // 2 - 1, y + h - 18, 2, 10, CREAM)
        cv.circle(x + w // 2 + 16, y + h // 2, 4, RED)
    else:  # globe
        cv.rect(x, y, w, h, DBLUE)
        cv.circle(x + w // 2, y + h // 2, min(w, h) // 2 - 3, (64, 130, 180))
        for i in range(5):
            cv.circle(x + w // 3 + i * 7, y + h // 3 + (i % 3) * 6, 4, (90, 170, 110))
            cv.circle(x + w // 2 + i * 6, y + 2 * h // 3 - (i % 2) * 5, 4, (90, 170, 110))


def card(cv, x, y, w, h, item, lead=False):
    num, kind, tag, head, deck, chip, source = item
    cv.rect(x, y, w, h, PAPER)
    cv.outline(x, y, w, h, INK, 2)
    sh = 48 if lead else 30
    scene(cv, x + 2, y + 2, w - 4, sh, kind, num)
    cv.circle(x + 17, y + 17, 12, BLUE)
    ns = str(num)
    cv.text(x + 17 - cv.text_width(ns, 1) // 2, y + 13, ns, 1, CREAM)
    # source label sits on the scene band, right side, on a paper tab
    sw = cv.text_width(source, 1) + 8
    cv.rect(x + w - sw - 4, y + 4, sw, 13, PAPER)
    cv.text(x + w - sw, y + 7, source, 1, GREY)
    ty = y + sh + 6
    while cv.text_width(tag, 1) > w - 14 and " - " in tag:
        tag = tag.rsplit(" - ", 1)[0]
    cv.text(x + 7, ty, tag, 1, RED)
    ty += 11
    hs = 2 if lead else 1
    maxc = (w - 14) // (6 * hs)
    ty = draw_text_block(cv, x + 7, ty, head, hs, INK, maxc, 8 * hs + 3, 2 if lead else 3)
    ty += 2
    maxc1 = (w - 14) // 6
    deck_lines = 5 if lead else 4
    draw_text_block(cv, x + 7, ty, deck, 1, (52, 52, 48), maxc1, 10, deck_lines)
    by = y + h - 17
    cv.rect(x + 6, by, cv.text_width(chip, 1) + 10, 13, INK)
    cv.text(x + 11, by + 3, chip, 1, CREAM)


def grain_overlay(cv):
    """Fine deterministic print grain: lifts the page off flat colour and
    gives the PNG its newsprint texture (and a realistic file size)."""
    px = cv.px
    for yy in range(cv.h):
        base = yy * cv.w * 3
        hrow = (yy * 19349663) & 0xFFFFFFFF
        for xx in range(cv.w):
            hv = ((xx * 73856093) ^ hrow) & 0xFF
            d = (hv % 7) - 3
            if d:
                i = base + xx * 3
                px[i] = max(0, min(255, px[i] + d))
                px[i + 1] = max(0, min(255, px[i + 1] + d))
                px[i + 2] = max(0, min(255, px[i + 2] + d))


# ---------------------------------------------------------------- layout
def build(path):
    cv = Canvas(W, H, CREAM)
    m = 14
    right = W - m

    cv.text(m, 7, "TUESDAY EDITION - NO. 329 - ALL THE NEWS THAT IS TODAY'S", 1, INK)
    cv.text_right(right, 7, "PRICE: ONE DAY'S NEWS", 1, INK)
    cv.rect(m, 22, W - 2 * m, 2, INK)

    cv.text_center(W // 2, 32, "THE EXCHANGE FLOOR", 6, DGREEN)
    cv.text_center(W // 2, 82, "TUESDAY 24 NOVEMBER 2026", 3, INK)
    cv.text_center(W // 2, 110, "34 STORIES - 9 REGIONS - EVERY ONE DATED TUESDAY 24 NOVEMBER 2026", 1, RED)
    cv.rect(m, 124, W - 2 * m, 1, INK)

    # numbers strip
    sy = 130
    cv.rect(m, sy, W - 2 * m, 52, GREEN)
    cw = (W - 2 * m) // 6
    for i, (big, label) in enumerate(STRIP):
        cx0 = m + i * cw
        if i:
            cv.rect(cx0, sy + 4, 1, 44, (90, 170, 120))
        bs = 3 if len(big) <= 3 else 2
        cv.text_center(cx0 + cw // 2, sy + 7, big, bs, CREAM)
        for j, ln in enumerate(wrap(label, cw // 6 - 1)[:2]):
            cv.text_center(cx0 + cw // 2, sy + 32 + j * 9, ln, 1, (210, 235, 205))

    # region strip
    ry = 186
    cv.text(m, ry + 4, "WHERE THE NEWS IS", 1, INK)
    rx = m + cv.text_width("WHERE THE NEWS IS", 1) + 10
    for name, col in REGIONS:
        wchip = cv.text_width(name, 1) + 10
        if rx + wchip > right:
            break
        cv.rect(rx, ry, wchip, 15, col)
        cv.text(rx + 5, ry + 4, name, 1, CREAM)
        rx += wchip + 5

    # timeline
    tly = 208
    cv.text(m, tly, "TUESDAY 24 NOVEMBER - AS THE DAY UNFOLDED (TIMES AS REPORTED)", 1, DGREEN)
    tly += 12
    tw = (W - 2 * m - 5 * 6) // 6
    for i, (when, what) in enumerate(TIMELINE):
        tx = m + i * (tw + 6)
        cv.outline(tx, tly, tw, 38, GREY, 1)
        cv.text(tx + 5, tly + 4, when, 1, RED)
        draw_text_block(cv, tx + 5, tly + 15, what, 1, INK, (tw - 10) // 6, 8, 3)

    # lead cards
    ly = 266
    lw = (W - 2 * m - 2 * 8) // 3
    for i, item in enumerate(LEADS):
        card(cv, m + i * (lw + 8), ly, lw, 186, item, lead=True)

    # grid cards, two rows of five
    gy = 460
    gw = (W - 2 * m - 4 * 6) // 5
    for r in range(2):
        for cidx in range(5):
            item = GRID[r * 5 + cidx]
            card(cv, m + cidx * (gw + 6), gy + r * 156, gw, 148, item)

    # also-on + map
    ay = 772
    cv.text(m, ay, "ALSO ON - 21 MORE STORIES FROM THE DAY", 1, DGREEN)
    cv.text(640, ay, "WHERE IT HAPPENED - PINS MATCH STORY NUMBERS", 1, DGREEN)
    ay += 12
    half = 11
    colw = 305
    for col in range(2):
        yy = ay
        for item in BRIEF_SHORT[col * half:(col + 1) * half]:
            cv.text(m + col * (colw + 8), yy, item, 1, INK)
            yy += 10
    # dotted world map (stylised, original)
    mx, my, mw, mh = 640, ay, right - 640, 106
    cv.rect(mx, my, mw, mh, DBLUE)
    land = [(0.06, 0.18, 0.20, 0.16), (0.16, 0.52, 0.10, 0.22),
            (0.42, 0.14, 0.24, 0.18), (0.47, 0.40, 0.13, 0.24),
            (0.62, 0.20, 0.30, 0.22), (0.70, 0.52, 0.12, 0.16),
            (0.86, 0.72, 0.08, 0.10)]
    for (fx, fy, fw, fh) in land:
        gx = mx + int(fx * mw)
        gy2 = my + int(fy * mh)
        for dx in range(0, int(fw * mw), 7):
            for dy in range(0, int(fh * mh), 7):
                if (dx // 7 + dy // 7) % 3 != 2:
                    cv.rect(gx + dx, gy2 + dy, 3, 3, (120, 190, 220))
    for num, fx, fy in [(1, 300, 34), (3, 268, 24), (2, 258, 14), (5, 330, 40),
                        (6, 292, 44), (7, 304, 52), (4, 282, 34), (20, 36, 20),
                        (10, 22, 50), (14, 54, 38), (11, 336, 92)]:
        px = mx + fx
        py = my + fy
        cv.circle(px, py, 9, RED)
        ns = str(num)
        cv.text(px - cv.text_width(ns, 1) // 2, py - 3, ns, 1, CREAM)
    cv.text(mx + 6, my + mh - 11, "LEGEND: PIN NUMBER = CARD NUMBER ON THIS PAGE", 1, CREAM)

    # date check: two columns, one line per discarded item
    dy = 898
    cv.outline(m, dy, W - 2 * m, 62, RED, 2)
    cv.text(m + 8, dy + 5, "DATE CHECK - NOT TODAY'S NEWS: THESE HAPPENED EARLIER; THEY ARE NOT TODAY'S STORIES.", 1, RED)
    for col in range(2):
        yy = dy + 17
        for item in DATE_CHECK[col * 4:(col + 1) * 4]:
            cv.text(m + 8 + col * 492, yy, item, 1, INK)
            yy += 9
    cv.text(m + 8, dy + 52, "TONIGHT'S REAL COUNT: 7 SEA DRONES, AT THE TOP OF THIS PAGE.", 1, DGREEN)

    # footer
    fy = 970
    cv.rect(m, fy - 4, W - 2 * m, 1, INK)
    cv.text(m, fy, "SOURCES: REUTERS - AP - BBC - CNN - TIMES - WSJ - GUARDIAN - COINPAPRIKA - TREASURY - KCNA - JAGRANJOSH - OBSERVERVOICE - HK NEWS TV - GADGETS360 - SALONVISION.", 1, GREY)
    cv.text(m, fy + 14, "REPORTED = AS REPORTED BY THE NAMED SOURCE. PICTURES AND MAP: ORIGINAL DRAWINGS, DRAWN IN CODE.", 1, INK)
    cv.text(m, fy + 28, "ORIGINAL DRAWINGS - THE EXCHANGE FLOOR - TUESDAY 24 NOVEMBER 2026 - PAGE ONE OF ONE.", 1, DGREEN)

    grain_overlay(cv)
    return save_png(cv, path)


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    n = build(out)
    print("entry.png bytes:", n)
