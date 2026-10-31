# Final fixed arithmetic checks and requested stopping point

User-directed closing pass, 28 October2026. Exactly one fresh PARI invocation covers all21 exact curves:10 publications,11 reconstructed omissions,six streams. No retuning or further predicate/class-group/isogeny rounds.

All63 curve-order certificates pass: original, opposite-b and nontrivial quadratic twist for every curve. Separate Python arithmetic verifies 63 point witnesses, exact factor-wise point orders and the unique possible multiple in the Hasse interval. This freshly certifies the supplied original and twist orders without a new SEA count. PARI rigorously rechecks the field/order/factor primalities. Full points, commands, versions, stdout/stderr and immutable hashes are retained in runs/final-01, FROZEN.json and VERIFICATION.json.

| Fixed flag | Published true | Omitted true | Not applicable | Full-cohort separator |
|---|---:|---:|---:|---|
| field_prime | 10/10 | 11/11 | 0 | False |
| nonsingular | 10/10 | 11/11 | 0 | False |
| b_seed_relation | 10/10 | 11/11 | 0 | False |
| order_prime | 10/10 | 11/11 | 0 | False |
| order_certified | 10/10 | 11/11 | 0 | False |
| non_anomalous | 10/10 | 11/11 | 0 | False |
| order_bit_cap | 10/10 | 11/11 | 0 | False |
| MOV20_pass | 10/10 | 11/11 | 0 | False |
| MOV100_pass | 10/10 | 11/11 | 0 | False |
| b_lower | 5/10 | 6/11 | 0 | False |
| b_even | 6/10 | 6/11 | 0 | False |
| b_matches_p3_exponent | 9/10 | 8/11 | 4 | False |
| opposite_b_order_prime | 2/10 | 3/11 | 0 | False |
| opposite_b_same_order | 1/10 | 3/11 | 0 | False |
| quadratic_twist_order_prime | 1/10 | 0/11 | 0 | False |
| twist_largest_prime_MOV20_pass | 10/10 | 11/11 | 0 | False |
| twist_largest_prime_MOV100_pass | 10/10 | 11/11 | 0 | False |

There are 0 perfect separators among these fixed flags, including their complements. No combinations were searched. The p=3mod4 exponent-root flag is explicitly not applicable to the four224-bit rows; model/root conventions are not intrinsic curve properties. Both b roots are prime-order isomorphic models in that field; elsewhere the opposite-b model has the nontrivial quadratic-twist order. The separate nonsquare-twist check uses the first integer nonsquare d>=2, with coefficients a*d^2,b*d^3.

The25 same-field twist-factor comparisons contain both directions: an omission can have either a larger or a smaller largest twist prime than a publication. This prevents a uniform monotone twist-strength cutoff from separating the cohort. No cutoff was fitted. Two exact counterexamples:

* {'omitted': 'skip-863711343-36', 'published': 'prime239v1', 'field_bits': 239, 'sign_omitted_minus_published': 1, 'omitted_largest_bits': 138, 'published_largest_bits': 86}
* {'omitted': 'skip-863711343-36', 'published': 'prime239v2', 'field_bits': 239, 'sign_omitted_minus_published': -1, 'omitted_largest_bits': 138, 'published_largest_bits': 147}

MOV bounds20 and100 were fixed before the run, checked in one modular-power pass per original order and largest twist prime. SEC1v2 AppendixB records that the historical bound20 was increased to100: https://www.secg.org/sec1-v2.pdf . A no-hit result proves only absence of embedding degrees in the stated range, not the exact embedding degree. Original ANSI PDF refresh returned502; existing source identities and factor records are pinned in INPUTS.json.

Controls use E/F101 with a=-3,b=6,N=109, an incorrect proposed N=107, a singular model and malformed point, low-embedding-degree positives and the anomalous equality detector. A control-only GP expression-precedence error was repaired before cohort execution and retained; the full cohort was run once with0 retries. No outcome-dependent code, cutoff or feature change followed the run.

## Closing conclusion

These specified arithmetic checks do not identify the historical selection rule. The available evidence cannot determine the original rule without the NIST/Certicom generator source, run logs or equivalent direct historical provenance. A finite collection of null arithmetic tests does not establish that the rule cannot depend on any arithmetic property.

The investigation loop stops here at the user's requested boundary. The original historical objective remains unresolved and will be paused, not labeled solved. No additional class-group, isogeny, predicate-library or historical-code rounds are scheduled. Reconstructed omissions remain distinct from documented original rejection events.
