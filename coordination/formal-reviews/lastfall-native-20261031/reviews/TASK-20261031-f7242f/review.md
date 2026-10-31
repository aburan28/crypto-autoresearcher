# TASK-20261031-f7242f — source correspondence joint

**Verdict: holds, for the pinned conditional mathematical claim.** Caminata–Gorla Definition 1.5 (printed page 6), Definitions 2.5–2.6 (page 9), and Theorem 2.8 with its proof (pages 9–10) give the target's closed spaces, individual fall degree, fall predicate, and equality of the last fall degree with the greatest fall degree. The target states finiteness of `d_F` explicitly; the paper states it immediately after Definition 1.5 as a consequence of a Gröbner basis, then invokes it inside Theorem 2.8's proof. This is a scoped strengthening of the assumptions, not an omitted condition.

## Exact inputs and boundary

- Handoff: `adb26ef1295b2d97d6b8328875670c866e602377:coordination/formal-reviews/lastfall-native-20261031/handoffs/TASK-20261031-f7242f.yaml`.
- Target and research note: `5c405f05539649cffb7f796ac586db65cdde1661:formal/targets/lastfall-is-max-degree-fall.yaml` and `:research/THM_FALLDEG_INVARIANTS1.md`.
- Primary source: Caminata and Gorla, *Solving degree, last fall degree, and related invariants*, arXiv:2112.05579v2, https://arxiv.org/pdf/2112.05579v2. PDF SHA256 and all input hashes are in `raw/input-hashes.txt`.
- This joint compares mathematical source and pinned target prose. The named Lean declaration, its elaborated type, proof, source coverage, axioms, and hosted verification are assigned to TASK-20261031-43dc46 and were not read or run here. The finite-profile blind derivation is assigned to TASK-20261031-9a6bc2.

## Clause-by-clause correspondence

| Target clause | Primary-source location | Finding |
| --- | --- | --- |
| Field `k`, polynomial ring `k[x_1,...,x_n]`, system `F`, ideal `(F)` | §1 opening, printed page 2 | Matches. The paper writes a finite listed system `F={f_1,...,f_r}`; the target allows a subset. Its explicit finite `d_F` premise and the direct proof below make the equality valid for an arbitrary subset as well. |
| `V_{F,i}` least vector space containing `F ∩ R_{<=i}` and closed under admissible multiplication | Definition 1.5, page 6 | Matches both closure clauses. The paper also defines `V_{F,∞}` and `V_{F,-1}`; neither is used by the finite conditional equality. |
| `d_F=min{d: every f in (F) lies in V_{F,max(d,deg f)}}` | Definition 1.5, page 6 | Matches the finite branch of the paper's `N ∪ {∞}` definition. The target assumes that branch exists. |
| `d_f=min{d:f∈V_{F,d}}`, `d_f≥deg f`, and fall iff `d_f>deg f` | Definitions 2.5–2.6, page 9 | Matches. The fall quantifier is over `(F)`, not just the original generator set. |
| Nonempty fall set and finite `d_F` imply `d_F=max{d_f: f∈(F), d_f>deg f}` | Theorem 2.8 and proof, pages 9–10 | Matches. The paper's theorem states the fall premise; its proof uses finiteness of `d_F`, established in the preceding prose. |
| Finite measured Macaulay profile needs the `V_{F,i}` bridge and a later-fall cutoff for a global maximum | Definition 1.5 discussion and equation (1), page 6; target note | Faithful as a limitation. The paper gives `V_{F,d}=rowsp(M_d)` for its iteratively processed matrix with degree-compatible order, citing a separate proof. A generic finite rank profile is not itself the global theorem. |

The paper's proof starts its first inequality with “f in F” on page 9, while its displayed supremum and theorem use `f in (F)`. Applying that step to arbitrary `f in (F)` is necessary and follows from the same definitions; `raw/edge-case-derivation.md` gives both inequalities without that wording slip. This does not change the published theorem's quantified claim.

## Controls and direct derivation

- **Empty `F`:** ideal and every finite `V_{F,i}` are zero. With the target's natural degree convention for zero, no fall exists; the theorem's fall premise is false. The paper does not spell out the empty-system convention.
- **`F={x}`:** every nonzero ideal member `xq` enters at its own degree, so no fall exists and `d_F=0`; the fall premise is false. This also accords with Lemma 2.7 on page 9.
- **Actual fall:** for `F={x²,x²+x}` in `k[x]`, `V_1=0`, while `x=(x²+x)-x²∈V_2`, so `d_x=2>1`. Every ideal member enters by `max(2,deg f)` and `d_F=2`, giving a nonvacuous equality in every characteristic.

The general argument in `raw/edge-case-derivation.md` shows that finite `d_F` bounds every fall degree; nonemptiness gives a maximum; and membership at each `d_f` then makes that maximum admissible in the definition of `d_F`. It also explains why the paper's finite-system syntax does not obstruct the explicitly conditional arbitrary-subset target.

## Unresolved obligations and scope

The actual Lean declaration must be checked independently for its quantifiers, treatment of zero, construction and monotonicity of `V_{F,i}`, finiteness and fall premises, and axioms. No machine-verification verdict is issued by this joint. A measured matrix profile still requires a checked equality to closed `V_{F,i}` at every claimed degree and a bound excluding later falls before identifying its observed maximum with global `d_F`.

**Raw checks:** `raw/input-hashes.txt` and `raw/edge-case-derivation.md`. No scientific trial, cloud job, Lean build, Cargo build, or instance was used.
