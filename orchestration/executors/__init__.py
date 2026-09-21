"""External execution backends for research tasks.

Executors run bounded work while the crypto-autoresearcher remains responsible
for task selection, evidence classification, validation, and ledger updates.
"""

from .autolab import (
    AutoLabConfig,
    AutoLabExecutionError,
    AutoLabExecutor,
    AutoLabResult,
)

__all__ = [
    "AutoLabConfig",
    "AutoLabExecutionError",
    "AutoLabExecutor",
    "AutoLabResult",
]
