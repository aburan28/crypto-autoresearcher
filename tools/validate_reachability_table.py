#!/usr/bin/env python3
"""validate_reachability_table.py — EXP-BINSTD-f9a860 Stages 0–3.

Per-cell reachability shard validator (HOLD-F corrected schema).

Live checks:
  (i)   schema shape (extended fields, controlled vocabularies)
  (ii)  certificate integrity (re-hash artifact_path vs pinned sha256)
  (iii) provenance freshness (cited input record_id exists and is not superseded)
  (iv)  OPEN-cell liveness (informational): grep proposals/hypotheses for
        missing_quantity; never blocking alone

Also rebuilds the gitignored generated table view.

This tool makes NO break / attack-cost claim. certificate.kind on experiment
run manifests remains `none`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML required", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REACHABILITY = REPO_ROOT / "analysis" / "binstd-curve-audit" / "reachability"
DEFAULT_VIEW = (
    REPO_ROOT / "analysis" / "binstd-curve-audit" / "reachability_table.generated.yaml"
)
SCHEMA_OUTLINE = (
    REPO_ROOT
    / "experiments"
    / "EXP-BINSTD-f9a860"
    / "stage0"
    / "schema-outline.yaml"
)

VERDICTS = {
    "STRUCTURALLY_EMPTY",
    "COMPUTED",
    "OPEN",
    "NOT_YET_ASSESSED",
}
UNITS = {
    "group_ops_rho_bits",
    "field_ops",
    "sat_conflicts",
    "wall_clock",
    "bits",
    "none",
}
PROVENANCE_TIERS = {"proposal_arithmetic", "analysis", "evidence"}
MISSING_QUANTITY_VOCAB = {
    "covering_genus_g_H",
    "factor_base_size_B",
    "oracle_cost_per_attempt",
    "decomposition_floor_bits",
    "lattice_rounding_cost",
    "matched_rho_bits",
    "qsp_attempt_bound",
    "descent_degree_bound",
    "other_named_quantity",
}
REQUIRED_TOP = [
    "curve_row",
    "method_column",
    "verdict",
    "unit",
    "m",
    "floor_bits",
    "budget_bits",
    "formula",
    "N_used",
    "rho_convention",
    "provenance_tier",
    "certificate",
    "inputs",
    "missing_quantity",
    "superseded_by",
    "recorded_at",
    "seed_source",
]


@dataclass
class Finding:
    severity: str  # error | warning | info
    check: str
    cell: str | None
    message: str
    pointer: str | None = None


@dataclass
class Ctx:
    root: Path
    reachability: Path
    ledger_root: Path
    findings: list[Finding] = field(default_factory=list)
    cells: dict[str, dict[str, Any]] = field(default_factory=dict)

    def err(self, check: str, msg: str, cell: str | None = None, pointer: str | None = None):
        self.findings.append(Finding("error", check, cell, msg, pointer))

    def warn(self, check: str, msg: str, cell: str | None = None, pointer: str | None = None):
        self.findings.append(Finding("warning", check, cell, msg, pointer))

    def info(self, check: str, msg: str, cell: str | None = None, pointer: str | None = None):
        self.findings.append(Finding("info", check, cell, msg, pointer))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _cell_key(curve: str, column: str) -> str:
    return f"{curve}/{column}"


def load_cells(ctx: Ctx) -> None:
    if not ctx.reachability.is_dir():
        ctx.err("load", f"reachability dir missing: {ctx.reachability}")
        return
    for path in sorted(ctx.reachability.glob("*/*.yaml")):
        if path.name.endswith(".superseded.yaml"):
            continue
        try:
            data = _load_yaml(path)
        except Exception as exc:  # noqa: BLE001
            ctx.err("load", f"YAML parse failed: {exc}", cell=str(path.relative_to(ctx.root)))
            continue
        if not isinstance(data, dict):
            ctx.err("load", "cell root must be a mapping", cell=str(path.relative_to(ctx.root)))
            continue
        # Support either bare mapping or wrapped under `cell:`
        cell = data.get("cell", data)
        if not isinstance(cell, dict):
            ctx.err("load", "cell payload must be a mapping", cell=str(path.relative_to(ctx.root)))
            continue
        try:
            rel = str(path.relative_to(ctx.root))
        except ValueError:
            # Scratch-copy battery may place shards outside the repo root.
            rel = str(path)
        curve = path.parent.name
        column = path.stem
        cell.setdefault("curve_row", curve)
        cell.setdefault("method_column", column)
        cell["_path"] = rel
        key = _cell_key(cell["curve_row"], cell["method_column"])
        if key in ctx.cells:
            ctx.err("load", f"duplicate cell key {key}", cell=rel)
        ctx.cells[key] = cell


def check_schema(ctx: Ctx) -> None:
    for key, cell in ctx.cells.items():
        path = cell.get("_path", key)
        for field_name in REQUIRED_TOP:
            if field_name not in cell:
                ctx.err("schema", f"missing required field `{field_name}`", cell=path, pointer=field_name)
        verdict = cell.get("verdict")
        if verdict not in VERDICTS:
            ctx.err("schema", f"bad verdict {verdict!r}", cell=path, pointer="verdict")
        unit = cell.get("unit")
        if unit not in UNITS:
            ctx.err("schema", f"bad unit {unit!r} (HOLD-F: every seeded cell needs a unit)", cell=path, pointer="unit")
        tier = cell.get("provenance_tier")
        if tier not in PROVENANCE_TIERS:
            ctx.err("schema", f"bad provenance_tier {tier!r}", cell=path, pointer="provenance_tier")
        if cell.get("method_column") == "matched_rho":
            if cell.get("rho_convention") != "CORR-20260922-81aeab":
                ctx.err(
                    "schema",
                    "matched_rho requires rho_convention CORR-20260922-81aeab",
                    cell=path,
                    pointer="rho_convention",
                )
        # STRUCTURALLY_EMPTY → certificate required
        if verdict == "STRUCTURALLY_EMPTY":
            cert = cell.get("certificate")
            if not isinstance(cert, dict):
                ctx.err("schema", "STRUCTURALLY_EMPTY requires certificate mapping", cell=path, pointer="certificate")
            else:
                for f in ("artifact_path", "sha256", "assertion"):
                    if not cert.get(f):
                        ctx.err("schema", f"certificate missing `{f}`", cell=path, pointer=f"certificate.{f}")
        # COMPUTED → inputs non-empty
        if verdict == "COMPUTED":
            inputs = cell.get("inputs")
            if not isinstance(inputs, list) or not inputs:
                ctx.err("schema", "COMPUTED requires non-empty inputs", cell=path, pointer="inputs")
            else:
                for i, inp in enumerate(inputs):
                    if not isinstance(inp, dict) or not inp.get("record_id"):
                        ctx.err("schema", "input entry needs record_id", cell=path, pointer=f"inputs[{i}]")
            if not cell.get("formula"):
                ctx.err("schema", "COMPUTED requires formula", cell=path, pointer="formula")
        # OPEN → missing_quantity in vocab
        if verdict == "OPEN":
            mq = cell.get("missing_quantity")
            if mq not in MISSING_QUANTITY_VOCAB:
                ctx.err(
                    "schema",
                    f"OPEN missing_quantity {mq!r} not in controlled vocabulary",
                    cell=path,
                    pointer="missing_quantity",
                )
        # m / floor / budget types
        m = cell.get("m")
        if m is not None and not isinstance(m, int):
            ctx.err("schema", f"m must be int, got {type(m).__name__}", cell=path, pointer="m")


def check_certificate_hashes(ctx: Ctx) -> None:
    for key, cell in ctx.cells.items():
        if cell.get("verdict") != "STRUCTURALLY_EMPTY":
            continue
        path = cell.get("_path", key)
        cert = cell.get("certificate") or {}
        art = cert.get("artifact_path")
        pinned = cert.get("sha256")
        if not art or not pinned:
            continue
        art_path = ctx.root / art
        if not art_path.is_file():
            ctx.err(
                "hash",
                f"certificate artifact missing: {art}",
                cell=path,
                pointer=art,
            )
            continue
        digest = _sha256_file(art_path)
        if digest != pinned:
            ctx.err(
                "hash",
                f"certificate sha256 mismatch: pinned={pinned} actual={digest}",
                cell=path,
                pointer=art,
            )


def _find_record_file(ctx: Ctx, record_id: str) -> Path | None:
    """Locate a ledger/knowledge record by id (best-effort for battery)."""
    patterns = [
        ctx.ledger_root / "proposals" / f"{record_id}.yaml",
        ctx.ledger_root / "hypotheses" / f"{record_id}.yaml",
        ctx.ledger_root / "corrections" / f"{record_id}.yaml",
        ctx.ledger_root / "decisions" / f"{record_id}.yaml",
        ctx.ledger_root / "evidence" / f"{record_id}.yaml",
        ctx.root / "knowledge" / "literature" / f"{record_id}.md",
        ctx.root / "knowledge" / "findings" / f"{record_id}.md",
        ctx.root / "knowledge" / "techniques" / f"{record_id}.md",
    ]
    for p in patterns:
        if p.is_file():
            return p
    # slow fallback: glob by id stem under ledger/
    hits = list(ctx.ledger_root.rglob(f"{record_id}.yaml"))
    if hits:
        return hits[0]
    hits = list((ctx.root / "knowledge").rglob(f"{record_id}.md"))
    if hits:
        return hits[0]
    return None


def _record_superseded(path: Path) -> str | None:
    """Return superseded_by value if the record declares one."""
    try:
        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8")
            m = re.search(r"^superseded_by:\s*(\S+)", text, re.M)
            if m and m.group(1) not in ("null", "~", "None"):
                return m.group(1)
            return None
        data = _load_yaml(path)
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(data, dict):
        return None
    # unwrap common envelopes
    for key in ("correction", "proposal", "hypothesis", "decision", "evidence", "idea"):
        if key in data and isinstance(data[key], dict):
            data = data[key]
            break
    sb = data.get("superseded_by")
    if sb in (None, "null", "", False):
        # also check nested status blocks
        return None
    return str(sb)


def check_supersession(ctx: Ctx) -> None:
    for key, cell in ctx.cells.items():
        path = cell.get("_path", key)
        inputs = cell.get("inputs") or []
        if not isinstance(inputs, list):
            continue
        for inp in inputs:
            if not isinstance(inp, dict):
                continue
            rid = inp.get("record_id")
            if not rid:
                continue
            rec = _find_record_file(ctx, rid)
            if rec is None:
                ctx.err(
                    "supersession",
                    f"input record_id not found: {rid}",
                    cell=path,
                    pointer=rid,
                )
                continue
            sb = _record_superseded(rec)
            if sb:
                ctx.err(
                    "supersession",
                    f"input record {rid} is superseded by {sb}",
                    cell=path,
                    pointer=rid,
                )


def check_liveness(ctx: Ctx) -> None:
    """Informational only: OPEN cells whose missing_quantity appears in ledger text."""
    open_cells = [
        (k, c) for k, c in ctx.cells.items() if c.get("verdict") == "OPEN"
    ]
    if not open_cells:
        return
    # Build a cheap corpus from proposals + hypotheses
    corpus_files = list((ctx.ledger_root / "proposals").glob("*.yaml"))
    corpus_files += list((ctx.ledger_root / "hypotheses").glob("*.yaml"))
    texts: list[tuple[str, str]] = []
    for p in corpus_files:
        try:
            texts.append((str(p.relative_to(ctx.root)), p.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    for key, cell in open_cells:
        path = cell.get("_path", key)
        mq = cell.get("missing_quantity")
        if not mq:
            continue
        hits = [fp for fp, t in texts if mq in t]
        if hits:
            ctx.info(
                "liveness",
                f"OPEN missing_quantity {mq!r} appears in {len(hits)} ledger file(s); possibly closeable",
                cell=path,
                pointer=hits[0],
            )


def emit_view(ctx: Ctx, out_path: Path) -> None:
    rows: dict[str, dict[str, Any]] = {}
    for key, cell in sorted(ctx.cells.items()):
        curve = cell["curve_row"]
        col = cell["method_column"]
        rows.setdefault(curve, {})
        rows[curve][col] = {
            "verdict": cell.get("verdict"),
            "unit": cell.get("unit"),
            "m": cell.get("m"),
            "floor_bits": cell.get("floor_bits"),
            "budget_bits": cell.get("budget_bits"),
            "provenance_tier": cell.get("provenance_tier"),
            "path": cell.get("_path"),
            "superseded_by": cell.get("superseded_by"),
        }
    doc = {
        "generated_by": "tools/validate_reachability_table.py",
        "experiment_id": "EXP-BINSTD-f9a860",
        "note": (
            "GENERATED VIEW — do not commit. Rebuild from per-cell shards. "
            "No break / attack-cost claim."
        ),
        "cell_count": len(ctx.cells),
        "rows": rows,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False)
    ctx.info("view", f"wrote generated view to {out_path.relative_to(ctx.root)}")


def run_all(ctx: Ctx, emit: bool, view_path: Path) -> int:
    load_cells(ctx)
    check_schema(ctx)
    check_certificate_hashes(ctx)
    check_supersession(ctx)
    check_liveness(ctx)
    if emit:
        emit_view(ctx, view_path)
    return 1 if ctx.errors else 0


def findings_as_dicts(ctx: Ctx) -> list[dict[str, Any]]:
    return [
        {
            "severity": f.severity,
            "check": f.check,
            "cell": f.cell,
            "message": f.message,
            "pointer": f.pointer,
        }
        for f in ctx.findings
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="repository root",
    )
    ap.add_argument(
        "--reachability",
        type=Path,
        default=None,
        help="per-cell shard directory (default: analysis/binstd-curve-audit/reachability)",
    )
    ap.add_argument(
        "--ledger-root",
        type=Path,
        default=None,
        help="ledger root for supersession/liveness (default: <root>/ledger)",
    )
    ap.add_argument(
        "--emit-view",
        action="store_true",
        help="write gitignored generated table view",
    )
    ap.add_argument(
        "--view-path",
        type=Path,
        default=None,
        help="override generated view path",
    )
    ap.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="optional machine-readable findings path",
    )
    ap.add_argument(
        "--quiet",
        action="store_true",
        help="suppress human findings on stdout",
    )
    args = ap.parse_args(argv)

    root = args.root.resolve()
    reachability = (args.reachability or (root / "analysis/binstd-curve-audit/reachability")).resolve()
    ledger_root = (args.ledger_root or (root / "ledger")).resolve()
    view_path = (args.view_path or (root / "analysis/binstd-curve-audit/reachability_table.generated.yaml")).resolve()

    ctx = Ctx(root=root, reachability=reachability, ledger_root=ledger_root)
    rc = run_all(ctx, emit=args.emit_view, view_path=view_path)

    if not args.quiet:
        for f in ctx.findings:
            loc = f.cell or "-"
            ptr = f" pointer={f.pointer}" if f.pointer else ""
            print(f"[{f.severity}] {f.check} cell={loc}{ptr}: {f.message}")
        print(
            f"summary: cells={len(ctx.cells)} errors={len(ctx.errors)} "
            f"warnings={sum(1 for x in ctx.findings if x.severity=='warning')} "
            f"info={sum(1 for x in ctx.findings if x.severity=='info')} rc={rc}"
        )

    if args.json_out:
        payload = {
            "rc": rc,
            "cell_count": len(ctx.cells),
            "error_count": len(ctx.errors),
            "findings": findings_as_dicts(ctx),
        }
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return rc


if __name__ == "__main__":
    sys.exit(main())
