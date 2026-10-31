#set page(paper: "a4", margin: 20mm)
#set text(size: 10.5pt)
= Certified n45 polynomial04: LFD at least five
The original independent checker accepted the D4 certificate for the unchanged fresh-n45-poly-04 input. All 46 variable-multiplication checks passed; it verified 1 not in W_4(F) and codimension at least *12,744*. Fresh exhaustive enumeration found *zero* Boolean solutions. The strict inequality establishes *LFD at least 5* for this named presentation.

The certificate is 288,550,808 bytes with SHA-256 dc87ce3fe229236b0fe0aa9505208fde8f59212121009069ed2e6e8cc86cc98f. The collector verified all 47 worker artifacts, the frozen request and protocol, and terminal success. Three per-worker controls passed byte identity, exact count, and independent checker tests. The full certificate is retained at /home/ec2-user/fall-degree-data-20261029/panel-local-n45-poly04-001/attempt-001/certificate.bin for separate publication.

#image("flow.svg", width: 100%)

Admission passed after 535.495 seconds at 45,312,360,448 bytes available against the 40 GiB child cap plus 2 GiB reserve. Producer and checker took 3,088.882 and 208.650 seconds on a shared L0 host; no runtime comparison follows. The original 32-input panel now has 27 terminal and 20 certified LFD-at-least-five inputs, with five original n45 random inputs remaining. No input was redrawn.

Frozen source fe215d2f392fe42d85eacdbfd83c845bb89ee38e; protocol 505d717654959efa30b04ead5aca0e66173e4d96ca164e1e08596725eb675169. Raw evidence: validation/panel-local-n45-poly04-final-001.
