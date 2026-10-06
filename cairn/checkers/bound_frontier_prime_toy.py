"""cairn evaluator: a measured ECDLP bound, scored against the generic floor.

Stage 2 of docs/cairn-integration-plan.md, one domain: the frontier of the
`ecdlp.single_target` problem on prime-field curves with planted targets, in
the `ecbench.gae` unit, at the `toy` tier (fields of at most 32 bits).  The
artifact is a bound record (`ecbench.bound/v1`, aburan28/crypto
`docs/bounds/README.md`), and the score is the parts per million of the
generic collision floor the method achieves: a method at the floor scores
1 000 000, `rho.negation` on the committed prime session about 682 000,
`bsgs.negation` about 867 000.  Higher is closer to the floor, so a ratchet
on this objective climbs toward the bound nobody beats generically.

# What is checked, and what is not

The checker recomputes everything the artifact lets it recompute: every
size's `S = mean_gae / sqrt(r)` and its ratio to the floor `sqrt(pi / 2A)`,
the pooled ratio as the run-weighted mean of the sizes, the tier from the
field sizes, the domain from its fields, the unit, admissibility.  A record
whose stated figures disagree with its own counts is refused, as is one that
measures time (the unit is counted, never clocked), one outside this domain
or tier, and one that is not admissible by its own account.

It cannot check that the sessions the record names exist and replay: a
sandboxed checker has no filesystem and no `ecbench`.  That is the measuring
repository's CI (`ecbench bound check`, `ecbench verify --replay-all`) and an
independent replay receipt, both cited by hash inside the record.  An accept
here is therefore a receipt for a well-formed, self-consistent frontier entry
in this domain -- exactly that strong and no stronger -- and backs no
`direction` in this program's ledger on its own (plan invariant (b)).

# Zero imports, constants in the text

As every checker here (see discrete_log.py): the sandbox gives a checker no
path back into this repository, and a pinned hash must cover everything the
checker does.  The domain is bound by the constants below, not by an argument,
so one objective is one domain and one tier (plan invariant (d)); another
domain is a copy with other constants, another hash, another objective.
"""

SCHEMA = "ecbench.bound/v1"
PROBLEM = "ecdlp.single_target"
FAMILY = "prime"
TARGET_KIND = "planted"
UNIT = "ecbench.gae"
TIER = "toy"
MAX_FIELD_BITS = 32
PI = 3.141592653589793
# Relative agreement required between a stated figure and its recomputation:
# the record's floats went through one JSON round trip, nothing more.
TOLERANCE = 1e-9
SCALE = 1_000_000


