#!/usr/bin/env python3
"""Compose the run schema's five companion artifacts for a MULTI-INVOCATION run.

Written by the Coordinator on 2026-09-16, after tools/validate_ledger.py reported six
schema errors against this run that the epoch-1 -> epoch-2 supersession routed but did
not clear, because they are real: the run schema
(tools/validate_ledger.py:741-771) models ONE command per run -- one command.txt, one
stdout.log, one stderr.log, one raw-result.json -- and this run is an acceptance harness
that made many independent invocations across two epochs, writing per-invocation logs.

This script DERIVES the four missing companions from bytes already committed. It
fabricates nothing:

  command.txt      the commands each epoch actually RECORDED, quoted from the manifests
                   and from the argv that epoch 1's own JSON outputs captured, with the
                   epoch-1 wrapper invocations whose argv NOTHING RECORDS listed as
                   unrecoverable rather than reconstructed.
  stdout.log       a delimited concatenation of the per-invocation .out files, each
                   section naming its source path and that file's sha256, so any section
                   can be checked against the file it came from.
  stderr.log       the same for .err files.
  raw-result.json  a composition that EMBEDS the machine-readable rows (results.jsonl,
                   results_engine.jsonl, acceptance.json) and REFERENCES the epoch-1
                   measurement JSONs by path and hash.

Nothing here is a measurement and nothing here is new evidence. Re-running this script
on an unchanged tree reproduces all four files byte-for-byte, which is the only property
that makes a derived artifact worth committing.

THE ONE GAP THIS SCRIPT DISCLOSES AND CANNOT FILL: epoch 1's manifest carries no
`commands` block and its PROGRESS.md records no invocation strings, so for three of its
phases the exact command is UNRECORDED. The artifact policy requires the exact command,
so that is a real defect of the epoch-1 record. It is reported in command.txt and in
manifest_v2.yaml's `code.command_completeness`, not papered over.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import yaml

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: str) -> str:
    return os.path.relpath(path, RUN)


def load_manifests() -> tuple[dict, dict]:
    with open(os.path.join(RUN, "manifest.yaml"), encoding="utf-8") as handle:
        e1 = yaml.safe_load(handle)["run"]
    with open(os.path.join(RUN, "manifest-epoch2.yaml"), encoding="utf-8") as handle:
        e2 = yaml.safe_load(handle)["run"]
    return e1, e2


def epoch1_recovered_argv() -> list[tuple[str, str]]:
    """Return (source pointer, command) for every argv epoch 1's JSONs actually recorded."""
    out: list[tuple[str, str]] = []
    for name in sorted(os.listdir(os.path.join(RUN, "logs"))):
        if not name.endswith(".json"):
            continue
        path = os.path.join(RUN, "logs", name)
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
        hits: list[tuple[str, object]] = []

        def walk(node: object, prefix: str = "") -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    if key in ("argv", "command", "cmd"):
                        hits.append((prefix + key, value))
                    else:
                        walk(value, prefix + key + ".")
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, prefix + "[%d]." % index)

        walk(doc)
        for pointer, value in hits:
            text = " ".join(value) if isinstance(value, list) else str(value)
            out.append(("logs/%s :: %s" % (name, pointer), text))
    return out


