#set page(paper: "a4", margin: (x: 17mm, y: 15mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 8.8pt)
#set par(leading: 0.55em, spacing: 0.65em)
#text(size: 20pt, weight: "bold", "Exact serialization software controls")
#par(justify: false)[#text("Retained v1 / final v2 • TASK-20261016-282fd3 • capture6e6a5f • RQ-IC-a39c7e")]
#par(justify: false)[#text("This report records actual bounded software controls and a corrected implementation attempt. It is observations only: no scientific run, independent review, source acceptance, full-grid adequacy, baseline-S improvement, ECDLP advantage or execution-proof claim.")]
#block(above: 7pt, below: 4pt)[#text(size: 12pt, weight: "bold", "Frozen workload and operational history")]
#par(justify: false)[#text("The exact frozen fixture SHA256 is 443012913a6cd015391ecf665029775d95b6132c56c6e96c54d0a1c606e369df. Small uses 32 rows and no ballast; headroom uses 800,000 references to one shared nested row, with Fraction(-7,13), Path(\"synthetic/é\"), large exact integers, tuple/null/bool/-0.0 and nested empty mappings. Only the writer allocates and retains 1,342,177,280 bytes (1280 MiB) independent ballast. Fresh reader processes allocate ZERO writer ballast; their fixture.resident_ballast_bytes is a writer workload descriptor, not reader process state. Hard and soft RLIMIT_AS are 2,147,483,648 bytes, applied before imports; one worker and OPENBLAS_NUM_THREADS=1.")]
#par(justify: false)[#text("The historical baseline core 461c19c5… failed at the same recursive _json_safe call on the synthetic headroom writer; no raw/manifest was produced. It was not rerun unnecessarily. Candidate v1 passed its software controls but root identified selected manifest parameters/checks snapshots after clock sampling, unlike historical timing semantics. V1 source, payload, transcripts, manifests and actual output remain retained unchanged. Candidate v2 moves those normalized independent snapshots before the sample and adds a controlled-clock assertion; it reran the same frozen candidate controls in new directories. No fixture resizing or retuning.")]
#image("graph.svg", width: 100%)
#par(justify: false)[#text("Figure: measured completed calls only; baseline failure is a separate callout. One observation per phase. Reader ballast 0; RSS lifetime high-water. Full source data: plot-data.json and software-insight.json.")]
#pagebreak()
#block(above: 7pt, below: 4pt)[#text(size: 12pt, weight: "bold", "Recorded calls — no ratio or baseline-completion claim")]
#table(columns: (1.25fr, 1.3fr, 0.9fr, 1fr, 1fr, 1.2fr), inset: 4pt, align: left, text(weight: "bold", "Revision"),
text(weight: "bold", "Phase / rows"),
text(weight: "bold", "Status"),
text(weight: "bold", "Wall s"),
text(weight: "bold", "CPU s"),
text(weight: "bold", "Peak RSS KiB"),
text(size: 7.8pt, "baseline"),
text(size: 7.8pt, "write / 32"),
text(size: 7.8pt, "pass"),
text(size: 7.8pt, "0.007125"),
text(size: 7.8pt, "0.006169"),
text(size: 7.8pt, "15,872"),
text(size: 7.8pt, "baseline"),
text(size: 7.8pt, "check / 32"),
text(size: 7.8pt, "pass"),
text(size: 7.8pt, "0.000533"),
text(size: 7.8pt, "0.000530"),
text(size: 7.8pt, "15,488"),
text(size: 7.8pt, "v1 retained"),
text(size: 7.8pt, "write / 32"),
text(size: 7.8pt, "pass"),
text(size: 7.8pt, "0.009831"),
text(size: 7.8pt, "0.008886"),
text(size: 7.8pt, "15,788"),
text(size: 7.8pt, "v1 retained"),
text(size: 7.8pt, "check / 32"),
text(size: 7.8pt, "pass"),
text(size: 7.8pt, "0.000352"),
text(size: 7.8pt, "0.000348"),
text(size: 7.8pt, "15,532"),
text(size: 7.8pt, "v2 final"),
text(size: 7.8pt, "write / 32"),
text(size: 7.8pt, "pass"),
text(size: 7.8pt, "0.010844"),
text(size: 7.8pt, "0.009301"),
text(size: 7.8pt, "15,988"),
text(size: 7.8pt, "v2 final"),
text(size: 7.8pt, "check / 32"),
text(size: 7.8pt, "pass"),
text(size: 7.8pt, "0.000368"),
text(size: 7.8pt, "0.000365"),
text(size: 7.8pt, "15,536"),
text(size: 7.8pt, "baseline"),
text(size: 7.8pt, "write / 800000"),
text(size: 7.8pt, "fail"),
text(size: 7.8pt, "9.352211"),
text(size: 7.8pt, "9.346519"),
text(size: 7.8pt, "2,061,568"),
text(size: 7.8pt, "baseline"),
text(size: 7.8pt, "check / 800000"),
text(size: 7.8pt, "censored"),
text(size: 7.8pt, "—"),
text(size: 7.8pt, "—"),
text(size: 7.8pt, "—"),
text(size: 7.8pt, "v1 retained"),
text(size: 7.8pt, "write / 800000"),
text(size: 7.8pt, "pass"),
text(size: 7.8pt, "73.091858"),
text(size: 7.8pt, "73.082956"),
text(size: 7.8pt, "1,332,784"),
text(size: 7.8pt, "v1 retained"),
text(size: 7.8pt, "check / 800000"),
text(size: 7.8pt, "pass"),
text(size: 7.8pt, "3.092453"),
text(size: 7.8pt, "3.090241"),
text(size: 7.8pt, "1,331,844"),
text(size: 7.8pt, "v2 final"),
text(size: 7.8pt, "write / 800000"),
text(size: 7.8pt, "pass"),
text(size: 7.8pt, "72.911390"),
text(size: 7.8pt, "72.898922"),
text(size: 7.8pt, "1,332,792"),
text(size: 7.8pt, "v2 final"),
text(size: 7.8pt, "check / 800000"),
text(size: 7.8pt, "pass"),
text(size: 7.8pt, "2.837928"),
text(size: 7.8pt, "2.837641"),
text(size: 7.8pt, "1,331,812"))
#par(justify: false)[#text("Rows are measured native calls. Writer headroom ballast 1,342,177,280 bytes; all reader process ballast 0. RSS is lifetime high-water, not phase increment; 2 GiB limits address space. Failed baseline writer duration ends in MemoryError; its reader was not launched. No confidence interval is available.")]
#block(above: 7pt, below: 4pt)[#text(size: 12pt, weight: "bold", "Timing boundary and exact-byte/correctness controls")]
#par(justify: false)[#text("Manifest preparation timing includes driver work through result assembly, full raw-validation prepass and selected normalized independent protocol snapshots. It excludes subsequent manifest construction/provenance validation and streamed raw/manifest encoding, incremental hashing and writes. Separately measured write_artifacts call wall/CPU includes validation, encoding, hashing and I/O; check_artifacts call timing covers fresh parser/hash/envelope work. Extra parsed row checks run after the timed checker call. Process-launch wall and lifetime peak RSS are different measures and remain in exact logs; intervals are not added.")]
#par(justify: false)[#text("Final v2 unittest log records 107 tests in 3.255s, OK: 21 core and 86 unchanged four-consumer regressions. Coverage includes canonical bytes/types/normalized keys and collisions, nonfinite/deep/late invalid values, provenance/timing/seed checks, exclusive paths/symlinks, partial I/O/hash tampering and snapshot independence. Tests use non-study arithmetic/integer fixtures or mocked run_experiment; no full scientific grid ran. Small output has 13,193 bytes/SHA6a05e32795098c0be31a8c053ba8d77a12e6b7d6679e4cc8c0793f5440436329; both actual headroom candidate outputs have 325,600,173 bytes/SHA9c7247f5ad5c4cc1d25c670de4375d16df868e38dfa0f620cc47b42003ed57ec. An independently assembled exact-byte oracle checks full raw SHA/size (full byte equality for small); fresh parsed readers verify 800,000 cases and exact first/middle/last rows. These are software controls, not independent scientific review.")]
#pagebreak()
#block(above: 7pt, below: 4pt)[#text(size: 12pt, weight: "bold", "Retained failures, evidence and limits")]
#par(justify: false)[#text("Preserved deviations: v1 timing-boundary defect and its correction; failed dependency install followed by successful scratch-only install; absent requested /usr/local/bin/python3 and actual CPython 3.12.14; cloud runtime skill read late; unverified hand-entered frozen_at label, with original bytes/additive note retained; declared 1200 s optional watchdog not actually armed; initially broad truncated status listing and incomplete pre-recorder setup/tool output captures. The original label and filesystem mtime are operational declarations, not external preregistration. Actual command times are retained; no timeout is invented. The initial verbal 24-core-test count was corrected to actual 21; no log or frozen fixture was rewritten.")]
#par(justify: false)[#text("One observation per control, no confidence interval and no completion-time comparison against the failed baseline. Full scientific object shape/size/headroom remains unknown. Full JSON parser/text transients, selected materialized manifest subtrees, active mapping sorts, recursion depth, largest integer token and downstream scientific checker allocations retain memory costs. Unchanged consumer CLIs still materialize JSON. Shared nested rows plus ballast isolate a software allocation pattern; they do not reconstruct the lost result or prove a fresh full grid/checker can finish. Small candidate calls are slower in these recorded observations; no performance ratio or scientific improvement is inferred.")]
#block(above: 7pt, below: 4pt)[#text(size: 12pt, weight: "bold", "Actual artifact custody")]
#par(justify: false)[#text("software-insight.json preserves exact v1/v2 producer JSON bytes, all 117 bound native evidence files plus final source2 bytes, and 21 actual compressed output/source/fixture artifacts. Each embedded gzip payload was base64-decoded, checked for compressed SHA/size, then decompressed in 1 MiB chunks to verify raw SHA/size; no output or workload was regenerated. Actual EFBIG27 left a 1,024-byte partial raw/SHA13c4813f252941f0ab3eb15d05843e1c6d0fd09686dbdae2b58862be5090a3bd, with no manifest; this remains embedded. Exact original fixture/control/guard/recorder text, raw v1/v2 transcripts and the preservation manifest appear in controls-transcript.txt. No durability depends solely on a /tmp pointer; original scratch paths remain provenance labels.")]
#par(justify: false)[#text("Exact producer bytes: v1 payload SHA 3d56c1922c4564722bb0e4133799cf13069e8e7565fcf1a7efac0c9c7bb7ccc2; v2 payload SHA 8fa5c9839e790df2dd377d9f86e043893a1c4658ae8d06a82e8dc34c84a85ea9. Both full original transcripts and final source2 are retained by SHA/byte count; raw command logs remain recoverable from embedded native-evidence blobs.")]
#block(above: 7pt, below: 4pt)[#text(size: 12pt, weight: "bold", "Source and runtime provenance")]
#par(justify: false)[#text("Root supplied final source inspection and actual payload; Coordinator independently checked source/payload/transcript/measurement/log hashes and streamed embedded artifacts, without rerunning tests or benchmarks. Host: AMD EPYC 9V74, x86_64, Linux 6.18.44/glibc2.41, CPython 3.12.14; SymPy 1.14.0, PyYAML 6.0.3, scratch fpylll 0.6.4/cysignals 1.12.5. Original runtime/path and failed setup are retained verbatim. Requested Executor/Coordinator policies at high remain distinct from actual serving backend/model/probe, which are unverified.")]
#par(justify: false)[#text("Final core SHA 27b88681a5be468eca8ebbfb278333dd71ec178965ed3a5025cd7e85d0d28fec; tests SHA 652bd0b62c301d6fe947d1d4bdcd9e417650a7838ac0156425807ec1b97344ba. V1 source is retained separately; current source is not yet officially archived/accepted.")]
#block(above: 7pt, below: 4pt)[#text(size: 12pt, weight: "bold", "Uncompleted gates")]
#par(justify: false)[#text("This capture remains queued pending actual root inspection of every PDF page and actual-parent report7+ownreceipt8 native archival. Core2+ownreceipt3 source snapshot remains separate; later currentclosure5 cannot union old/new source proofs. Original scientific archive 3047d1/local 9403cb and all blind/full/local independent reviews remain uncompleted. Historical three failed attempts and their frozen records remain unchanged. No canonical scientific graph changes because no validated scientific observation or decision changed. Execution-proof integration and scientific inference remain separate open obligations.")]
