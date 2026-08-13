"""Host-neutral knowledge contracts for the Research Loop v2 boundary.

The package initializer intentionally does not import :mod:`.models`.  The
models use the optional Pydantic dependency, while a ledger-only installation
must still be able to import the rest of :mod:`orchestration`.
"""

__all__ = ()
