#set page(paper: "a4", margin: 18mm)
#set text(font: "Liberation Sans", size: 10pt)
#set heading(numbering: none)

= Native LastFall review: conditional theorem and finite-profile boundary

*Producer:* crypto-autoresearcher PR #2824 at `5c405f0`.
*Plan:* PR #2828, merged as `17225ce` before the three reviewer sessions.

The source and statement comparisons support the conditional LastFall theorem at
their stated scope. The blind reviewer derived a counterexample to treating a
truncated profile as a global last-fall-degree certificate. Exact-head hosted run `41191503149` passed the named target build and transitive axiom audit. The conditional theorem is validated at its stated scope; the stronger finite-profile exactness inference needs revision.

#figure(image("claim-boundary.svg", width: 100%), caption: [Three independent joints and the remaining measurement bridge.])

== What each joint checked

- *TASK-20261031-f7242f, source:* Definition 1.5 and Theorem 2.8 match the
  target's conditional claim. Empty and no-fall controls fail the fall premise;
  `F={x²,x²+x}` is a nonvacuous one-variable fall example.
- *TASK-20261031-43dc46, Lean:* the pinned source states a conditional
  `IsGreatest` result. The initial review was frozen while the hosted build was pending; a terminal supplement records the successful named target receipt from run `41191503149`.
- *TASK-20261031-9a6bc2, blind:* `G_D` and `H_D` have the same ideal `(x)` and
  zero closed-space profiles through `D−1`, but their global degrees are `D`
  and `D+1`. The prefix plus the known ideal witness gives a lower bound,
  not a finite upper bound.

== Archive boundary

The earlier T-1105/T-1106/T-1107 packets remain historical and unchanged.
This round uses native TASK IDs and separate review paths. The repository's
independence checker tests ownership and declared reads; it does not itself
authenticate the mathematical argument or Lean execution. No hypothesis or
ledger decision is made by this technical packet.

*Next:* establish a measured row-space-to-closed-space bridge and a later-fall
cutoff before identifying any finite profile with global `d_F`.
