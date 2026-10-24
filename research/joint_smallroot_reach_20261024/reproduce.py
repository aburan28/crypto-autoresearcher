#!/usr/bin/env python3
"""Reproduce the software audit and render its descriptive report.

No ECDLP experiment, root-recovery benchmark, or performance claim is run.
Artifacts and reports are write-once. Dependencies: pytest, sympy, matplotlib,
and typst; an optional --deps directory is prepended to Python's import path.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone


HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]


def save(path, content):
    with path.open("x",encoding="utf-8") as stream:
        stream.write(content)


def capture(name, command, directory, environment):
    start=datetime.now(timezone.utc).isoformat()
    result=subprocess.run(command,cwd=REPO,env=environment,text=True,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    save(directory/f"{name}.stdout.txt",result.stdout)
    save(directory/f"{name}.stderr.txt",result.stderr)
    return {"command":command,"started_utc":start,
            "finished_utc":datetime.now(timezone.utc).isoformat(),
            "exit_code":result.returncode}


def render(directory):
    data=json.loads((directory/"finite-audit.json").read_text())
    manifest=json.loads((directory/"manifest.json").read_text())
    table=[]
    for family in ("single_s3","joint_union_support"):
        for row in data[family]:
            table.append(f"| {family} | {row['multiplicity']} | {row['dimension']} | "
                         f"{row['equal_bound_volume_per_equation']} | "
                         f"{row['dense_matrix_entries']} |")
    source_commit=manifest["source_commit"]
    text=f"""# Joint small-root finite accounting audit

This is a descriptive software audit, not an ECDLP experiment or a scientific
state transition. It records exact determinant arithmetic and finite candidate
constructions. No root-recovery or complete IC improvement is established.

## Objective and current execution status

Original objective: establish the reach-cost tradeoff of joint-system small-root
decomposition and demonstrate a verified improvement over the current prime-field
IC baseline. That objective remains incomplete. This audit implements the
accounting prerequisite. Optimized external shifts, higher-rank GAPs, root
extraction, random-target relation yield/rank, and matched full-pipeline
measurements have not been completed.

No EXP/RUN identifier is minted for software checks. Prepared independent blind
review TASK-20261024-da3810 was not dispatched: its required input publication
was refused by automatic approval review. No independent attestation exists.
TASK-20261024-6c911a owns local archival. No hypothesis, goal, or leaderboard
status is changed. The software diagnostics are not an official evidence record.

## Inputs, provenance and commands

- Historical source: main `dcfdd16cdf7783a059ca1e6e4cc5efbf77434b7b`.
- Candidate source snapshot: `{source_commit}`; exact file hashes and dirty
  state are in [manifest.json](artifacts/manifest.json).
- Integer S3 coefficients a=2,b=3; joint xQ=5; coordinate order x1,x2,x3,x4,u,v.
- Exact determinant fixtures use p=101 and all column bounds 2. The joint
  fixture is an algebraic coefficient fixture, not an identified subgroup.
- Scope was fixed in [PROTOCOL.md](PROTOCOL.md) before successor diagnostics.
- Platform, dependency versions, argv, exit codes and source hashes are retained
  in the manifest. Tests and baseline output are captured verbatim beside it.

The historical command `tools/smallroot_reach.py --validate --m 4` reproduces
the hard-coded 0.840814 value and -0.0481 reported margin. This reproduces its
output, not a validated multivariate reach. Its extended-support function at
t_max=10 separately returns 0.8531320298632261, so neither the hard-coded
precision nor an asymptotic optimum follows from that finite call.

## Exact finite determinant accounting (derived)

For N triangular monic-pivot rows, each evaluating to a multiple of p^t,
write q for the sum of row modulus exponents and s_i for the column exponent
sums. Their scaled determinant is

    det(L) = p^q * product_i X_i^s_i.

