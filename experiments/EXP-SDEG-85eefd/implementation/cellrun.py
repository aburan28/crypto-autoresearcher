"""Execute one (fixture, deck) cell: oracle, forward table, B0/B1/B2 per query,
witness replay, agreement checks. Shared by smoke.py and driver.py."""

from __future__ import annotations

import signal
import time

import b2split
import backends
import decks as decks_mod
from fparith import OpCounter
from oracle import A5Oracle
from verify import O

WATCHDOG_SECONDS = 3600


class WatchdogStop(RuntimeError):
    pass


class ProcedureDefect(RuntimeError):
    """A stopping-rule event: failed identity, oracle disagreement, unverified witness."""


def _alarm(signum, frame):
    raise WatchdogStop("per-query watchdog expired")


def _with_watchdog(fn, seconds):
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return fn(), None
    except WatchdogStop as e:
        return None, str(e)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def fixed_xR_cost(fx, sem, R) -> int:
    """Charged cost of B1's per-query specialization at x(R), recomputed on a
    fresh counter (used when the query itself was stopped by the watchdog)."""
    if R is O:
        return 0
    from fparith import Fp
    ctr = OpCounter()
    sem.spec_last(Fp(fx["p"], ctr), sem.S5, R[0])
    return ctr.W()


def _pt(P):
    return None if P is O else list(P)


def run_cell(fx, deck, sem, ns, n_planted, n_random, audit_ids=frozenset(),
             watchdog_s=WATCHDOG_SECONDS, stop_on_defect=True, log=print,
             b2_split: bool | None = None) -> dict:
    """b2_split: run the no-Sage split cross-check of B2 on every query
    (default: at L = 8 only, per the driver default ruled in OQ-5)."""
    if b2_split is None:
        b2_split = fx["L"] == 8
    t0 = time.time()
    orc = A5Oracle(fx, deck)
    t_oracle = time.time() - t0
    table = backends.ForwardTable(fx, deck, build_poly=True)
    table_ops = {"B0": table.ops_points, "B1": table.ops}
    queries = decks_mod.targets(fx, deck, ns, n_planted, n_random)
    nq = len(queries)
    cell = {"fixture": f"L{fx['L']}-s{fx['seed']}", "L": fx["L"], "seed": fx["seed"], "q": fx["N"],
            "p": fx["p"], "deck": deck.name, "V": deck.V, "V_size": deck.size,
            "deck_notes": deck.notes, "deck_construction_ops": deck.construction_ops,
            "forward_table": {"size_finite": table.size, "has_inf": table.has_inf,
                              "ops_points_and_inserts": table.ops_points, "ops_with_FT": table.ops},
            "oracle": {"enumerated_multisets": orc.enumerated, "expected": orc.expected_multisets,
                       "distinct_members": orc.distinct_members, "seconds": t_oracle},
            "n_queries": nq, "queries": [], "records": [], "defects": [],
            "b2_split_checked": bool(b2_split), "b2_split_mismatches": []}
    for qd in queries:
        R = qd["R"]
        member = orc.member(R)
        qrec = {"query_id": qd["query_id"], "kind": qd["kind"], "R": _pt(R),
                "planted_terms": qd.get("planted_terms"), "k": qd.get("k"),
                "oracle_member": member, "backends": {}}
        if qd["kind"] == "planted" and not member:
            cell["defects"].append(f"{qd['query_id']}: planted target not an oracle member")
        for be in ("B0", "B1"):
            ctr = OpCounter()
            keep = qd["query_id"] in audit_ids
            if be == "B0":
                fn = lambda: backends.b0_query(fx, deck, table, R, keep_log=keep, counter=ctr)  # noqa: E731
            else:
                fn = lambda: backends.b1_query(fx, deck, table, sem, R, keep_log=keep, counter=ctr)  # noqa: E731
            ts = time.time()
            res, stop = _with_watchdog(fn, watchdog_s)
            secs = time.time() - ts
            amort = (table_ops[be]["W"] + deck.construction_ops["W"]) / nq
            if stop:
                res = {"backend": be, "member": None, "W_query": ctr.W(), "ops": ctr.as_dict(),
                       "status": "watchdog_stop", "lower_bound": True, "hits": [], "hit_triples": []}
            else:
                res["status"] = "ok"
                res["lower_bound"] = False
            res["seconds"] = secs
            if res["status"] == "ok" and res.get("W_query_to_first_hit") is not None:
                res["W_query_decision"] = res["W_query_to_first_hit"]
            else:  # non-member (or stopped): full enumeration
                res["W_query_decision"] = res["W_query"]
            res["W_full"] = res["W_query"] + amort
            res["W"] = res["W_query_decision"] + amort
            if be == "B1":
                res["W_fixed_xR"] = (res["W_components"]["fixed_xR_specialization"]
                                     if res["status"] == "ok" else fixed_xR_cost(fx, sem, R))
            else:
                res["W_fixed_xR"] = 0
            res["W_triple"] = res["W"] - res["W_fixed_xR"]
            res["W_amortization_share"] = amort
            res["table_ops"] = table_ops[be]
            res["deck_construction_ops"] = deck.construction_ops
            res["n_queries_in_cell"] = nq
            res["query_id"] = qd["query_id"]
            wit = [backends.extract_and_verify(fx, deck, table, sem, R, tuple(h["triple"]), h)
                   for h in res.get("hits", [])]
            res["witness_checks"] = wit
            res["all_witnesses_verified"] = all(w["verified"] for w in wit)
            if res["status"] == "ok" and not res["all_witnesses_verified"]:
                cell["defects"].append(f"{qd['query_id']} {be}: unverified witness")
            qrec["backends"][be] = res
        b2 = backends.b2_query(fx, deck, R, return_roots=b2_split)
        if b2_split:
            xR = None if R is O else R[0]
            b2["split_crosscheck"] = b2split.crosscheck(sem, fx["p"], deck.V, xR, b2.pop("roots"))
            if not b2["split_crosscheck"]["match"]:
                cell["b2_split_mismatches"].append(qd["query_id"])
        qrec["backends"]["B2"] = b2
        b0, b1 = qrec["backends"]["B0"], qrec["backends"]["B1"]
        if b0["status"] == "ok" and b1["status"] == "ok":
            agree = (b0["member"] == b1["member"] == member)
            same_triples = sorted(map(tuple, b0["hit_triples"])) == sorted(map(tuple, b1["hit_triples"]))
            qrec["agreement"] = {"decision": agree, "hit_triple_sets_equal": same_triples}
            if not agree:
                cell["defects"].append(f"{qd['query_id']}: B0/B1/oracle disagreement "
                                       f"({b0['member']}, {b1['member']}, {member})")
            if not same_triples:  # FX-3 (AMD-20260928-d3ed9e): stops the run like a disagreement
                cell["defects"].append(f"{qd['query_id']}: B0/B1 hit-triple set mismatch")
        else:
            qrec["agreement"] = {"decision": None, "hit_triple_sets_equal": None}
        for be in ("B0", "B1"):
            r = qrec["backends"][be]
            cell["records"].append({
                "fixture": cell["fixture"], "L": fx["L"], "seed": fx["seed"], "q": fx["N"],
                "deck": deck.name, "query_id": qd["query_id"], "backend": be,
                "member": member if r["status"] == "ok" else None, "status": r["status"],
                "W": r["W"], "W_full": r["W_full"], "W_triple": r["W_triple"],
                "W_fixed_xR": r["W_fixed_xR"], "W_query": r["W_query"],
                "W_query_to_first_hit": r.get("W_query_to_first_hit"),
                "sub_degree": r.get("sub_degree_sum") if be == "B1" else None})
        cell["records"].append({
            "fixture": cell["fixture"], "L": fx["L"], "seed": fx["seed"], "q": fx["N"],
            "deck": deck.name, "query_id": qd["query_id"], "backend": "B2", "member": member,
            "status": "ok", "W": None, "W_full": None, "W_triple": None, "elim_degree": b2["elim_degree"]})
        for be in ("B0", "B1"):  # keep op logs only in the audit sample
            if qrec["backends"][be].get("op_log") is None:
                qrec["backends"][be].pop("op_log", None)
        cell["queries"].append(qrec)
        log(f"{qd['query_id']}: oracle={member} B0={b0['member']} B1={b1['member']} "
            f"B2deg={b2['elim_degree']} W0={b0['W_query']} W1={b1['W_query']}")
        if cell["defects"] and stop_on_defect:
            cell["stopped_on_defect"] = True
            break
    cell["seconds"] = time.time() - t0
    return cell


