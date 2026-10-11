"""Workload-specific GPU/CPU efficiency: how close a workload runs to its own roofline.

Modules: metrics (parse samples), observe (reduce a window), profiles (roofs),
score (the score), export (Prometheus text and recording rules), prom (live
queries), probe (machine profiles from measured ceilings).  See README.md.
Standard library only, Python 3.8+.
"""
