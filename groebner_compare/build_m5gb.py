"""Compile a local bridge against the pinned, separately obtained M5GB tree.

Usage: python -m groebner_compare.build_m5gb UPSTREAM_DIR OUTPUT_BINARY
Source: https://github.com/manschga/M5GB, commit below. No upstream code is
vendored or silently replaced by an F5 solver.
"""

import argparse
from pathlib import Path
import subprocess

COMMIT = "2d063f748e8a16ac5a1d74641c79725df29f67ac"
SOURCES = ("other_fct.cpp", "lab_poly.cpp", "M5GB.cpp", "poly.cpp",
           "signature.cpp")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    revision = subprocess.check_output(["git", "-C", str(args.source),
                                        "rev-parse", "HEAD"], text=True).strip()
    if revision != COMMIT:
        raise ValueError(f"expected pinned M5GB commit {COMMIT}; got {revision}")
    dirty = subprocess.check_output(["git", "-C", str(args.source), "status",
                                     "--porcelain", "--untracked-files=no"], text=True).strip()
    if dirty:
        raise ValueError("upstream M5GB tree must be clean to retain pinned provenance")
    # Checked std::vector indexing turns exhausted upstream term tables into
    # an explicit bounded-trial failure instead of undefined memory access.
    subprocess.run(["g++", "-std=c++17", "-O2", "-D_GLIBCXX_ASSERTIONS",
                    "-I", str(args.source),
                    str(Path(__file__).with_name("m5gb_bridge.cpp")),
                    *(str(args.source / file) for file in SOURCES),
                    "-o", str(args.output)], check=True)
    print(f"M5GB {revision} binary: {args.output}")


if __name__ == "__main__":
    main()