def write_command_txt(e1: dict, e2: dict) -> None:
    lines: list[str] = []
    lines.append("# RUN-ICPERF-a4a24b -- exact commands, composed 2026-09-16")
    lines.append("#")
    lines.append("# DERIVED FILE. The run schema expects one command per run; this run made many")
    lines.append("# across two epochs. Every line below is quoted from a committed artifact, and the")
    lines.append("# artifact it came from is named. Generator: accept/compose_companions.py.")
    lines.append("#")
    lines.append("# Epoch 1 stopped mid-measurement on a model-quota exhaustion; epoch 2 resumed the")
    lines.append("# remaining phases under the same frozen contract and the same verified code tree.")
    lines.append("")

    lines.append("## EPOCH 2 -- recorded in manifest-epoch2.yaml `commands` (complete)")
    lines.append("")
    for item in e2.get("commands") or []:
        lines.append("# phase: %s" % item.get("phase", "(unnamed)"))
        if item.get("cwd"):
            lines.append("# cwd: %s" % item["cwd"])
        lines.append(str(item.get("command", "")).strip())
        for key in ("stdout", "stderr"):
            if item.get(key):
                lines.append("#   %s -> %s" % (key, item[key]))
        for log in item.get("engine_logs") or []:
            lines.append("#   engine log -> %s" % log)
        if item.get("engine_argv"):
            lines.append("#   engine argv -> %s" % " ".join(str(a) for a in item["engine_argv"]))
        lines.append("")

    lines.append("## EPOCH 1 -- NO `commands` BLOCK EXISTS IN manifest.yaml")
    lines.append("#")
    lines.append("# manifest.yaml records epoch 1's code tree, inputs, timings, resources and")
    lines.append("# per-criterion verdicts, but no invocation strings, and logs/PROGRESS.md records")
    lines.append("# none either. THIS IS A REAL DEFECT OF THE EPOCH-1 RECORD against the artifact")
    lines.append("# policy's 'exact command' requirement, and it is disclosed rather than filled:")
    lines.append("# reconstructing a plausible command line would be a fabrication under core rule 9.")
    lines.append("#")
    lines.append("# What IS recoverable: epoch 1's own JSON outputs captured the argv of the child")
    lines.append("# processes they spawned. Those are quoted verbatim below, with their source.")
    lines.append("")
    recovered = epoch1_recovered_argv()
    if recovered:
        for pointer, text in recovered:
            lines.append("# recovered from %s" % pointer)
            lines.append(text.strip())
            lines.append("")
    else:
        lines.append("# (none recovered)")
        lines.append("")

    lines.append("# UNRECOVERABLE -- wrapper invocations named by their own output but with no argv")
    lines.append("# recorded in any committed artifact. Each JSON below carries an `invocation` label")
    lines.append("# and its measurements, so WHAT ran is known and the exact ARGV is not:")
    for name in ("probe_check", "sumreg", "watchdog_null"):
        path = os.path.join(RUN, "logs", name + ".json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                label = json.load(handle).get("invocation")
            lines.append("#   logs/%s.json  invocation=%r  argv: NOT RECORDED" % (name, label))
    lines.append("")
    with open(os.path.join(RUN, "command.txt"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def write_stream_log(suffix: str, out_name: str) -> None:
    logs = sorted(
        name for name in os.listdir(os.path.join(RUN, "logs"))
        if name.endswith(suffix)
    )
    parts: list[str] = []
    parts.append("=" * 78)
    parts.append("RUN-ICPERF-a4a24b -- composed %s, 2026-09-16" % out_name)
    parts.append("")
    parts.append("DERIVED FILE. This run made many invocations across two epochs and each wrote")
    parts.append("its own log; the run schema expects a single %s. This is a delimited" % out_name)
    parts.append("concatenation of every logs/*%s in sorted order. Each section names its" % suffix)
    parts.append("source path and that file's sha256, so any section can be verified against the")
    parts.append("file it was taken from. No content is edited, reordered within a file, or omitted.")
    parts.append("Generator: accept/compose_companions.py.")
    parts.append("=" * 78)
    parts.append("")
    for name in logs:
        path = os.path.join(RUN, "logs", name)
        size = os.path.getsize(path)
        parts.append("-" * 78)
        parts.append("BEGIN logs/%s" % name)
        parts.append("  sha256: %s" % sha256(path))
        parts.append("  bytes:  %d%s" % (size, "  (empty)" if size == 0 else ""))
        parts.append("-" * 78)
        with open(path, encoding="utf-8", errors="replace") as handle:
            body = handle.read()
        parts.append(body if body.endswith("\n") or not body else body + "\n")
        parts.append("END logs/%s" % name)
        parts.append("")
    with open(os.path.join(RUN, out_name), "w", encoding="utf-8") as handle:
        handle.write("\n".join(parts))


def write_raw_result() -> None:
    def jsonl(name: str) -> list[dict]:
        path = os.path.join(RUN, name)
        if not os.path.exists(path):
            return []
        rows = []
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def embed(name: str) -> object:
        path = os.path.join(RUN, name)
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    referenced = {}
    for name in ("logs/probe_check.json", "logs/sumreg.json",
                 "logs/watchdog_null.json", "logs/mem_headroom_probe.json"):
        path = os.path.join(RUN, name)
        if os.path.exists(path):
            referenced[name] = {"sha256": sha256(path),
                                "bytes": os.path.getsize(path)}

    doc = {
        "_composed": {
            "what": "RUN-ICPERF-a4a24b raw machine-readable results, composed 2026-09-16",
            "why": (
                "DERIVED FILE. The run schema requires one raw-result.json; this run wrote "
                "its rows across several files over two epochs. This composition embeds the "
                "row-level results and the acceptance table verbatim and REFERENCES the "
                "epoch-1 measurement JSONs by path and sha256 rather than copying them, so "
                "there is exactly one authoritative copy of each measurement."),
            "not_a_measurement": (
                "Nothing here was computed by this file. Every value is a copy of, or a "
                "pointer to, bytes committed by the executor."),
            "generator": "accept/compose_companions.py",
            "sources_embedded": ["results.jsonl", "results_engine.jsonl", "acceptance.json"],
            "sources_referenced": sorted(referenced),
        },
        "results_watchdog_control": jsonl("results.jsonl"),
        "results_engine": jsonl("results_engine.jsonl"),
        "acceptance": embed("acceptance.json"),
        "epoch_1_measurement_json": referenced,
    }
    with open(os.path.join(RUN, "raw-result.json"), "w", encoding="utf-8") as handle:
        json.dump(doc, handle, indent=2, sort_keys=False)
        handle.write("\n")


def main() -> int:
    e1, e2 = load_manifests()
    write_command_txt(e1, e2)
    write_stream_log(".out", "stdout.log")
    write_stream_log(".err", "stderr.log")
    write_raw_result()
    for name in ("command.txt", "stdout.log", "stderr.log", "raw-result.json"):
        path = os.path.join(RUN, name)
        print("%-18s %8d bytes  sha256 %s" % (name, os.path.getsize(path), sha256(path)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
