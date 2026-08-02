#!/usr/bin/env python3
"""mutation_control_v2.py -- repaired mutation control for GOAL-AES-001.

Task:    TASK-20260731-702 (executor, GOAL-AES-001 BATCH-002)
Scope:   INSTRUMENT ONLY. This file makes NO cryptanalytic claim of any kind.
         A repaired control is a reproducibility fact about an instrument,
         never a result about AES.

=============================================================================
WHAT THIS SUPERSEDES
=============================================================================
This module supersedes -- it does NOT modify -- the mutation-control section
(`check_detection_power`) of the verification driver archived verbatim inside

    coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/
        TASK-20260731-602/run_record.md      (driver sha256 675ff4d5...4a6d)

and the `detection_power_mutation_control` section of

    coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/
        TASK-20260731-602/vector_check_receipt.json

Every BATCH-001 artifact is read strictly read-only. `aes_reduced.py` is read
from its committed BATCH-001 path, hashed, and mutated only into copies under a
scratch directory. Nothing in BATCH-001 is written, re-run into, or deleted.
The BATCH-001 archived green stands as recorded.

=============================================================================
DEFECTS ADDRESSED
=============================================================================
H-1 (repaired here).  The BATCH-001 scoring credited an import-time
    `AssertionError` as `rejected_by_module_self_check` / `detected: True`.
    The independent validator (TASK-20260731-604 sec. 4.3) showed the earlier
    narrowing was genuine but incomplete: an import-time `AssertionError`
    UNRELATED to the injected fault still produced `verdict=pass` with all
    mutants credited as detected, without any comparison having run.

    REPAIR (the "preferred and simpler to defend" option in the handoff):
    the self-check detection path is REMOVED ENTIRELY. `detected: true` is
    now emitted on one basis only -- POSITIVE EVIDENCE that ciphertext
    comparisons actually executed and at least one diverged:

        detected := (comparisons_executed > 0) and (divergences > 0)

    `comparisons_executed` counts (mutant ciphertext, reference ciphertext)
    pairs that were both physically produced and compared. No exception, of
    any class, at any point, can increment it. Any import-time or run-time
    failure of the mutant is an INFRASTRUCTURE OUTCOME: status names the
    exception class, `detected: false`, `detection_mechanism: null`, and the
    overall verdict is FAIL (AGENTS.md rule 5 -- a control that could not run
    its comparison produced no evidence about detection power).

H-3 (repaired here).  BATCH-001 had zero mutants on the reduced-round path.
    This control adds five round-structure mutants (`_is_final_round`,
    `encrypt_partial` level bounds, round-key indexing at r < Nr, initial
    AddRoundKey miscount) and scores every mutant SEPARATELY at r < Nr and at
    r = Nr, so a detection that happens only at full rounds is visible as
    such and does not close H-3.

H-2 (NOT repaired, recorded).  `aes_reduced.py`'s import-time consistency
    check is an `assert`, which `python3 -O` strips. This control does not
    repair that. Because the self-check detection path is removed, H-2 can no
    longer produce a false green *here*, but the underlying module-level
    weakness stands. H-2 IS NOT CLOSED.

H-4 (declared limitation, NOT removed).  See COMPARISON TARGETS below.

=============================================================================
COMPARISON TARGETS -- what each verdict does and does not establish
=============================================================================
Two, named explicitly, used for disjoint task sets:

  TARGET-EXT  pycryptodome 3.23.0, used for r = Nr tasks only.
      An implementation authored outside this program. Divergence at r = Nr
      is measured against an EXTERNAL reference.

  TARGET-REF  `RefAES`, defined below in this file: a second, independently
      authored implementation of the documented C1/C2/C3 reduced-round
      convention. It is deliberately structurally different from
      `aes_reduced.py` (S-box via log/antilog tables rather than by
      exponentiation `GF.inv`; MixColumns via `xtime` per row rather than a
      matrix product; Rcon as a literal table rather than a computed power;
      state carried as a list rather than `bytes`). It is anchored to
      TARGET-EXT at r = Nr for all three key sizes before use.

  WHAT TARGET-REF ESTABLISHES: that a mutated round-structure produces
      ciphertexts differing from those of a second, structurally different
      implementation of the SAME WRITTEN CONVENTION. That is a statement
      about the SENSITIVITY of this control and about prose-to-code agreement
      between two implementations.

  WHAT TARGET-REF DOES NOT ESTABLISH: that the C1/C2/C3 convention is the
      convention used anywhere else. RefAES was authored in this task from
      the same prose, by the same agent, in the same session. It is NOT an
      external reference and cannot become one. H-4 -- the reduced-round path
      has no external reference and cannot obtain one in this environment --
      STANDS UNCHANGED AND IS NOT CLAIMED REMOVED. A green reduced-round
      detection here means "the control fires when the round structure is
      perturbed", not "the round structure is correct".

  Note: the unmutated `aes_reduced.py` is NEVER used as a comparison target.

=============================================================================
ISOLATION (and why it matters -- escape routes 3 and 4)
=============================================================================
BATCH-001 imported each mutant INTO THE SCORING PROCESS. That gives the
mutated source arbitrary import-time side effects on the very process that
scores it. Two consequences are demonstrated by probes C and D below:

  * a mutant can monkeypatch the driver's own reference oracle at import
    time, so that a SEMANTICS-PRESERVING module is scored `detected: true`
    (a manufactured detection: escape route 3);
  * a mutant can raise `SystemExit`, which is a `BaseException` and is not
    caught by `except Exception`, so it escapes the scoring loop entirely
    (escape route 4).

Here every mutant runs in a SEPARATE `python3` subprocess that emits only
ciphertext hex strings. Reference ciphertexts are computed in the parent
BEFORE any mutant runs. A mutant therefore cannot touch the reference, the
counters, or the verdict. Its residual power is to hide its own fault (a
false NEGATIVE, reported as an undetected mutant), never to manufacture a
detection.

=============================================================================
DETERMINISM
=============================================================================
All randomness comes from the seeds in `SEEDS` below, via `random.Random`.
`--out` receipts contain volatile fields (timestamps, wall clock); the
`results_digest` is computed over the deterministic scored content only and
is byte-identical across re-runs. Use `--prior-digest` to assert that.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import random
import subprocess
import sys
import tempfile
import time
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Fixed configuration
# ---------------------------------------------------------------------------

TASK_ID = "TASK-20260731-702"
CONTROL_VERSION = "mutation_control_v2 / 1.0"

DEFAULT_MODULE_PATH = os.path.join(
    "coordination", "goals", "GOAL-AES-001", "batches", "BATCH-001",
    "tasks", "TASK-20260731-602", "aes_reduced.py",
)

SEEDS = {
    "full_round_tasks": 7020260731,
    "reduced_round_tasks": 7020260732,
    "legacy_replica_pairs": 7020260733,
}

# Task-set sizes (kept small: every comparison is an exact byte comparison,
# so detection power does not need large samples; the counts are recorded).
N_FULL_PER_KEYSIZE = 12
N_REDUCED_PER_CASE = 8
REDUCED_ROUND_COUNTS = {16: (1, 2, 3, 4, 5), 24: (1, 2, 3), 32: (1, 2, 3)}
FULL_ROUNDS = {16: 10, 24: 12, 32: 14}


# ---------------------------------------------------------------------------
# TARGET-REF: independently authored implementation of C1/C2/C3
# ---------------------------------------------------------------------------

def _build_ref_tables() -> Tuple[List[int], List[int], List[int]]:
    """S-box via log/antilog tables over GF(2^8), generator 3.

    Deliberately a different construction from aes_reduced.py, which computes
    inverses by exponentiation inside GF.inv.
    """
    alog = [0] * 512
    log = [0] * 256
    x = 1
    for i in range(255):
        alog[i] = x
        log[x] = i
        # multiply by 3 = x + 1
        x = x ^ ((x << 1) ^ (0x11B if x & 0x80 else 0)) & 0xFF
        x &= 0xFF
    for i in range(255, 512):
        alog[i] = alog[i - 255]

    def inv(a: int) -> int:
        return 0 if a == 0 else alog[255 - log[a]]

    def rotl8(v: int, n: int) -> int:
        return ((v << n) | (v >> (8 - n))) & 0xFF

    sbox = []
    for a in range(256):
        b = inv(a)
        sbox.append(b ^ rotl8(b, 1) ^ rotl8(b, 2) ^ rotl8(b, 3) ^ rotl8(b, 4) ^ 0x63)
    return sbox, log, alog


_REF_SBOX, _REF_LOG, _REF_ALOG = _build_ref_tables()

# Literal Rcon table (aes_reduced.py computes it as a power of x).
_REF_RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80,
             0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A, 0x2F, 0x5E, 0xBC, 0x63]


def _xtime(a: int) -> int:
    a <<= 1
    if a & 0x100:
        a ^= 0x11B
    return a & 0xFF


class RefAES:
    """Second implementation of the documented C1/C2/C3 convention.

    C1: round `rounds` is the final round and omits MixColumns unless
        final_mix_columns is True.
    C2: the initial AddRoundKey is whitening and is not counted as a round.
    C3: round keys are the first rounds+1 keys of the untruncated FIPS-197
        schedule for the key length; nothing renumbered.
    """

    def __init__(self, key: bytes, rounds: Optional[int] = None,
                 final_mix_columns: bool = False) -> None:
        self.key = bytes(key)
        nk = len(self.key) // 4
        if nk not in (4, 6, 8):
            raise ValueError("bad key length")
        self.nk = nk
        self.full_rounds = FULL_ROUNDS[len(self.key)]
        self.rounds = self.full_rounds if rounds is None else int(rounds)
        self.final_mix_columns = bool(final_mix_columns)
        self.rk = self._expand(self.rounds + 1)

    def _expand(self, n_round_keys: int) -> List[List[int]]:
        nk = self.nk
        w = [list(self.key[4 * i:4 * i + 4]) for i in range(nk)]
        for i in range(nk, 4 * n_round_keys):
            t = list(w[i - 1])
            if i % nk == 0:
                t = t[1:] + t[:1]
                t = [_REF_SBOX[b] for b in t]
                t[0] ^= _REF_RCON[i // nk]
            elif nk == 8 and i % nk == 4:
                t = [_REF_SBOX[b] for b in t]
            w.append([a ^ b for a, b in zip(w[i - nk], t)])
        return [[b for word in w[4 * r:4 * r + 4] for b in word]
                for r in range(n_round_keys)]

    @staticmethod
    def _shift_rows(s: List[int]) -> List[int]:
        out = [0] * 16
        for r in range(4):
            for c in range(4):
                out[c * 4 + r] = s[((c + r) % 4) * 4 + r]
        return out

    @staticmethod
    def _mix_columns(s: List[int]) -> List[int]:
        # per-row xtime form, not a matrix product
        out = [0] * 16
        for c in range(4):
            a0, a1, a2, a3 = s[4 * c:4 * c + 4]
            t = a0 ^ a1 ^ a2 ^ a3
            out[4 * c + 0] = a0 ^ t ^ _xtime(a0 ^ a1)
            out[4 * c + 1] = a1 ^ t ^ _xtime(a1 ^ a2)
            out[4 * c + 2] = a2 ^ t ^ _xtime(a2 ^ a3)
            out[4 * c + 3] = a3 ^ t ^ _xtime(a3 ^ a0)
        return out

    def encrypt_block(self, pt: bytes) -> bytes:
        s = [a ^ b for a, b in zip(pt, self.rk[0])]          # C2 whitening
        for i in range(1, self.rounds + 1):
            s = [_REF_SBOX[b] for b in s]
            s = self._shift_rows(s)
            is_final = (i == self.rounds) and not self.final_mix_columns
            if not is_final:                                  # C1
                s = self._mix_columns(s)
            s = [a ^ b for a, b in zip(s, self.rk[i])]        # C3
        return bytes(s)


def pycrypto_encrypt(key: bytes, pt: bytes) -> bytes:
    from Crypto.Cipher import AES as PyAES
    return PyAES.new(key, PyAES.MODE_ECB).encrypt(pt)


# ---------------------------------------------------------------------------
# Mutant catalogue
# ---------------------------------------------------------------------------
# Every entry lists textual edits (old -> new) applied to the committed
# aes_reduced.py source. An edit whose `old` text is absent, or whose
# application leaves the source unchanged, makes the mutant NOT_APPLIED and
# UNSCORED -- never silently skipped.

MUTANTS: List[Dict] = [
    # ---- component class (BATCH-001 continuity, scored at r = Nr) ---------
    {
        "name": "sbox_transpose_0x53_0x54",
        "class": "component",
        "reduced_round_structure": False,
        "description": "two S-box entries transposed",
        "expected_detected": True,
        "edits": [(
            "    sbox = tuple(_affine(GF.inv(x)) for x in range(256))",
            "    sbox = list(_affine(GF.inv(x)) for x in range(256))\n"
            "    sbox[0x53], sbox[0x54] = sbox[0x54], sbox[0x53]\n"
            "    sbox = tuple(sbox)",
        )],
    },
    {
        "name": "shiftrows_offsets_swapped",
        "class": "component",
        "reduced_round_structure": False,
        "description": "ShiftRows offsets (0,1,2,3) -> (0,1,3,2)",
        "expected_detected": True,
        "edits": [(
            "    shift_offsets: Tuple[int, int, int, int] = (0, 1, 2, 3)",
            "    shift_offsets: Tuple[int, int, int, int] = (0, 1, 3, 2)",
        )],
    },
    {
        "name": "rcon_off_by_one",
        "class": "component",
        "reduced_round_structure": False,
        "description": "Rcon exponent off by one in the key schedule",
        "expected_detected": True,
        "edits": [(
            "    for _ in range(i - 1):\n        v = GF.mul(v, 0x02)",
            "    for _ in range(i):\n        v = GF.mul(v, 0x02)",
        )],
    },

    # ---- H-3: reduced-round round-structure class ------------------------
    {
        "name": "RR1_final_round_mixcolumns_retained",
        "class": "reduced_round_structure",
        "reduced_round_structure": True,
        "target_logic": "AES._is_final_round",
        "description": "_is_final_round always False: MixColumns incorrectly "
                       "RETAINED in the final round at every round count",
        "expected_detected": True,
        "edits": [(
            "        return i == self.rounds and not self.final_mix_columns",
            "        return False",
        )],
    },
    {
        "name": "RR2_is_final_round_off_by_one",
        "class": "reduced_round_structure",
        "reduced_round_structure": True,
        "target_logic": "AES._is_final_round",
        "description": "off-by-one in round indexing: round rounds-1 is treated "
                       "as the final round instead of round rounds",
        "expected_detected": True,
        "edits": [(
            "        return i == self.rounds and not self.final_mix_columns",
            "        return i == self.rounds - 1 and not self.final_mix_columns",
        )],
    },
    {
        "name": "RR3_encrypt_partial_upper_bound_off_by_one",
        "class": "reduced_round_structure",
        "reduced_round_structure": True,
        "target_logic": "AES.encrypt_partial level bounds",
        "description": "encrypt_partial level range upper bound off by one: the "
                       "last requested round is silently not applied",
        "expected_detected": True,
        "edits": [(
            "        for i in range(start_level + 1, end_level + 1):",
            "        for i in range(start_level + 1, end_level):",
        )],
    },
    {
        "name": "RR4_final_roundkey_from_untruncated_schedule",
        "class": "reduced_round_structure",
        "reduced_round_structure": True,
        "target_logic": "round-key indexing at r < Nr (convention C3)",
        "description": "the final round uses RK[Nr] of the untruncated schedule "
                       "instead of RK[r]. BY CONSTRUCTION INVISIBLE AT r = Nr "
                       "(where RK[Nr] is the correct key) and visible only at "
                       "r < Nr -- exactly the bug class H-3 says BATCH-001 "
                       "could not see.",
        "expected_detected": True,
        "edits": [
            (
                "        self.round_keys = key_expansion(key, self.rounds + 1, components.key_sbox)",
                "        self.round_keys = key_expansion(key, max(self.rounds, self.full_rounds) + 1, components.key_sbox)",
            ),
            (
                "        return add_round_key(s, self.round_keys[i])",
                "        return add_round_key(s, self.round_keys[i] if i < self.rounds "
                "else self.round_keys[self.full_rounds])",
            ),
        ],
    },
    {
        "name": "RR5_initial_addroundkey_miscounted",
        "class": "reduced_round_structure",
        "reduced_round_structure": True,
        "target_logic": "AES.whiten (convention C2)",
        "description": "initial AddRoundKey miscounted: whitening applies RK[1] "
                       "instead of RK[0], i.e. the whitening key is taken from "
                       "the round sequence",
        "expected_detected": True,
        "edits": [(
            "        return add_round_key(bytes(plaintext), self.round_keys[0])",
            "        return add_round_key(bytes(plaintext), self.round_keys[1])",
        )],
    },

    # ---- control of the control: semantics-preserving no-op --------------
    {
        "name": "NOOP_is_final_round_rewritten",
        "class": "noop_control",
        "reduced_round_structure": True,
        "target_logic": "AES._is_final_round (source text changed, function unchanged)",
        "description": "semantics-preserving rewrite of _is_final_round on the "
                       "reduced-round path: same boolean function, different "
                       "source text. MUST be scored detected: false.",
        "expected_detected": False,
        "edits": [(
            "        return i == self.rounds and not self.final_mix_columns",
            "        is_last = (i == self.rounds)\n"
            "        keeps_mix_in_last = self.final_mix_columns\n"
            "        return is_last and (not keeps_mix_in_last)",
        )],
    },
]

# ---------------------------------------------------------------------------
# Injected-failure-shape probes (H-1 proof obligation + escape-route search)
# ---------------------------------------------------------------------------
# Each probe takes a BASE source (the unmutated module, or a known-faulty
# mutant) and prepends an import-time injection immediately before `__all__`.

INJECT_ANCHOR = "__all__ = ["

PROBES: List[Dict] = [
    {
        "name": "probeA_import_time_unrelated_AssertionError",
        "shape": "import-time AssertionError UNRELATED to the injected fault "
                 "(the exact H-1 shape from TASK-20260731-604 sec. 4.3)",
        "base": "sbox_transpose_0x53_0x54",
        "expected_exception": "AssertionError",
        "expected_detected": False,
        "expected_standalone_verdict": "FAIL",
        "injection": (
            "# --- probe A injection: import-time AssertionError unrelated to the fault ---\n"
            "assert False, 'unrelated import-time assertion injected by probeA'\n"
        ),
    },
    {
        "name": "probeB_import_time_AttributeError",
        "shape": "import-time non-AssertionError: the original false-green shape "
                 "AttributeError: 'NoneType' object has no attribute '__dict__'",
        "base": "sbox_transpose_0x53_0x54",
        "expected_exception": "AttributeError",
        "expected_detected": False,
        "expected_standalone_verdict": "FAIL",
        "injection": (
            "# --- probe B injection: import-time AttributeError ---\n"
            "_probe_b_trigger = None.__dict__\n"
        ),
    },
    {
        "name": "probeC_import_time_oracle_tamper",
        "shape": "ESCAPE ROUTE 3 (found by this task): a SEMANTICS-PRESERVING "
                 "module that monkeypatches the scoring process's reference "
                 "oracle at import time. Under in-process scoring this "
                 "manufactures a detection on a module whose cipher is "
                 "byte-identical to the original.",
        "base": None,                      # unmutated source: cipher unchanged
        "expected_exception": None,
        "expected_detected": False,
        "expected_standalone_verdict": "no_detection_credited",
        "injection": (
            "# --- probe C injection: import-time tamper with the reference oracle ---\n"
            "try:\n"
            "    from Crypto.Cipher import AES as _tamper_mod\n"
            "    def _tamper_new(*a, **k):\n"
            "        class _Fake:\n"
            "            def encrypt(self, d):\n"
            "                return bytes(len(d))\n"
            "            def decrypt(self, d):\n"
            "                return bytes(len(d))\n"
            "        return _Fake()\n"
            "    _tamper_mod.new = _tamper_new\n"
            "except Exception:\n"
            "    pass\n"
        ),
    },
    {
        "name": "probeD_import_time_SystemExit",
        "shape": "ESCAPE ROUTE 4 (found by this task): SystemExit at import "
                 "time. SystemExit is a BaseException, so `except Exception` "
                 "does not catch it and it escapes an in-process scoring loop "
                 "entirely.",
        "base": "sbox_transpose_0x53_0x54",
        "expected_exception": "SystemExit",
        "expected_detected": False,
        "expected_standalone_verdict": "FAIL",
        "injection": (
            "# --- probe D injection: import-time SystemExit ---\n"
            "raise SystemExit(3)\n"
        ),
    },
]


# ---------------------------------------------------------------------------
# Task sets
# ---------------------------------------------------------------------------

def build_tasks() -> Tuple[List[Dict], List[Dict]]:
    """(full_round_tasks, reduced_round_tasks). Deterministic from SEEDS."""
    rng = random.Random(SEEDS["full_round_tasks"])
    full: List[Dict] = []
    for klen in (16, 24, 32):
        for _ in range(N_FULL_PER_KEYSIZE):
            full.append({
                "key_hex": bytes(rng.randrange(256) for _ in range(klen)).hex(),
                "pt_hex": bytes(rng.randrange(256) for _ in range(16)).hex(),
                "rounds": None,
                "final_mix_columns": False,
                "regime": "full_round",
                "target": "TARGET-EXT(pycryptodome-3.23.0)",
            })

    rng = random.Random(SEEDS["reduced_round_tasks"])
    reduced: List[Dict] = []
    for klen in (16, 24, 32):
        for r in REDUCED_ROUND_COUNTS[klen]:
            for fmc in (False, True) if klen == 16 else (False,):
                for _ in range(N_REDUCED_PER_CASE):
                    reduced.append({
                        "key_hex": bytes(rng.randrange(256) for _ in range(klen)).hex(),
                        "pt_hex": bytes(rng.randrange(256) for _ in range(16)).hex(),
                        "rounds": r,
                        "final_mix_columns": fmc,
                        "regime": "reduced_round",
                        "target": "TARGET-REF(RefAES, this file)",
                    })
    return full, reduced


def reference_ciphertexts(tasks: List[Dict]) -> List[str]:
    """Computed in the PARENT, before any mutant runs."""
    out = []
    for t in tasks:
        key = bytes.fromhex(t["key_hex"])
        pt = bytes.fromhex(t["pt_hex"])
        if t["regime"] == "full_round":
            out.append(pycrypto_encrypt(key, pt).hex())
        else:
            out.append(RefAES(key, t["rounds"], t["final_mix_columns"])
                       .encrypt_block(pt).hex())
    return out


# ---------------------------------------------------------------------------
# The isolated mutant runner
# ---------------------------------------------------------------------------

RUNNER_SRC = r'''
import importlib.util, json, sys

def main():
    mod_path, tasks_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(tasks_path) as fh:
        tasks = json.load(fh)
    try:
        spec = importlib.util.spec_from_file_location("mutant_under_test", mod_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["mutant_under_test"] = mod
        spec.loader.exec_module(mod)
    except BaseException as exc:
        with open(out_path, "w") as fh:
            json.dump({"ok": False, "phase": "import",
                       "error_type": type(exc).__name__,
                       "error": str(exc)}, fh)
        return 0
    cts = []
    for t in tasks:
        key = bytes.fromhex(t["key_hex"]); pt = bytes.fromhex(t["pt_hex"])
        try:
            c = mod.AES(key, t["rounds"], t["final_mix_columns"]).encrypt_block(pt)
            cts.append(c.hex())
        except BaseException as exc:
            with open(out_path, "w") as fh:
                json.dump({"ok": False, "phase": "encrypt",
                           "error_type": type(exc).__name__,
                           "error": str(exc)}, fh)
            return 0
    with open(out_path, "w") as fh:
        json.dump({"ok": True, "ct": cts}, fh)
    return 0

sys.exit(main())
'''


def run_isolated(runner_path: str, module_path: str, tasks: List[Dict],
                 workdir: str, tag: str, commands: List[Dict]) -> Dict:
    tasks_path = os.path.join(workdir, f"tasks_{tag}.json")
    out_path = os.path.join(workdir, f"out_{tag}.json")
    with open(tasks_path, "w") as fh:
        json.dump(tasks, fh)
    cmd = [sys.executable, runner_path, module_path, tasks_path, out_path]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    elapsed = time.time() - t0
    commands.append({
        "command": " ".join(cmd),
        "exit_status": proc.returncode,
        "wall_clock_seconds": round(elapsed, 3),
        "stderr_tail": proc.stderr.strip()[-400:],
    })
    if proc.returncode != 0 or not os.path.exists(out_path):
        return {"ok": False, "phase": "subprocess",
                "error_type": "SubprocessFailure",
                "error": f"exit={proc.returncode} stderr={proc.stderr.strip()[-300:]}"}
    with open(out_path) as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Scoring -- the H-1 repair lives here
# ---------------------------------------------------------------------------

def score(result: Dict, tasks: List[Dict], refs: List[str]) -> Dict:
    """Score one isolated mutant run.

    THE ONLY PATH TO `detected: true`: comparisons_executed > 0 AND
    divergences > 0. There is no exception-based detection path of any kind.
    """
    if not result.get("ok"):
        etype = result.get("error_type", "Unknown")
        return {
            "status": f"mutant_{result.get('phase', 'run')}_error:{etype}",
            "detected": False,
            "detection_mechanism": None,
            "comparisons_executed": 0,
            "divergences": 0,
            "per_regime": {},
            "infrastructure_outcome": True,
            "error_type": etype,
            "error_detail": str(result.get("error"))[:400],
            "note": "No comparison executed. Under AGENTS.md rule 5 this run "
                    "produced NO evidence about detection power. It is an "
                    "infrastructure outcome, never a detection.",
        }

    cts = result["ct"]
    if len(cts) != len(tasks):
        return {
            "status": "mutant_output_arity_mismatch",
            "detected": False,
            "detection_mechanism": None,
            "comparisons_executed": 0,
            "divergences": 0,
            "per_regime": {},
            "infrastructure_outcome": True,
            "note": f"expected {len(tasks)} ciphertexts, got {len(cts)}",
        }

    per_regime: Dict[str, Dict] = {}
    total_cmp = total_div = 0
    for t, ref, got in zip(tasks, refs, cts):
        if t["regime"] == "full_round":
            bucket = "r_eq_Nr"
            rk = "full"
        else:
            bucket = "r_lt_Nr"
            rk = str(t["rounds"])
        d = per_regime.setdefault(bucket, {
            "comparison_target": t["target"],
            "comparisons_executed": 0,
            "divergences": 0,
            "round_counts_compared": [],
            "divergences_by_round_count": {},
        })
        if rk not in d["round_counts_compared"]:
            d["round_counts_compared"].append(rk)
        d["comparisons_executed"] += 1
        total_cmp += 1
        if got != ref:
            d["divergences"] += 1
            total_div += 1
            d["divergences_by_round_count"][rk] = \
                d["divergences_by_round_count"].get(rk, 0) + 1

    detected = (total_cmp > 0) and (total_div > 0)
    detected_at_reduced = per_regime.get("r_lt_Nr", {}).get("divergences", 0) > 0
    detected_at_full = per_regime.get("r_eq_Nr", {}).get("divergences", 0) > 0
    return {
        "status": "compared" if detected else "compared_no_divergence",
        "detected": detected,
        "detection_mechanism": (
            "differential ciphertext comparison (mutant subprocess output vs "
            "reference computed in the parent before any mutant ran)"
            if detected else None
        ),
        "comparisons_executed": total_cmp,
        "divergences": total_div,
        "detected_at_r_lt_Nr": detected_at_reduced,
        "detected_at_r_eq_Nr": detected_at_full,
        "invisible_at_full_rounds": (detected_at_reduced and not detected_at_full),
        "per_regime": per_regime,
        "infrastructure_outcome": False,
    }


# ---------------------------------------------------------------------------
# Legacy in-process scoring replica (used ONLY to exhibit escape routes)
# ---------------------------------------------------------------------------

def legacy_inprocess_replica(mutant_path: str, name: str) -> Dict:
    """Faithful replica of the BATCH-001 `check_detection_power` scoring core.

    Reproduced here, in this file, ONLY so that escape routes 3 and 4 can be
    exhibited against the design they escape. It is NOT used to score any
    mutant and contributes nothing to this control's verdict. The BATCH-001
    driver itself is not executed and not modified.
    """
    from Crypto.Cipher import AES as PyAES
    saved_new = PyAES.new
    modname = f"legacy_replica_{name}"
    try:
        spec = importlib.util.spec_from_file_location(modname, mutant_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[modname] = mod
        try:
            spec.loader.exec_module(mod)
        except AssertionError as exc:
            return {"status": "rejected_by_module_self_check", "detected": True,
                    "detail": f"AssertionError: {exc}",
                    "comparisons_executed": 0}
        except Exception as exc:
            return {"status": "driver_import_error", "detected": False,
                    "detail": f"{type(exc).__name__}: {exc}",
                    "comparisons_executed": 0}

        rng = random.Random(SEEDS["legacy_replica_pairs"])
        flagged = total = 0
        for _ in range(30):
            key = bytes(rng.randrange(256) for _ in range(16))
            pt = bytes(rng.randrange(256) for _ in range(16))
            total += 1
            if mod.AES(key).encrypt_block(pt) != PyAES.new(key, PyAES.MODE_ECB).encrypt(pt):
                flagged += 1
        return {"status": "applied", "detected": flagged > 0,
                "random_pairs_flagged": flagged, "random_pairs_total": total,
                "comparisons_executed": total}
    except BaseException as exc:
        return {"status": "escaped_scoring_loop", "detected": None,
                "detail": f"{type(exc).__name__}: {exc} (not caught by "
                          f"`except Exception` in the BATCH-001 scoring loop)",
                "comparisons_executed": 0}
    finally:
        PyAES.new = saved_new                 # undo any tamper
        sys.modules.pop(modname, None)


# ---------------------------------------------------------------------------
# Source construction
# ---------------------------------------------------------------------------

def apply_edits(src: str, edits) -> Tuple[Optional[str], List[Dict]]:
    out = src
    log = []
    ok = True
    for old, new in edits:
        n = out.count(old)
        log.append({"anchor_occurrences": n, "anchor_head": old.strip()[:80]})
        if n != 1:
            ok = False
            continue
        out = out.replace(old, new)
    if not ok or out == src:
        return None, log
    return out, log


def inject(src: str, injection: str) -> Optional[str]:
    if src.count(INJECT_ANCHOR) < 1:
        return None
    return src.replace(INJECT_ANCHOR, injection + "\n" + INJECT_ANCHOR, 1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def tool_versions() -> Dict:
    def run(cmd):
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return (p.stdout + p.stderr).strip().splitlines()[0]
        except Exception as exc:                                   # pragma: no cover
            return f"unavailable: {type(exc).__name__}: {exc}"
    import Crypto
    return {
        "python": sys.version.split()[0],
        "python_full": sys.version.replace("\n", " "),
        "python_executable": sys.executable,
        "pycryptodome": Crypto.__version__,
        "openssl_cli": run(["openssl", "version"]),
        "gcc": run(["gcc", "-dumpfullversion"]),
        "platform": platform.platform(),
        "note": "Every string above is reported BY THE TOOL ITSELF at run time "
                "(sys.version, Crypto.__version__, `openssl version`, "
                "`gcc -dumpfullversion`); none is transcribed.",
    }


def git_state(repo_root: str) -> Dict:
    def run(args):
        p = subprocess.run(["git", "-C", repo_root] + args,
                           capture_output=True, text=True)
        return p.stdout.strip(), p.returncode
    head, _ = run(["rev-parse", "HEAD"])
    porcelain, _ = run(["status", "--porcelain"])
    return {
        "commit": head,
        "dirty": bool(porcelain.strip()),
        "dirty_paths": [l for l in porcelain.splitlines() if l.strip()],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", default=None,
                    help="path to the committed aes_reduced.py (read-only)")
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--out", default=None, help="write the receipt JSON here")
    ap.add_argument("--prior-digest", default=None)
    ap.add_argument("--meta", default=None,
                    help="path to a JSON file embedded verbatim under "
                         "`executor_meta` (inference block, run ledger, "
                         "deviations). Its contents are author-supplied and "
                         "are labelled as such; nothing in it is measured.")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = args.repo_root or os.path.abspath(
        os.path.join(here, "..", "..", "..", "..", "..", "..", ".."))
    module_path = args.module or os.path.join(repo_root, DEFAULT_MODULE_PATH)
    module_path = os.path.abspath(module_path)

    started = time.time()
    commands: List[Dict] = []
    checks_not_run: List[Dict] = [
        {
            "check": "cross-check of any r < Nr mutant against an EXTERNAL "
                     "reduced-round AES reference",
            "reason": "No such reference exists in this environment (defect "
                      "H-4, declared and irreducible). pycryptodome and the "
                      "openssl CLI implement r = Nr only. Not run; not "
                      "obtainable.",
        },
        {
            "check": "NIST CAVP / AESAVS response-file vectors",
            "reason": "Files not present locally and csrc.nist.gov is "
                      "unreachable under this harness's network policy.",
        },
        {
            "check": "repair of H-2 (assert-based module self-check stripped "
                     "under python3 -O)",
            "reason": "OUT OF SCOPE by handoff TASK-20260731-702: H-2 is "
                      "RECORDED, NOT REPAIRED. No workaround was applied.",
        },
        {
            "check": "re-execution of the BATCH-001 verification driver itself",
            "reason": "Not run. BATCH-001 artifacts are committed and immutable; "
                      "this control supersedes rather than re-runs them. The "
                      "in-process scoring core is instead REPLICATED here "
                      "(legacy_inprocess_replica) solely to exhibit escape "
                      "routes 3 and 4.",
        },
        {
            "check": "decrypt-direction and non-ECB mode comparisons for mutants",
            "reason": "Not run: the detection rule is defined on encryption "
                      "ciphertext comparison only. Recorded as a coverage "
                      "boundary of this control, not as a passing check.",
        },
    ]

    with open(module_path) as fh:
        src = fh.read()

    full_tasks, reduced_tasks = build_tasks()
    all_tasks = full_tasks + reduced_tasks

    # --- anchor TARGET-REF against TARGET-EXT at r = Nr -------------------
    anchor_rows = []
    anchor_ok = True
    arng = random.Random(SEEDS["full_round_tasks"] ^ 0xA5A5)
    for klen in (16, 24, 32):
        agree = 0
        n = 8
        for _ in range(n):
            key = bytes(arng.randrange(256) for _ in range(klen))
            pt = bytes(arng.randrange(256) for _ in range(16))
            if RefAES(key).encrypt_block(pt) == pycrypto_encrypt(key, pt):
                agree += 1
        anchor_rows.append({"key_bits": klen * 8, "cases": n, "agreeing": agree})
        anchor_ok = anchor_ok and (agree == n)

    refs = reference_ciphertexts(all_tasks)

    tmpdir = tempfile.mkdtemp(prefix="mutation_control_v2_")
    runner_path = os.path.join(tmpdir, "mutant_runner.py")
    with open(runner_path, "w") as fh:
        fh.write(RUNNER_SRC)

    # --- mutants -----------------------------------------------------------
    mutant_rows: List[Dict] = []
    mutant_sources: Dict[str, str] = {}
    for spec in MUTANTS:
        msrc, edit_log = apply_edits(src, spec["edits"])
        row = {
            "mutant": spec["name"],
            "class": spec["class"],
            "perturbation": spec["description"],
            "target_logic": spec.get("target_logic"),
            "expected_detected": spec["expected_detected"],
            "edit_log": edit_log,
        }
        if msrc is None:
            row.update({
                "status": "NOT_APPLIED",
                "scored": False,
                "detected": False,
                "detection_mechanism": None,
                "reason": "mutation anchor absent or not unique; mutant UNSCORED",
            })
            mutant_rows.append(row)
            continue
        mutant_sources[spec["name"]] = msrc
        mpath = os.path.join(tmpdir, f"mutant_{spec['name']}.py")
        with open(mpath, "w") as fh:
            fh.write(msrc)
        res = run_isolated(runner_path, mpath, all_tasks, tmpdir,
                           spec["name"], commands)
        sc = score(res, all_tasks, refs)
        row.update(sc)
        row["scored"] = True
        row["mutant_source_sha256"] = hashlib.sha256(msrc.encode()).hexdigest()
        row["matches_expectation"] = (sc["detected"] == spec["expected_detected"])
        mutant_rows.append(row)

    # --- probes ------------------------------------------------------------
    probe_rows: List[Dict] = []
    for p in PROBES:
        base_src = src if p["base"] is None else mutant_sources.get(p["base"])
        row = {
            "probe": p["name"],
            "failure_shape": p["shape"],
            "base_source": p["base"] or "unmutated aes_reduced.py (cipher unchanged)",
            "injected_source": p["injection"],
            "injection_point": f"immediately before `{INJECT_ANCHOR}` (module top level)",
            "expected_detected": p["expected_detected"],
        }
        if base_src is None:
            row.update({"status": "NOT_APPLIED", "scored": False,
                        "reason": "base mutant unavailable; probe UNSCORED"})
            probe_rows.append(row)
            continue
        psrc = inject(base_src, p["injection"])
        if psrc is None:
            row.update({"status": "NOT_APPLIED", "scored": False,
                        "reason": "injection anchor absent; probe UNSCORED"})
            probe_rows.append(row)
            continue
        ppath = os.path.join(tmpdir, f"probe_{p['name']}.py")
        with open(ppath, "w") as fh:
            fh.write(psrc)

        res = run_isolated(runner_path, ppath, all_tasks, tmpdir,
                           p["name"], commands)
        sc = score(res, all_tasks, refs)
        row["v2_scored_output"] = sc
        row["v2_detected"] = sc["detected"]
        row["exception_raised"] = sc.get("error_type")
        row["exception_detail"] = sc.get("error_detail")
        # verdict this probe would produce if it were the whole control run
        if sc["detected"]:
            standalone = "pass"
        elif sc.get("infrastructure_outcome"):
            standalone = "FAIL"
        else:
            standalone = "no_detection_credited"
        row["v2_standalone_verdict"] = standalone
        row["expected_standalone_verdict"] = p["expected_standalone_verdict"]
        row["matches_expectation"] = (
            sc["detected"] == p["expected_detected"]
            and standalone == p["expected_standalone_verdict"]
        )
        # the same probe under a replica of the BATCH-001 in-process scoring
        row["legacy_inprocess_replica_outcome"] = \
            legacy_inprocess_replica(ppath, p["name"])
        row["scored"] = True
        probe_rows.append(row)

    # --- verdict -----------------------------------------------------------
    unscored = [r["mutant"] for r in mutant_rows if not r.get("scored")] + \
               [r["probe"] for r in probe_rows if not r.get("scored")]
    faults_ok = all(r.get("detected") for r in mutant_rows
                    if r.get("expected_detected") and r.get("scored"))
    noop_ok = all(not r.get("detected") for r in mutant_rows
                  if not r.get("expected_detected") and r.get("scored"))
    h3_ok = all(r.get("detected_at_r_lt_Nr") for r in mutant_rows
                if r.get("class") == "reduced_round_structure" and r.get("scored"))
    probes_ok = all(r.get("matches_expectation") for r in probe_rows
                    if r.get("scored"))
    verdict = "pass" if (anchor_ok and faults_ok and noop_ok and h3_ok
                         and probes_ok and not unscored) else "FAIL"

    receipt = {
        "schema": "crypto.autoresearch.mutation_control_v2.receipt.v1",
        "task_id": TASK_ID,
        "control_version": CONTROL_VERSION,
        "verdict": verdict,
        "verdict_components": {
            "target_ref_anchored_to_target_ext_at_full_rounds": anchor_ok,
            "all_fault_mutants_detected_by_comparison": faults_ok,
            "noop_mutant_not_detected": noop_ok,
            "every_reduced_round_mutant_detected_at_r_lt_Nr": h3_ok,
            "all_injected_failure_probes_behaved_as_required": probes_ok,
            "unscored_items": unscored,
        },
        "detection_rule": (
            "detected := (comparisons_executed > 0) and (divergences > 0). "
            "comparisons_executed counts (mutant ciphertext, reference "
            "ciphertext) pairs physically produced and compared. No exception "
            "of any class, at import time or at run time, can increment it or "
            "produce detected: true. The BATCH-001 self-check detection path "
            "(`except AssertionError -> rejected_by_module_self_check, "
            "detected: True`) is REMOVED, not narrowed."
        ),
        "comparison_targets": {
            "TARGET-EXT": {
                "what": "pycryptodome ECB, external to this program",
                "used_for": "r = Nr tasks only",
                "establishes": "divergence from an external AES implementation",
            },
            "TARGET-REF": {
                "what": "RefAES, a second implementation of the documented "
                        "C1/C2/C3 convention authored inside this task "
                        "(log/antilog S-box, xtime MixColumns, literal Rcon, "
                        "list-based state)",
                "used_for": "r < Nr tasks",
                "anchored_to": "TARGET-EXT at r = Nr, all three key sizes",
                "establishes": "SENSITIVITY of this control to round-structure "
                               "perturbation, and agreement between two "
                               "structurally different implementations of the "
                               "same written convention",
                "does_not_establish": "that the C1/C2/C3 convention is correct, "
                                      "standard, or the one used anywhere else. "
                                      "RefAES was authored in this task from the "
                                      "same prose by the same agent and is NOT an "
                                      "external reference.",
            },
            "H4_status": "H-4 (no external reference exists for r < Nr) STANDS "
                         "AND IS NOT CLAIMED REMOVED.",
            "unmutated_module_as_target": "NOT USED.",
        },
        "target_ref_anchor": {"per_key_size": anchor_rows, "ok": anchor_ok},
        "module_under_mutation": {
            "path": os.path.relpath(module_path, repo_root),
            "sha256": sha256_file(module_path),
            "read_only": True,
            "note": "read from its committed BATCH-001 location; mutated only "
                    "into copies under a scratch tmpdir",
        },
        "task_sets": {
            "full_round_tasks": len(full_tasks),
            "reduced_round_tasks": len(reduced_tasks),
            "reduced_round_counts": {str(k): list(v)
                                     for k, v in REDUCED_ROUND_COUNTS.items()},
            "final_mix_columns_variants_covered": [False, True],
        },
        "seeds": SEEDS,
        "randomness_sources": [
            "random.Random(SEEDS['full_round_tasks']) -- full-round task set",
            "random.Random(SEEDS['reduced_round_tasks']) -- reduced-round task set",
            "random.Random(SEEDS['full_round_tasks'] ^ 0xA5A5) -- anchor cases",
            "random.Random(SEEDS['legacy_replica_pairs']) -- legacy replica pairs",
        ],
        "mutants": mutant_rows,
        "injected_failure_shape_probes": probe_rows,
        "escape_routes_examined": [
            {
                "id": "ER-1",
                "description": "import-time AssertionError credited as a "
                               "detection (defect H-1)",
                "status_in_v2": "closed by removing the self-check detection "
                                "path; exhibited by probe A",
            },
            {
                "id": "ER-2",
                "description": "import-time non-AssertionError credited as a "
                               "detection (the original BATCH-001 false green)",
                "status_in_v2": "closed; exhibited by probe B",
            },
            {
                "id": "ER-3",
                "description": "a mutant monkeypatches the scoring process's "
                               "reference oracle at import time, manufacturing "
                               "a detection on a semantics-preserving module. "
                               "FOUND BY THIS TASK; applies to any in-process "
                               "scoring design, including BATCH-001's.",
                "status_in_v2": "closed by subprocess isolation plus computing "
                                "reference ciphertexts in the parent before any "
                                "mutant runs; exhibited by probe C",
            },
            {
                "id": "ER-4",
                "description": "a mutant raises SystemExit (a BaseException) at "
                               "import, escaping `except Exception` in an "
                               "in-process scoring loop. FOUND BY THIS TASK.",
                "status_in_v2": "closed: the isolated runner catches "
                                "BaseException and a nonzero subprocess exit is "
                                "an infrastructure outcome; exhibited by probe D",
            },
            {
                "id": "ER-5",
                "description": "residual, NOT closed: a mutant can still HIDE "
                               "its fault -- e.g. by emitting correct "
                               "ciphertexts from a tampered output path. That "
                               "direction produces a FALSE NEGATIVE (an "
                               "undetected mutant, reported as undetected), "
                               "never a false green.",
                "status_in_v2": "open by design; recorded, not repaired",
            },
        ],
        "H2_status": "RECORDED, NOT REPAIRED. aes_reduced.py's import-time "
                     "consistency check is an `assert` and is stripped by "
                     "python3 -O. Removing the self-check DETECTION path means "
                     "H-2 can no longer produce a false green in this control, "
                     "but the module-level weakness is unchanged and H-2 IS NOT "
                     "CLOSED.",
        "supersedes": [
            "coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/"
            "TASK-20260731-602/run_record.md :: check_detection_power (driver "
            "sha256 675ff4d568c03f6b12aa5d8931c6185ec7c5b08344ef826616fd9580d4c84a6d)",
            "coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/"
            "TASK-20260731-602/vector_check_receipt.json :: "
            "detection_power_mutation_control",
        ],
        "scope_statement": "INSTRUMENT ONLY. Nothing here is a cryptanalytic "
                           "claim, an evidence-strength assignment, or a "
                           "statement about AES at any round count.",
        "commands_executed": commands,
        "checks_not_run": checks_not_run,
        "tool_versions": tool_versions(),
        "git": git_state(repo_root),
        "environment": {
            "cpu_count": os.cpu_count(),
            "cwd": os.getcwd(),
            "tmpdir": tmpdir,
        },
        "timing": {
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                         time.gmtime(started)),
            "wall_clock_seconds": None,
        },
        "control_source_sha256": sha256_file(os.path.abspath(__file__)),
    }

    # deterministic digest over scored content only
    digest_payload = json.dumps({
        "mutants": mutant_rows,
        "probes": [{k: v for k, v in r.items()
                    if k != "legacy_inprocess_replica_outcome"}
                   for r in probe_rows],
        "anchor": anchor_rows,
        "verdict": verdict,
        "refs": refs,
    }, sort_keys=True, default=str)
    receipt["results_digest"] = hashlib.sha256(digest_payload.encode()).hexdigest()
    if args.prior_digest:
        receipt["prior_digest"] = args.prior_digest
        receipt["determinism_rerun_digest_matches"] = \
            (args.prior_digest == receipt["results_digest"])
    receipt["timing"]["wall_clock_seconds"] = round(time.time() - started, 3)

    if args.meta:
        with open(args.meta) as fh:
            meta = json.load(fh)
        meta["_provenance"] = ("author-supplied, embedded verbatim from "
                               f"{os.path.basename(args.meta)}; not measured "
                               "by this control")
        receipt["executor_meta"] = meta
        if isinstance(meta.get("inference"), dict):
            receipt["inference"] = meta["inference"]

    text = json.dumps(receipt, indent=2, default=str)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    print(text)
    return 0 if verdict == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
