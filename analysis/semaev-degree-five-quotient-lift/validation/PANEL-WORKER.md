# Full panel worker controls

`run_panel_worker.py` runs qualified node-local controls, exact counting,
retained-candidate verification or bounded closure construction, and the
unchanged independent checker. Completed stages upload to the job-specific
S3 prefix before later work. No upper bound follows from producer output.

The six local controls in `panel-worker-local-20261029/` passed:

- Three original fixtures: certificate bytes match the original reference;
  counts 3,1,1 match enumeration; checked codimension equals count and no
  LFD lower bound is emitted.
- Retained-candidate reuse: original checker accepts, no redundant producer.
- Conservative memory refusal: resource_capped, no bound.
- Corrupt candidate with a matching transport hash: independent checker
  rejects and the worker reports failed without a bound.

These are software controls, not new scientific data. Remote durable uploads
still need a scientific job and S3 GET/hash reconciliation before that job can
be counted complete. A Spot interruption within elimination may lose that
unfinished stage; uploaded previous stages remain available. Never duplicate
an existing live job.
