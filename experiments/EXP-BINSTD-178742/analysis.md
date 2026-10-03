# Analysis — EXP-BINSTD-178742 Part 1 (TASK-20261001-1da6b9)

Review plan: `experiments/EXP-BINSTD-178742/review/review-plan.yaml`
(REVIEW-BINSTD-178742-20261001). Snapshot tip: `9e6aa7898`.

## Observation

- Two Part-1 scientific runs under `runs/`: R1 `RUN-BINSTD-372339`
  (`--run --execute-scoring`), R2 `RUN-BINSTD-668b84` (`--run --score-part1`).
  Manifests `completed_valid`; `certificate.kind=none`;
  `successor_contract_sha256` begins `ffacf110…`.
- Deployed census n∈{131,163,233,283,409,571}: measured
  ord_n(2) = {130,162,29,94,204,114}; stable-dimension sets match the
  frozen structural_certificate tables; both routes agree; `order_verified`.
- Eleven standardized rows: six primary (K-163..K-571, ECC2K-130) verdict
  **TRUE** with `r_mod_k=1`; five c2pnb rows **NOT COMPUTED** (`IMP-X962`).
  No FALSE; SR-4 not fired.
- IR-12: `stage1/ir12-determinism.yaml` reports census and k-row JSON
  byte-identical across R1/R2.
- Part 2: `part2_status.json` records `IMP-PART2-CURVE-LIBS-1` (stdlib-only
  typed tree cannot build Koblitz cells). Gate/relation/rank files present
  as explicit `NOT COMPUTED` stubs — not fabricated passes.
- AUXIN-339fb0 skipped this tick: `IMP-ADMISSION-TOOLS-1` (ecm/cypari2
  missing; not provisioned during /run).
- No Bedrock. No break / exponent / O-SUPPORT / n≥131 attack text in manifests.

## Comparison

- Blind re-derivation (from quantity statement + public design r strings;
  **not** from `part1_surface.py` / run JSON):
  - ord_131(2) by prime-divisor test on 130 = 2·5·13 → **130** (matches).
  - ord_233(2) by prime-divisor test on 232 = 2³·29 → **29** (matches).
  - ECC2K-130 r ≡ **1** (mod 131); K-163 r ≡ **1** (mod 163) (match).
- Success-criterion limbs: Part-1 census + primary k|r-1 limbs hold on
  this package. Part-2 limbs (G0–G4, CERT-*, ranks) **untested**.
  Full O-SUPPORT therefore unreachable.

## Inference

- Validity of the Part-1 run set is acceptable for a **refine** decision:
  schema, certificates, IR-12, claim boundary, and honest Part-2 impediment
  disclosure hold.
- H-BINSTD-ce4f38 Part-1 arithmetic limbs (deployed census + six primary
  k|r-1) are **observationally reproduced** at this instrument.
- H Part-2 (quotient/raw/ker-g ranks) is **not** supported or refuted —
  blocked by infrastructure/dependency, never negative math evidence.
- Preferred official transition: **refine**; H/EXP `approved` → `analyzed`;
  strength **preliminary**; no KN-FIND; next concrete action is a Part-2
  dependency amendment or stdlib toy-cell builder (see new IDEA filings).

## Limitation

- Part 2 entirely unexecuted (IMP-PART2-CURVE-LIBS-1).
- Five c2pnb rows remain NOT COMPUTED (IMP-X962).
- Toy degrees not included on this /run (`include_toys=false`).
- Coordinator-direct review (PD-1) and same-session producer (PD-2).
- No O-SUPPORT; no break; no exponent; no n=131 attack transfer.
