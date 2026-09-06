Proposal snapshot TASK-20260905-8443e4

BATCH-23ec69 archives two producer bundles and eleven canonically filed proposal
records on two user-directed ECDLP avenues (instruction of 2026-09-05):

- TASK-20260905-a6ea8a (novel point representations, RQ-ECDLP-623a32): five records,
  IDEA-20260905-d0fee4, -24b41a, -579fcc, -ab4a6e, -0e0982; two assigned identifiers
  (-1af7ac, -2d77c3) left unused; a sixth candidate withdrawn by the producer as a
  repackaging.
- TASK-20260905-282872 (SAT/SMT technology for relation finding, RQ-ECDLP-f0a7b0): six
  records, IDEA-20260905-24d827, -a6f98e, -3de445, -a94b5f, -79112a, -3993c3; one
  assigned identifier (-1226bf) left unused.

Binding mode content_first: the bundles and filed records were committed in working
checkpoints before this archive task ran (both producers were cut off by an API rate
limit and resumed; that is an infrastructure event and evidence of nothing). The
receipt in dispatch_queue.json binds every declared path by sha256.

Deviations, disclosed: (1) the runtime refused each producer's write of report.md, so
the Coordinator transcribed each producer's returned report verbatim under a
provenance note inside the file; (2) the representation handoff predates
docs/object-frame-ideation.md (adopted on main during the run); its declarations were
supplied to the producer as an additive Coordinator message and are carried in the
records' fixed fields; (3) the crypto-kb search tool was unavailable to the producers;
the Coordinator ran a file-backed index built this session and returned four unnamed
neighbours to the SAT producer, which cited them before filing.

All eleven records remain status proposed and novelty_status unverified. No experiment,
hypothesis, approval, scientific conclusion, novelty certification or goal status
change is asserted. Independent Red Team review (TASK-20260905-ac087e) follows this
commit.
