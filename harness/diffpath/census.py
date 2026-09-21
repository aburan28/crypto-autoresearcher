"""The CENSUS: what differential paths this program actually holds.

THREE COUNTS, REPORTED SEPARATELY AND NEVER SUMMED (contract metrics.primary):

  readable                entries with real path data, from a source an agent
                          in this program ACTUALLY OPENED
  quarantined_not_read    pointers to content this task may not read (BCP-1)
  acquisition_gap         pointers to sources this task could not open

Only `readable` entries are canonicalised, counted in an orbit, or contribute
to any covering number.  Every covering number reported must state how many
pointers it excluded.

IR-2: NO CENSUS ENTRY IS POPULATED FROM RECOLLECTION.  A source not opened is
an acquisition-gap pointer with path_data None.  AN EMPTY READABLE CENSUS IS A
CORRECT AND COMPLETE OUTCOME -- it is the frozen contract's pre-registered
prediction P-1 (readable_md5 = 0, readable_sha1 = 0), and it is reported as the
measured acquisition gap it is, never quietly filled in.

IR-1 / IR-10: the scanner NEVER descends into
coordination/goals/GOAL-MD5-001/quarantine/**, and this module performs no
network access of any kind.  The quarantined payload is opened ONLY in binary
mode by `quarantine_attestation()`, which hashes the bytes and never decodes,
parses or inspects them.
"""
from __future__ import annotations

import hashlib
import os
import random
import re
from dataclasses import dataclass, field

from .pathobj import PathObject, plant_from_pair, seeded_pair

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

QUARANTINE_DIR = "coordination/goals/GOAL-MD5-001/quarantine"
QUARANTINE_FILE = f"{QUARANTINE_DIR}/MD5-COLLISION-PATH-WANG-2004-199.yaml"
QUARANTINE_EXPECTED_SHA256 = (
    "e44a3fed81e9e7621697432b2124b357fc2c3f502f4bc6779df5c377b0a3e3c5")

SCAN_ROOTS = ("knowledge", "inputs")
SCAN_SUFFIXES = (".md", ".yaml", ".yml", ".json", ".txt")

# A file is a CANDIDATE if it mentions the subject matter at all.
CANDIDATE_RE = re.compile(
    r"(md5|sha-?0|sha-?1)\b.{0,200}?"
    r"(differential (path|characteristic)|disturbance vector|collision path|"
    r"sufficient condition|message difference|near-collision)",
    re.I | re.S)

# A candidate carries PATH DATA only if it exhibits machine-readable path
# structure: a delta_m / DV word table, or per-step signed differences.  This
# test is deliberately STRUCTURAL: "the paper is cited" is not path data, and
# a scanner that counted mentions would report a census this program does not
# have.
PATH_DATA_RE = (
    re.compile(r"\bdelta_?m\s*[:=]\s*[\[\{]", re.I),
    re.compile(r"\bdisturbance_?vector\s*[:=]\s*[\[\{]", re.I),
    re.compile(r"\bdv\s*[:=]\s*\[\s*(0x)?[0-9a-f]{4,}", re.I),
    re.compile(r"(^|\n)\s*(step|t)\s*[:=]?\s*\d+\s*[,|]\s*(0x)?[0-9a-f]{8}"
               r"\s*[,|]\s*(0x)?[0-9a-f]{8}", re.I),
    re.compile(r"\bsufficient_?conditions?\s*[:=]\s*[\[\{]", re.I),
)


@dataclass
class CensusEntry:
    id: str
    primitive: str
    status: str                 # readable | quarantined_not_read | acquisition_gap
    provenance: str             # recalled | retrieved | kb | internal
    source_ref: str
    citation: str
    tier: str | None = None     # A | B | C  (AMD-20260824-DIFFP-ACQ-1)
    acquisition_status: str | None = None
    sha256: str | None = None
    orbit: str | None = None
    path_data: dict | None = None
    obj: PathObject | None = None
    notes: str = ""

    def to_record(self) -> dict:
        return {
            "id": self.id, "primitive": self.primitive, "status": self.status,
            "provenance": self.provenance, "source_ref": self.source_ref,
            "citation": self.citation, "tier": self.tier,
            "acquisition_status": self.acquisition_status,
            "sha256": self.sha256, "orbit": self.orbit,
            "path_data": self.path_data, "notes": self.notes,
        }