The determinant-level target is p^(t*N). Thus the available budget is

    sum_i beta_i*s_i < t*N - q,   where X_i = p^beta_i.

LLL approximation and evaluation-norm losses make the usable finite budget
smaller. Independent short polynomials and successful root extraction are
additional obligations. These determinant statistics do not certify either.

For the t=1 S3 matrix, N=13, q=12 and (s_x,s_y,s_z)=(11,11,11).
Its exact determinant is 101^12 * 2^33. The available modulus exponent is 1;
the historical calculator instead places 12 on the right-hand side. The new
tests expand S3 independently in SymPy and compute actual integer determinants
for both the 13-column single and 31-column joint fixtures.

For the specified full-box shifts the derived equal-beta asymptote is
2/[n*d*(n+1)], with volume exponent 2/[d*(n+1)]. In one variable this is
1/d, explaining why asymptotic univariate calibration cannot distinguish the
two accounting formulas. This statement covers this explicit shift family;
it is not a bound on all small-root algorithms.

## Finite candidate data (exact counts)

Equal-bound volume per equation means sum(beta_i)/number_of_equations on the
equal-beta slice. Single and joint normalizations differ. A single scalar
does not certify arbitrary unequal leaf/internal bounds or validate a
comparison with the historical 8/9 model demand.

| Family | t | Rows/columns | Equal-bound volume per equation | Dense entry count |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(table)}

![Finite determinant statistics versus dimension](reach-cost.svg)

These are deterministic structural counts, with one exact construction per
cell and no statistical uncertainty. Dense entry counts are hypothetical
square-matrix storage proxies, not measured RAM or runtime. Large matrices
are counted without being materialized. Actual lattice reduction and root
extraction have not been timed. All displayed bounds omit LLL/norm losses.

The joint candidate uses products of all three S3 equations. Its column set
is the t-fold Minkowski sum of their support union. Each column receives the
largest total power whose shifted product stays within that set. Distinct
monic pivots establish row independence for this constructed lattice. This
does not establish globally optimal shifts or algebraic independence after LLL.

A second explicit total-degree candidate is recorded in finite-audit.json.
Its exact counts use pairwise-disjoint leading monomials and are checked
against independent direct monomial enumeration at t=1 and t=2. They are
another construction, not an upper bound on the possible joint optimum.

## Software checks and failures

The captured pytest output reports 23 passed tests (ten historical and thirteen
successor test cases). They check symbolic S3 coefficients, exact determinants,
finite full-box counts, the univariate asymptote, divisibility on a public toy
elliptic addition, and joint total-degree counts. Passing historical tests does
not validate their reach interpretation.

Earlier setup failures are retained in initial-attempts.json. The first pytest
attempt lacked the sparse orchestration module; materializing that tracked
directory resolved the import, with no test disabled. The first git add omitted
--sparse and staged nothing; the explicit scoped retry succeeded. A direct
network probe without network permission could not reach the proxy; the
network-enabled read succeeded. Automatic review rejected the GitHub push as
unauthorized external publication, and it was not bypassed. A read of the Ryan
artifact page returned HTTP 403. These are operational observations, not
mathematical evidence against the lead.

## Interpretation, limits and next action

Interpretation: the historical near-threshold argument needs reconciliation
before selecting experiments from its quoted 0.0481 gap. The successor supplies
checkable finite budgets and a joint construction, with no claim of an IC gain.

The missing next objects are an independently reviewed normalization and an
applicable optimized joint shift construction, followed by verified extraction
of actual bounded roots. The external AsymptoticBounds README and Variant I/II
source were inspected; they require SageMath. They were not executed or proved
applicable. No external-tool superiority claim is made. Higher-rank GAPs remain
unimplemented, and no random-target or complete DLP comparison was attempted.

See the [named obstruction](../../problems/joint-smallroot-reach-baseline-and-oracle-unverified.md)
for acceptance conditions. A useful negative outcome for these finite candidates
does not close the family. Publication authorization, independent review, and
an executable oracle are still required before the user's full goal can be met.

