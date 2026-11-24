[![Bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![Rank](https://make.fun/badge/news-image-20261124/kombinasisayur/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![Reward](https://make.fun/badge/news-image-20261124/kombinasisayur/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

# THE PORTSIDE GAZETTE — Tuesday 24 November 2026 in one image

Bounty: [news-image-20261124 on make.fun](https://make.fun/bounty/news-image-20261124)

One front page that sums up the world's news of Tuesday 24 November 2026:
36 stories across 7 regions — 15 cards + 21 briefs — drawn entirely in code.

## The edition

- **Lead:** GTA VI takes $3.8bn on day one — the biggest entertainment launch
  on record. Bitcoin steadies near $61,284; gold rebounds 1.5% to $3,588.
- **Markets:** Nvidia brings back Jensen Huang as CEO; shares +31%.
- **War & diplomacy:** Ukraine sinks the Russian corvette Merkury off Libya
  (7 sea drones); Sparta II towed clear; 15 killed near Kyiv; COP31 ends
  with no deal — the first since 2000; US sanctions ~30 Iran-linked
  exchange houses.
- **Also inside:** Wellington Test drawn, Liverpool 4–0 Man Utd, Democrats
  take both chambers 258–173, plus a dotted world map with numbered pins,
  a Tuesday timeline, and a DATE CHECK box naming what is *not* today's news.

Every card carries its certainty tag (REPORTED) and its source; every number
comes from the locked NI24 pool (Reuters / AP / CNN / Times / WSJ / BBC /
Guardian / CoinPaprika and others, as credited on the page).

## How it is built

- `compose.py` — fresh compose engine written for this entry: draws the
  whole front page at 3900 px (Playfair Black masthead, flat layered
  scenes, dotted world map from simplified real coastlines), then scales
  it to 1024×1024 and quantises to 256 colours.
- `main.py` — stdlib-only program: verifies the PNG gate (exactly
  1024×1024, at most 1 MiB) and copies `entry.png` to the output directory.
- `entry.png` — the finished page: 1024×1024, 239,258 bytes.
- `fonts/` — Playfair Display (variable font, OFL) for the masthead and
  headlines; body text uses system DejaVu Sans.

## Entry

- Competition: `news-image-20261124`
- Entrant: [@kombinasisayur0566](https://make.fun/) (GitHub: kombinasisayur)
- License: MIT
