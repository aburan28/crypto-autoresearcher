# Solver environment for RQ-SATIC-1ae57a (measured 2026-09-04)

Capability inventory taken on the machine hosting worktree
`brother-printer-id-b2a073`, so that cost and feasibility estimates in
`IDEA-*` records filed against `RQ-SATIC-1ae57a` rest on what is actually
installable rather than on assumption. **Nothing here is a result.**

## Present and usable today

| Tool     | Path                        | Role in this lane                       |
| -------- | --------------------------- | --------------------------------------- |
| `cadical`| `/opt/homebrew/bin/cadical` | Generic CDCL control, no XOR reasoning  |
| `kissat` | `/opt/homebrew/bin/kissat`  | Second generic CDCL control             |
| `sage`   | `/usr/local/bin/sage`       | Grobner (F4/F5 via Singular) baseline   |

`src/semaev_tree.py` already produces the descended systems, including
`gen_decomposable_R` (planted-satisfiable) and `make_V_subspace` (the
l-dimensional factor base). The missing pieces are a CNF-XOR encoder and the
solver bindings.

**Consequence:** an ablation or null-object experiment restricted to
`cadical` + `kissat` + Sage is runnable immediately with no new dependencies.

## Absent, and what that costs

| Tool | Status | Consequence |
| ---- | ------ | ----------- |
| CryptoMiniSat | no binary, no `pycryptosat` | Must be built |
| MiniSat, Glucose | no binaries | Must be built |
| `python-sat` / `pysat` | not installed | Encoder must emit DIMACS directly, or the package must be added |
| WDSat | not in this repo | Must be fetched and built; the one component with no packaged distribution |
| **Magma** | **not available** | **See below — this is the load-bearing gap** |

### The Magma gap is the one that constrains claims

The source's Gröbner baseline (`SRC-SATIC-TRIMOSKA-2019`, claim C6) is
**Magma's F4**. Magma is not available here. Any Gröbner baseline this program
runs is Sage/Singular — a *different implementation with different constants*.

A Sage-vs-solver ratio measured here is therefore **not comparable** to the
source's Magma-vs-WDSat ratio, and no record may present it as if it were. This
belongs in the interpretation limits of every idea that touches the baseline.

### CryptoMiniSat's branching-order patch is not upstream

Claim C2 — core-variable branching order recovering most of the speedup — was
obtained by the authors **patching CryptoMiniSat's source**. That patch is not
in upstream CMS. Any experiment depending on C2 must either budget for building
a patched CMS, or reach the same effect through a solver that already exposes
decision control (assumption ladders over the `ml` core variables, phase
saving, or a decision-order API), so the result does not hinge on one
unmaintained patch.

## Reading

Recorded because the `estimated_cost` field of an idea is a real commitment in
this program, and an estimate written without knowing that Magma is missing and
WDSat must be built from source is not an estimate.
