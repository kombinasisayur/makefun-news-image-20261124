"""Entry point for THE EXCHANGE FLOOR (Akun 16, News Image 20261124).

Verified copy runner: renders the page via compose.build() into temporary
files, verifies each render (PNG signature, IHDR dimensions 1024x1024,
byte-identical output across two independent runs), and only then moves
the verified render into place as entry.png with an atomic rename.
Standard library only.
"""
import hashlib
import importlib.util
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_W = 1024
EXPECTED_H = 1024


def load_compose():
    path = os.path.join(HERE, "compose.py")
    spec = importlib.util.spec_from_file_location("exchange_floor_compose", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_png(path):
    """Check the PNG signature and the IHDR width/height; return (size, sha256)."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("render is not a PNG: bad signature in " + path)
    if data[12:16] != b"IHDR":
        raise ValueError("render has no IHDR chunk in " + path)
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECTED_W, EXPECTED_H):
        raise ValueError(
            "render dimensions %dx%d, expected %dx%d"
            % (width, height, EXPECTED_W, EXPECTED_H)
        )
    return len(data), hashlib.sha256(data).hexdigest()


def render_once(compose, tmp_path):
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    compose.build(tmp_path)
    return verify_png(tmp_path)


def main():
    compose = load_compose()
    out = os.path.join(HERE, "entry.png")
    tmp_a = os.path.join(HERE, ".entry-run-a.tmp.png")
    tmp_b = os.path.join(HERE, ".entry-run-b.tmp.png")
    try:
        size_a, digest_a = render_once(compose, tmp_a)
        size_b, digest_b = render_once(compose, tmp_b)
        if digest_a != digest_b or size_a != size_b:
            raise ValueError(
                "two renders differ: run A %d bytes %s, run B %d bytes %s"
                % (size_a, digest_a, size_b, digest_b)
            )
        os.replace(tmp_a, out)
        size, digest = verify_png(out)
        if digest != digest_a:
            raise ValueError("entry.png changed during atomic rename")
    finally:
        for tmp in (tmp_a, tmp_b):
            if os.path.exists(tmp):
                os.remove(tmp)
    print("main: entry.png verified at", out, "-", size, "bytes, sha256", digest)


if __name__ == "__main__":
    main()