def opcount_rows(cell) -> list:
    """Canonical per-(query, backend) charged op counts: the host-independent
    part of a cell (no timings, pids or paths), sorted by query id, backend."""
    rows = []
    for q in cell["queries"]:
        for be in ("B0", "B1"):
            r = q["backends"][be]
            rows.append({"query_id": q["query_id"], "backend": be, "status": r["status"],
                         "member": r.get("member"), "ops": r["ops"], "W_query": r["W_query"],
                         "W_query_to_first_hit": r.get("W_query_to_first_hit"),
                         "W_fixed_xR": r.get("W_fixed_xR"),
                         "W_components": r.get("W_components"),
                         "hit_triples": [list(t) for t in r.get("hit_triples", [])],
                         "prs_steps": r.get("prs_steps"), "sub_degree_sum": r.get("sub_degree_sum")})
        b2 = q["backends"]["B2"]
        rows.append({"query_id": q["query_id"], "backend": "B2", "elim_degree": b2["elim_degree"],
                     "roots_sha256": b2["roots_sha256"]})
    return sorted(rows, key=lambda x: (x["query_id"], x["backend"]))


def canonical_opcounts_bytes(rows) -> bytes:
    import json
    return (json.dumps(sorted(rows, key=lambda x: (x["query_id"], x["backend"])),
                       sort_keys=True, separators=(",", ":")) + "\n").encode()