Canonical graph check: the earlier atlas snapshot and closure report are frozen
historical views and were not rewritten. The current lead links this additive
audit; its disposition remains open_next_step. This report adds its own graph.
"""
    save(HERE/"report.md",text)
    os.environ.setdefault("MPLCONFIGDIR",str(directory/"matplotlib-config"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes=plt.subplots(1,2,figsize=(10,3.5),sharey=True)
    for ax,family,title in zip(axes,("single_s3","joint_union_support"),
                               ("Single S3: one equation","Joint S3 tree: three equations")):
        rows=data[family]
        xs=[r["dimension"] for r in rows]
        ys=[float(Fraction(r["equal_bound_volume_per_equation"])) for r in rows]
        ax.plot(xs,ys,"o-",color="#146b68")
        for x,y,row in zip(xs,ys,rows):
            ax.annotate(f"t={row['multiplicity']}",(x,y),xytext=(3,6),textcoords="offset points",fontsize=8)
        ax.set_xscale("log")
        ax.set_xlabel("Lattice rows / columns (log scale)")
        ax.set_title(title)
        ax.grid(alpha=.2)
        ax.set_ylim(0,.29)
    axes[0].set_ylabel("Equal-bound volume exponent per equation")
    fig.suptitle("Finite determinant statistics; LLL and root extraction excluded",fontsize=11)
    fig.tight_layout()
    fig.savefig(HERE/"reach-cost.svg")
    plt.close(fig)
    typst_source="""#set page(paper: "a4", margin: 19mm)
#set text(size: 10pt)
#set heading(numbering: "1.")
= Joint small-root finite accounting audit
Software diagnostics, 2026-10-24. No ECDLP experiment or IC speedup is claimed.

== Objective and status
Establish the reach-cost tradeoff of joint-system small-root decomposition and
demonstrate a verified improvement over the prime-field IC baseline. This goal
remains incomplete. The delivered work is a finite accounting prerequisite.

== Exact accounting
For N triangular rows with modulus exponent sum q, each evaluating to a multiple
of p to the power t, the determinant-level available budget is t N minus q.
Column scaling consumes the sum of each coordinate exponent times its bound
exponent. LLL approximation and evaluation-norm factors further reduce the
finite budget. Independent short polynomials and root extraction remain separate.

The t=1 single S3 fixture has 13 rows, q=12 and coordinate sums (11,11,11).
Its determinant is exactly 101 to the power 12 times 2 to the power 33. The
available modulus exponent is 1. The historical calculator instead uses 12.
The univariate large-multiplicity calibration cannot expose this difference.

== Finite joint construction
The three equations are S3(x1,x2,u), S3(x3,x4,v), S3(u,v,xQ), with xQ fixed.
Products of all three inputs are used. The finite column set and distinct monic
pivots are checked. No globally optimal shift construction is asserted.

#image("reach-cost.svg", width: 100%)

Exact diagnostic counts: one construction per plotted cell; no random sample or
statistical interval. Joint t=1,2,3 dimensions are 31,382,2591 and normalized
equal-bound determinant statistics are 3/41,98/1039,640/5417. Dense entry counts
are structural proxies, not actual memory or total solver time. Large matrices
were counted, not reduced. Single and joint normalization differ.

== Checks and remaining obligations
23 software tests pass, including independently expanded S3 coefficients, exact
single/joint determinants, finite direct counts and toy root divisibility.
The ten historical tests remain unchanged. Details, exact argv, source hashes,
dependency versions, logs and rational values are in report.md and artifacts/.

No optimized external shifts, higher-rank GAP substitution, root extraction,
random-target relation yield/rank, or full IC comparison has been completed.
The earlier 0.8408 versus 8/9 argument requires reconciliation; the diagnostic
does not establish that the lead is impossible. Independent review task
TASK-20261024-da3810 is prepared but unexecuted. No independent attestation exists.

