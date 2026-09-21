"""harness.diffpath -- the differential-path NOVELTY ADJUDICATOR (EXP-DIFFP-fe894e).

Built under the frozen contract experiments/EXP-DIFFP-fe894e/specification.yaml
for TASK-20260824-c6625a (GOAL-DIFFP-84d641, BATCH-f8bf86).

WHAT THIS PACKAGE IS.  An instrument that makes "this differential path is new"
a CHECKABLE statement: reference primitives, a path conformance verifier, a
declared-and-individually-verified equivalence relation, a machine-readable
census with per-entry provenance, and a membership adjudicator that reports a
STRICT verdict (verified generators only) and a PERMISSIVE verdict (all declared
generators) as SEPARATE fields.

WHAT THIS PACKAGE IS NOT.  It runs no search over the difference space, attempts
no collision, and claims no path is new (IR-8).  A MEMBER verdict means
"equivalent to a census entry under the verified generators"; a NON-MEMBER
verdict is scoped to the census that produced it and against an empty census
carries no information at all.

FIREWALL.  No module here reads, parses or reconstructs
coordination/goals/GOAL-MD5-001/quarantine/** (IR-1), and nothing here performs
network acquisition by any route (IR-10).  The quarantined payload is touched
only as opaque bytes, to recompute its sha256 (CTL-QUAR).
"""
