#!/usr/bin/env python3
"""J1 only: verify frozen source custody, offsets, and direct-host retrieval."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import platform
import ssl
import subprocess
import sys
import urllib.error
import urllib.request

import yaml
from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas


HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "AGENTS.md").exists())
REL = pathlib.Path("coordination/goals/GOAL-SCURVE-48e06c/batches/BATCH-aa389e")
SOURCE = ROOT / REL / "tasks/TASK-20261001-762c5f"
RECEIPT = ROOT / REL / "archives/TASK-20261011-071e47/snapshot-receipt.json"
PLAN = ROOT / "coordination/review/scurve-l5-20261011/review-plan.yaml"
HOST = "https://safecurves.cr.yp.to/"
PAGES = ("base", "equation", "field", "transfer")
TASK = "TASK-20261011-ae5aa8"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bytes_at(data: bytes, value: str) -> list[int]:
    needle = value.encode("ascii")
    result = []
    start = 0
    while (pos := data.find(needle, start)) != -1:
        result.append(pos)
        start = pos + 1
    return result


def position(data: bytes, offset: int) -> dict:
    line = data[:offset].count(b"\n") + 1
    column = offset - (data.rfind(b"\n", 0, offset) + 1) + 1
    return {"byte_offset_zero_based": offset, "line_one_based": line, "column_one_based": column}


def draw_visual(route_ok: bool, values_ok: bool) -> Drawing:
    d = Drawing(540, 180)
    navy, green, amber, grey = map(HexColor, ("#18324f", "#237f51", "#ad6a08", "#526071"))
    boxes = [
        (8, 96, 144, 58, "Producer snapshot", "5 custody hashes match", green),
        (196, 96, 144, 58, "Frozen HTML", "6 offsets match", green if values_ok else amber),
        (384, 96, 144, 58, "Claimed tuple", "6 digit strings bound", green if values_ok else amber),
        (196, 4, 144, 58, "Direct host", "4 raw URLs attempted", green if route_ok else amber),
    ]
    for x, y, w, h, title, subtitle, color in boxes:
        d.add(Rect(x, y, w, h, rx=8, ry=8, fillColor=color, strokeColor=color))
        d.add(String(x + 10, y + 33, title, fontName="Helvetica-Bold", fontSize=11, fillColor=HexColor("#ffffff")))
        d.add(String(x + 10, y + 15, subtitle, fontName="Helvetica", fontSize=8, fillColor=HexColor("#ffffff")))
    for a, b, c, e in [(152, 125, 196, 125), (340, 125, 384, 125), (268, 96, 268, 62)]:
        d.add(Line(a, b, c, e, strokeColor=navy, strokeWidth=2))
    d.add(String(350, 37, "Primary-host provenance", fontName="Helvetica-Bold", fontSize=9, fillColor=grey))
    d.add(String(350, 23, "verified" if route_ok else "unresolved: retrieval unavailable", fontName="Helvetica", fontSize=9, fillColor=green if route_ok else amber))
    d.add(String(8, 169, f"{TASK}  |  source-provenance joint only", fontName="Helvetica-Bold", fontSize=10, fillColor=navy))
    return d


def make_pdf(report: dict, drawing: Drawing) -> None:
    out = HERE / "report.pdf"
    c = canvas.Canvas(str(out), pagesize=letter)
    width, height = letter
    y = height - 42

    def paragraph(text: str, *, size: int = 9, bold: bool = False, gap: int = 8) -> None:
        nonlocal y
        font = "Helvetica-Bold" if bold else "Helvetica"
        lines = simpleSplit(str(text), font, size, width - 88)
        if y - (len(lines) * (size + 3)) - gap < 48:
            c.showPage()
            y = height - 42
        c.setFont(font, size)
        for line in lines:
            c.drawString(44, y, line)
            y -= size + 3
        y -= gap

    paragraph("SCURVE L5 J1 | independent source-provenance review", size=15, bold=True, gap=13)
    paragraph(f"Task {TASK}  |  {report['recorded_at_utc']}")
    paragraph(f"Joint verdict: {report['verdict'].upper()}", size=11, bold=True)
    paragraph(report["finding"], size=9)
    y -= 4
    renderPDF.draw(drawing, c, 36, y - 180)
    y -= 202
    paragraph("Observation", bold=True)
    paragraph("The snapshot receipt hashes match the source-binding YAML and four frozen HTML files. Each of p, a, b, x1, y1, and l occurs at its recorded zero-based byte offset and one-based line; its digit string matches the plan tuple.")
    paragraph("Independent route", bold=True)
    paragraph("Four HTTPS URLs on safecurves.cr.yp.to were attempted through Python urllib with proxies disabled and default TLS verification. The run-specific URL, time, response/failure, byte length, SHA-256, and offsets are retained in replay.stdout.txt and review-report.yaml.")
    paragraph("Inference and limit", bold=True)
    paragraph(report["inference"])
    paragraph("This joint assesses source binding only. It supplies no arithmetic, transfer, attack-cost, SafeCurves criterion, or curve-safety verdict.")
    paragraph("Source and output pointers", bold=True)
    paragraph("Frozen receipt: TASK-20261011-071e47/snapshot-receipt.json; producer source-binding: TASK-20261001-762c5f/source-binding.yaml; full replay output and exact offsets: this task's replay.stdout.txt and review-report.yaml.")
    c.showPage()
    c.save()


def main() -> None:
    receipt = json.loads(RECEIPT.read_bytes())
    names = ["source-binding.yaml"] + [f"safecurves-{page}.html" for page in PAGES]
    custody = {}
    frozen = {}
    for name in names:
        path = SOURCE / name
        data = path.read_bytes()
        key = str(path.relative_to(ROOT))
        expected = receipt["source_paths"][key]
        actual = {"path": key, "size_bytes": len(data), "sha256": digest(data),
                  "receipt_size_bytes": expected["size_bytes"], "receipt_sha256": expected["sha256"]}
        actual["matches_receipt"] = actual["size_bytes"] == actual["receipt_size_bytes"] and actual["sha256"] == actual["receipt_sha256"]
        custody[name] = actual
        frozen[name] = data
    if not all(item["matches_receipt"] for item in custody.values()):
        print(json.dumps({"fatal": "source custody mismatch; source claims were not read", "custody": custody}, indent=2))
        raise SystemExit(2)

    binding = yaml.safe_load(frozen["source-binding.yaml"])
    plan = yaml.safe_load(PLAN.read_bytes())["review_plan"]
    parameters = plan["blind_rederivation"]["parameters"]
    local_values = {}
    for row in binding["value_table"]:
        name, value, filename = row["value"], str(row["string"]), row["file"]
        data = frozen[filename]
        offset = row["byte_offset"]
        located = position(data, offset)
        exact = data[offset:offset + len(value)] == value.encode("ascii")
        row_start = data.rfind(b"<tr>", 0, offset)
        row_end = data.find(b"</tr>", offset)
        row_bytes = data[row_start:row_end] if row_start >= 0 and row_end >= 0 else b""
        local_values[name] = {
            "value": value, "url": HOST + filename.removeprefix("safecurves-"),
            "frozen_file": filename, "frozen_sha256": custody[filename]["sha256"],
            "cited_offset_zero_based": offset, "cited_line_one_based": row["line"],
            "actual_position": located, "all_frozen_occurrences_zero_based": bytes_at(data, value),
            "exact_at_cited_offset": exact, "line_matches": located["line_one_based"] == row["line"],
            "matches_plan_parameter": value == str(parameters[name]),
            "frozen_html_row_contains_anomalous_label": b"Anomalous" in row_bytes,
            "producer_provenance_label": row["provenance"],
            "frozen_line_ascii": data.splitlines()[row["line"] - 1].decode("ascii", "replace"),
        }

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    attempts = {}
    raw = {}
    for page in PAGES:
        url = HOST + page + ".html"
        item = {"url": url, "transport_route": "direct HTTPS via urllib; ProxyHandler({}); system DNS; default TLS verification",
                "attempted_at_utc": utc_now(), "response_status": None, "final_url": None,
                "returned_bytes": None, "returned_sha256": None, "failure": None}
        try:
            with opener.open(urllib.request.Request(url, headers={"User-Agent": "SCURVE-L5-J1-review/1"}), timeout=10) as response:
                data = response.read()
                raw[page] = data
                item.update(response_status=response.status, final_url=response.geturl(),
                            returned_bytes=len(data), returned_sha256=digest(data))
        except Exception as exc:
            reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
            item["failure"] = {"class": type(reason).__name__, "detail": str(reason)}
        item["finished_at_utc"] = utc_now()
        attempts[page] = item

    for name, value in local_values.items():
        page = value["frozen_file"].removeprefix("safecurves-").removesuffix(".html")
        data = raw.get(page)
        if data is None:
            value["direct_host_occurrences_zero_based"] = None
            value["direct_host_exact_at_cited_offset"] = None
            value["direct_host_absence_reason"] = attempts[page]["failure"]
        else:
            value["direct_host_occurrences_zero_based"] = bytes_at(data, value["value"])
            value["direct_host_exact_at_cited_offset"] = data[value["cited_offset_zero_based"]:value["cited_offset_zero_based"] + len(value["value"])] == value["value"].encode("ascii")
            value["direct_host_absence_reason"] = None

    frozen_ok = all(v["exact_at_cited_offset"] and v["line_matches"] and v["matches_plan_parameter"]
                    and v["frozen_html_row_contains_anomalous_label"] for v in local_values.values())
    direct_ok = all(attempts[p]["response_status"] == 200 for p in PAGES)
    direct_values_ok = direct_ok and all(v["direct_host_occurrences_zero_based"] for v in local_values.values())
    direct_identical = direct_ok and all(attempts[p]["returned_sha256"] == custody[f"safecurves-{p}.html"]["sha256"] for p in PAGES)
    if not frozen_ok or (direct_ok and not direct_values_ok):
        verdict = "breaks"
        finding = "The exact frozen tuple binding or independently fetched source values contradict the producer record."
        inference = "The source-binding claim fails within J1's tested scope; inspect per-value offsets and hashes before using the tuple as externally sourced."
    elif direct_ok and direct_identical:
        verdict = "holds"
        finding = "The four direct-host byte streams match the frozen source files, and all six integer offsets agree with the plan tuple."
        inference = "Direct-host source binding is reproduced for these four URLs and this retrieval time; this does not assess the separate arithmetic or security claims."
    else:
        verdict = "inconclusive"
        finding = "The frozen source custody and six integer offsets agree, but this session did not reproduce all four direct-host byte streams."
        inference = "The producer's primary_host_direct label remains an unverified producer statement. C-1 remains unresolved; network failure is not mathematical evidence."

    recorded = utc_now()
    report = {
        "review_report": {
            "task_id": TASK, "goal_id": "GOAL-SCURVE-48e06c", "batch_id": "BATCH-aa389e",
            "review_plan": str(PLAN.relative_to(ROOT)), "joint": "J1 -- source provenance and exact tuple binding",
            "recorded_at_utc": recorded, "verdict": verdict, "finding": finding,
            "observations": [
                "Snapshot custody hashes verified before reading the frozen source claims.",
                "The six frozen value strings were checked at the producer's cited zero-based byte offsets and one-based lines.",
                "Direct HTTPS retrieval was attempted independently for all four page URLs without a proxy.",
            ],
            "comparison": {"frozen_offsets_and_plan_tuple_all_match": frozen_ok,
                           "all_four_direct_http_200": direct_ok,
                           "direct_tuple_strings_all_present": bool(direct_values_ok),
                           "all_four_direct_bytes_identical_to_frozen": bool(direct_identical)},
            "inference": inference,
            "provenance_label_assessment": "reproduced_direct_host" if direct_identical else "producer_reported_primary_host_direct_unverified",
            "capsule_conflict_C_1": "closed_for_direct_provenance" if direct_identical else "unresolved",
            "producer_route_claim": {"source_route_taken": binding["source_route_taken"],
                                      "fallback_routes_run": binding["fallback_routes_run"],
                                      "limitation": "The source-binding file does not retain exact producer URLs, curl commands, retrieval times, response headers, or peer addresses."},
            "custody": custody, "direct_retrieval_attempts": attempts, "values": local_values,
            "earlier_access_observations": [
                {"route": "local system DNS precheck", "host": "safecurves.cr.yp.to",
                 "time_utc": "2026-10-11T17:21:38.918017+00:00", "result": "gaierror [Errno 8] nodename nor servname provided, or not known",
                 "http_status": None, "returned_bytes": None, "sha256": None},
                {"route": "web.open mediated retrieval; not a raw primary-host byte stream",
                 "time_utc": None, "time_absence_reason": "tool did not expose retrieval timestamps",
                 "urls_and_tool_statuses": {HOST + "base.html": "400 Timeout fetching",
                                           HOST + "equation.html": "502 Bad Gateway",
                                           HOST + "field.html": "400 Timeout fetching",
                                           HOST + "transfer.html": "400 Timeout fetching"},
                 "returned_bytes": None, "sha256": None},
                {"route": "first replay.py invocation, direct HTTPS no proxy",
                 "time_utc": None, "time_absence_reason": "stdout was redirected but the script failed before printing while rendering SVG; per-URL transport receipts were not retained",
                 "known_failure": "renderSVG AttributeError: 'str' object has no attribute 'red'",
                 "http_status": None, "returned_bytes": None, "sha256": None},
            ],
            "negative_or_inconclusive_details": [
                "Unsuccessful retrieval leaves direct-host provenance unverified; it does not contradict the six frozen strings or the separate C4 arithmetic.",
                "No J1 source mismatch was observed in the frozen files." if frozen_ok else "A frozen binding mismatch is recorded in the per-value table.",
            ],
            "scope_limit": "J1 only; no C1-C4 arithmetic, controls, transfer, attack-cost, SafeCurves criterion, or safety verdict.",
            "review_attestation": {
                "task_id": TASK, "joints_owned": ["J1 -- source provenance and exact tuple binding"],
                "verdict": verdict, "read_sibling_reports": False,
                "sources_read": ["AGENTS.md", ".claude/skills/research-visuals/SKILL.md",
                                 "ledger/handoffs/TASK-20261011-ae5aa8.yaml",
                                 "tools/check_review_independence.py",
                                 str(RECEIPT.relative_to(ROOT)), str(PLAN.relative_to(ROOT))]
                                + [str((SOURCE / name).relative_to(ROOT)) for name in names],
                "sibling_reports_read": [], "sibling_reports_read_count": 0,
                "repo_history_read": "git log -1 only; no sibling report or producer arithmetic output read",
                "execution_receipts": [{"command": "python3 replay.py > replay.stdout.txt", "interpreter": sys.executable,
                                        "python_version": platform.python_version(), "recorded_at_utc": recorded}],
            },
            "visual_record": {"diagram": "diagram.svg", "pdf": "report.pdf",
                              "canonical_graph_check": "No canonical graph changed: J1 has no verified new mathematical edge or frontier measurement."},
            "procedure_deviations": ["agents/reviewer.md is absent in this checkout; the handoff, review plan, and AGENTS.md supplied the J1 scope.",
                                     "An earlier replay invocation fetched before its SVG renderer failed and printed no transport receipts; exact per-URL time/status are unavailable for that invocation. The successful replay records all four later attempts."],
        }
    }
    drawing = draw_visual(direct_identical, frozen_ok)
    renderSVG.drawToFile(drawing, str(HERE / "diagram.svg"))
    (HERE / "review-report.yaml").write_text(yaml.safe_dump(report, sort_keys=False, allow_unicode=True), encoding="utf-8")
    make_pdf(report["review_report"], drawing)
    print(json.dumps({"task_id": TASK, "recorded_at_utc": recorded, "verdict": verdict,
                      "custody": custody, "direct_retrieval_attempts": attempts,
                      "values": local_values, "comparison": report["review_report"]["comparison"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
