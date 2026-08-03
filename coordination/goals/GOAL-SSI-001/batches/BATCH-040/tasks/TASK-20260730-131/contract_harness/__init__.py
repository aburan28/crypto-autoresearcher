"""Adversarial harness for the BATCH-040 host-integration width contract and
QM-STOPPING obstruction analysis (TASK-20260730-131).

The harness holds the sourced structural facts (frozen hook ids, scaffold stage
live-sets, the composition-operator id, the CollimationSieve pin) independently of
the produced artifacts, so an artifact that disagrees — an invented per-slot
width, an invented unit or peak, an out-of-protocol hook/member, an illicit
clearance flag, an invented tau, or an obstruction claim masquerading as a §4
closure — is rejected.

Explicit non-claims: zero curve/isogeny/quantum compute; no CollimationSieve API
is invented or called; no numeric width/peak/tau/security value is asserted.
"""
