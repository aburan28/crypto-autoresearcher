# Frontier checkpoint disk admission

The general lab worker currently declares 10 GiB ephemeral storage. The n47 random00 input has 48 Boolean variables, 213053 seed columns, 1925357 output columns, and 187583 working coordinates. `runtime/frontier-checkpoint-disk-envelope-001.json` records exact conservative byte arithmetic from the committed serializers. These are derived sizes, not measurements.

Two maximum snapshots plus the uncompressed seed occupy 10429731008 bytes, leaving 307687232 bytes before runtime overhead. The conservative certificate bound is 45161173824 bytes and cannot be admitted under 10 GiB. A small fixture or successful matrix restore does not resolve this bound.

Next implementation: bind the disk allowance to the worker request; account for runtime files and restore/download staging; preserve a verified phase 2 checkpoint before export; calculate exact certificate size from its relation rank and refuse/defer export if it will not fit. Any refusal retains state and remains inconclusive for LFD. Qualify the allow/refuse boundaries before frontier use. Do not enlarge a Kubernetes limit through an unsupported tool parameter or let an unchecked output trigger eviction.

Exit: checked arithmetic and actual runtime admission, qualified durable phase 2 export refusal, then a frozen frontier attempt with exact original input and independent final checker.
