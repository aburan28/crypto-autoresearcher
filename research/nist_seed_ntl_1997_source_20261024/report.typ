#set page(paper:"a4",margin:(x:17mm,y:16mm))
#set text(font:"Helvetica",size:10pt)
#set par(justify:true)

= A period NTL source check narrows the RNG explanation

*24 October 2026 UTC. Retrospective primary-source audit; no NTL executable run.*

Four 1997 Internet Archive payloads match their exact CDX digests. The March and August source snapshots contain identical normalized bodies for the default prime-test and modular-square-root routines. A May 10 homepage already advertises NTL 1.5: the August capture is not its release date and does not establish the exact bytes present in May.

== One higher-level call has a different literal prefix

NTL's default #raw("ProbPrime(n)") first chooses one small random base, then ten full-size bases. With 26-bit limbs, each full-size base consumes one more limb draw than the input occupies. Each draw advances the modular RNG at least once; internal rejection can add advances.

#align(center)[
  *192-bit input:* 1 + 10 × 9 = *at least 91 advances* \
  *239-bit input:* 1 + 10 × 11 = *at least 111 advances*
]

#image("call_bounds.svg",width:100%)

_Source-derived bounds for twelve exact inputs: p and n on six May curves. Both arguments agree within each curve. These are recurrence advances, not running times or final-state measurements. Data: analysis.json; separate static/integer replay: verification.json; editable graph: render.py._

The earlier configured FreeLIP replay reproduced the six published Gx values after seven advances supplied by raw eight-base primality calls. NTL's higher-level default has a different base-selection path. Its source-derived lower bound cannot describe a literal seven-advance call. This calculation alone makes no claim about final-state equivalence across arbitrary call sequences or periods.

#image("inference.svg",width:100%)

The modular RNG used by NTL/FreeLIP is separate from the clock-seeded lrand48 stream that supplied curve seeds. Explaining skipped seed windows through another routine requires an original caller that connects those streams. Neither archive supplies that attribution or a rejection log.

#pagebreak()

== What the acquired source establishes

The March 1 archive predates the May seed inputs. Its relevant source bodies agree, after whitespace and comment removal, with the August 1 NTL 1.5 capture. The May homepage advertises that version before the seed timestamps. Capture dates bound the archival objects; they do not identify the library installed in the original curve generator.

#table(columns:(1.2fr,1.5fr,1fr),inset:6pt,align:left,
  [*Object*],[*Capture UTC*],[*Bytes*],
  [March source],[1997-03-01 12:25:40],[335,767],
  [August 1.5 source],[1997-08-01 21:44:29],[446,513],
  [May homepage],[1997-05-10 21:44:00],[1,915],
  [March tour],[1997-03-01 12:24:59],[23,563],
)

Every payload matches its CDX SHA-1 base32 digest. The machine-readable analysis also records SHA-256, URLs, source-file hashes, function fingerprints and archive inventories. This guards the source comparison against a substituted nearby snapshot. Raw source archives remain externally retrievable and are not redistributed with this report.

== A randomized square root is another workflow detail

Both snapshots implement a randomized Cipolla-style square root using trial values from #raw("RandomBnd"). The header assumes an odd prime modulus and an input that is a square. Correct calls can consume a variable number of modular RNG draws. We have no evidence that the original generator made a particular such call, violated the precondition, or skipped a named curve because of it.

Caller-selected trial counts, other APIs, other initialization, restored state, alternate limb widths and other libraries remain possible. A point-counter stopping rule or error also remains possible. The prior raw FreeLIP check accepts all 21 named prime orders, and the present source audit supplies no mathematical rejection property. The 1997 draft's fifty-test requirement also prevents equating the earlier eight-base reconstruction with its mandatory check.

== Evidence, reproduction and limits

The source extraction is retrospective: the functions were read before SCOPE.md was written. The separate verifier checks the four payload bindings, both function comparisons and all twelve integer bounds. It is a same-session static replay, not an independent research-state review. There is no NTL binary run, original point counter, historical build configuration, runtime measurement or measured final RNG state in this audit.

Full curve UIDs, exact p,n, source provenance, commands and all digests are in report.md and analysis.json. Reproduction: download the four pinned archive objects, then run analyze.py and verify.py into fresh output records; render with render.py, Graphviz and Typst. Both PDF pages were visually inspected.

The historical-selection problem remains open. A dated caller and candidate trace must reproduce the published seed ordinals and rejected decisions. A proposed mathematical explanation must give a subgroup advantage and an independent prediction. This source check changes no ECDLP frontier or scientific status.

#set par(justify:false)
*Primary sources:* archived cs.wisc.edu/~shoup/ntl March source, August ntl-1.5 source, May homepage and March tour; exact archive URLs and raw-payload digests in analysis.json. *Prior result:* ../nist_seed_freelip_prefix_20261024/report.md. *Open problem:* ../../problems/nist-seed-selection-rule-unexplained.md. The secondary LLFourn/secg-curves report supplied the archive lead; its other conclusions are not adopted here.
