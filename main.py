#!/usr/bin/env python3
# NI24 G2 — THE EXCHANGE FLOOR
"""THE EXCHANGE FLOOR - entry carrier for account 16 (NI24 wave 2).

Stdlib-only, copy-only: reads the embedded front-page image that sits
beside this file (entry.png, drawn locally by compose_exchange.py) and
writes its bytes, unchanged, to /output/entry.png. No network, no PIL.
Running it any number of times produces byte-identical output.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out = os.environ.get("MAKEFUN_OUTPUT", "/output/entry.png")
    outdir = os.path.dirname(out)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    with open(src, "rb") as fh:
        data = fh.read()
    with open(out, "wb") as fh:
        fh.write(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
