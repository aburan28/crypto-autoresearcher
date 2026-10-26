"""The producer and refusal controls share this completion guard."""
SENTINEL = "F2_PASS2_PANEL_COMPLETE"


def guarded_call(function):
    result = function()
    if not isinstance(result, dict) or result.get("completion_sentinel") != SENTINEL:
        raise RuntimeError("producer returned without the final completion sentinel")
    return result
