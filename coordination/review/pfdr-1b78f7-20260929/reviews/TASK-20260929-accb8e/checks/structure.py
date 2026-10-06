"""Sanitised structure printer (RV-4). Prints key paths and leaf TYPES of a JSON file;
every numeric leaf is replaced by <num>; subtrees whose path mentions A7 / floor
(case-insensitive) are summarised by key names only, and only boolean leaves are shown
there. Usage: python structure.py <file.json> [maxdepth]"""
import json, re, sys
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e/checks")
import rl  # noqa

FLOORY = re.compile(r"(a7|floor)", re.I)


def show(o, path, depth, maxd, floory=False):
    pad = "  " * depth
    fl = floory or bool(FLOORY.search(path.split("/")[-1] if path else ""))
    if isinstance(o, dict):
        if depth >= maxd:
            print(f"{pad}{path}: dict[{len(o)}] keys={list(o)[:12]}")
            return
        print(f"{pad}{path}: dict[{len(o)}]{' (A7/floor subtree: keys only)' if fl else ''}")
        for k, v in o.items():
            show(v, f"{path}/{k}", depth + 1, maxd, fl)
    elif isinstance(o, list):
        print(f"{pad}{path}: list[{len(o)}]")
        if o and depth < maxd:
            show(o[0], f"{path}[0]", depth + 1, maxd, fl)
    elif isinstance(o, bool):
        print(f"{pad}{path}: bool={o}")
    elif isinstance(o, (int, float)):
        print(f"{pad}{path}: <num>")
    elif o is None:
        print(f"{pad}{path}: null")
    else:
        s = str(o)
        if fl:
            print(f"{pad}{path}: <str len {len(s)}>")
        else:
            print(f"{pad}{path}: str={s[:80]!r}")


if __name__ == "__main__":
    p = sys.argv[1]
    md = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    rl.opened(p, f"structure only (sanitised: numbers masked, A7/floor subtrees keys only), depth {md}")
    import yaml
    obj = yaml.safe_load(open(p)) if p.endswith((".yaml", ".yml")) else json.load(open(p))
    show(obj, "", 0, md)
