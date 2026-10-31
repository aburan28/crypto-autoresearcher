#set page(paper: "a4", margin: 20mm)
#set text(size: 10pt)
= Certified n49 polynomial-basis input: LFD at least five
The original independent checker accepted all 50 variable multiplication checks for fresh-n49-poly-00. It certified *1 not in W4* and codimension at least *32,291*. A fresh exhaustive count found *2* solutions. Thus the strict inequality establishes *LFD at least 5* for this named Boolean presentation.

#image("flow.svg", width: 100%)

The D4 candidate came from the interrupted frozen frontier run. Its SHA-256 is b4f6043cbc48c34a6cbaeca802b0d5cfa222394456ac72ca9c0bb9873a3370d5. The later recheck matched the certificate, input system, and frozen plan hashes, then ran the original checker and pinned counter. Checker and counter elapsed times were 737.422 and 17.990 seconds. Public and canonical-store readback of the certificate and evidence passed.

The D5 stage is unknown. Original plan SHA-256: cc503cf2523b8b202476e03aeb493ad4f8a2e85500e825f75067b3baf855c4b7. Recovery protocol SHA-256: 73dad26981fed6a8e21edccc70851b63183820f789283c65a07308ec2633124e.
