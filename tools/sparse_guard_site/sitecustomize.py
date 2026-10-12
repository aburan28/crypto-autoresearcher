"""Loads tools/ci_sparse_guard.py's audit hook into every Python process of a
sparse CI shard (validate.yml puts this directory on PYTHONPATH)."""
import os
import sys

if os.environ.get("CI_SPARSE_GUARD_ROOT"):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import ci_sparse_guard

    ci_sparse_guard.install()
    sys.path.pop(0)
