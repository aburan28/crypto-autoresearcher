import runpy, sys, io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path("coordination/goals/GOAL-ICEX-001/batches/BATCH-227e0d/tasks/TASK-20261001-1894f8/rederive_j3.py")
for pk, pre in g["prefixes"].items():
    for mode in ["rej_top_c0bare", "rej_low_c0bare", "mod_N"]:
        for i in range(256):
            lab = f"{pre}|heldout|16|21|{i}"
            k = g["scalar"](lab, mode)
            S = g["mul"](k, g["G"])
            t, h, e = g["stage2"](S)
            if h:
                hits = [P1 for P1 in g["F"] if (lambda D: D is not None and D[0] < g["B_p"])(g["add"](S, g["neg"](P1)))]
                print(pk, mode, i, "k=", k, "S=", S, "hits", h, "P1s", hits, "S-P1:", [g["add"](S, g["neg"](P)) for P in hits])
print("sumset", {k: v for k, v in g["sumset"].items()})