Automatic approval review rejected publication of the branch. Work is committed
locally; no PR is claimed. External artifact retrieval also encountered HTTP 403.
Those are operational limits, not mathematical conclusions. The next step is
publication authorization, independent budget review and an applicable executable
optimized joint construction. See the linked named problem in report.md.
"""
    save(HERE/"report.typ",typst_source)
    import typst
    typst.compile(str(HERE/"report.typ"),output=str(HERE/"report.pdf"))


def main():
    parser=argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--deps",type=Path)
    args=parser.parse_args()
    if args.deps:
        sys.path.insert(0,str(args.deps))
    artifacts=HERE/"artifacts"
    artifacts.mkdir(exist_ok=False)
    environment=os.environ.copy()
    if args.deps:
        environment["PYTHONPATH"]=str(args.deps)+os.pathsep+environment.get("PYTHONPATH","")
    commands={}
    commands["historical"]=capture("historical",[
        sys.executable,"tools/smallroot_reach.py","--validate","--m","4",
        "--out",str(artifacts/"historical.json")],artifacts,environment)
    commands["tests"]=capture("tests",[
        sys.executable,"-m","pytest","-q","tests/test_smallroot_reach.py",
        "tests/test_joint_smallroot_reach.py"],artifacts,environment)
    commands["finite_audit"]=capture("finite_audit",[
        sys.executable,"tools/joint_smallroot_reach.py","--out",
        str(artifacts/"finite-audit.json")],artifacts,environment)
    from sympy import Matrix
    sys.path.insert(0,str(REPO))
    from tools import joint_smallroot_reach as J
    matrices=[]
    for joint in (False,True):
        polys=J.joint_system() if joint else [J.s3()]
        r,columns,descriptors=(J.joint_lattice(polys,1) if joint else J.single_lattice(polys[0],1))
        bounds=[2]*len(columns[0])
        rows=J.coefficient_matrix(polys,1,columns,descriptors,101,bounds)
        actual=abs(int(Matrix(rows).det()))
        expected=J.predicted_determinant(r,101,bounds)
        matrices.append({"family":"joint" if joint else "single","p":101,
                         "bounds":bounds,"rows":rows,"columns":columns,
                         "actual_determinant":str(actual),
                         "predicted_determinant":str(expected),"equal":actual==expected})
    save(artifacts/"exact-matrices.json",json.dumps(matrices,indent=2)+"\n")
    files=["tools/smallroot_reach.py","tools/joint_smallroot_reach.py",
           "tests/test_smallroot_reach.py","tests/test_joint_smallroot_reach.py",
           str((HERE/"PROTOCOL.md").relative_to(REPO)),
           str(Path(__file__).resolve().relative_to(REPO))]
    manifest={"schema":"smallroot-software-audit-manifest-v1",
              "source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO,text=True).strip(),
              "dirty_state":subprocess.check_output(["git","status","--porcelain","--untracked-files=no"],cwd=REPO,text=True),
              "python":sys.version,"platform":platform.platform(),
              "dependencies":{name:importlib.metadata.version(name) for name in ("pytest","sympy","matplotlib","typst")},
              "source_sha256":{f:hashlib.sha256((REPO/f).read_bytes()).hexdigest() for f in files},
              "commands":commands,"independent_review_completed":False,
              "pipeline_improvement_demonstrated":False,
              "research_experiments_run":0}
    save(artifacts/"manifest.json",json.dumps(manifest,indent=2)+"\n")
    if any(c["exit_code"] for c in commands.values()) or any(not r["equal"] for r in matrices):
        raise SystemExit("Software check failed; artifacts retained; report not rendered.")
    render(artifacts)
    print(f"Report: {HERE/'report.md'}")
    print(f"PDF: {HERE/'report.pdf'}")


if __name__=="__main__":
    main()
