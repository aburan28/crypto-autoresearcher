#!/usr/bin/env sage -python
"""Verify Atkin projective orders and allowed traces using extension fields."""
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from sage.all import GF, ZZ, gcd, kronecker, prime_range
from sage.env import SAGE_VERSION

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / "research/nist_seed_1997_selection_extension_20261023/sea_signature/runs/scan-20261023T1840Z/raw.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory):
    raw = json.loads((directory/"raw.json").read_text())
    receipt = json.loads((directory/"receipt.json").read_text())
    assert receipt["status"] == "completed" and receipt["raw_sha256"] == sha(directory/"raw.json")
    assert receipt["protocol_sha256"] == sha(HERE/"PROTOCOL.md")
    assert receipt["code_sha256"] == sha(HERE/"scan.py")
    assert sha(INPUT) == receipt["input_sha256"] == "4a0df1de260e4533253ef591f7b084b73e86fac5e03558ec3609081c750f48fe"
    source = {r["curve_uid"]: r for r in json.loads(INPUT.read_text())["rows"]}
    assert len(source) == len(raw["rows"]) == 19
    ell_list = list(map(int, prime_range(3, 998)))
    assert raw["odd_primes"] == ell_list and len(ell_list) == 167
    extensions, sets = {}, {}
    atkin_count = 0
    for row in raw["rows"]:
        prior = source[row["curve_uid"]]
        for key in ("name", "label", "field_bits", "p_hex", "n_hex", "trace_hex_signed"):
            assert row[key] == prior[key]
        p, n = int(row["p_hex"],16), int(row["n_hex"],16)
        trace = p+1-n
        assert trace == int(row["trace_hex_signed"],16) and trace*trace <= 4*p
        M, A, elkies_M = ZZ(1), ZZ(1), ZZ(1)
        cutoff, old_cutoff = None, None
        assert [cell["ell"] for cell in row["cells"]] == ell_list
        for cell in row["cells"]:
            ell = cell["ell"]
            F = GF(ell)
            u, q = F(trace), F(p)
            chi = int(kronecker(ZZ(trace*trace-4*p), ell))
            if chi == 1:
                assert cell["type"] == "elkies" and cell["r"] is None
                expected = [int(u)]
                elkies_M *= ell
            elif chi == 0:
                assert cell["type"] == "ramified" and cell["r"] is None
                expected = sorted(int(x) for x in (4*q).sqrt(all=True))
            else:
                assert cell["type"] == "atkin"
                atkin_count += 1
                if ell not in extensions:
                    extensions[ell] = GF(ell**2, name="z")
                K = extensions[ell]
                lam = (K(u) + K(u*u-4*q).sqrt())/2
                r = int((lam**2/K(q)).multiplicative_order())
                assert r == cell["r"] and r > 1 and (ell+1) % r == 0
                key = (ell, int(q), r)
                if key not in sets:
                    z0 = K.multiplicative_generator() ** ((ell**2-1)//r)
                    assert int(z0.multiplicative_order()) == r
                    traces = set()
                    for k in range(1, r+1):
                        if gcd(k,r) != 1:
                            continue
                        z = z0**k
                        square = K(q)*(z+1/z+2)
                        assert square**ell == square and square.polynomial().degree() <= 0
                        base = F(square.polynomial()[0])
                        if base.is_square():
                            traces.update(int(x) for x in base.sqrt(all=True))
                    sets[key] = sorted(traces)
                    assert len(sets[key]) == ZZ(r).euler_phi()
                expected = sets[key]
                assert sorted((-x) % ell for x in expected) == expected
            assert expected == cell["allowed"] and len(expected) == cell["size"] and int(u) in expected
            M *= ell
            A *= len(expected)
            if cutoff is None and M*M > 16*p*A*A:
                cutoff = ell
            if old_cutoff is None and elkies_M*elkies_M > 16*p:
                old_cutoff = ell
        assert cutoff == row["residue_density_cutoff"]
        assert old_cutoff == row["elkies_only_cutoff"] == prior["cutoff_ell"]
    expected_comparisons = []
    for a in raw["rows"]:
        for b in raw["rows"]:
            if a["label"] == "omitted" and b["label"] == "published" and a["p_hex"] == b["p_hex"]:
                av, bv = a["residue_density_cutoff"], b["residue_density_cutoff"]
                expected_comparisons.append({"omitted":a["name"],"published":b["name"],"omitted_cutoff":av,"published_cutoff":bv,"omitted_lower":av<bv,"published_lower":bv<av,"tie":av==bv})
    assert expected_comparisons == raw["comparisons"] and len(expected_comparisons) == 25
    assert {k:sum(c[k] for c in expected_comparisons) for k in ("omitted_lower","published_lower","tie")} == raw["pair_summary"]
    assert raw["real_cells"] == 3173 and raw["synthetic_controls_passed"]
    F = GF(3)
    K = GF(9, name="control")
    lam = K(-1).sqrt()
    assert (lam**2).multiplicative_order() == 2
    assert not (ZZ(4)**2 > 16) and ZZ(5)**2 > 16
    return {"verified_real_cells":3173, "verified_atkin_cells":atkin_count,"distinct_atkin_sets":len(sets),"verified_pairs":25,"pair_summary":raw["pair_summary"]}


if __name__ == "__main__":
    directory = Path(sys.argv[1])
    output = directory/"verification.json"
    assert not output.exists()
    started = {"command":sys.argv,"sage_version":SAGE_VERSION,"started_utc":datetime.now(timezone.utc).isoformat(),"raw_sha256":sha(directory/"raw.json"),"verifier_sha256":sha(Path(__file__))}
    (directory/"verification_started.json").write_text(json.dumps(started,indent=2,sort_keys=True)+"\n")
    wall, cpu = time.monotonic(), time.process_time()
    try:
        result = verify(directory)
        result.update(started)
        result.update({"status":"passed","wall_seconds":time.monotonic()-wall,"cpu_seconds":time.process_time()-cpu,"finished_utc":datetime.now(timezone.utc).isoformat()})
        output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        (directory/"verification_stdout.log").write_text(json.dumps(result,sort_keys=True)+"\n")
        (directory/"verification_stderr.log").write_text("")
        print(json.dumps(result,sort_keys=True))
    except BaseException:
        (directory/"verification_stderr.log").write_text(traceback.format_exc())
        raise