@dataclass
class Census:
    readable: list[CensusEntry] = field(default_factory=list)
    quarantined_not_read: list[CensusEntry] = field(default_factory=list)
    acquisition_gap: list[CensusEntry] = field(default_factory=list)
    shadow: list[CensusEntry] = field(default_factory=list)
    scan: dict = field(default_factory=dict)

    def counts(self) -> dict:
        return {
            "readable": len(self.readable),
            "readable_md5": sum(1 for e in self.readable if e.primitive == "md5"),
            "readable_sha1": sum(1 for e in self.readable if e.primitive == "sha1"),
            "quarantined_not_read": len(self.quarantined_not_read),
            "acquisition_gap": len(self.acquisition_gap),
            "shadow_planted": len(self.shadow),
            "NEVER_SUMMED": "the three counts above are separate populations "
                            "and are not added into a single census size",
        }

    def plantable_entries(self) -> list[CensusEntry]:
        """Entries a candidate could POSSIBLY match -- what makes a null non-vacuous."""
        return [e for e in self.readable + self.shadow if e.obj is not None]


def quarantine_attestation() -> dict:
    """CTL-QUAR: hash the quarantined payload's BYTES; never parse them.

    Opened 'rb', read, hashed, discarded.  The bytes are not decoded, not
    parsed as YAML, not searched, not logged, and no field of the payload is
    inspected.  Permitted and required by IR-1; anything more is a breach.
    """
    path = os.path.join(REPO, QUARANTINE_FILE)
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            size += len(chunk)
            h.update(chunk)
    digest = h.hexdigest()
    return {
        "path": QUARANTINE_FILE,
        "bytes_hashed": size,
        "sha256_recomputed": digest,
        "sha256_expected": QUARANTINE_EXPECTED_SHA256,
        "match": digest == QUARANTINE_EXPECTED_SHA256,
        "read_mode": "rb, streamed, hashed, discarded",
        "parsed": False,
        "attestation": (
            "This task did NOT read, parse, extract, reconstruct or paraphrase "
            "the quarantined payload. Its bytes were streamed into a sha256 "
            "context and discarded without decoding. No field, table, message "
            "word, condition or difference from it entered any artifact of "
            "TASK-20260824-c6625a. No Tier-A content was obtained by any route, "
            "including the network (IR-10): this task made ZERO network "
            "requests."),
    }


def scan_corpus() -> dict:
    """Enumerate every openable source under knowledge/ and inputs/.

    Returns integer counts and the candidate list.  The quarantine directory is
    excluded by prefix BEFORE any file is opened.
    """
    files_seen = 0
    files_read = 0
    unreadable: list[str] = []
    candidates: list[dict] = []
    for root_name in SCAN_ROOTS:
        root = os.path.join(REPO, root_name)
        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, REPO)
            if rel_dir.startswith(QUARANTINE_DIR):
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames
                           if not os.path.join(rel_dir, d).startswith(QUARANTINE_DIR)]
            for fn in sorted(filenames):
                if not fn.endswith(SCAN_SUFFIXES):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, fn), REPO)
                if rel.startswith(QUARANTINE_DIR):
                    continue
                files_seen += 1
                try:
                    with open(os.path.join(REPO, rel), "r", encoding="utf-8",
                              errors="strict") as fh:
                        text = fh.read()
                except (OSError, UnicodeDecodeError):
                    unreadable.append(rel)
                    continue
                files_read += 1
                if not CANDIDATE_RE.search(text):
                    continue
                hits = [r.pattern for r in PATH_DATA_RE if r.search(text)]
                candidates.append({
                    "path": rel,
                    "carries_path_data": bool(hits),
                    "path_data_patterns_matched": hits,
                    "sha256": hashlib.sha256(text.encode()).hexdigest(),
                })
    return {
        "roots": list(SCAN_ROOTS), "suffixes": list(SCAN_SUFFIXES),
        "files_seen": files_seen, "files_read": files_read,
        "files_unreadable": len(unreadable),
        "unreadable_sample": sorted(unreadable)[:10],
        "quarantine_excluded_by_prefix": QUARANTINE_DIR,
        "candidate_files": len(candidates),
        "candidates_carrying_path_data": sum(1 for c in candidates
                                             if c["carries_path_data"]),
        "candidates": candidates,
    }


