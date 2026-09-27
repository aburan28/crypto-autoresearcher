"""JSONL adapters for bounded alternatives to the standard Boolean GB flow."""

import contextlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from .certificate import terms
from .experiments import BooleanF4, elimlin, hybrid, xor_sat


def m5gb(equations, n):
    binary = os.environ.get("M5GB_BINARY")
    if not binary or not Path(binary).is_file():
        return {"status": "unavailable", "reason": "set M5GB_BINARY to the pinned upstream bridge binary"}
    rows = [row for row in equations if row]
    if not rows:
        return {"status": "unavailable", "reason": "upstream M5GB requires nonempty inputs"}
    input_data = "\n".join([f"{n} {len(rows)}", *(" ".join(map(str, [len(row), *row]))
                                                   for row in rows)]) + "\n"
    with subprocess.Popen([binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True) as process:
        process.stdin.write(input_data)
        process.stdin.close()
        output = None
        for line in process.stdout:
            if line.startswith("M5GB_RESULT "):
                output = line.split()[1:]
            else:
                print(line, end="", file=sys.stderr, flush=True)
        code = process.wait()
    if code or output is None:
        return {"status": "error", "reason": f"upstream M5GB exit {code}; no complete basis"}
    numbers = [int(x) for x in output]
    count = numbers[0]
    basis, offset = [], 1
    for _ in range(count):
        if offset >= len(numbers):
            raise ValueError("truncated upstream M5GB basis")
        length = numbers[offset]
        basis.append(numbers[offset + 1:offset + 1 + length])
        offset += length + 1
    if count < 0 or offset != len(numbers):
        raise ValueError("malformed upstream M5GB basis")
    return {"status": "ok", "basis_terms": basis,
            "solver_version": "upstream-m5gb-2d063f7+binary-sha256:"
            + hashlib.sha256(Path(binary).read_bytes()).hexdigest(), "metrics": {}}


def native_xor_sat(equations, n):
    import pycryptosat
    solver = pycryptosat.Solver(threads=1)
    symbols = {m: n + i + 1 for i, m in enumerate(sorted({
        m for row in equations for m in row if m.bit_count() > 1}))}
    for monomial, aux in symbols.items():
        factors = [i + 1 for i in range(n) if monomial & (1 << i)]
        for factor in factors:
            solver.add_clause([-aux, factor])
        solver.add_clause([aux] + [-factor for factor in factors])
    for row in equations:
        rhs = bool(0 in row)
        clause = [symbols.get(m, m.bit_length()) for m in row if m]
        if clause:
            solver.add_xor_clause(clause, rhs)
        elif rhs:
            return None, {"xor_sat_gates": len(symbols), "xor_sat_native": True,
                          "contradiction": True}
    sat, model = solver.solve()
    root = (sum((1 << i) for i in range(n) if model[i + 1]) if sat else None)
    return root, {"xor_sat_gates": len(symbols), "xor_sat_native": True}


def solve(name, request):
    if request["operation"] != "solve":
        return {"status": "incompatible", "reason": "no trace support"}
    n = request["ring"]["nvars"]
    instance = request["instance"]
    equations = terms(instance["equations"], n)
    blocks = instance.get("blocks")
    def progress(stats):
        print("GROEBNER_TELEMETRY " + json.dumps(stats, sort_keys=True),
              file=sys.stderr, flush=True)
    if name == "m5gb":
        return m5gb(equations, n)
    if name in ("xor-sat", "cryptominisat"):
        if name == "xor-sat":
            root, metrics = xor_sat(equations, n)
        else:
            root, metrics = native_xor_sat(equations, n)
        if root is None:
            return {"status": "unknown", "reason": "no witness returned; UNSAT unverified",
                    "metrics": metrics}
        return {"status": "ok", "solutions": [root], "metrics": metrics}
    if name in ("block-f4", "elimlin-f4"):
        supplementary, prep = (elimlin(equations, n, degree=min(6, n)) if name == "elimlin-f4"
                               else ([], {}))
        f4 = BooleanF4(n, blocks if name == "block-f4" else None, progress=progress)
        basis = f4.solve(equations + supplementary)
        return {"status": "ok", "basis_terms": basis,
                "basis_blocks": blocks if name == "block-f4" else None,
                "metrics": {**f4.stats, **prep}}
    if name in ("hybrid-f4", "hybrid-cryptominisat"):
        guess = instance.get("hybrid_guess", 2)
        root, branches = hybrid(equations, n, guess=guess, blocks=blocks,
                                branch_solver=(native_xor_sat if
                                               name == "hybrid-cryptominisat" else None),
                                progress=progress)
        metrics = {"branches_attempted": len(branches),
                   "branches_exhausted": sum(b["status"] == "exhausted" for b in branches),
                   "branches_without_witness": sum(b["status"] == "no_witness"
                                                   for b in branches)}
        if root is None:
            return {"status": "unknown", "reason": "no witness in searched branches",
                    "branches": branches, "metrics": metrics}
        return {"status": "ok", "solutions": [root], "branches": branches,
                "metrics": metrics}
    return {"status": "unavailable", "reason": f"unknown solver: {name}"}


def main():
    name = sys.argv[1]
    for line in sys.stdin:
        request = json.loads(line)
        try:
            with contextlib.redirect_stdout(sys.stderr):
                result = solve(name, request)
        except ImportError as error:
            result = {"status": "unavailable", "reason": str(error)}
        except (TimeoutError, ValueError) as error:
            result = {"status": "error", "reason": str(error)}
        result["request_id"] = request["request_id"]
        print(json.dumps(result, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
