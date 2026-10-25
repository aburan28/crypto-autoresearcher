# Fresh Git-runtime metadata successor: exact execution handoff

Real source commit 0e845993953578fce6fc71380ffa1e1d02bc9159 was published before actual native preapproval returned approvable:true with no blockers. Exact bytes are approved under DEC-20261018-15d481.

| EXP | executor TASK | RUN A | RUN B | raw archive |
| --- | --- | --- | --- | --- |
| EXP-ECDLP-53b1c3 | TASK-20261018-8614ca | RUN-ECDLP-ef9a36 | RUN-ECDLP-449da5 | TASK-20261018-9d69d5 |

Require ordinaryready, actual native task offer, fresh goal_lanes claim, publish and explicit origin fetch before launch. Run exactly:

```sh
env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.preloadIndex GIT_CONFIG_VALUE_0=false /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 tools/experiment_execution.py run --plan experiments/EXP-ECDLP-53b1c3/trial-plan.json --owner executor-ideas-20261018 --epoch ACTUAL
```

The env prefix belongs to the OUTER supervisor only. Frozen direct child argv/check_argv, source, science and1GiB stay unchanged. Release by actual native status and publish; preserve every actual byte and yield Git for exact isolated archive before further lane work. No overwrite or consumed-slot retry. Original615invalid outcome stays immutable. Controls/output validity and original prediction comparisons remain separate; no hypothesis/goal promotion.
