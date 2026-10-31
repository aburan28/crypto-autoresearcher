#set page(paper: "a4", margin: 16mm)
#set text(font: "DejaVu Sans", size: 10pt)
= Original n50/n51 frontier cascade panel

The frozen 18-input continuation completed every remaining original n50/n51 record after poly00 and poly01. Six n50 and all ten n51 inputs produced independently checked D3 certificates. Each checked codimension lower bound exceeded its fresh exact solution count, establishing named-input LFD at least 4. Two n50 inputs reported `W3_one 1` and produced no certificate.

#image("checked-d3.svg", width: 100%)

Every attempted D4 lift returned `lift allocation gate refused` under the pinned 16 GiB cap. The outcomes are 16 `resource_capped` and two `seed_without_certificate`; no D4 or D5 certificate was produced by this panel. The run records are `runs/n50n51-cascade-local-terminal-001/`. The 16 retained D3 seeds are in the `semaev-frontier-d3-seeds-20261031` release, with full compressed and decompressed hash readback.

The panel ran sequentially with one thread, 60,000-row chunks and a 21,600-second per-command watchdog. Timing records are marked invalid for comparison. Read-only bounded D4 profiles range from 13,207,168,721 to 28,263,000,132 bytes; these are allocation arithmetic, not observed RSS or D4 results. A separately frozen continuation will attempt D4 on all 16 accepted seeds.
