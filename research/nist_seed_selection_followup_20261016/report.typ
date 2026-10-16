#set page(paper: "a4", margin: (x: 18mm, y: 16mm))
#set text(size: 9pt)
#set par(justify: true)
#set heading(numbering: none)

= P-224 seed-selection follow-up

_16 October 2026 · Derived structural result · historical selection cause unresolved_

== Question and new result

Could the original generator have passed over P-224 seed blocks 777, 1485 and 5736 because it preferred the largest prime factor in the quadratic-twist order? The previous study left block 1485 unfactored after a 20-second cap. A new bounded PARI/GP attempt completed it. The four qualifying blocks now have largest twist-prime-factor sizes of *83, 122, 106 and 118 bits*, respectively; block 7026 is the published P-224 curve. Thus the published curve was not the maximum under this specific proposed rule. A threshold of 112 bits would admit both skipped block 1485 and P-224.

#image("p224_twist.svg", width: 100%)

== Exact calculation

Block 1485 in the stream initialized at Unix timestamp `891607927` has EC1 identity `EC1P224Cskip891607927i1485hb216c63c6aeb`. The earlier curve assessment fixes its field, coefficient, prime ordinary-group order and exact quadratic-twist order. The twist order factors as:

`3 × 31 × 103338691145424448535900484671 × 2805260028296929757374709219448951881`.

The two new factors have 97 and 122 bits. PARI/GP 2.17.3 `isprime` returned 1 for each. The adjacent `verify_twist_1485.py` multiplies all four factors to the exact twist order, checks the old source SHA-256, and rechecks the published P-224 comparator. Its output is `verification.json`. The chart source is `render_visuals.py`.

The first retry hit PARI's default 8 MB stack limit after 58.444 seconds. The second used `gp -q -s 134217728` and a 120-second process cap; it completed in 90.757 seconds. These are local bounded calculation times, not historical cost estimates.

== Interpretation

The P-224 result refutes a preference for the *largest twist prime factor* in that stream. It does not refute every possible twist predicate. The 192-bit ANSI controls already show skipped curves with larger twist factors than published curves. The P-256 pair points the other way: published P-256 has a 241-bit largest twist factor and its earlier candidate has 201 bits. One favorable pair does not establish a rule.

The first-qualifying-candidate rule fails for P-224 and P-256. Positive trace or group order below the field prime also fail to explain the skipped P-224 blocks; the published `prime239v2` curve contradicts a universal positive-trace rule. Modern primality checks establish that all four P-224 ordinary groups have prime order, but do not replay a 1997 implementation. Extra random-generator calls, a historical validation error, and an undocumented mathematical criterion remain open mechanisms.

Twist factor size is a structural diagnostic, not an ECDSA security rating. Exploiting a twist requires a protocol or arithmetic interface that processes unsuitable points. The recovered 20-byte blocks also do not reveal how many timestamps or separate program runs were tried.

== Sources and next evidence

#link("https://csrc.nist.gov/files/pubs/fips/186-2/final/docs/fips186-2.pdf")[FIPS 186-2 Appendix 6.4] specifies seed-to-curve generation and a suitable-order retry, but no complete acceptance trace. #link("https://saweis.net/posts/nist-curve-seed-origins.html")[Stephen Weis reproduces Solinas's 2015 correspondence], which names Bob Reiter as the original coder and says their archives were not found; this is retrospective testimony. #link("https://www.anthropic.com/research/ecdsa-curve-origins")[Anthropic] and #link("https://words.filippo.io/seeds-solved/")[Valsorda] give the 2026 seed-stream reconstruction and candidate ordinals. Exact earlier curve and twist inputs are under `research/nist_seed_selection_deep_20261016/` and `research/nist_seed_skipped_curves_20261016/`.

The best next evidence is the original program or call log. Otherwise, a candidate rule must be specified before testing held-out historical selections. This report changes no ECDLP attack or official research-state claim; the open obstruction remains `problems/nist-seed-selection-rule-unexplained.md`.
