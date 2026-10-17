"""Parse archived public inputs and check exact membership, never rank.

No network, height computation, independence test or lattice enumeration.
Only the two explicitly supported source equation formats are accepted.
"""
from fractions import Fraction
from pathlib import Path
import hashlib
import html
import json
import re


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path, count):
    text = html.unescape(re.sub(r"<[^>]+>", " ", path.read_text()))
    prefix = {30: r"y\s*2\s*\+\s*xy\s*=\s*x\s*3\s*-\s*(\d+)x\s*\+\s*(\d+)",
              31: r"y\s*2\s*\+\s*xy\s*\+\s*y\s*=\s*x\s*3\s*\+\s*x\s*2\s*-\s*(\d+)x\s*\+\s*(\d+)"}
    matches = re.findall(prefix[count], text)
    if len(matches) != 1:
        raise ValueError("Expected one equation in the explicitly supported source format")
    a4, a6 = matches[0]
    ainvs = [1, 0 if count == 30 else 1, 0 if count == 30 else 1, -int(a4), int(a6)]
    raw = re.findall(r"P\s*(\d+)\s*=\s*\[\s*([-\d/]+),\s*([-\d/]+)\s*\]", text)
    if [int(row[0]) for row in raw] != list(range(1, count + 1)):
        raise ValueError("Point indices/count are incomplete, duplicate or out of order")
    points = [(Fraction(x), Fraction(y)) for _, x, y in raw]
    a1, a2, a3, a4, a6 = ainvs
    b2, b4, b6 = a1*a1 + 4*a2, a1*a3 + 2*a4, a3*a3 + 4*a6
    b8 = a1*a1*a6 + 4*a2*a6 - a1*a3*a4 + a2*a3*a3 - a4*a4
    discriminant = -b2*b2*b8 - 8*b4**3 - 27*b6**2 + 9*b2*b4*b6
    if not discriminant:
        raise ValueError("Source equation is singular")
    if any(y*y+a1*x*y+a3*y != x*x*x+a2*x*x+a4*x+a6 for x,y in points):
        raise ValueError("A parsed point is not on the exact source equation")
    return dict(scope="Candidate point input; exact equation membership only",
                source_path=path.name, source_sha256=sha(path),
                ainvs=list(map(str, ainvs)), points=[[str(x),str(y)] for x,y in points],
                discriminant=str(discriminant), nonsingular=True,
                exact_membership_checks=len(points), membership_failures=0,
                independently_certified_rank=False, saturated_basis=False,
                gram_matrix_supplied=False, numerical_heights_recomputed=False)


def main():
    folder = Path(__file__).resolve().parent
    repo = next(p for p in folder.parents if (p / "AGENTS.md").is_file())
    archived = repo / "coordination/goals/GOAL-ECRANK-002/batches/BATCH-52b70c/tasks/TASK-20260905-cfce83/fetched/icarm_curve302.json"
    candidates = {count: parse(folder / f"rank-{count}-source.html", count) for count in (30,31)}
    old = json.loads(archived.read_text())
    new = candidates[31]
    if list(map(str,old["ainvs"])) != new["ainvs"]:
        raise ValueError("The two rank-31 source equations disagree")
    if [[str(Fraction(x)),str(Fraction(y))] for x,y in old["points"]] != new["points"]:
        raise ValueError("The two rank-31 source point lists disagree")
    for count, data in candidates.items():
        with (folder / f"candidate-{count}.json").open("x") as handle:
            json.dump(data, handle, indent=2); handle.write("\n")
    report = dict(scope="Source reconciliation and exact rational membership; no rank certification",
                  source_base_commit="fd49e52ff70a859a09febf52112f3cfae0ec9455",
                  prepared_point_counts=[30,31], exact_on_curve_checks=61,
                  rank31_archived_source=str(archived.relative_to(repo)),
                  rank31_archived_source_sha256=sha(archived),
                  rank31_cross_source_equation_and_points_equal=True,
                  prior_review_caveats=[
                      "The existing independence step uses a numerical regulator, not certified intervals.",
                      "The executor's supposed factor-10^10 regulator mismatch was corrected by both reviews.",
                      "No full Gram matrix, height-error certificate or saturated full MW basis is supplied here."],
                  original_d1_protocol_run=False, scientific_state_changed=False,
                  candidate_independence_verified_in_this_session=False)
    with (folder / "input-reconciliation.json").open("x") as handle:
        json.dump(report, handle, indent=2);handle.write("\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
