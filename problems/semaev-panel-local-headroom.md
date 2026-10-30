# Original n45 panel inputs need local memory headroom

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
