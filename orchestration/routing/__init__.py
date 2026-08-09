"""Host-neutral routing contracts for Research Loop v2.

This initializer is intentionally import-free.  Importing ``.models`` is an
explicit opt-in to the optional Pydantic contract dependency; no plugin host
or ledger-only command acquires that dependency merely by importing this
package.
"""

__all__ = ()
