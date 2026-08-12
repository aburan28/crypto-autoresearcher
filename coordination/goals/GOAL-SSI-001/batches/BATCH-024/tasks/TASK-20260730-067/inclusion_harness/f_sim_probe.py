"""Honest scaffold-local F_sim channel treatment (TASK-20260730-067).

BATCH-012 definition:
  F_sim = { the invocation does not emit its complete declared simulator
            report for the supplied arguments }.

Honesty rules retained from BATCH-012/017/023:
- Normal complete report production is F_sim^c and is NOT success under F
  (report-only completion is already a failure mode relative to Verify).
- There is no implementation-derived F_sim → F implication that would
  clear QUERY_MEMORY.
- BATCH-022 FailureChannel enum has no F_sim member; this probe wires a
  write-scope-local tracker only.

Do NOT invent CollimationSieve APIs. Zero curve compute.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .scaffold_import import import_scaffold_modules


@dataclass
class SimulatorReport:
    """Scaffold-local declared simulator report (write-scope only)."""

    arguments: Dict[str, Any]
    sections_required: List[str]
    sections_emitted: List[str] = field(default_factory=list)
    complete: bool = False

    def emit_section(self, name: str) -> None:
        if name not in self.sections_emitted:
            self.sections_emitted.append(name)
        self.complete = set(self.sections_required).issubset(set(self.sections_emitted))


@dataclass
class FSimOutcome:
    in_F_sim: bool
    report_complete: bool
    maps_to_F: bool
    in_common_F_via_report_only_rule: Optional[bool]
    note: str


class ScaffoldLocalSimulator:
    """Write-scope F_sim tracker; not a BATCH-022 FailureChannel."""

    REQUIRED_SECTIONS = ("schedule", "sieve_stats", "report_footer")

    def __init__(self) -> None:
        self.last_report: Optional[SimulatorReport] = None

    def start(self, arguments: Dict[str, Any]) -> SimulatorReport:
        self.last_report = SimulatorReport(
            arguments=dict(arguments),
            sections_required=list(self.REQUIRED_SECTIONS),
        )
        return self.last_report

    def classify(self) -> FSimOutcome:
        if self.last_report is None:
            return FSimOutcome(
                in_F_sim=True,
                report_complete=False,
                maps_to_F=False,
                in_common_F_via_report_only_rule=None,
                note="No report started; F_sim by definition; no F_sim→F map.",
            )
        in_f_sim = not self.last_report.complete
        # recovery_spec: report-only completion (even complete) is not success
        # under F — but that is NOT an F_sim→F implication.
        report_only_in_F = True  # no Verify performed in this simulator channel
        return FSimOutcome(
            in_F_sim=in_f_sim,
            report_complete=self.last_report.complete,
            maps_to_F=False,
            in_common_F_via_report_only_rule=report_only_in_F,
            note=(
                "F_sim tracks incomplete declared report only. "
                "F_sim^c (complete report) is still not Verify-success; "
                "report-only ∈ F by recovery_spec, but that does not "
                "constitute an F_sim→F map and does not clear QUERY_MEMORY."
            ),
        )


def probe_f_sim_treatment() -> Dict[str, Any]:
    """Exercise scaffold-local F_sim; certify no F_sim→F clearance map."""
    mods = import_scaffold_modules()
    FailureChannel = mods["types"].FailureChannel
    enum_names = [c.value for c in FailureChannel]
    f_sim_in_batch022_enum = "F_sim" in enum_names

    sim = ScaffoldLocalSimulator()

    # Path A: incomplete report ⇒ in F_sim; maps_to_F remains false.
    report_incomplete = sim.start({"args": "symbolic"})
    report_incomplete.emit_section("schedule")
    # deliberately omit sieve_stats and report_footer
    out_incomplete = sim.classify()

    # Path B: complete report ⇒ F_sim^c; still not Verify-success; no F_sim→F.
    sim2 = ScaffoldLocalSimulator()
    report_complete = sim2.start({"args": "symbolic"})
    for section in ScaffoldLocalSimulator.REQUIRED_SECTIONS:
        report_complete.emit_section(section)
    out_complete = sim2.classify()

    # Negative control: BATCH-022 enum still has no F_sim.
    # Attempting to treat F_sim as FailureChannel.F_* would be illicit.
    illicit_map_refused = (
        not f_sim_in_batch022_enum
        and out_incomplete.maps_to_F is False
        and out_complete.maps_to_F is False
    )

    return {
        "definition_ref": "BATCH-012 process_extraction / recovery_spec",
        "definition": (
            "F_sim = { the invocation does not emit its complete declared "
            "simulator report for the supplied arguments }"
        ),
        "batch022_FailureChannel_enum_has_F_sim": f_sim_in_batch022_enum,
        "scaffold_local_channel_wired": True,
        "scaffold_local_channel_scope": "write_scope_TASK-20260730-067_only",
        "treatment_status": "scaffold_local_wired_no_map_to_F",
        "maps_to_F": False,
        "map_status": "no_implementation_derived_implication",
        "query_memory_cleared_by_f_sim": False,
        "paths": {
            "incomplete_report": {
                "in_F_sim": out_incomplete.in_F_sim,
                "report_complete": out_incomplete.report_complete,
                "maps_to_F": out_incomplete.maps_to_F,
                "sections_emitted": list(report_incomplete.sections_emitted),
                "note": out_incomplete.note,
            },
            "complete_report_F_sim_complement": {
                "in_F_sim": out_complete.in_F_sim,
                "report_complete": out_complete.report_complete,
                "maps_to_F": out_complete.maps_to_F,
                "in_common_F_via_report_only_rule": (
                    out_complete.in_common_F_via_report_only_rule
                ),
                "sections_emitted": list(report_complete.sections_emitted),
                "note": out_complete.note,
            },
        },
        "illicit_F_sim_to_F_map_refused": illicit_map_refused,
        "honesty": (
            "Wired a write-scope-local F_sim completeness tracker. Certified "
            "absence of F_sim from BATCH-022 FailureChannel enum. Explicitly "
            "refuse F_sim→F implication. Report-only completion remains a "
            "failure relative to Verify under recovery_spec without being an "
            "F_sim→F map. Not QUERY_MEMORY clearance."
        ),
        "summary": {
            "f_sim_channel_present_locally": True,
            "f_sim_in_batch022_enum": f_sim_in_batch022_enum,
            "f_sim_to_F_map_exists": False,
            "query_memory_cleared": False,
        },
    }
