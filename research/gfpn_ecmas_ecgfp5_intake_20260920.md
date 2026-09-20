# GFPN intake: EcGFp5 / EcMasFp5 security and index-calculus program (2026-09-20)

User-supplied idea batch for the Goldilocks-quintic curves EcGFp5 (Pornin
ePrint 2022/274) and EcMasFp5 (HackMD design note). Area token **GFPN**.

## Sources that must be frozen before a number is quoted

| Source | Status | What may be quoted once frozen |
| --- | --- | --- |
| Pornin, *EcGFp5: a Specialized Elliptic Curve*, ePrint 2022/274 | **Frozen** `inputs/PORNIN-2022-274-ECGFP5/` (`SRC-PORNIN-2022-274-ECGFP5`, `KN-LIT-8aff72`) | Field `p = 2^64-2^32+1`, extension degree 5, Gaudry-attack lower bound **≥ 2^142**, Diem/Gaudry citations, curve construction |
| EcMasFp5 HackMD design note | **Frozen** `inputs/ECMASFP5-HACKMD-2025/` (`SRC-ECMASFP5-HACKMD-2025`, `KN-LIT-47d541`) | Equation `y^2 = x^3 + 3x + 8z^4`, modulus `z^5-3`, self-reported **twist security 101.93 bits**, inherited ~142-bit field claim |
| Diem, *The GHS attack in odd characteristic* (Pornin [6]) | **Not yet frozen** | Exact statement of the odd-char GHS cover-genus bound; whether "n ≥ 11" (as some notes paraphrase) covers n = 5 |
| Gaudry, index calculus for small-dimension AV (Pornin [8]) | **Not yet frozen** | PDP / decomposition cost model used to derive the ≥2^142 bound |
| Joux–Vitse / Granger oracle-assisted static DH | **Not yet frozen** | Query and work figures for the OA-SDH setting at these parameters |
| SafeCurves criteria + twist-order recipes | Partially in-repo under SCURVE | Certificate format for a SafeCurves-style audit |
| Trimoska EC-Index-Calculus / WDSat future-work statements | Partially in-repo under ICPERF | Exact wording of "WDSat + torsion symmetrization + coset typing" future work |
| Galbraith "larger group actions" slides / notes | Pointer only until frozen | Context for the translation-descent lemma |

**Rule.** Until a row is frozen and read, any figure attributed to it in conversation
is `provenance: recalled` and supports nothing (AGENTS.md rule 9). Intake
analysis figures that are not in a frozen source are labeled **provisional**
below and in the IDEA records; they are hypotheses to measure, not evidence.

## Opened proposals (tokens fixed by user)

| Priority | IDEA | One-line claim |
| --- | --- | --- |
| high | `IDEA-20260920-a639a1` | Measure D and per-PDP cost per symmetrization arm at n = 5 on a toy-p ladder; locate the Gaudry/PDP band at the real p = 2^64 against the design notes' ≥2^142. Provisional intake reading: EcMasFp5 is the stronger curve (S_5 only); EcGFp5's 2-torsion is what drops it into the band — to be confirmed or falsified by measurement. |
| high | `IDEA-20260920-73dc35` | Cost oracle-assisted static DH on both curves; neither design note analyses it. Provisional intake band ~2^64 queries / ~2^85–2^93 work pending JV/Granger freeze and re-derivation. |
| medium | `IDEA-20260920-10547b` | Odd-char GHS cover genus for both curves and their isogeny class; check whether Diem's bound the notes rely on actually covers n = 5. |
| medium | `IDEA-20260920-63a902` | SafeCurves-style certificate audit; EcMasFp5 self-reports 101.93-bit twist security (`KN-LIT-47d541`). |
| low | `IDEA-20260920-9e672a` | JV (n−1) full-DLP variant: closed by arithmetic on these parameters — file the closure so no budget is spent there. |
| low (theory) | `IDEA-20260920-0490f5` | Descent lemma for Galbraith's "larger group actions": a translation descends through the degree-2 negation quotient iff 2T = O. Proof in `research/THM_QUOTIENT_DESCENT1.md`; Lean stub for minting. |
| low | `IDEA-20260920-18dc28` | Trimoska's stated future work: WDSat + torsion symmetrization + coset typing combined; expected constant-factor only. |

## Deliberately not opened (and why)

| Avenue | Why not opened here |
| --- | --- |
| Coset bases | Already opened as `IDEA-20260918-c05e71` (SEMBIN in-regime successor). Duplicating under GFPN would split the measurement. |
| Torsion quotients | Already opened as `IDEA-20260918-7a11c2`. GFPN may *use* that instrument later; it does not re-propose it. |
| Sarkar–Singh | Already opened as `IDEA-20260918-5a9a51` (2026-09-18 Galbraith thread). Source ePrint 2015/179 still to freeze there. |
| Linear-invariance pruning | Already treated in `research/THM_FALLDEG_INVARIANTS1.md` §3.1; not a GFPN-specific proposal. |
| GRUMPY / FROB / QSP | Separate ECC areas with their own goals; these curves are not their objects. |
| Finite-field-DLP analogy | Heuristic transfer without a frozen correspondence or null-object plan; premature as an experiment. |

## Required harness edit

`GFPN` added to `ecc_areas` in `orchestration/research-priority.yaml` so
`GOAL-GFPN-*` / `RQ-GFPN-*` / `IDEA-*-*` under this area inherit ECC-first
unlimited budget and open-idea design ranking.

## Unified patch (priority file)

```yaml
  - GFPN      # EcGFp5 (Pornin ePrint 2022/274) and EcMasFp5 (HackMD) over
              # F_{p^5}, p = 2^64-2^32+1: Gaudry/PDP band, oracle-assisted
              # static DH, odd-char GHS at n = 5, SafeCurves-style audit, and
              # related closures. Added 2026-09-20 on user intake of seven
              # proposals (IDEA-20260920-{a639a1,73dc35,10547b,63a902,9e672a,
              # 0490f5,18dc28}). ECC because both targets are named elliptic
              # curves; letters-only token because RQ/H/EXP reject digits.
```