# ---------------------------------------------------------------------------
# the acquisition-gap list, tier-labelled per AMD-20260824-DIFFP-ACQ-1
# ---------------------------------------------------------------------------
# Bibliographic pointers ONLY.  path_data is None on every one of them.  These
# are `recalled` provenance: this task did not open them, may not open them
# (Tier A/B) or holds no capability to acquire them (IR-10), and a recalled
# reference is a POINTER FOR A REVIEWER AND NEVER SUPPORT (AGENTS.md rule 9).
# They appear here, and only here, so that batch 2's acquisition task is
# specified by measurement rather than by hope.

ACQUISITION_GAP_SPEC = [
    dict(id="AGAP-MD5-WANG-2004-199", primitive="md5", tier="A",
         citation="Wang, Feng, Lai, Yu -- Collisions for Hash Functions MD4, "
                  "MD5, HAVAL-128 and RIPEMD (IACR ePrint 2004/199)",
         source_ref="KN-LIT-87e00e",
         acquisition_status="hard_refusal_tier_a",
         notes="NOT an acquisition target. Listed so the list is complete and "
               "so no later task mistakes its absence for an oversight. Tier A "
               "of AMD-20260824-DIFFP-ACQ-1: not acquired, not fetched, not "
               "parsed, not reconstructed, BY ANY ROUTE, and no escalation is "
               "available to this goal. Its payload is carried instead as the "
               "quarantined_not_read pointer."),
    dict(id="AGAP-MD5-STEVENS-SINGLEBLOCK", primitive="md5", tier="B",
         citation="Stevens -- single-block MD5 collision differential path "
                  "tables (bibliographic pointer only; no path data held)",
         source_ref="recalled:no-KN-LIT-entry-in-this-corpus",
         acquisition_status="blocked_pending_cross_goal_decision",
         notes="Tier B. Not refused on the merits and NOT a closure of the MD5 "
               "lane. Unblocking route: a committed GOAL-MD5-001 coordinator "
               "decision under AMD-20260824-DIFFP-ACQ-1 tier B "
               "`unblocking_route`."),
    dict(id="AGAP-MD5-STEVENS-CHOSENPREFIX", primitive="md5", tier="B",
         citation="Stevens et al. -- chosen-prefix MD5 collision path tables "
                  "(bibliographic pointer only; no path data held)",
         source_ref="recalled:no-KN-LIT-entry-in-this-corpus",
         acquisition_status="blocked_pending_cross_goal_decision",
         notes="Tier B, same unblocking route."),
    dict(id="AGAP-MD5-HASHCLASH-CONDITIONS", primitive="md5", tier="B",
         citation="hashclash published differential paths and condition sets "
                  "(bibliographic pointer only; no path data held)",
         source_ref="recalled:no-KN-LIT-entry-in-this-corpus",
         acquisition_status="blocked_pending_cross_goal_decision",
         notes="Tier B, same unblocking route."),
    dict(id="AGAP-SHA1-FIPS-180-4", primitive="sha1", tier="C",
         citation="FIPS 180-4, the SHA-1 specification itself",
         source_ref="recalled:no-pinned-copy-in-this-repository",
         acquisition_status="acquirable_by_a_role_holding_web_capability",
         notes="Tier C, PERMITTED to the goal but NOT to this task: the "
               "Executor holds run_commands and deliberately not web_search "
               "(IR-10, OB-5). SHA-1 here is implemented from specification and "
               "gated on published digests instead. Acquiring the pin would "
               "convert two `recalled` digests into a `retrieved` check."),
    dict(id="AGAP-SHA1-DV-CLASSIFICATION", primitive="sha1", tier="C",
         citation="Primary sources classifying SHA-1 disturbance vectors and "
                  "their two-block families (bibliographic pointer only; no DV "
                  "data held)",
         source_ref="recalled:no-KN-LIT-entry-in-this-corpus",
         acquisition_status="acquirable_by_a_role_holding_web_capability",
         notes="Tier C. THE SINGLE HIGHEST-VALUE GAP FOR THIS GOAL: it is the "
               "only listed source class that is both unblocked and carries the "
               "path data the census needs. No firewall in this program covers "
               "SHA-1 material."),
    dict(id="AGAP-SHA1-COLLISION-PATHS", primitive="sha1", tier="C",
         citation="Primary sources for published SHA-1 near-collision "
                  "differential paths, including the first full SHA-1 collision "
                  "(bibliographic pointer only; no path data held)",
         source_ref="recalled:no-KN-LIT-entry-in-this-corpus",
         acquisition_status="acquirable_by_a_role_holding_web_capability",
         notes="Tier C."),
    dict(id="AGAP-SHA0-EXPANSION-SOURCE", primitive="sha1", tier="C",
         citation="FIPS 180 (SHA-0), needed only to pin the nearby-object "
                  "control's expansion",
         source_ref="recalled:no-pinned-copy-in-this-repository",
         acquisition_status="acquirable_by_a_role_holding_web_capability",
         notes="Tier C. CTL-NEARBY's SHA-0 expansion is implemented here from "
               "the stated one-rotation difference and is NOT gated on a "
               "published SHA-0 digest; that is a stated limit of CTL-NEARBY."),
]


