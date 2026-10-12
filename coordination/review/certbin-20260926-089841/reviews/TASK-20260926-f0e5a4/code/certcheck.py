"""Certificate checkers for flat-v1 and wdag-v1, written from
EXP-CERTBIN-ddfe75 object.certificate_format. Own Boolean-ring arithmetic
(bring.py). Imports nothing from this repository.

flat-v1: C = list of (mu as sorted index list, k); claim sum_C mu*f_k = 1 in B.
wdag-v1: {"D": 4, "nv": 18, "nodes": [{"id", "rows": [[mu, k]..], "prods": [[j, c]..]}],
          "output": o}; poly(i) = sum_rows mu*f_k + sum_prods v_j * poly(c).
  (a) every child id c < i; (b) every |mu| <= D-2 = 2 and 0 <= k <= 16;
  (c) every child c used in prods has deg poly(c) <= D-1 = 3;
  (d) every node has deg poly(i) <= D; (e) poly(output) == 1.
"""
import numpy as np

import bring
from layout import NEQ, NV, mask_to_idx

D_FROZEN = 4
NV_FROZEN = 18


def system_polys(rows_monomials):
    """17 lists of monomial masks -> 17 numpy polynomials."""
    return [bring.parity_reduce(np.array(ms, dtype=np.int64)) for ms in rows_monomials]


def _mu_parse(mu):
    """Returns (mask, well_formed, note)."""
    if not isinstance(mu, list):
        return None, False, "mu not a list"
    for i in mu:
        if not isinstance(i, int) or isinstance(i, bool) or i < 0 or i >= NV:
            return None, False, "mu index out of range"
    if len(set(mu)) != len(mu):
        return None, False, "mu has repeated index"
    m = 0
    for i in mu:
        m |= 1 << i
    note = None if mu == sorted(mu) else "mu not sorted"
    return m, True, note


def _k_ok(k):
    return isinstance(k, int) and not isinstance(k, bool) and 0 <= k < NEQ


def residual_info(P):
    """P = computed sum; residual = P + 1."""
    R = bring.add(P, bring.ONE)
    sample = [mask_to_idx(int(m)) for m in R[:5]]
    return int(R.size), sample


def check_flat(body, F):
    out = {"format_ok": True, "format_notes": []}
    if not isinstance(body, list):
        out.update(format_ok=False, verified=False, reason="body not a list")
        return out
    terms = []
    max_mu = -1
    seen = set()
    dup = 0
    prev = None
    unsorted = False
    for ent in body:
        if not (isinstance(ent, list) and len(ent) == 2):
            out.update(format_ok=False, verified=False, reason="entry not [mu, k]")
            return out
        mu, k = ent
        m, ok, note = _mu_parse(mu)
        if not ok:
            out.update(format_ok=False, verified=False, reason=note)
            return out
        if note:
            out["format_notes"].append(note)
        if not _k_ok(k):
            out.update(format_ok=False, verified=False, reason="k out of range")
            return out
        key = (tuple(mu), k)
        if key in seen:
            dup += 1
        seen.add(key)
        if prev is not None and key < prev:
            unsorted = True
        prev = key
        max_mu = max(max_mu, len(mu))
        if F[k].size:
            terms.append(F[k] | np.int64(m))
    P = bring.parity_reduce(np.concatenate(terms)) if terms else bring.EMPTY
    verified = bring.is_one(P)
    rs, sample = residual_info(P)
    out.update(verified=verified, size=len(body), max_mu=max_mu,
               residual_size=rs, residual_sample=sample,
               duplicates=dup, sorted=not unsorted,
               reason=None if verified else "sum != 1")
    if unsorted:
        out["format_notes"].append("C not sorted")
    if dup:
        out["format_notes"].append("C has duplicate entries")
    out["format_notes"] = sorted(set(out["format_notes"]))
    return out


