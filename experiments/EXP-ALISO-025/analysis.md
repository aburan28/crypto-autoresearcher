# Analysis — Autolab isogeny: p1243_parity_repaired_kani_probe

## Observation
Historical Autolab experiment with retained result artifacts.

Source excerpt / raw summary:

```
{
  "all_pass": true,
  "artifact_hashes": {
    "contract_sha256": "0b2065cea36f78f81338182bf0f41f0138280cbdf9d16306be1fa1d292e785fb",
    "source_sha256": "edc6c59d66820408d51ac5a5e7c35d795cd9f0eff0c2bed3a3576ce5960cffe7"
  },
  "claim_status": "ARITHMETIC LEMMA EVIDENCE / HEURISTIC SMOOTH SEARCH / NO KANI OR TRANSVERSE-ISOGENY IMPLEMENTATION",
  "complexity_claim": {
    "candidate_expensive_term": "T*u*B^4",
    "candidate_guess_term": "T*s_c*sqrt(c*d/m)",
    "source_expensive_term": "T*u*B^8",
    "source_guess_term": "T*sqrt(d/m)"
  },
  "families": [
    {
      "L": 740,
      "L_representation": [
        26,
        8
      ],
      "allowed_smooth_primes": [
        5,
        7,
        11,
        13,
        17,
        19,
        23,
        29,
        31,
        37,
        41,
        43,
        47,
        53,
        59,
        61
      ],
      "c3_repair": 3,
 
... [truncated]
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
