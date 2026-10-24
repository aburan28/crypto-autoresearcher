#set page(paper: "a4", margin: 20mm)
#set text(font: "Helvetica", size: 10pt)
= Candidate modular solver implementation controls

2026-10-22. On the public 19-point group, the Q-in-base case had rank 2 of 2
and recovered scalar 7. The Q-outside-base case had rank 3 of 3 and recovered
scalar 2. A one-target input had rank 0 of 2 and remained censored.

#image("rank_control.svg", width: 100%)

A separate Sage checker verified each completed Q scalar, all three base
orbits, 18 targets and 56 reported triples per full control. A copied
scalar changed from 7 to 8 was rejected. Saved JSON contains internal phase
times only; this control does not measure P29/P37 full solve feasibility,
end-to-end ECDLP time or matched rho.
