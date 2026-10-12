"""RV-4 reading filter. Prints a YAML/text file with every digit masked inside any block
whose key line mentions A7 / floor / TW-FLOOR / tw_floor (case-insensitive), tracked
by indentation, and on any line that mentions them. Logs the read.
Usage: python sanitize.py <file> [first_line] [last_line]"""
import re, sys
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e/checks")
import rl  # noqa

PAT = re.compile(r"(a7|floor)", re.I)


def main():
    p = sys.argv[1]
    a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    b = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
    rl.opened(p, f"read through checks/sanitize.py lines {a}-{b if b < 10**9 else 'end'} (digits masked in A7/floor contexts)")
    ctx = None  # indentation of the active A7/floor key
    for i, line in enumerate(open(p, errors="replace"), start=1):
        s = line.rstrip("\n")
        ind = len(s) - len(s.lstrip(" "))
        stripped = s.strip()
        if ctx is not None and stripped and ind <= ctx and not stripped.startswith("- ") :
            ctx = None
        if ctx is not None and stripped.startswith("- ") and ind < ctx:
            ctx = None
        if PAT.search(s):
            if ctx is None:
                ctx = ind
            masked = re.sub(r"\d", "#", s)
        elif ctx is not None:
            masked = re.sub(r"\d", "#", s)
        else:
            masked = s
        if a <= i <= b:
            print(f"{i:6d}  {masked}")


if __name__ == "__main__":
    main()
