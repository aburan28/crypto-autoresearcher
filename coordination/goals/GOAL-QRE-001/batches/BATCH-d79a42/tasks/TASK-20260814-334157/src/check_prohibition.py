"""Scan EVERY file in this task's write scope for the absolutely prohibited
content: dates, timelines, arrival probabilities, forecasts, migration or
policy advice.

BATCH-973b49's open defect D-V3 records that its own scanner covered 4 of 17
files and contained no date pattern. This one walks the whole task directory,
reports the file count it covered, and includes date patterns.

Known-benign matches are declared explicitly rather than silently excluded:
program record identifiers, the deterministic RNG seed, arXiv identifiers of
filed-but-unread sources, ledger provenance fields, and prohibited vocabulary
appearing inside a sentence that DENIES it (an artifact's own prohibition
statement). Every such exemption is listed in the output with its matching
line, so a reviewer checks each one individually rather than trusting the
filter. Two files are self-excluded by name and reported as such: this
scanner's source, which must spell the vocabulary to detect it, and its own
report, which quotes every match.

Passing this scan is a mechanical sweep with an auditable exemption list. It
is not a proof of compliance.
"""
import json
import os
import re
import sys

# A bare four-digit integer is not a date: this package is full of gate counts,
# qubit widths and primes. What is prohibited is a DATE STATEMENT, so the year
# patterns require prose context (a preposition, a month, or a quarter) rather
# than firing on every integer between 1900 and 2199.
PATTERNS = {
    "dated_year": r"\b(in|by|before|after|since|until|during|around|circa|"
                  r"through|towards?|the year)\s+(19|20|21)\d{2}\b",
    "month_year": r"\b(january|february|march|april|may|june|july|august|"
                  r"september|october|november|december|Q[1-4])\s*,?\s*"
                  r"(19|20|21)\d{2}\b",
    "iso_date": r"\b(19|20|21)\d{2}-\d{2}-\d{2}\b",
    "relative_horizon": r"\b(within|in)\s+(the\s+)?(next\s+)?"
                        r"(\d+|a|a few|several|many)\s+"
                        r"(years?|decades?|months?)\b",
    "timeline_word": r"\b(timeline|roadmap|schedule[sd]?|deadline|forecast\w*|"
                     r"when will|years? away|decades? away|arrival|imminent|"
                     r"cryptographically relevant quantum computer|CRQC)\b",
    "probability_of_arrival": r"\b(probability|likelihood|chance|odds)\b"
                              r"[^.]{0,60}\b(arriv|avail|exist|build|break|"
                              r"threat|deploy)",
    "policy_advice": r"\b(migrat\w+|should (?:now )?(?:adopt|deprecate|switch|"
                     r"transition)|recommend\w* that|policy (?:advice|"
                     r"guidance|implication)|post-quantum transition)\b",
}

# Declared exemptions. Each is listed with its full matching line in the output
# so a reviewer checks it individually rather than trusting the filter.
DENIAL_MARKERS = (
    "prohibition_statement", "prohibition statement", "contains no date",
    "may never contain", "no date, timeline", "no date/timeline",
    "absolute prohibition", "prohibition_scan", "prohibition scan",
    "no date, no timeline", "contains, and may never contain",
)

BENIGN = [
    (r"(TASK|DEC|CORR|GOAL|BATCH|EV|RQ|EXP|RUN|KN|VAL|IDEA)-[A-Z0-9]+-?[0-9a-f]{6,}",
     "program record identifier"),
    (r"\b20260814\b", "deterministic RNG seed declared in PREREGISTRATION "
                      "clause 1.10"),
    (r"arXiv:\d{4}\.\d{4,5}", "arXiv identifier of a filed, unread source"),
    (r"recorded_at|\badded:", "ledger provenance field of a cited record"),
]


# The scanner cannot scan itself: its source must SPELL the prohibited
# vocabulary in order to detect it, and its report must QUOTE every match it
# found. Both are declared here by name and reported as self-excluded rather
# than silently skipped.
SELF_EXCLUDED = {
    os.path.join("src", "check_prohibition.py"):
        "this scanner's own source; it must spell the prohibited vocabulary "
        "in its patterns in order to detect it",
    os.path.join("logs", "check_prohibition.json"):
        "this scanner's own report; it quotes every match it found",
}


def benign_reason(line, match):
    low = line.lower()
    for marker in DENIAL_MARKERS:
        if marker in low:
            return ("occurs inside a sentence that DENIES the prohibited "
                    "content (the artifact's own prohibition statement or a "
                    "description of this scanner), marker: %r" % marker)
    for pat, why in BENIGN:
        for m in re.finditer(pat, line, re.I):
            if m.start() <= match.start() < m.end():
                return why
    return None


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files, hits, exempt = [], [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in sorted(filenames):
            if fn.endswith(".pyc"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root)
            if rel in SELF_EXCLUDED:
                continue
            files.append(rel)
            with open(path, "r", errors="replace") as fh:
                prev = ["", ""]
                for ln, line in enumerate(fh, 1):
                    window = prev[0] + " " + prev[1] + " " + line
                    prev = [prev[1], line]
                    for name, pat in PATTERNS.items():
                        for m in re.finditer(pat, line, re.I):
                            why = benign_reason(window, m) or \
                                benign_reason(line, m)
                            rec = {"file": rel, "line": ln, "pattern": name,
                                   "match": m.group(0),
                                   "context": line.strip()[:200]}
                            if why:
                                rec["exempt_because"] = why
                                exempt.append(rec)
                            else:
                                hits.append(rec)
    out = {"task": "TASK-20260814-334157",
           "artifact": "logs/check_prohibition.json",
           "scope": "every file under the task directory, recursively",
           "files_scanned": len(files), "file_list": files,
           "self_excluded_files": SELF_EXCLUDED,
           "patterns": list(PATTERNS),
           "unexplained_matches": hits,
           "unexplained_match_count": len(hits),
           "declared_benign_matches": exempt,
           "declared_benign_match_count": len(exempt),
           "clean": not hits,
           "note": "Every declared-benign match is listed in full with its "
                   "line so a reviewer can check each one individually. "
                   "Passing this scan is not a proof of compliance; it is a "
                   "mechanical sweep whose exemption list is auditable."}
    dest = os.path.join(root, "logs", "check_prohibition.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=2)
    print("scanned %d files; %d unexplained, %d declared-benign"
          % (len(files), len(hits), len(exempt)))
    for h in hits[:40]:
        print("  !", h["file"], h["line"], h["pattern"], repr(h["match"]),
              "|", h["context"][:120])
    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main())
