#set page(paper:"a4",margin:18mm)
#set text(size:10pt)
= Interrupted n43 polynomial-basis input 03

#image("flow.svg",width:100%)

Observation only. The fixed input fresh-n43-poly-03 lost its first v3 worker before a completed closure result was uploaded. Kubernetes confirms terminal failure at 2026-10-29T17:35:53Z. No pod or log remains available, so the cause is unknown; this report does not attribute the loss to Spot eviction, memory exhaustion, or a timeout.

The uploaded controls passed, all 25 control-artifact hashes verify, and the original request bytes match the fixed archive. The exact solution count 4 completed successfully. No result.json or certificate was uploaded. The count alone establishes no LFD bound. This input remains unfinished; the four other completed panel inputs remain unchanged. The original failed attempt is preserved and a separately frozen one-input retry will not count as an additional independent sample.

Readback.json records the original S3 prefix, local raw location, count-stage result and verification scope. Terminal-observation.json preserves the Job identity, terminal status, empty log response and full object inventory. The diagram marks the missing stage; it is not a statistical plot. Shared-host timing gives no speed claim.
