# Conservation and Specialization in Semaev-Based Index Calculus over Prime Fields

Manuscript draft. **Not submitted, not posted, and not cleared for either.**

- `paper.tex` — the manuscript (LaTeX, `article`; needs only `lmodern`,
  `amsmath/amssymb/amsthm`, `mathtools`, `booktabs`, `geometry`, `hyperref`).
  **This is the single source.** `arxiv/` stages it rather than copying it.
- `arxiv/` — the arXiv submission package: `make -f Makefile.arxiv` stages,
  compiles, guards and tarballs. See `arxiv/SUBMISSION.md` for the metadata and
  the three things that must happen before uploading.
- Verification code and artifacts: `../../experiments/EXP-SMON-e5cbe6/`
- Ledger: `H-SMON-db677d`, `EV-SMON-9c1c23`, `DEC-20260807-64df6a`,
  `CORR-20260807-652652`, `KN-FIND-a8990a`.

## What it says

1. **Theorem 3.4.** The Galois group of `S_m(t_1,…,t_{m-1},T)` over
   `K(t_1,…,t_{m-1})` is `(Z/2)^{m-2}` acting simply transitively, for every elliptic
   curve over every field in every characteristic. The splitting field is
   `K(E^{m-1}/Δ)` with `Δ` the diagonal inversion; the group is the deck group of the
   fibre product of `m-1` copies of `x : E → P¹`, modulo the diagonal. Arithmetic
   monodromy equals geometric monodromy.
2. **Theorem 4.2.** Over `F_q`, at every specialization outside an explicit degenerate
   locus of size `O_m(q^{m-2})`, `S_m(a,T)` is either totally split or a product of
   `2^{m-3}` irreducible quadratics — never a factor of degree `≥ 3`, never a mixed
   type — according as the `m-1` fibres of the `x`-map are simultaneously rational or
   not.
3. **Theorem 5.1.** The factor-base locus lies entirely inside the totally split locus,
   at every `m`.
4. **Proposition 6.1.** Conservation: mean decomposition yield is
   `binom(B+m-1,m)/N` for *every* factor base of size `B`.

Synthesis: generic-fibre arithmetic statistics and factor-base relation statistics are
different objects. Several proposed relation-rate levers are fixed either by
conservation or by complete splitting on the rational-point locus.

## What it does not say

No ECDLP speedup, no security reduction, no new hardness result, no change to any
complexity estimate. Section 5.1 explains at length why complete splitting is *not* an
algorithm — it solves for the last coordinate given the others, while relation search
does the opposite.

## One blocker, and one downgraded

1. **No peer review by a credentialed mathematician has been obtained.** An independent
   review pass (fresh context, no role in producing the proofs, tasked adversarially with
   finding a gap — full report at
   `experiments/_reviews/proofreview-20260807-followups.md`) read Lemma 2.3 and Lemma
   3.2 line by line, independently re-derived the characteristic-free invariant-theory
   facts Lemma 2.3 needs rather than trusting them, and separately verified Lemma 3.2's
   properness argument is insensitive to `E[2]`'s non-reducedness in characteristic 2. It
   passed both lemmas and Theorem 3.4 as stated in every characteristic, and found one
   real scope gap (Corollary 3.8's `m ≥ 4` case needed `char ≠ 2` stated on the corollary
   itself, not just in §5.2 three pages later) — now fixed in `paper.tex`. This is real,
   adversarial, independently-derived scrutiny, not a rubber stamp — but it is not peer
   review by a human expert in function fields or arithmetic geometry, and obtaining that
   remains the one real blocker before this manuscript's mathematics should be treated as
   settled.
2. **Novelty is not established** (though the check is now much better than it was).
   Three treatments that each set up the basic theory of `S_m` in detail were read in
   full text — Semaev arXiv:1504.01175, Kosters–Yeo arXiv:1503.08001, and
   Amadori–Pintore–Sala *Finite Fields Appl.* 51 (2018) — and none discusses the Galois
   group, splitting field, monodromy, or the factorization type of a specialized fibre.
   Section 9 says exactly that and invites pointers, rather than claiming priority.
   `eprint.iacr.org` was 403 from this environment, so Semaev 2004/031 was read only
   through those three; that changed no attribution, since Amadori–Pintore–Sala
   Theorem 2 restates its content with attribution.

## Reproducing the verification

```sh
cd experiments/EXP-SMON-e5cbe6/code
python3 verify.py --out ../runs/RUN-SMON-e5cbe6-002/raw-result.json   # ~70 s, no deps
```

Deterministic (seed `20260807`); the committed `RUN-SMON-e5cbe6-001/raw-result.json`
should be reproduced byte for byte. Content hashes are in that run's `manifest.yaml`.

## Building

Compiles clean with pdfLaTeX (TeX Live 2023): 15 pages, three passes, no errors,
no warnings, all fonts embedded Type 1.

```sh
cd arxiv && make -f Makefile.arxiv pdf
```