def build_census(seed_md5: int, seed_sha1: int, planted_per_primitive: int = 8,
                 scan: dict | None = None) -> Census:
    c = Census()
    c.scan = scan if scan is not None else scan_corpus()

    # --- readable entries, from the structural scan only (IR-2) ---
    for cand in c.scan["candidates"]:
        if not cand["carries_path_data"]:
            continue
        c.readable.append(CensusEntry(
            id=f"CEN-SCAN-{cand['sha256'][:12]}", primitive="unknown",
            status="readable", provenance="retrieved", source_ref=cand["path"],
            citation=cand["path"], sha256=cand["sha256"],
            path_data={"structural_scan_hit": cand["path_data_patterns_matched"]},
            notes="Structural scan reported machine-readable path-data "
                  "patterns; REQUIRES MANUAL CONFIRMATION before any covering "
                  "number is derived from it."))

    # --- the quarantined pointer (path_data None, orbit UNDETERMINED) ---
    q = quarantine_attestation()
    c.quarantined_not_read.append(CensusEntry(
        id="CEN-QUAR-KN-LIT-87e00e", primitive="md5",
        status="quarantined_not_read", provenance="kb",
        source_ref="KN-LIT-87e00e", tier="A",
        citation="Wang, Feng, Lai, Yu -- Collisions for Hash Functions MD4, "
                 "MD5, HAVAL-128 and RIPEMD (IACR ePrint 2004/199)",
        sha256=q["sha256_recomputed"], orbit="UNDETERMINED", path_data=None,
        notes="POINTER ONLY. The payload was hashed byte-wise and never "
              "parsed (CTL-QUAR). Its orbit under the declared equivalence is "
              "UNDETERMINED and cannot be determined by this goal. It "
              "contributes NOTHING to any orbit count or covering number."))

    # --- the acquisition gap ---
    for spec in ACQUISITION_GAP_SPEC:
        c.acquisition_gap.append(CensusEntry(
            id=spec["id"], primitive=spec["primitive"],
            status="acquisition_gap", provenance="recalled",
            source_ref=spec["source_ref"], citation=spec["citation"],
            tier=spec["tier"], acquisition_status=spec["acquisition_status"],
            orbit="UNDETERMINED", path_data=None, notes=spec["notes"]))

    # --- THE SHADOW CENSUS: mandatory, so that a false positive is POSSIBLE ---
    for prim, seed, steps in (("md5", seed_md5, 64), ("sha1", seed_sha1, 80)):
        rng = random.Random(seed)
        for k in range(planted_per_primitive):
            cv, m, mp = seeded_pair(rng, prim)
            obj = plant_from_pair(f"PLANT-{prim.upper()}-{k:02d}", prim, cv, m, mp,
                                  (0, steps - 1))
            c.shadow.append(CensusEntry(
                id=obj.id, primitive=prim, status="readable_shadow",
                provenance="internal", source_ref="TASK-20260824-c6625a",
                citation="synthetic planted path (the actual differential a "
                         "seeded random message pair induces; conforming by "
                         "construction)",
                path_data={"kind": "planted", "seed": seed, "index": k},
                obj=obj,
                notes="SHADOW CENSUS ENTRY. Synthetic, not literature. Present "
                      "so that CTL-NULL is non-vacuous and CTL-PLANT is "
                      "possible at readable-census size zero. NEVER counted as "
                      "a readable census entry and never cited as a published "
                      "path."))
    return c
