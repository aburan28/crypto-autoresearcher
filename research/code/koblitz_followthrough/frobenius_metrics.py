"""Shared measurement helpers for Koblitz/subfield follow-through experiments.

No cryptanalytic claim is made here.  The module only normalizes telemetry so
different experiment families can be compared without silently changing the
meaning of a "Frobenius speedup".
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass(frozen=True)
class FrobeniusMetrics:
    raw_factor_base_points: int
    effective_factor_base_columns: int
    baseline_solver_work: Optional[float] = None
    candidate_solver_work: Optional[float] = None
    baseline_relation_work: Optional[float] = None
    candidate_relation_work: Optional[float] = None
    baseline_la_dimension: Optional[int] = None
    candidate_la_dimension: Optional[int] = None

    def _ratio(self, baseline, candidate):
        if baseline is None or candidate is None or candidate <= 0:
            return None
        return baseline / candidate

    def to_dict(self):
        if self.raw_factor_base_points < 0 or self.effective_factor_base_columns <= 0:
            raise ValueError("factor-base counts must be nonnegative with positive effective columns")
        out = asdict(self)
        out.update({
            "orbit_column_reduction": self.raw_factor_base_points / self.effective_factor_base_columns,
            "solver_work_reduction": self._ratio(self.baseline_solver_work, self.candidate_solver_work),
            "relation_work_reduction": self._ratio(self.baseline_relation_work, self.candidate_relation_work),
            "linear_algebra_dimension_reduction": self._ratio(self.baseline_la_dimension, self.candidate_la_dimension),
        })
        return out
