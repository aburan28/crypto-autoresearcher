#!/usr/bin/env python3
"""
Family specification and specialisation.  FAMILY-AGNOSTIC by construction:
the pipeline never hard-codes a base family, it reads one from a JSON file.

Family spec (JSON)
------------------
{
  "name": "...",
  "params": ["t"],                       # one or more rational parameters
  "a_invariants": ["0","0","0","expr","expr"],   # rational functions of params
  "sections": [["x-expr","y-expr"], ...],        # optional Q(t)-points
  "claimed_generic_rank": 2,             # a CLAIM TO REPRODUCE, never a given
  "source": "citation or 'internal'",
  "notes": "..."
}

Expressions are ordinary Python arithmetic in the parameters (``^`` is accepted
and rewritten to ``**``); they are evaluated in exact Fraction arithmetic with
an empty builtins namespace.

Specialisation
--------------
Evaluating at a rational parameter point gives a Weierstrass model with
rational a-invariants.  Scaling (x,y) -> (u^2 x, u^3 y), i.e. a_i -> u^i a_i,
with u the lcm of the denominators, makes it integral; sections are carried
along by the same substitution.  Minimalisation is done afterwards, in
icarm_invariants / pipeline, by PARI.
"""
from fractions import Fraction as F
import json
import math


def _compile(expr):
    return compile(str(expr).replace('^', '**'), '<family>', 'eval')


class Family:
    def __init__(self, spec):
        self.spec = spec
        self.name = spec['name']
        self.params = list(spec['params'])
        self._ai = [_compile(e) for e in spec['a_invariants']]
        self._sections = [(_compile(x), _compile(y))
                          for x, y in spec.get('sections', [])]
        self.claimed_generic_rank = spec.get('claimed_generic_rank')
        self.source = spec.get('source', 'unspecified')

    @classmethod
    def load(cls, path):
        return cls(json.load(open(path)))

    def specialise(self, values):
        """values: dict param -> int/Fraction.  Returns dict or None if singular.

        Returns {'a_invariants': [int x5], 'scale_u': u, 'points': [[x,y],...],
                 'params': {...}}.  The a-invariants are INTEGRAL but not yet
                 minimal.  Points are exact Fractions on that integral model.
        """
        env = {'__builtins__': {}}
        env.update({k: F(v) for k, v in values.items()})
        try:
            ai = [F(eval(c, env)) for c in self._ai]
            pts = [(F(eval(cx, env)), F(eval(cy, env))) for cx, cy in self._sections]
        except ZeroDivisionError:
            return None
        u = 1
        for a in ai:
            u = u * a.denominator // math.gcd(u, a.denominator)
        for x, y in pts:
            for a in (x, y):
                u = u * a.denominator // math.gcd(u, a.denominator)
        aint = [int(ai[i] * u ** e) for i, e in enumerate((1, 2, 3, 4, 6))]
        spts = [[str(x * u * u), str(y * u ** 3)] for x, y in pts]
        return {'a_invariants': aint, 'scale_u': u,
                'points': spts,
                'params': {k: str(F(v)) for k, v in values.items()}}


def parameter_box(box):
    """Enumerate a parameter box.

    box: {"t": {"num_min": -20, "num_max": 20, "den_max": 1}} or
         {"t": {"values": ["1","3/2", ...]}}
    Yields dicts param -> Fraction, in increasing order of height
    max(|num|,den) so that "small parameters" come first.
    """
    names = list(box)
    grids = []
    for n in names:
        b = box[n]
        if 'values' in b:
            vals = [F(v) for v in b['values']]
        else:
            dmax = int(b.get('den_max', 1))
            vals = []
            for den in range(1, dmax + 1):
                for num in range(int(b['num_min']), int(b['num_max']) + 1):
                    v = F(num, den)
                    if v.denominator == den:
                        vals.append(v)
            vals = sorted(set(vals), key=lambda v: (max(abs(v.numerator), v.denominator), v))
        grids.append(vals)
    out = []

    def rec(i, cur):
        if i == len(names):
            out.append(dict(cur))
            return
        for v in grids[i]:
            cur[names[i]] = v
            rec(i + 1, cur)
    rec(0, {})
    out.sort(key=lambda d: sum(math.log(max(abs(v.numerator), v.denominator) + 1)
                               for v in d.values()))
    return out


def param_size(values):
    """log of the naive height of the parameter point (the 'small' in 'small
    parameters'): log max_i max(|num_i|, den_i)."""
    return math.log(max(max(abs(F(v).numerator), F(v).denominator)
                        for v in values.values()) + 0.0 or 1.0)
