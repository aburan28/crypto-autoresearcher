#set page(paper:"a4",margin:18mm)
#set text(size:9pt)
= Checkpoint transport controls

28 of 28 fixed local fake-S3 controls passed. The archive contains 553 hash-verified files. This is not actual cloud permission or durability evidence and establishes no LFD bound.

Export validation passed for the composite case rows.

#image("outcomes.svg",width:100%)

#table(columns:(auto,3fr,auto,auto),[Mode],[Case],[Passed],[Steps],[retain], [object\_put], [True], [3], [retain], [object\_get], [True], [3], [retain], [object\_corrupt\_get], [True], [3], [retain], [manifest\_put], [True], [3], [retain], [manifest\_get], [True], [3], [retain], [manifest\_corrupt\_get], [True], [3], [retain], [wrong\_snapshot\_context], [True], [1], [retain], [idempotent\_publication], [True], [2], [retain], [prune\_after\_readback], [True], [2], [retain], [fallback\_corrupt\_object], [True], [3], [retain], [fallback\_corrupt\_manifest], [True], [3], [retain], [wrong\_restore\_context], [True], [3], [retain], [truncated\_listing], [True], [3], [retain], [restore\_newest\_and\_replay], [True], [4], [prune], [object\_put], [True], [3], [prune], [object\_get], [True], [3], [prune], [object\_corrupt\_get], [True], [3], [prune], [manifest\_put], [True], [3], [prune], [manifest\_get], [True], [3], [prune], [manifest\_corrupt\_get], [True], [3], [prune], [wrong\_snapshot\_context], [True], [1], [prune], [idempotent\_publication], [True], [2], [prune], [prune\_after\_readback], [True], [2], [prune], [fallback\_corrupt\_object], [True], [3], [prune], [fallback\_corrupt\_manifest], [True], [3], [prune], [wrong\_restore\_context], [True], [3], [prune], [truncated\_listing], [True], [3], [prune], [restore\_newest\_and\_replay], [True], [4])

The workload uses a filesystem-only fake AWS executable. Controls cover interrupted PUT/GET, corruption, idempotence, verified pruning, fallback, context mismatch, incomplete listing, and native replay against retained reference certificate bytes. Child commands and their original stdout/stderr are in the evidence archive. Each child has a 1 GiB cap and 120-second watchdog; timings are L0 telemetry only. Inputs, code and native binary hashes are in plan.json. The source revision is pinned in protocol.json. Actual cloud publish, replacement-worker restore and independent certificate checking remain required. No canonical mathematical graph changes; this diagram records software-control status only.
