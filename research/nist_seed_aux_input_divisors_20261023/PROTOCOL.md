# Auxiliary-input divisor opportunity screen

Frozen 2026-10-23 UTC before computing this study's divisor metrics. This is a retrospective structural screen of the nineteen same-field published and omitted prime-order curves, not an ordinary ECDLP attack or a historical 1997 criterion.

## Source and mechanism

Use the eleven omitted and eight same-field published curve EC1 UIDs and certified orders in `research/nist_seed_skipped_curves_20261016/{assessed,traits}.json`. Read the complete, previously verified factorizations of each `n-1` and `n+1` from `research/nist_seed_order_certificate_20261023/runs/certificate-20261023T1747Z/`. Require its `complete.ok` marker and `verification.json` to bind 38 verified rows. Pin input file hashes. Check every factor product against `n±1`; stop on a mismatch. Do not refactor.

Cheon's auxiliary-input algorithm (Eurocrypt 2006; Journal of Cryptology 2010) has an `n-1` route when the attacker is supplied `G`, `[x]G`, and `[x^d]G` for a divisor `d | n-1`, and an `n+1` route requiring a much longer sequence of supplied powers through `[x^(2d)]G`. The output of this screen is only availability of divisor sizes. Ordinary ECDLP, ECDSA and ECDH do not supply these powers as part of their standard public inputs. The algorithm was published after the 1997–98 curve selection, so historical attribution would need separate evidence.

## Frozen metrics

For each curve and direction, enumerate all divisors from the certified factorization, with a fail-closed maximum of 2,000,000 divisors per integer. Record divisor count. For `n-1`, find the largest `d <= floor(sqrt(n))` and the exact gap ratio as rational `floor(sqrt(n))/d`. For `n+1`, find the largest `d <= floor(cuberoot(n))`, and separately the largest `d <= 1024` as a data-limited sensitivity case. The bound 1024 means that even this sensitivity case would require up to 2048 publicly supplied scalar powers; it is not an asserted protocol observation. Compute integer roots exactly. Use the largest-divisor result only as a necessary arithmetic opportunity, not an operation count or speedup claim.

Compare omitted and published rows only within the same prime field. For each metric report exact values, pairwise directions and counterexamples. A perfect label ordering is only a retrospective lead. Do not fit a threshold or claim a 1997 rule from these labels. If divisor enumeration is censored, report the affected rows and do not make a universal conclusion.

## Controls, limits and artifacts

Verify the exact-integer control `n=101`: divisors of `n-1=100` are `[1,2,4,5,10,20,25,50,100]`, so the `sqrt(n)` bound selects 10; divisors of `n+1=102` are `[1,2,3,6,17,34,51,102]`, so the `cuberoot(n)` bound selects 3. Verify these independently with a simple brute-force divisor loop. Reject an injected wrong factor or wrong group order. Bound the study to 19 curves, 38 factorizations and the stated divisor cap; no new search over group elements or scalar targets.

Retain exact script, JSON result, input hashes, a quantitative SVG comparison, an explanatory diagram with editable source, a dated Markdown report, and a visually inspected PDF. State that no graph of ordinary ECDLP attack cost changes because this screen provides no such cost or auxiliary-input access evidence.
