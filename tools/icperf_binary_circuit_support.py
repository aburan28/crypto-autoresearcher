"""Build exact XOR-AND circuits for the archived binary m=8 input equations.

This is a structural circuit encoding, not a solver or cost measurement. All
field multiplications use the same schoolbook polynomial-basis circuit. A
field square and multiplication by a constant are linear XOR networks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.icperf_ordinary_binary_fixture import FIELD_POLYNOMIAL  # noqa: E402
from tools.icperf_binary_boolean_support import N, fmul  # noqa: E402

SUPPORT = ROOT / "research/icperf_binary_boolean_support_20261017/support.json"
CONTROLS = ROOT / "research/icperf_binary_boolean_support_20261017/controls.json"


class Circuit:
    """Canonical binary-gate DAG with 0, 1, then primary inputs as node IDs."""

    def __init__(self, nvars: int):
        self.nodes: list[tuple[str, int, int]] = [("zero", 0, 0), ("one", 0, 0)]
        self.nodes += [("input", i, 0) for i in range(nvars)]
        self.nvars = nvars
        self.cache: dict[tuple[str, int, int], int] = {}
        self.reduced = [self._reduce_power(i) for i in range(2 * N - 1)]

    @staticmethod
    def _reduce_power(exponent: int) -> int:
        value = 1 << exponent
        while value.bit_length() > N:
            value ^= FIELD_POLYNOMIAL << (value.bit_length() - N - 1)
        return value

    def gate(self, op: str, a: int, b: int) -> int:
        if op == "xor":
            if a == 0:
                return b
            if b == 0:
                return a
            if a == b:
                return 0
        elif op == "and":
            if a == 0 or b == 0:
                return 0
            if a == 1:
                return b
            if b == 1 or a == b:
                return a
        else:
            raise ValueError(op)
        key = (op, min(a, b), max(a, b))
        if key not in self.cache:
            self.cache[key] = len(self.nodes)
            self.nodes.append(key)
        return self.cache[key]

    def xor_many(self, bits: list[int]) -> int:
        # Pairwise cancellation before building a deterministic reduction tree.
        parity: set[int] = set()
        for node in bits:
            if node in parity:
                parity.remove(node)
            elif node:
                parity.add(node)
        layer = sorted(parity)
        while len(layer) > 1:
            next_layer = [self.gate("xor", layer[i], layer[i + 1])
                          for i in range(0, len(layer) - 1, 2)]
            if len(layer) & 1:
                next_layer.append(layer[-1])
            layer = next_layer
        return layer[0] if layer else 0

    def constant(self, value: int) -> list[int]:
        return [1 if value & (1 << i) else 0 for i in range(N)]

    def variable(self, offset: int, width: int, first_bit: int) -> list[int]:
        bits = self.constant(offset)
        for i in range(width):
            bits[i] = self.gate("xor", bits[i], first_bit + i + 2)
        return bits

    def add(self, *elements: list[int]) -> list[int]:
        return [self.xor_many([item[i] for item in elements]) for i in range(N)]

    def linear_map(self, value: list[int], images: list[int]) -> list[int]:
        rows: list[list[int]] = [[] for _ in range(N)]
        for bit, image in zip(value, images):
            if bit == 0:
                continue
            for j in range(N):
                if image & (1 << j):
                    rows[j].append(bit)
        return [self.xor_many(row) for row in rows]

    def square(self, value: list[int]) -> list[int]:
        return self.linear_map(value, [self.reduced[2 * i] for i in range(N)])

    def multiply_constant(self, value: list[int], c: int) -> list[int]:
        return self.linear_map(value, [fmul(1 << i, c) for i in range(N)])

    def multiply(self, a: list[int], b: list[int]) -> list[int]:
        rows: list[list[int]] = [[] for _ in range(N)]
        for i, bit_a in enumerate(a):
            if bit_a == 0:
                continue
            for j, bit_b in enumerate(b):
                product = self.gate("and", bit_a, bit_b)
                if product == 0:
                    continue
                image = self.reduced[i + j]
                for k in range(N):
                    if image & (1 << k):
                        rows[k].append(product)
        return [self.xor_many(row) for row in rows]

    def phi3(self, a: list[int], b: list[int], c: list[int], gamma: int) -> list[int]:
        linearized = [self.add(self.square(v), v) for v in (a, b, c)]
        product = self.multiply(self.multiply(linearized[0], linearized[1]), linearized[2])
        return self.add(product, self.multiply_constant(self.square(self.add(a, b, c)), gamma))

    def raw3(self, a: list[int], b: list[int], c: list[int]) -> list[int]:
        # (ab+ac+bc) = (a+b)(b+c)+b^2 in characteristic two.
        e2 = self.add(self.multiply(self.add(a, b), self.add(b, c)), self.square(b))
        abc = self.multiply(self.multiply(a, b), c)
        return self.add(self.square(e2), abc, self.constant(31))

    def live_counts(self, outputs: list[int]) -> dict[str, int]:
        seen: set[int] = set()
        stack = list(outputs)
        counts = {"xor": 0, "and": 0, "input": 0}
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            op, a, b = self.nodes[node]
            if op in ("xor", "and"):
                counts[op] += 1
                stack.extend((a, b))
            elif op == "input":
                counts["input"] += 1
        counts["live_gate_total"] = counts["xor"] + counts["and"]
        return counts

    def evaluate(self, outputs: list[int], assignment: int) -> int:
        values = [0] * len(self.nodes)
        values[1] = 1
        for i in range(self.nvars):
            values[2 + i] = (assignment >> i) & 1
        for i in range(self.nvars + 2, len(self.nodes)):
            op, a, b = self.nodes[i]
            values[i] = values[a] ^ values[b] if op == "xor" else values[a] & values[b]
        return sum(values[node] << i for i, node in enumerate(outputs))


def make_arm(arm: dict, gamma: int) -> dict:
    kind = arm["kind"]
    width = arm["base_dimension"]
    offset = arm.get("selected_offset", arm.get("offset"))
    nvars = arm["boolean_variables"]
    circuit = Circuit(nvars)
    base = [circuit.variable(offset, width, i * width) for i in range(8)]
    full = [circuit.variable(0, N, 8 * width + i * N) for i in range(6)]
    triples = [[base[0], base[1], full[0]]]
    triples += [[full[i - 1], base[i + 1], full[i]] for i in range(1, 6)]
    triples += [[full[-1], base[-1], circuit.constant(arm["target_coordinate"])]]
    outputs = [circuit.phi3(*row, gamma) if kind == "torsion_phi" else
               circuit.raw3(*row) for row in triples]
    checks = []
    for trial in arm["trial_rows"]:
        assignment = int(trial["assignment_hex"], 16)
        actual = [circuit.evaluate(row, assignment) for row in outputs]
        assert actual == trial["field_equation_values"], (kind, actual, trial)
        checks.append({"assignment_hex": trial["assignment_hex"], "matched_all_seven": True})
    return {"kind": kind, "base_dimension": width, "offset": offset,
            "boolean_variables": nvars, "target_coordinate": arm["target_coordinate"],
            "per_equation_live": [circuit.live_counts(row) for row in outputs],
            "all_equations_live": circuit.live_counts([node for row in outputs for node in row]),
            "allocated_nodes_including_dead": len(circuit.nodes),
            "parent_trial_checks": checks}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    support_bytes, controls_bytes = SUPPORT.read_bytes(), CONTROLS.read_bytes()
    support, controls = json.loads(support_bytes), json.loads(controls_bytes)
    assert controls["parent_support_sha256"] == hashlib.sha256(support_bytes).hexdigest()
    # The chain binds the torsion-coordinate field constant to this fixture.
    chain_path = ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json"
    chain_bytes = chain_path.read_bytes()
    chain = json.loads(chain_bytes)
    assert support["chain_sha256"] == controls["chain_sha256"] == hashlib.sha256(chain_bytes).hexdigest()
    gamma = chain["gamma"]
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    arms = [make_arm(arm, gamma) for arm in support["arms"] + controls["arms"]]
    record = {"schema": "icperf-binary-circuit-support-v1",
              "scope": "exact schoolbook polynomial-basis XOR-AND input circuits; no solver, regularity, relation or speed claim",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "support_sha256": hashlib.sha256(support_bytes).hexdigest(),
              "controls_sha256": hashlib.sha256(controls_bytes).hexdigest(),
              "chain_sha256": hashlib.sha256(chain_bytes).hexdigest(),
              "field_polynomial": FIELD_POLYNOMIAL,
              "encoding": "canonical binary XOR and AND DAG; 0/1 nodes, then input bits; schoolbook GF(2^61) multiplication reduced modulo field polynomial; square and constant multiplication linear; live gates reachable from output bits",
              "raw_formula_optimization": "ab+ac+bc=(a+b)(b+c)+b^2; abc=(ab)c (3 field multiplications)",
              "torsion_formula": "prod_i(t_i^2+t_i)+gamma*(sum_i t_i)^2 (2 field multiplications)",
              "arms": arms,
              "preparation": {"wall_seconds": time.perf_counter() - start_wall,
                              "cpu_seconds": time.process_time() - start_cpu,
                              "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                                                (1 if sys.platform == "darwin" else 1024),
                              "loadavg_end": list(os.getloadavg()),
                              "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                         capture_output=True, text=True, check=True).stdout.strip(),
                              "git_status_porcelain": subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                                                      capture_output=True, text=True, check=True).stdout.splitlines(),
                              "python_version": sys.version}}
    with args.out.open("x") as stream:
        json.dump(record, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "gates": {a["kind"] + str(a["base_dimension"]):
                                                          a["all_equations_live"] for a in arms}}, sort_keys=True))


if __name__ == "__main__":
    main()
