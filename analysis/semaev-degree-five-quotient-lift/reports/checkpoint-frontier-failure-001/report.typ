#set page(paper: "a4", margin: 22mm)
#set text(size: 11pt)
= Frontier attempt 001: loss before D5
Observations only. Job semaev-n47-rand00-d5-checkpoint-20261030-1515 failed at 15:35:27 UTC on 30 October 2026. Kubernetes reported BackoffLimitExceeded. The pod was no longer retained and bounded log retrieval returned an empty string. The specific cause is unknown.

#image("flow.svg", width: 100%)

Four durable records remain: environment and memory admission, startup disk admission, completed seed transfer, and D4 checker start. The seed transfer verified 1,632,838,224 bytes. The full prefix contains no checker completion, fresh count, D5 start, checkpoint manifest, certificate, or final result. No D5 state can be restored and no new LFD bound follows.

Evidence: runs/checkpoint-frontier-terminal-001.json, runs/checkpoint-frontier-logs-001.json, and validation/checkpoint-frontier-001. Job UID: 2df3a8bf-e685-4dd0-866a-4ce34a067624.

The earlier bounded attempt accepted the identical seed for the identical system with codimension at least 61,196. Reusing that historical acceptance requires verified byte identity and evidence binding. Fresh solution enumeration and independent checking of any D5 certificate remain required. This report does not qualify that proposed continuation.

This diagram records a single failed attempt, so no quantitative comparison is made. Prior mathematical-bound graphs remain unchanged because this attempt produced no new bound.
