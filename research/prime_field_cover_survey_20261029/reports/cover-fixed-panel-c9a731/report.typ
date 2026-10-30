#set page(paper:"a4",margin:16mm)
#set text(size:9.5pt)
= Common-atom shifted-cover survey
Observations only. One physical complete admissibility survey; relation-collection attempts: zero. No performance claim or scientific-state transition is made.

Run #raw("cover-fixed-panel-c9a731"). The original two E curves and sixteen-atom bases remain fixed: p=4099,a=2,b=13,r=4021,P=(0,264), and b=16,r=4111,P=(0,4). For C_h: y²=f(x²+h), an atom (u,y) lifts exactly when u-h is square or zero. Every h=0 through4098 is retained; singular f(h)=0 is excluded from admissibility. All64 original public sources are assessed without selecting by relation yield. h=0 is the historical positive control.

#table(columns:(auto,auto,auto,auto,auto,auto),inset:4pt,
[b],[frames],[eligible],[nonzero eligible],[singular],[source points with lifts],
[13],[4099],[1],[0],[0],[30],
[16],[4099],[1],[0],[0],[34],
)
- b=13: eligible h=[0].
- b=16: eligible h=[0].

Exploratory subset readout from the retained masks: the best nonzero shift covers15/16 atoms for b=13 (h=3437), and14/16 for b=16 (h=3279,3343,3437,3769). These are all coverage-maximizing ties; no relation yield was measured or used to choose them. A same-subset h=0 versus h collector comparison remains unrun.

#image("admissibility.svg",width:100%)
Histogram counts are derived by counting recorded membership bits. Zero means no observed shift in that exact bin; no broader curve-population model or interval is implied. Source-point counts include a zero lift once and are not signed deck-lift multiplicities.

Panel complete: True; unknown fixtures: 0. All8198 coefficient/membership rows passed a full roots-set reference and128 source points were checked by separate arithmetic, including curve-order recounts. The reference uses polynomial convolution for coefficients. It is an implementation cross-check, not independent scientific review. Two survey cells and two reference-method cells share one physical process; duplicate object counts are not added.

== Resources and source boundary
Exit 0; timeout False; source unchanged True. User CPU 2.547s, system CPU 2.245s, wall 4.982s, peak RSS 61276160 bytes. Host AMD EPYC 9V74 80-Core Processor; wall_valid=false. Explicit membership counters omit helper primality guards, coefficient arithmetic, reference work and complete S.
- b=13: 327920 explicit membership powers; 521 setup group calls.
- b=16: 327920 explicit membership powers; 521 setup group calls.

Source commit #raw("0226ab37808d23c390f4316485ddf92c8206c5da"). Protocol canonical SHA256 #raw("f6a5dad9a5801bcb44f6a8c171f22bcce60f3031197d1251dde191dafc5c8e8d"). The committed protocol/release, input/interpreter/source locks, actual S3 gate, owner/PIDs, raw masks/coefficients, source points, phase records and export are beside the run. Lossless compression binds original bytes in archive-encoding.json. Data were published before this report.

== Follow-through and limits
This complete finite survey determines common-atom frame admissibility only on the two exact bases. An admissible shifted frame still needs a separately frozen collector with unchanged E/base/log columns/source schedule, corrected x⁴ and auxiliary terms, pole/residual/sign checks and full charged cost. A finite absence of a nonzero common-atom shift says nothing about declared subsets, other bases, other covers or function spaces. Natural-target recovery and partial-column cancellation remain separate tests.

Sources: shifted-covers.md (derived quotient identities), original Prym Context and fixed fixtures, cover-survey literature.md, PKM2016 sections3.1–3.2 (retrieved primary, solver/linear-algebra costs remain charged). Full EC1/fixture identities remain in raw cells and inputs. Historical graphs remain unchanged; this new graph covers only this survey. No isogeny, Jacobian or subgroup-eigenvalue certificate is asserted.