def _num(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError(f"{name} must be finite")
    return float(value)


def _int_like(value, name):
    # `r` is written as a JSON number while it fits 64 bits and as a decimal
    # string above that (ecbench `compat_u128`); the tier bound above keeps it
    # small here, but the reader accepts both forms rather than guessing.
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    raise ValueError(f"{name} must be an integer or a decimal string")


def _close(stated, recomputed, name):
    denom = max(abs(recomputed), 1e-300)
    if abs(stated - recomputed) / denom > TOLERANCE:
        raise ValueError(
            f"{name} is stated as {stated!r} but recomputes to {recomputed!r} from the record's own counts"
        )


def check(artifact):
    """`(ok, detail)`: ok when the record is a self-consistent, admissible
    bound in this domain and tier.  Never raises on hostile input."""
    try:
        score_value, detail = _evaluate(artifact)
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
        return False, f"refused: {exc}"
    return True, f"{detail}; score {score_value}"


def score(artifact):
    """The integer the ratchet reads: parts per million of the generic floor
    achieved.  Raises on a record that `check` would refuse."""
    score_value, _ = _evaluate(artifact)
    return score_value


def _evaluate(artifact):
    if not isinstance(artifact, dict):
        raise ValueError("artifact must be an object")
    if artifact.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    bound_id = artifact.get("bound_id")
    if not isinstance(bound_id, str) or not bound_id.startswith("ECBND1h") or len(bound_id) != 19:
        raise ValueError("bound_id must be ECBND1h followed by 12 hex digits")
    domain = artifact["domain"]
    if not isinstance(domain, dict):
        raise ValueError("domain must be an object")
    for key, want in (("problem", PROBLEM), ("family", FAMILY), ("target_kind", TARGET_KIND), ("unit", UNIT), ("tier", TIER)):
        if domain.get(key) != want:
            raise ValueError(f"domain.{key} is {domain.get(key)!r}; this objective is {want!r}")
    envelope = domain.get("envelope")
    if not isinstance(envelope, dict) or envelope.get("targets") != 1 or envelope.get("precomputation") != "none":
        raise ValueError("domain.envelope must be one cold target with no precomputation")
    for word in ("wall", "second", "time", "clock", "ns"):
        if word in str(domain.get("unit")).lower():
            raise ValueError("a bound is never a wall-clock figure")

    admissibility = artifact["admissibility"]
    if not isinstance(admissibility, dict) or admissibility.get("status") != "admissible":
        raise ValueError("the record is not admissible by its own account")

    fit = artifact["fit"]
    if not isinstance(fit, dict) or fit.get("size_parameter") != "r":
        raise ValueError("fit.size_parameter must be r")

    sizes = artifact["sizes"]
    if not isinstance(sizes, list) or not sizes:
        raise ValueError("sizes must be a non-empty list")
    weighted = 0.0
    runs_total = 0
    seen = set()
    for index, row in enumerate(sizes):
        if not isinstance(row, dict):
            raise ValueError(f"sizes[{index}] must be an object")
        slug = row.get("slug")
        if not isinstance(slug, str) or not slug or slug in seen:
            raise ValueError(f"sizes[{index}].slug must be a distinct non-empty string")
        seen.add(slug)
        bits = _int_like(row["field_bits"], f"sizes[{index}].field_bits")
        if bits <= 0 or bits > MAX_FIELD_BITS:
            raise ValueError(f"sizes[{index}] has a {bits}-bit field; the {TIER} tier allows at most {MAX_FIELD_BITS}")
        r = _int_like(row["r"], f"sizes[{index}].r")
        if r < 5:
            raise ValueError(f"sizes[{index}].r is too small to measure")
        automorphisms = _int_like(row["automorphisms_available"], f"sizes[{index}].automorphisms_available")
        if automorphisms < 1:
            raise ValueError(f"sizes[{index}].automorphisms_available must be positive")
        verified = _int_like(row["verified"], f"sizes[{index}].verified")
        runs = _int_like(row["runs"], f"sizes[{index}].runs")
        if verified != runs or verified <= 0:
            raise ValueError(f"sizes[{index}]: {verified} of {runs} runs verified; every measured run must verify")
        floor = (PI / (2.0 * automorphisms)) ** 0.5
        _close(_num(row["floor_s"], f"sizes[{index}].floor_s"), floor, f"sizes[{index}].floor_s")
        mean_gae = _num(row["mean_gae"], f"sizes[{index}].mean_gae")
        if mean_gae <= 0:
            raise ValueError(f"sizes[{index}].mean_gae must be positive")
        mean_s = mean_gae / (r ** 0.5)
        _close(_num(row["mean_s"], f"sizes[{index}].mean_s"), mean_s, f"sizes[{index}].mean_s")
        ratio = mean_s / floor
        _close(_num(row["ratio_to_floor"], f"sizes[{index}].ratio_to_floor"), ratio, f"sizes[{index}].ratio_to_floor")
        weighted += ratio * verified
        runs_total += verified

    pooled = weighted / runs_total
    constant = artifact["constant"]
    stated = _num(constant["ratio_to_floor"]["value"], "constant.ratio_to_floor.value")
    _close(stated, pooled, "constant.ratio_to_floor.value")
    ops = artifact["dimensions"]["ops"]
    if ops.get("known") is not True:
        raise ValueError("dimensions.ops must be known")
    _close(_num(ops["value"], "dimensions.ops.value"), pooled, "dimensions.ops.value")
    provenance = artifact["provenance"]
    if _int_like(provenance["verified"], "provenance.verified") != runs_total:
        raise ValueError("provenance.verified does not equal the sum over sizes")
    if not isinstance(provenance.get("sessions"), list) or not provenance["sessions"]:
        raise ValueError("provenance.sessions must name at least one session")
    for index, session in enumerate(provenance["sessions"]):
        if not isinstance(session, dict):
            raise ValueError(f"provenance.sessions[{index}] must be an object")
        for key in ("session_id", "records_sha256", "dir"):
            if not isinstance(session.get(key), str) or not session[key]:
                raise ValueError(f"provenance.sessions[{index}].{key} is missing")

    if pooled <= 0:
        raise ValueError("the pooled ratio to the floor must be positive")
    value = int(round(SCALE / pooled))
    method = artifact.get("method", {}).get("id") if isinstance(artifact.get("method"), dict) else None
    detail = (
        f"verified: {method or 'method'} at {pooled:.4f} x the generic floor over "
        f"{len(sizes)} size(s) and {runs_total} runs in the {FAMILY} {TIER} domain"
    )
    return value, detail
