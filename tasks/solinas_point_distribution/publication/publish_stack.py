"""Publish previously authorized prepared archives plus the current measurement."""
import datetime
import json
import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
OLD = REPO / "experiments/EXP-ECDLP-5184f7/runs/RUN-ECDLP-d0e449/publication"
plan = json.loads((OLD / "publication-plan.json").read_text())
rows = [dict(row, body=str(OLD / row["body"])) for row in plan["branches"]]
rows += [
    {"head": "feat/ec-relation-ml-20261011", "base": "run/nist-prime-resistance-20261011",
     "title": "Bridge exact elliptic-curve relations to an ML solver-selection pilot", "body": str(OWN / "05-ml.md")},
    {"head": "run/solinas-point-distribution-20261012", "base": "feat/ec-relation-ml-20261011",
     "title": "Measure Solinas whole-curve point distributions with matched prime controls", "body": str(OWN / "06-point-distribution.md")},
]
result = {"started_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "PRs": [], "commands": []}
env = dict(os.environ, GIT_TERMINAL_PROMPT="0")


def call(argv):
    process = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True)
    result["commands"].append({"argv": argv, "exit_code": process.returncode, "stdout": process.stdout, "stderr": process.stderr})
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip())
    return process.stdout.strip()


try:
    call(["gh", "api", "user", "--jq", ".login"])
    refs = ["claude/snfs-ecdlp-g-experiments"] + [row["head"] for row in rows]
    call(["git", "-c", "credential.helper=!gh auth git-credential", "push", "--atomic", "origin", *refs])
    for row in rows:
        existing = json.loads(call(["gh", "pr", "list", "--repo", plan["repo"], "--head", row["head"], "--base", row["base"],
                                    "--state", "open", "--json", "number,url,isDraft"]))
        if existing:
            pr = existing[0]
            if pr["isDraft"]:
                call(["gh", "pr", "ready", str(pr["number"]), "--repo", plan["repo"]])
            url = pr["url"]
        else:
            url = call(["gh", "pr", "create", "--repo", plan["repo"], "--head", row["head"], "--base", row["base"],
                        "--title", row["title"], "--body-file", row["body"]])
        result["PRs"].append({"head": row["head"], "base": row["base"], "url": url, "isDraft": False})
        print(url, flush=True)
    result["status"] = "published_ready"
except RuntimeError as error:
    result["status"] = "publication_failed"
    result["error"] = str(error)
finally:
    result["finished_at_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    filename = "publication-" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S") + ".json"
    with (OWN / filename).open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "record": filename, "error": result.get("error")}), flush=True)
if result["status"] != "published_ready":
    raise SystemExit(1)
