# Producer snapshot — TASK-20260905-2b52a7

This snapshot preserves the terminal pre-execution failure receipt from TASK-20260905-ae8941 (zero solver/version calls) and the excerpt-only prerequisite intake from TASK-20260905-53d333. It asserts no solver readiness, mathematical result, or completed scientific audit. Producer resource-probe timestamps and intake budget telemetry have disclosed gaps. Independent validation follows this archive.

The control plane additionally ran a separate isolated resource-capability recheck outside the sandbox, without invoking a solver. The captured output is preserved below; the same limit-setting exception was observed, and its underlying cause is not determined here. This recheck did not rerun or alter the producer record.

```json
{
  "recorded_at": "2026-09-05T16:15:32.882162+00:00",
  "scope": "isolated resource-limit capability probe only; no solver invocation",
  "sandbox_execution": "require_escalated",
  "platform": "macOS-26.6-arm64-arm-64bit-Mach-O",
  "python": "3.13.1 (v3.13.1:06714517797, Dec  3 2024, 14:00:22) [Clang 15.0.0 (clang-1500.3.9.4)]",
  "observations": [
    {
      "resource": "RLIMIT_AS",
      "returncode": 0,
      "stdout": "{\"before\": [9223372036854775807, 9223372036854775807], \"ok\": false, \"error\": \"ValueError: current limit exceeds maximum limit\"}\n",
      "stderr": "",
      "elapsed_seconds": 0.024105832970235497
    },
    {
      "resource": "RLIMIT_RSS",
      "returncode": 0,
      "stdout": "{\"before\": [9223372036854775807, 9223372036854775807], \"ok\": false, \"error\": \"ValueError: current limit exceeds maximum limit\"}\n",
      "stderr": "",
      "elapsed_seconds": 0.023722834012005478
    },
    {
      "resource": "RLIMIT_DATA",
      "returncode": 0,
      "stdout": "{\"before\": [9223372036854775807, 9223372036854775807], \"ok\": false, \"error\": \"ValueError: current limit exceeds maximum limit\"}\n",
      "stderr": "",
      "elapsed_seconds": 0.02266683301422745
    }
  ]
}
```
