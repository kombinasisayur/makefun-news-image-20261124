"""Entry point for THE EXCHANGE FLOOR (Akun 16, News Image 20261124).

Copy-only runner: executes the page composer written in compose.py,
which renders entry.png into this repository root. Standard library only.
"""
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    compose_path = os.path.join(HERE, "compose.py")
    runpy.run_path(compose_path, run_name="__main__")
    out = os.path.join(HERE, "entry.png")
    size = os.path.getsize(out)
    print("main: entry.png ready at", out, "-", size, "bytes")


if __name__ == "__main__":
    main()
