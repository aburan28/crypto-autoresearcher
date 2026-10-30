"""Declaration discovery and a separate, explicit compiled-environment export.

Source discovery is deliberately labelled source-only. It never upgrades a
theorem because a proof-shaped string or a report says that it passed.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from research_kb.catalog import digest

STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def uncomment(text: str) -> str:
    out, i, depth, quoted = [], 0, 0, False
    while i < len(text):
        pair = text[i : i + 2]
        ch = text[i]
        if depth:
            if pair == "/-":
                depth += 1
                out.extend("  ")
                i += 2
                continue
            if pair == "-/":
                depth -= 1
                out.extend("  ")
                i += 2
                continue
            out.append("\n" if ch == "\n" else " ")
        elif quoted:
            out.append("\n" if ch == "\n" else " ")
            if ch == "\\" and i + 1 < len(text):
                out.append(" ")
                i += 2
                continue
            if ch == '"':
                quoted = False
        elif pair == "/-":
            depth = 1
            out.extend("  ")
            i += 2
            continue
        elif pair == "--":
            end = text.find("\n", i)
            end = len(text) if end < 0 else end
            out.append(" " * (end - i))
            i = end
            continue
        elif ch == '"':
            quoted = True
            out.append(" ")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def environment_info(path: Path, root: Path):
    project = root
    for parent in [path.parent, *path.parents]:
        if not parent.is_relative_to(root):
            break
        if (parent / "lakefile.toml").exists() or (parent / "lakefile.lean").exists():
            project = parent
            break
    pins = {}
    for name in ("lean-toolchain", "lakefile.toml", "lakefile.lean", "lake-manifest.json"):
        candidates = [project / name, root / name]
        for candidate in candidates:
            if candidate.is_file():
                pins[name] = candidate.read_text()[:128000]
                break
    return {
        "digest": digest(json.dumps(pins, sort_keys=True)),
        "pins": pins,
        "project": str(project),
        "module": ".".join(path.relative_to(project).with_suffix("").parts),
    }


def discover(text: str, version_id: str, module: str, environment: str):
    clean = uncomment(text)
    lines, original = clean.splitlines(), text.splitlines()
    scopes = []
    variables = []
    result = []
    pattern = re.compile(
        r"^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|unsafe|partial)\s+)*(theorem|lemma|def|abbrev|axiom|opaque)\s+(«[^»]+»|[\w'.]+)"
    )
    for i, line in enumerate(lines):
        stripped = line.strip()
        if m := re.match(r"^(namespace|section)\b\s*(\S*)", stripped):
            scopes.append((m[1], m[2]))
            continue
        if re.match(r"^end(?:\s|$)", stripped):
            if scopes:
                scopes.pop()
                variables = [(depth, value) for depth, value in variables if depth <= len(scopes)]
            continue
        if re.match(r"^variables?\b", stripped):
            variables.append((len(scopes), original[i]))
            continue
        m = pattern.match(line)
        if not m:
            continue
        kind, name = m.groups()
        namespace = ".".join(n for k, n in scopes if k == "namespace" and n)
        full_name = (
            name.removeprefix("_root_.")
            if name.startswith("_root_.")
            else ".".join(x for x in (namespace, name) if x)
        )
        # Keep the source statement, not a guessed elaborated type.
        end, parts = i, []
        for j in range(i, min(i + 100, len(lines))):
            if j > i and (pattern.match(lines[j]) or re.match(r"^\s*(end|namespace|section)\b", lines[j])):
                break
            parts.append(original[j])
            end = j
            if ":=" in lines[j] or " where" in lines[j] or (j > i and not lines[j].strip()):
                break
        statement = "\n".join(parts).split(":=", 1)[0].strip()
        if variables:
            statement = "\n".join(value for _, value in variables) + "\n" + statement
        result.append(
            {
                "id": "lean:" + digest(f"{version_id}:{full_name}:{i}")[:32],
                "name": full_name,
                "module": module,
                "kind": kind,
                "statement": statement,
                "line_start": i + 1,
                "line_end": end + 1,
                "environment": environment,
            }
        )
    return result


def export_environment(project: Path, modules: list[str], timeout: int = 300):
    if not modules or any(not re.fullmatch(r"[\w.]+", m) for m in modules):
        raise ValueError("supply at least one valid Lean module name")
    exporter = Path(__file__).parent / "lean/Export.lean"
    # Runs only from the operator CLI; this is not an MCP tool.
    proc = subprocess.run(
        ["lake", "env", "lean", "--run", str(exporter), *modules],
        cwd=project,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=True,
    )
    return [json.loads(line) for line in proc.stdout.splitlines() if line.startswith("{")]


def audit_project(library, project: Path, modules: list[str]):
    """Compile locally and attach receipts only to identical indexed source bytes."""
    from datetime import datetime, timezone
    from research_kb.ingest import writer_lock

    project = project.resolve()
    if not modules or any(not re.fullmatch(r"[\w.]+", m) for m in modules):
        raise ValueError("supply valid module names")
    env = environment_info(project / "Placeholder.lean", project)
    candidates = []
    with library.catalog.connect() as db:
        rows = list(
            db.execute(
                "SELECT t.id,t.name,t.module,t.environment,v.content_hash,l.repo,l.path FROM declarations t JOIN versions v ON t.version_id=v.id JOIN documents d ON d.active_version=v.id JOIN locations l ON l.version_id=v.id WHERE l.present=1"
            )
        )
    roots = {s.name: s.root for s in library.settings.sources()}
    for row in rows:
        root = roots.get(row["repo"])
        if root is None:
            continue
        file = (root / row["path"]).resolve()
        if file.is_relative_to(project) and row["environment"] == env["digest"]:
            if file.is_file() and digest(file.read_bytes()) == row["content_hash"]:
                candidates.append((dict(row), file))
    subprocess.run(
        ["lake", "build", *modules], cwd=project, check=True, timeout=600, capture_output=True, text=True
    )
    exported = export_environment(project, modules)
    by_name = {(r["module"], r["name"]): r for r in exported}
    if environment_info(project / "Placeholder.lean", project)["digest"] != env["digest"]:
        raise ValueError("Lean environment changed during compilation; reindex before auditing")
    updates = []
    for row, file in candidates:
        if digest(file.read_bytes()) != row["content_hash"]:
            raise ValueError("Lean source changed during compilation; reindex before auditing")
        record = by_name.get((row["module"], row["name"]))
        if record is None:
            continue
        extra = set(record["axioms"]) - STANDARD_AXIOMS
        status = (
            "nonstandard-axioms"
            if extra
            else "kernel-axiom-audited"
            if record["kind"] == "theorem"
            else "compiled"
        )
        receipt = {
            "method": "local-lake-build-and-compiled-environment-axiom-audit",
            "environment": env["digest"],
            "source_sha256": row["content_hash"],
            "checked_at": datetime.now(timezone.utc).isoformat(),
            **record,
        }
        updates.append((status, json.dumps(record["axioms"]), json.dumps(receipt), row["id"]))
    with writer_lock(library.settings.home), library.catalog.connect(True) as db:
        db.executemany("UPDATE declarations SET verification=?,axioms=?,receipt=? WHERE id=?", updates)
    return {
        "exported": len(exported),
        "attached": len(updates),
        "environment": env["digest"],
        "failed_axiom_checks": sum(x[0] == "nonstandard-axioms" for x in updates),
    }
