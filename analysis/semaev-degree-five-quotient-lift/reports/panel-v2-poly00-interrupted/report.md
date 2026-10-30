# Interrupted n43-poly00 attempt

The original n43-poly00 v2 job ended failed at16:41:25UTC. The controls passed and exact count0 was durably uploaded;25 control artifact hashes were verified after download. No result.json or completed certificate was present. A fresh status query confirms terminalfailure and an empty podlist. Logs were empty. The cause is unknown; do not assume Spot reclamation, timeout, OOM or a mathematical failure.

The count alone gives no LFD lower bound. The incomplete closure remains unknown. Raw S3 and local paths are in readback.json; authoritative terminaljob status is in job-status.json. A separately frozen single-input retry uses the already-qualified portableworker, preserves the originalinput and failedattempt, and does not add an independent sample. Protocol: ../../panel-poly00-retry-protocol.json.

The original32-input continuation still has two independently verified n42 bounds and30 unfinished mathematical outcomes. A separate n43-poly01 portable job remains active; the total concurrency cap remains two panel jobs.
