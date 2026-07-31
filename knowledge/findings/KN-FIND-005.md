---
id: KN-FIND-005
title: Raised deg-a≤4 non-isotrivial free-x still admit inf-norm-1 MW relations; deg x≤3 empty on deg-b=6
type: internal_finding
status: established
tags: [lifting, xedni, function-field, non-isotrivial, mordell-weil, coefficient-bound, methodology, toy-scale]
evidence: [EV-XEDN-004]
decision: [DEC-20260725-002]
---

# KN-FIND-005

On non-isotrivial surfaces `y²=x³+a(t)x+b(t)` with `a≠0`, `deg a≤4`, `deg b=6`,
and non-constant `j`, free-x sections `deg x≤2`, `deg y≤3` still admit
group-law-verified Mordell–Weil relations with infinity-norm 1 at
`p∈{7,13,19,31}` (EXP-XEDN-005 / EV-XEDN-004), including a thickened p=31 cell
of 10 eligible surfaces. μ₃ orbits remain absent.

Separately: raising free-x to `deg x≤3` while keeping `deg b=6` yields no
polynomial sections, because `deg(x³+ax+b)=9` is odd and cannot be a square in
`F_p[t]`. A genuine free-x degree raise requires a joint increase of `deg b`
(so that `deg f` is even). The executable RT-XEDN-004 control executed here is
therefore the deg-a window raise.

Scope: toy only; not B2 / crypto-scale.