def check_wdag(body, F, evaluate_even_if_a_fails=False):
    """Returns dict with per-rule booleans, first_violated_rule, verified."""
    res = {"rules": {"a": True, "b": True, "c": True, "d": True, "e": True},
           "violations": [], "format_ok": True, "format_notes": []}

    def fail(rule, detail):
        res["rules"][rule] = False
        if len(res["violations"]) < 20:
            res["violations"].append({"rule": rule, "detail": detail})

    if not isinstance(body, dict):
        res.update(format_ok=False, verified=False, first_violated_rule="format", reason="body not an object")
        return res
    if body.get("D") != D_FROZEN or body.get("nv") != NV_FROZEN:
        res["format_ok"] = False
        res["format_notes"].append("D or nv not the frozen (4, 18): %r, %r" % (body.get("D"), body.get("nv")))
    nodes = body.get("nodes")
    output = body.get("output")
    if not isinstance(nodes, list) or not nodes:
        res.update(format_ok=False, verified=False, first_violated_rule="format", reason="no nodes")
        return res
    ids = []
    for nd in nodes:
        if not isinstance(nd, dict) or not isinstance(nd.get("id"), int):
            res.update(format_ok=False, verified=False, first_violated_rule="format", reason="node without int id")
            return res
        ids.append(nd["id"])
    if len(set(ids)) != len(ids):
        res.update(format_ok=False, verified=False, first_violated_rule="format", reason="duplicate node ids")
        return res
    idset = set(ids)
    if output not in idset:
        res.update(format_ok=False, verified=False, first_violated_rule="format", reason="output id not a node")
        return res
    if ids != list(range(len(ids))):
        res["format_notes"].append("node ids are not 0..n-1 in list order")
    byid = {nd["id"]: nd for nd in nodes}

    # rule (a): topological order; also well-formed prods
    max_mu = -1
    n_rows = 0
    n_prods = 0
    for nd in nodes:
        i = nd["id"]
        for pr in nd.get("prods", []):
            if not (isinstance(pr, list) and len(pr) == 2):
                res.update(format_ok=False, verified=False, first_violated_rule="format", reason="prod not [j, c]")
                return res
            j, c = pr
            if not (isinstance(j, int) and 0 <= j < NV):
                res.update(format_ok=False, verified=False, first_violated_rule="format", reason="prod variable out of range")
                return res
            if c not in idset:
                res.update(format_ok=False, verified=False, first_violated_rule="format", reason="prod child not a node")
                return res
            if not c < i:
                fail("a", {"node": i, "child": c})
            n_prods += 1
        # rule (b)
        for ent in nd.get("rows", []):
            if not (isinstance(ent, list) and len(ent) == 2):
                res.update(format_ok=False, verified=False, first_violated_rule="format", reason="row not [mu, k]")
                return res
            mu, k = ent
            m, ok, note = _mu_parse(mu)
            if not ok:
                res.update(format_ok=False, verified=False, first_violated_rule="format", reason=note)
                return res
            if note:
                res["format_notes"].append(note)
            if len(mu) > D_FROZEN - 2:
                fail("b", {"node": i, "mu": mu, "k": k, "deg_mu": len(mu)})
            if not _k_ok(k):
                fail("b", {"node": i, "mu": mu, "k": k, "reason": "k out of 0..16"})
            max_mu = max(max_mu, len(mu))
            n_rows += 1
    res.update(node_count=len(nodes), size=n_rows, n_prods=n_prods, max_mu=max_mu)

    if not res["rules"]["a"] and not evaluate_even_if_a_fails:
        res["rules"]["c"] = res["rules"]["d"] = res["rules"]["e"] = None
        res.update(verified=False, first_violated_rule="a", max_child_degree=None,
                   reason="topological order violated; not evaluated")
        res["format_notes"] = sorted(set(res["format_notes"]))
        return res

    # evaluate in increasing id order (valid when (a) holds); in the diagnostic
    # mode (a failed) evaluate in dependency order if the graph is acyclic
    order = sorted(ids)
    if not res["rules"]["a"]:
        order = []
        state = {}
        cyclic = False

        def visit(x):
            nonlocal cyclic
            if state.get(x) == 2:
                return
            if state.get(x) == 1:
                cyclic = True
                return
            state[x] = 1
            for _, cc in byid[x].get("prods", []):
                visit(cc)
            state[x] = 2
            order.append(x)

        for x in sorted(ids):
            visit(x)
        if cyclic:
            res["rules"]["c"] = res["rules"]["d"] = res["rules"]["e"] = None
            res.update(verified=False, first_violated_rule="a", max_child_degree=None,
                       reason="cyclic child references; not evaluated")
            return res
    polys = {}
    degs = {}
    max_child_deg = -1
    children_used = set()
    for i in order:
        nd = byid[i]
        parts = []
        for mu, k in nd.get("rows", []):
            if not _k_ok(k):
                continue
            m = 0
            for x in mu:
                m |= 1 << x
            if F[k].size:
                parts.append(F[k] | np.int64(m))
        for j, c in nd.get("prods", []):
            if c not in polys:  # only when (a) failed and we evaluate anyway
                continue
            children_used.add(c)
            if polys[c].size:
                parts.append(polys[c] | np.int64(1 << j))
        P = bring.parity_reduce(np.concatenate(parts)) if parts else bring.EMPTY
        polys[i] = P
        degs[i] = bring.degree(P)
        if degs[i] > D_FROZEN:
            fail("d", {"node": i, "degree": degs[i]})
    for c in sorted(children_used):
        max_child_deg = max(max_child_deg, degs[c])
        if degs[c] > D_FROZEN - 1:
            fail("c", {"child": c, "degree": degs[c]})
    Pout = polys[output]
    if not bring.is_one(Pout):
        rs, sample = residual_info(Pout)
        fail("e", {"residual_size": rs, "residual_sample": sample})
        res.update(residual_size=rs, residual_sample=sample)
    else:
        res.update(residual_size=0, residual_sample=[])
    first = None if res["format_ok"] else "format"
    for r in "abcde":
        if first is None and res["rules"][r] is False:
            first = r
            break
    res.update(max_child_degree=max_child_deg,
               node_degrees=[degs[i] for i in sorted(ids)] if len(ids) <= 64 else None,
               first_violated_rule=first,
               verified=(first is None and res["format_ok"]),
               reason=None if first is None else "rule (%s) violated" % first)
    res["format_notes"] = sorted(set(res["format_notes"]))
    return res
