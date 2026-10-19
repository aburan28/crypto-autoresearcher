src = open('r3_checks.lean').read()
header, body = src.split("namespace R3\n", 1)
body, axioms = body.split("end R3\n", 1)
sections = body.split("\n-- (")
pre = sections[0]
parts = {}
for s in sections[1:]:
    num = s.split(")")[0]
    parts[num] = "-- (" + s
groups = {'A': ['1','2'], 'B': ['3','4'], 'C': ['5'], 'D': ['6','7']}
for g, nums in groups.items():
    txt = header + "namespace R3\n" + pre + "\n" + "\n".join(parts[n] for n in nums) + "\nend R3\n"
    open(f'r3_{g}.lean','w').write(txt)
open('r3_E.lean','w').write(header + axioms)
