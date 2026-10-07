"""Strassen 2x2 identity: exact micro-kernel check.

Why Strassen and not Schonhage here: an earlier draft of this task
hand-transcribed Schonhage's 10-product coefficient tables from memory and
the module's own randomized check FAILED (outer (3,3) entry mismatch) -- so
it was deleted, not fixed by hand. Transcribing that identity correctly
requires the paper source or the Lean formalization in hand, and silent
hand-repair would be fabrication. Strassen's 7-product identity below is
fully standard and is checked exactly over Python integers (no floats, no
modular reduction): 200 randomized trials plus zero / identity / big-int
controls. It demonstrates the mechanism class the paper builds on
(encode -> fewer products -> decode), nothing more.
"""

from __future__ import annotations


def direct(a, b):
    return [[a[i][0] * b[0][j] + a[i][1] * b[1][j] for j in range(2)]
            for i in range(2)]


def strassen(a, b):
    m1 = (a[0][0] + a[1][1]) * (b[0][0] + b[1][1])
    m2 = (a[1][0] + a[1][1]) * b[0][0]
    m3 = a[0][0] * (b[0][1] - b[1][1])
    m4 = a[1][1] * (b[1][0] - b[0][0])
    m5 = (a[0][0] + a[0][1]) * b[1][1]
    m6 = (a[1][0] - a[0][0]) * (b[0][0] + b[0][1])
    m7 = (a[0][1] - a[1][1]) * (b[1][0] + b[1][1])
    return [[m1 + m4 - m5 + m7, m3 + m5],
            [m2 + m4, m1 - m2 + m3 + m6]], 7


def check(n_trials=200, seed=20261006):
    import random
    rng = random.Random(seed)

    def trial(a, b, label):
        assert strassen(a, b)[0] == direct(a, b), label

    for t in range(n_trials):
        a = [[rng.randint(-1000, 1000) for _ in range(2)] for _ in range(2)]
        b = [[rng.randint(-1000, 1000) for _ in range(2)] for _ in range(2)]
        trial(a, b, f"random:{t}")
    z = [[0, 0], [0, 0]]
    e = [[1, 0], [0, 1]]
    trial(z, [[3, -1], [2, 5]], "control:zero-left")
    trial([[3, -1], [2, 5]], z, "control:zero-right")
    trial([[3, -1], [2, 5]], e, "control:identity")
    big = 2 ** 60
    trial([[big, -big], [1, big]], [[1, big], [-big, 1]], "control:big-int")
    return {"trials": n_trials + 4, "failures": 0,
            "mults_per_product": 7, "direct_mults": 8, "saved_mults": 1,
            "note": "mechanism-class demonstration only; Schonhage 10-product "
                    "transcription deferred to paper/Lean source after a "
                    "hand-transcription failed its own check and was deleted"}
