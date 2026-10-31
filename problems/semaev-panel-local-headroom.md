# Original n45 panel inputs need local memory headroom

Update 2026-10-30 20:31 UTC: local03 also refused before worker launch,
available39,264,284,672bytes. The [third refusal](../analysis/semaev-degree-five-quotient-lift/validation/panel-local-n45-poly02-refusal-003/result.json)
preserves the measurement. Two earlier sufficient readings did not persist
through preparation. Next construction: a bounded pre-worker admission wait,
with every sample retained, unchanged cap/reserve and both ownership locks,
rather than another immediate attempt based on stale headroom. This needs
implementation checks and a new prospective execution record.

Update 2026-10-30 20:21 UTC: separately frozen polynomial02 local02 was
also refused, with available39,073,169,408bytes below45,097,156,608required.
Headroom had temporarily recovered during preparation but fell before
launch. No worker started. Preserve the [second refusal](../analysis/semaev-degree-five-quotient-lift/validation/panel-local-n45-poly02-refusal-002/result.json)
and wait for sustained headroom before preparing another attempt.

Update 2026-10-30 20:14 UTC: polynomial01 subsequently completed and its
certificate was independently accepted and published (q12742 > count0).
The next original input, polynomial02, was refused before worker launch:
available42039373824bytes < required45097156608bytes, exit73. The
[latest refusal](../analysis/semaev-degree-five-quotient-lift/validation/panel-local-n45-poly02-refusal-001/result.json)
and [report](../analysis/semaev-degree-five-quotient-lift/reports/panel-local-n45-poly02-refusal-001/report.md)
preserve it. Eight original panel inputs remain unfinished. No cap or
ownership guard was changed; no automatic retry was launched. The earlier
polynomial01 refusal below is historical and remains retained.

The first local attempt was refused before worker creation. The launcher
acquired both campaign locks, measured 35,684,368,384 available bytes,
and returned 73 because the unchanged 40 GiB child cap plus 2 GiB reserve
requires 45,097,156,608 bytes. No count or certificate computation ran.

The [admission and observed exit](../analysis/semaev-degree-five-quotient-lift/validation/panel-local-n45-poly01-refusal-001/result.json)
and [operational report](../analysis/semaev-degree-five-quotient-lift/reports/panel-local-n45-poly01-refusal-001/report.md)
are retained. This is neither a mathematical negative result nor a
completed panel input. The original inventory still has nine unfinished
inputs. The degree-six high-memory search is unchanged.

Other compiler processes were observed using substantial memory. Their
ownership and purpose were not changed. The admission cap and reserve
were not lowered. The current output directory must not be overwritten.

Next test: observe actual memory headroom and campaign ownership again.
After sufficient headroom returns, prepare a separately identified,
prospectively frozen continuation of the same original input under the
same cap. Success requires the original counter, producer and independent
checker to finish with retained evidence. A passing admission alone does
not resolve the scientific work. Repeated capacity refusals remain
charged infrastructure outcomes, never population evidence or an upper
bound on LFD.

## 2026-10-30 bounded admission succeeded
Attemptlocal04 retained ten admission samples and admitted after91.2846seconds when available memory reached48251219968bytes, above the unchanged45097156608byte requirement. All three controls passed and fresh exactcount6 completed. Native producerPID1136402 remains active; closed records are in validation/panel-local-n45-poly02-progress-005. Prior immediate refusals remain unchanged.
