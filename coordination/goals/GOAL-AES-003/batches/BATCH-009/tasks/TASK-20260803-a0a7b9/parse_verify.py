#!/usr/bin/env python3
"""Parse EVERY structured artifact of TASK-20260803-a0a7b9 WHOLE.

JSON files are json.load-ed in full (not sniffed). JSONL files are parsed line
by line with every line required to parse. Markdown files are scanned for
```yaml fences and every fence is yaml.safe_load-ed in full. Anything that fails
is reported; the script exits non-zero so a failure cannot pass silently."""
import json, os, re, sys, yaml

D = os.path.dirname(os.path.abspath(__file__))
report = {"json": {}, "jsonl": {}, "markdown_yaml_blocks": {}, "failures": []}

for root, _, fs in os.walk(D):
    for f in sorted(fs):
        p = os.path.join(root, f)
        rel = os.path.relpath(p, D)
        try:
            if f.endswith(".json"):
                with open(p) as fh:
                    obj = json.load(fh)          # WHOLE file
                report["json"][rel] = {"parsed": True,
                                       "top_level_keys": len(obj) if isinstance(obj, dict) else None,
                                       "bytes": os.path.getsize(p)}
            elif f.endswith(".jsonl"):
                n = 0
                with open(p) as fh:
                    for line in fh:
                        if line.strip():
                            json.loads(line); n += 1
                report["jsonl"][rel] = {"parsed": True, "records": n}
            elif f.endswith(".md"):
                blocks = re.findall(r"```yaml\n(.*?)```", open(p).read(), re.S)
                oks = [bool(yaml.safe_load(b)) for b in blocks]
                report["markdown_yaml_blocks"][rel] = {
                    "yaml_fences": len(blocks), "all_parsed": all(oks)}
        except Exception as e:
            report["failures"].append({"file": rel, "error": repr(e)})

report["summary"] = {
    "json_files_parsed_whole": len(report["json"]),
    "jsonl_files_parsed_whole": len(report["jsonl"]),
    "markdown_files_with_yaml_scanned": len(report["markdown_yaml_blocks"]),
    "failures": len(report["failures"]),
    "all_pass": not report["failures"],
}
json.dump(report, open(os.path.join(D, "runs", "parse_report.json"), "w"), indent=1)
print(json.dumps(report["summary"], indent=1))
if report["failures"]:
    print(json.dumps(report["failures"], indent=1)); sys.exit(1)
