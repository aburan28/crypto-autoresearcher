# Cloud checkpoint controls: attempt 001

Observations only. All three source fixture rows failed with FileNotFoundError before any native child step completed. The first executable requested was prlimit; the original exception did not retain its filename. No snapshot was published, and the dependent restore worker was not launched. This is an infrastructure result, not evidence about LFD.

The frozen protocol requires six rows. Only the three actual failed source rows are exported, so the export is incomplete. Original request, input hashes, code and terminal pod status remain retained. The next separately frozen version uses Python resource.setrlimit with the same cap and inputs. No canonical mathematical graph changes.

Job: `semaev-checkpoint-source-20261030-0612`; pod UID `cab04a96-e0b1-4756-bd5a-ea361fe578f1`. Protocol SHA: `f16d2b01b88f6e84e969680f7ba8b68e3c511dd461dc04b90e5e0f76c2a942ea`.

![Actual execution](outcomes.svg)
