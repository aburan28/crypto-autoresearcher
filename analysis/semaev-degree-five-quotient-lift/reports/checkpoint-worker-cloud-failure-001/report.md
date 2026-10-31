# Cloud worker source attempt 001

Observations only. The source job `semaev-worker-source-20261030-1450` failed with exit 1 before creating any control run. The bootstrap downloaded and hash-verified the published bundle, then the driver failed at `out.mkdir(exist_ok=False)` because `/work/results` did not exist. Zero of the six source-pod controls executed; the three dependent restore controls were withheld. This is an operational failure, not a failed mathematical certificate or a new LFD result.

The terminal job UID is `d5409284-f622-444d-9ba2-311aa246de86`, pod UID `989394c0-f79a-4a11-9ed6-d41df745fbf9`. Terminal status and bounded traceback are preserved in `runs/checkpoint-worker-cloud-source-{terminal,logs}-001.json`. No trial rows are fabricated for this bootstrap failure. The nine-row protocol remains incomplete for this attempt.

Correction: create the results parent in the bootstrap before invoking the unchanged packaged driver. Freeze a separately named follow-up protocol and job; retain the original attempt and do not launch its dependent restore.
