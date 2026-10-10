"""`yaml.safe_load` through libyaml; the pure loader decides what libyaml rejects.

Corpus staging parses ~20k front-matter blocks and records, and parsing was
95% of the staging test's time. PyYAML's `safe_load` always uses the pure
parser; libyaml is ~10x faster. A document libyaml rejects is re-parsed by the
pure loader, so the outcome is always what `yaml.safe_load` gives.
"""

from __future__ import annotations

from typing import Any


def safe_load(text: str) -> Any:
    import yaml

    loader = getattr(yaml, "CSafeLoader", None)
    if loader is not None:
        try:
            return yaml.load(text, Loader=loader)
        except yaml.YAMLError:
            pass
    return yaml.safe_load(text)
