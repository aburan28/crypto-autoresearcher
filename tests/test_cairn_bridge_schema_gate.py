"""The Stage 0 bridge's schema gate.

The gate exists to keep one distinction sharp, because collapsing it turns a
coverage gap into an accusation: a `reject` is the pinned checker saying the
witness is wrong, and a statement it cannot read is the checker saying nothing
at all. Only the first should ever refuse a run.

None of these tests need a cairn binary. The gate is checked before anything
is provisioned or any subprocess is launched, which is the property that lets
a machine with no cairn build run this file unchanged.
"""
from __future__ import annotations

import pytest

from tools import cairn_bridge


def test_required_fields_come_from_the_objective_file():
    """Read from the committed objective, never restated in the module -- the
    objective is the contract, and a second copy of it is a second thing to
    drift."""
    assert cairn_bridge._required_fields("discrete_log") == frozenset(
        {"curve", "P", "Q", "k"}
    )
    assert cairn_bridge._required_fields("decomposition") == frozenset(
        {"curve", "target", "summands"}
    )


@pytest.mark.parametrize(
    "kind, statement, missing",
    [
        # A discrete_log naming its curve by `curve_id` a level up rather than
        # inlining it -- EXP-ECTD-001 and EXP-ECTD-9e4248 write this shape.
        ("discrete_log", {"P": [1, 2], "Q": [3, 4], "k": 5}, ["curve"]),
        # A decomposition over an additive group, not a curve at all --
        # EXP-DS-001's null control.
        (
            "decomposition",
            {"group": {"modulus": 753848, "law": "additive"},
             "target": 587847, "summands": [1, 2]},
            ["curve"],
        ),
    ],
)
def test_unreadable_shapes_are_not_applicable_rather_than_rejected(
    kind, statement, missing
):
    with pytest.raises(cairn_bridge.CairnNotApplicableError) as caught:
        cairn_bridge.score_certificate({"kind": kind, "statement": statement})
    assert str(missing) in str(caught.value)


def test_not_applicable_is_not_an_unavailable():
    """Distinct types because they mean different things to a reader of the
    run record: `unavailable` is retry-later, this one is nobody-wrote-that-
    checker. Both are non-fatal, which is why the difference has to live in
    the type rather than in whether the harness survives."""
    assert not issubclass(
        cairn_bridge.CairnNotApplicableError, cairn_bridge.CairnUnavailableError
    )


def test_a_complete_statement_passes_the_gate():
    """The gate must not become a second verifier. It checks that the keys the
    objective requires are present and stops -- whether the values are *right*
    is the pinned checker's question, and answering it here would grow exactly
    the unpinned second implementation Stage 0 exists to avoid."""
    complete = {"curve": {"p": 223, "a": 0, "b": 171}, "P": [105, 42],
                "Q": [81, 42], "k": 2}
    assert cairn_bridge._missing_required_fields("discrete_log", complete) == []
    # Same keys, a scalar that does not hold: still the checker's call, not ours.
    wrong = dict(complete, k=3)
    assert cairn_bridge._missing_required_fields("discrete_log", wrong) == []
