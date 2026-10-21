"""Compile the vendored WDSat parser with ANF-derived bounds and parse only.

This is a bounded implementation check, not a WDSat solve or a scientific run.
It currently admits at most 64 unary variables and 1,000 nonlinear terms.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VENDORED = ROOT / "inputs/TRIMOSKA-WDSAT-2024/upstream/src"
PROBE = Path(__file__).with_name("wdsat_parser_probe.c")
GENERATOR = Path(__file__).resolve().parents[1] / "code/affine_weil_descent.py"


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def anf_bounds(path: Path):
    lines = path.read_text().splitlines()
    header = lines[0].split()
    if header[:2] != ["p", "cnf"] or len(header) != 4:
        raise ValueError("malformed ANF header")
    unary, equation_count = map(int, header[2:])
    if equation_count != len(lines) - 1:
        raise ValueError("ANF equation count disagrees with header")
    nonlinear = set()
    max_degree = 1
    for line in lines[1:]:
        tokens = line.split()
        if tokens[0] != "x" or tokens[-1] != "0":
            raise ValueError("malformed ANF equation")
        position = 1
        while position < len(tokens) - 1:
            token = tokens[position]
            if token == "T":
                position += 1
                continue
            if token.startswith("."):
                degree = int(token[1:])
                position += 1
                term = tuple(sorted(map(int, tokens[position:position + degree])))
                if len(term) != degree or min(term) < 1 or max(term) > unary:
                    raise ValueError("invalid nonlinear ANF term")
                nonlinear.add(term)
                max_degree = max(max_degree, degree)
                position += degree
            else:
                variable = int(token)
                if variable < 1 or variable > unary:
                    raise ValueError("invalid linear ANF term")
                position += 1
    if unary > 64 or len(nonlinear) > 1000:
        raise ValueError("parser probe exceeds its implementation-check bounds")
    return unary, equation_count, len(nonlinear), max_degree


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("anf", type=Path)
    parser.add_argument("--instance-manifest", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    unary, equations, nonlinear, degree = anf_bounds(args.anf)
    maximum_id = unary + nonlinear
    config = (
        "#define __XG_ENHANCED__\n"
        f"#define __MAX_ANF_ID__ {unary + 1}\n"
        f"#define __MAX_DEGREE__ {degree + 1}\n"
        f"#define __MAX_ID__ {maximum_id}\n"
        "#define __MAX_BUFFER_SIZE__ 60000\n"
        "#define __MAX_EQ__ 5000\n"
        f"#define __MAX_EQ_SIZE__ {degree + 2}\n"
        f"#define __MAX_XEQ__ {equations + 1}\n"
        f"#define __MAX_XEQ_SIZE__ {maximum_id + 1}\n"
    )
    source_files = ["wdsat_utils.c", "dimacs.c", "cnf.c", "xorset.c",
                    "xorgauss.c", "wdsat.c"]
    with tempfile.TemporaryDirectory(prefix="icperf-wdsat-parser-") as temp:
        directory = Path(temp)
        shutil.copytree(VENDORED, directory, dirs_exist_ok=True)
        (directory / "config.h").write_text(config)
        shutil.copy2(PROBE, directory / "wdsat_parser_probe.c")
        subprocess.run(["gcc", "-O2", "-w", "-I", ".", "wdsat_parser_probe.c",
                        *source_files, "-lm", "-o", "parser_probe"], cwd=directory,
                       check=True, capture_output=True, text=True, timeout=60)
        result = subprocess.run([str(directory / "parser_probe"),
                                 str(args.anf.resolve()), str(equations)], cwd=directory,
                                check=False, capture_output=True, text=True, timeout=10)
        if result.returncode:
            raise RuntimeError(f"parser probe failed with {result.returncode}: "
                               f"stdout={result.stdout!r} stderr={result.stderr!r}")
    receipt = {
        "kind": "parser_only_implementation_check",
        "result": "PASS",
        "anf_sha256": sha256(args.anf),
        "generator_sha256": sha256(GENERATOR),
        "vendored_dimacs_sha256": sha256(VENDORED / "dimacs.c"),
        "parser_checker_sha256": sha256(Path(__file__)),
        "parser_probe_sha256": sha256(PROBE),
        "unary_variables": unary,
        "nonlinear_monomials": nonlinear,
        "max_degree": degree,
        "max_id": maximum_id,
        "xor_equations": equations,
        "config": config,
        "parser_stdout": result.stdout.strip(),
        "solver_search_invoked": False,
    }
    if args.instance_manifest:
        receipt["instance_manifest"] = json.loads(args.instance_manifest.read_text())
    output = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.out:
        with args.out.open("x") as stream:
            stream.write(output)
    print(output, end="")


if __name__ == "__main__":
    main()
