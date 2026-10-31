#set page(paper: "a4", margin: 22mm)
#set text(size: 11pt)
= Cloud worker bootstrap failure, attempt 001
Observations only. The published bundle downloaded and passed its hash check. Driver initialization then failed before any control ran: /work/results did not exist, so creating its worker-control child raised FileNotFoundError.

#image("outcomes.svg", width: 100%)

Job semaev-worker-source-20261030-1450 exited 1. Its source controls were not executed, and the dependent restore pod was never launched. No certificate or mathematical bound was produced. The terminal state and complete bounded traceback are preserved in the runs directory. No trial rows are fabricated for a pre-trial bootstrap failure.

The next separately frozen attempt creates the results parent in the bootstrap before invoking the unchanged packaged driver. Both the original attempt and its incomplete protocol remain preserved.
