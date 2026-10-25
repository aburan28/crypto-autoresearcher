"""`yaml.safe_load` through libyaml, with the pure loader as the reference.

PyYAML's `safe_load` always uses the pure-Python parser, even when the C
library is installed, and parsing dominates the corpus-wide tools: 97% of
validate_ledger.py and 98% of build_knowledge_index.py. libyaml is ~7-10x
faster. A document it rejects is re-parsed by the pure loader, so every error
and its message -- which baselines and CI gates compare -- is exactly what
`yaml.safe_load` produces. Without libyaml this is `yaml.safe_load`.

This is the one implementation; `tools/fast_yaml.py` re-exports it for
scripts run from tools/. validate_ledger.py keeps its own copy because it
must run as a standalone file, and kb/ (a separate package) has its own.
"""
from __future__ import annotations

import io
from typing import Any

import yaml

CSafeLoader = getattr(yaml, "CSafeLoader", None)


def safe_load(source: Any) -> Any:
    """Same result and same errors as `yaml.safe_load(source)`, faster."""
    if CSafeLoader is None:
        return yaml.safe_load(source)
    if not hasattr(source, "read"):
        try:
            return yaml.load(source, Loader=CSafeLoader)
        except yaml.YAMLError:
            return yaml.safe_load(source)
    data = source.read()
    try:
        return yaml.load(data, Loader=CSafeLoader)
    except yaml.YAMLError:
        # Replay what was read as a stream with the same name: the pure
        # loader's marks then read exactly as they would have on `source`,
        # which may be unseekable (stdin) or not at its start.
        replay = io.BytesIO(data) if isinstance(data, bytes) else io.StringIO(data)
        if hasattr(source, "name"):
            replay.name = source.name
        return yaml.safe_load(replay)
