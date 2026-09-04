"""harness.rl_isogeny -- reinforcement-learning search over (isogeny-class member,
point-decomposition presentation) states, scored by the exact F_p Macaulay meter.

Design note: analysis/rl-isogeny-search/DESIGN.md.  Driver: tools/rl_isogeny_search.py.
Claim tier of everything this package produces: toy.
"""
from .reward import Measurement, PresentationSpec, RewardMeter, Weights, build_presentation, coverage_estimate, fibre_poly_general, scan, shape_feasible, yield_log2_trials
from .env import CHAINED_GRID, Curve, GridSpec, GRIDS, IsogenyPDPEnv, LARGE_GRID, MEDIUM_GRID, SMALL_GRID
from .agents import PPOAgent, RandomAgent, TabularQAgent, evaluate, make_agent, run_episode, train
from .controls import compare, exhaustive_oracle, summarize
from .leading_forms import Certificate, certify, certify_grid, leading_forms

__all__ = [
    "Measurement", "PresentationSpec", "RewardMeter", "Weights", "build_presentation", "coverage_estimate",
    "fibre_poly_general", "scan", "shape_feasible", "yield_log2_trials",
    "CHAINED_GRID", "Curve", "GridSpec", "GRIDS", "IsogenyPDPEnv", "LARGE_GRID", "MEDIUM_GRID", "SMALL_GRID",
    "PPOAgent", "RandomAgent", "TabularQAgent", "evaluate", "make_agent", "run_episode", "train",
    "compare", "exhaustive_oracle", "summarize",
    "Certificate", "certify", "certify_grid", "leading_forms",
]
