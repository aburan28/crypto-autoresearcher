"""`yaml.safe_load` through libyaml, with the pure loader as the reference.

PyYAML's `safe_load` always uses the pure-Python parser, even when the C
library is installed, and parsing dominates the corpus-wide tools: 97% of
validate_ledger.py and 98% of build_knowledge_index.py. libyaml is ~7-10x
faster. A document it rejects is re-parsed by the pure loader, so every error
and its message -- which baselines and CI gates compare -- is exactly what
`yaml.safe_load` produces. Without libyaml this is `yaml.safe_load`.

validate_ledger.py keeps its own copy: it must run as a standalone file.
"""
from __future__ import annotations

from typing import Any

import yaml

CSafeLoader = getattr(yaml, "CSafeLoader", None)


def safe_load(source: Any) -> Any:
    """Same result and same errors as `yaml.safe_load(source)`, faster."""
    if CSafeLoader is None:
        return yaml.safe_load(source)
    stream = hasattr(source, "read")
    data = source.read() if stream else source
    try:
        return yaml.load(data, Loader=CSafeLoader)
    except yaml.YAMLError:
        if stream:
            source.seek(0)
            return yaml.safe_load(source)
        return yaml.safe_load(data)
