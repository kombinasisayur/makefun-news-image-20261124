#!/usr/bin/env python3
"""THE PORTSIDE GAZETTE — NI24 entry program (account 16).

Stdlib-only copy carrier: copies the finished front page (entry.png,
drawn in this session by compose.py) to the grader's output directory.
No network, no third-party code, deterministic: the same bytes every run.
"""
import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")

MAX_BYTES = 1048576


def verify_png(path):
    """Gate: the entry must be exactly 1024x1024 and at most 1 MiB.

    Reads the PNG IHDR by hand (no image library): signature + width +
    height + chunk CRC presence. Anything else refuses to copy, so a bad
    build can never be submitted by accident.
    """
    with open(path, "rb") as f:
        head = f.read(33)
    if len(head) < 33 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG file")
    if head[12:16] != b"IHDR":
        raise SystemExit("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", head[16:24])
    if (width, height) != (1024, 1024):
        raise SystemExit(f"entry.png is {width}x{height}, must be 1024x1024")
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise SystemExit(f"entry.png is {size} bytes, over the 1 MiB gate")
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print(f"gate ok: 1024x1024, {size} bytes, sha256 {digest}")
    return digest


def main():
    digest = verify_png(SRC)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    back = hashlib.sha256(open(dst, "rb").read()).hexdigest()
    if back != digest:
        raise SystemExit("output bytes differ from entry.png")
    print(f"copied {SRC} -> {dst} ({os.path.getsize(dst)} bytes, verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
