"""Detect a narrow operational stall without judging research progress.

Only complete, consecutive tool rounds in which EVERY result is an explicit
tool error/refusal qualify. Arguments and complete results must be identical;
changing a call id or parallel-result order does not make it new work.
Successful polling, timeouts and command exit codes are deliberately excluded.
The transcript remains the evidence; no model call or external probe is used.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Sequence

from langchain_core.messages import AIMessage, AnyMessage, ToolMessage

DEFAULT_FAILURE_ROUNDS = 3
_ERROR_STRING_TOOLS = {
    "read_file", "search_files", "write_file", "edit_file", "run_command",
}


def _is_error(message: ToolMessage, tool_name: str) -> bool:
    if getattr(message, "status", None) == "error":
        return True
    # These are the repository tools' own wrapper outcomes, not arbitrary
    # prose containing the word error. Command stdout follows an exit header;
    # file contents follow line numbers and do not match these prefixes.
    return (tool_name in _ERROR_STRING_TOOLS
            and isinstance(message.content, str)
            and message.content.startswith(("DENIED: ", "ERROR: ")))


def repeated_tool_failure(messages: Sequence[AnyMessage], *,
                          rounds: int = DEFAULT_FAILURE_ROUNDS) -> dict[str, Any] | None:
    if isinstance(rounds, bool) or not isinstance(rounds, int) or rounds < 2:
        raise ValueError("failure rounds must be an integer of at least two")
    cursor = len(messages) - 1
    expected: str | None = None
    tool_names: list[str] = []
    for _ in range(rounds):
        results: dict[str, ToolMessage] = {}
        while cursor >= 0 and isinstance(messages[cursor], ToolMessage):
            result = messages[cursor]
            if result.tool_call_id in results:
                return None
            results[result.tool_call_id] = result
            cursor -= 1
        if cursor < 0 or not isinstance(messages[cursor], AIMessage):
            return None
        calls = messages[cursor].tool_calls
        cursor -= 1
        ids = [call["id"] for call in calls]
        if not calls or len(ids) != len(set(ids)) or set(ids) != set(results):
            return None
        entries = []
        for call in calls:
            result = results[call["id"]]
            if not _is_error(result, call["name"]):
                return None
            entries.append(json.dumps(
                [call["name"], call["args"], result.content,
                 getattr(result, "status", None)],
                sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        fingerprint = hashlib.sha256(
            json.dumps(sorted(entries), separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if expected is not None and fingerprint != expected:
            return None
        expected = fingerprint
        tool_names = sorted({call["name"] for call in calls})
    return {
        "consecutive_rounds": rounds,
        "fingerprint_sha256": expected,
        "tool_names": tool_names,
        "classification": "operational_tool_failure",
        "asserts_nothing_about": "the science or campaign completion",
        "next_action": (
            "Correct the tool arguments or resolve the recorded prerequisite "
            "before a Coordinator-authorized retry. Do not relax task scope."
        ),
    }
