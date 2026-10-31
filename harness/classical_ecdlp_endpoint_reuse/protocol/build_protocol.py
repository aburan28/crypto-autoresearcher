#!/usr/bin/env python3
"""Build the review-required protocol draft from the fixed scientific design.

This command neither freezes nor approves a protocol, draws confirmation
instances, constructs a solver table, launches a measurement, nor creates an
export. Actual image/binary/runner bindings are supplied only when observed.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
PREFIX = "harness/classical_ecdlp_endpoint_reuse"
ARMS = ("static_small", "static_full", "static_filled", "harvest", "harvest_disabled", "rho_reference")
PREFIXES = (1, 8, 16, 32, 64)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def metric(ident, name, unit, definition, source, *, kind="counted",
           aggregation="per_row", uncertainty="none_exact"):
    return {"id": ident, "name": name, "unit": unit, "kind": kind,
            "definition": definition, "source": source, "aggregation": aggregation,
            "resolution": "1" if kind != "timed" else "OS rusage clock resolution, recorded by worker",
            "uncertainty": uncertainty}

def build(ids, source_commit=None, binary_sha256=None, image_digest=None):
    shared_instrument = {"repo": "isogeny-labs/crypto-autoresearcher", "commit": source_commit,
                         "build": None, "binary_sha256": binary_sha256,
                         "flags": {}, "env": {"OMP_NUM_THREADS": "1"},
                         "threads": 1, "image_digest": image_digest}
    descriptions = {
        "static_small": ("baseline", "Actual source-pinned Bernstein-Lange with C0 requested setup chains; no retention/growth."),
        "static_full": ("reference", "Same Bernstein-Lange core, C=4*C0 requested setup chains and no online growth."),
        "static_filled": ("reference", "C0 initial chains plus explicit charged known-scalar precomputation walks until C DISTINCT canonical endpoints fill the same C-slot arena; then static original lookup/solve. Fill failures and all work are retained."),
        "harvest": ("candidate", "C0 setup chains; stage failed target-walk (D,a) in unused arena slots, commit e=x+a mod r only after public verification of x, then in-place sort/dedup."),
        "harvest_disabled": ("control_aa", "The small-static path with the growth/retention feature disabled, same public settings and common random numbers."),
        "rho_reference": ("reference", "Named source-pinned rho reference on the same valid public targets, no hidden BSGS or candidate fallback.")}
    arms = []
    for arm in ARMS:
        role, description = descriptions[arm]
        value = {"id": arm, "role": role, "description": description,
                 "instrument": copy.deepcopy(shared_instrument),
                 "parameters": {"cli_arm": arm, "threads": 1, "walks": 1, "early_abort": 0,
                                "initial_chain_rule": "C" if arm == "static_full" else "C0",
                                "C0": "floor(r/2^(2*t)+1/2), t=floor(bit_length(r)/3)",
                                "C": "4*C0; requested full-arm chain budget and maximum endpoint arena slots; only static_filled requires C distinct endpoints",
                                "fill_goal": "C distinct canonical endpoints" if arm == "static_filled" else None}}
        if arm == "rho_reference":
            value["parameters"] = {"cli_arm": arm, "threads": 1, "rho_auto_requested": True,
                                   "r": 0, "walks": 0, "dp_bits": -1, "negation_map": True,
                                   "max_ops": "settings.max_online_ops; actual domain-separated rho_seed is retained per target",
                                   "BL_table_parameters": "unused"}
        else:
            value["parameters"]["adding_steps"] = 20
            value["parameters"]["max_online_attempts"] = 512
        if arm != "static_small":
            value["same_instrument_as"] = "static_small"
        arms.append(value)
    primary = [
        metric("verified_targets_m64", "Verified complete target answers", "targets out of64 per cell",
               "Final public [x]G=Q checks for all64 fixed target ordinals; native answers are cross-checked by the independent public verifier.",
               "native target status/verified_scalar; independent verifier target_arm_cases and verified_case_witnesses"),
        metric("group_additions_m64", "Complete setup plus64target EC group invocations", "shared dec::Ops group_additions invocations",
               "Sum setup.counters.group_additions and target[0..63].counters.group_additions, including solve, public final verification and endpoint growth group work. One counter per ECadd/double function invocation, including identity cases. Nested scalar_multiplications/doublings are not added. Common input certification/parsing/output/orchestration and non-EC bookkeeping remain separate recorded costs.",
               "native JSONL counters.group_additions on setup and target rows", aggregation="paired_ratio", uncertainty="paired_bootstrap_ci95")]
    secondary = [metric("group_additions_m" + str(n), "Complete EC group invocations at reuse prefix" + str(n),
                        "group_additions invocations", "Setup plus target ordinals below" + str(n) + "; nested subset, not independent evidence.",
                        "native setup/target counters.group_additions", aggregation="paired_ratio", uncertainty="paired_bootstrap_ci95")
                 for n in PREFIXES[:-1]]
    secondary += [
        metric("endpoint_arena_bytes", "Known-plus-pending endpoint arena", "bytes",
               "One reserved C-slot arena of16bytes per slot includes known and pending entries;16bytes constant heapsort temporary is separate. Initial worker/copy buffers, jumps/fixed-base tables, objects, allocations, stacks and output are separate; this is not global RSS.", "native memory/occupancy counters"),
        metric("process_max_rss_bytes", "Observed one-cell/arm child process peak RSS", "bytes",
               "OS wait4 high-water mark over the whole fresh child, including setup/input/output and teardown; host OS normalization recorded. Not inferred from endpoint slots.", "worker rusage max_rss_bytes", aggregation="max"),
        metric("process_cpu_seconds", "INSTRUMENTED whole-child CPU observation", "seconds",
               "OS wait4 child user+systemCPU over parsing, common membership validation, setup, all64 solves, traceI/O and teardown. Trace volume differs byarm, so this is instrumented whole-child CPU, not the old solverAPI or uninstrumented algorithm time; secondary and usable as a clock only with actual observed L2/tierB+ and no restore. Otherwise retained with invalid-clock flag.", "worker rusage cpu_user_seconds+cpu_sys_seconds", kind="timed", aggregation="distribution", uncertainty="range"),
        metric("unique_public_queries", "UniqueQ and duplicate positions", "distinct public points per64draws",
               "Count distinct canonical public(Qx,Qy,infinity) tuples and report repeated ordinal/firstordinal pairs; never dedup inputs or drop outcomes.", "public target TSV, grouped by fixture/replicate")]
    variable = {
        "independent": [{"name": "endpoint_retention_policy", "levels": ["disabled", "verified_monotone_append"]},
                        {"name": "solver_policy", "levels": list(ARMS)},
                        {"name": "subgroup_bits", "levels": [12, 14, 16, 18]},
                        {"name": "reuse_prefix", "levels": list(PREFIXES)}],
        "factors": [
            {"name": "curve_selection", "treatment": "randomized", "how": "64 fresh ordinary, non-anomalous j!=0,1728 curves,16 perbit size; fixed exclusions and public post-freeze seed rule independent of arm."},
            {"name": "target_sampling", "treatment": "randomized", "how": "64 independent uniform scalars with replacement per curve/replicate, from a private post-freeze entropy root and frozen HMAC rejection sampler; no public reconstruction of labels."},
            {"name": "setup_and_solver_seeds", "treatment": "fixed", "how": "Common per cell public solver seed acrossBL arms, derived from frozen protocol hash, post-freeze public nonce, fixture/replicate and solver_cell domain; all actual native seed values retained."},
            {"name": "source_build_binary", "treatment": "fixed", "how": "One source-pinned executable for all arms; actual codecommit/build/binary/OCI identity must be bound before freeze and verified at launch."},
            {"name": "initial_chains_and_arena", "treatment": "fixed", "how": "Within primary small/growth/A-A comparisons, C0 setup and C-slot postbuild arena are identical; full-static reference separately changes its complete solver policy to C initialchains. Constructor underfill/collisions retained, no retuning."},
            {"name": "threads_and_work_limits", "treatment": "fixed", "how": "BL: threads1,walks1,early_abort0,adding_steps20 and fixed512attempt ceiling. Rho: Auto r0/walks0/dpbits-1,oneworker,negation enabled, actual effective statistics/seed retained. Registered APIwork caps and all outcomes remain visible."},
            {"name": "arm_and_cell_order", "treatment": "randomized", "how": "Frozen public hash/nonce domain-separated cell shuffle and arm shuffle; target order identical acrossarms."},
            {"name": "arm_alias", "treatment": "fixed", "how": "The static_small/harvest_disabled A/A pair differs only in its disabled-feature control label/code-selection alias; settings, random stream, endpoint table and actual ECcounter vector must match."},
            {"name": "host_frequency_smt_numa_kernel_hypervisor_cotenants_irqs_memory", "treatment": "measured", "how": "Actual per child host/isolation receipts, blockers, CPUmodel/governor/turbo/SMT/NUMA/kernel/hypervisor/PSI/steal/affinity/rusage; unknowns stay unknown."},
            {"name": "memory_layout_environment_warmup", "treatment": "measured", "how": "Fresh process per cell/arm; record ASLR, THP, environment/build identity and actual layout controls. Zero discarded warmups because counted work is primary."},
            {"name": "analyst", "treatment": "fixed", "how": "Analysis code hash frozen before confirmation data. Labels not masked; no analyst blindness or independent scientific review claimed."}],
        "comparisons": [
            {"id": "C-growth-filled", "arms": ["static_filled", "harvest"], "differs_in": ["solver_policy"], "design": "one_factor"},
            {"id": "C-growth-small", "arms": ["static_small", "harvest"], "differs_in": ["endpoint_retention_policy"], "design": "one_factor"},
            {"id": "C-growth-full", "arms": ["static_full", "harvest"], "differs_in": ["solver_policy"], "design": "one_factor"},
            {"id": "C-growth-rho", "arms": ["rho_reference", "harvest"], "differs_in": ["solver_policy"], "design": "one_factor"},
            {"id": "C-aa", "arms": ["static_small", "harvest_disabled"], "differs_in": ["arm_alias"], "design": "aa"}],
        "aa_not_applicable": None, "crosses_map": False}
    provenance = {"written_at": "2026-10-26", "first_recorded_in": "ledger/hypotheses/" + ids["hypothesis"] + ".yaml",
                  "sample_status": "out_of_sample", "data_seen": [
                      {"path": "experiments/EXP-ECDLP-9f7772/reports/run-20261025T1930Z/observations.md", "measured": "Earlier48curve/768target baseline and prefixcandidate costs, different frozen method/cohort."},
                      {"path": "crypto prior LEAD-RHO-advice-table-variants and EXP-ECDLP-1de2ec", "measured": "Prior actual generic growth/reselection runs and open EC follow-up, not merely stale hypothesis status; exact source audit retained separately."}]}
    protocol = {
        "schema": "experiment.protocol/v1", "protocol_id": ids["experiment"], "version": 1,
        "created": "2026-10-26", "repository": "crypto-autoresearcher",
        "study_dir": "experiments/" + ids["experiment"], "authors": ["delegated Coordinator, classical endpoint-reuse study"],
        "links": {"goal_id": ids["goal"], "hypothesis_ids": [ids["hypothesis"]],
                  "spec": "experiments/" + ids["experiment"] + "/specification.yaml",
                  "problem": "problems/classical-ecdlp-endpoint-reuse-isolated-runner-unavailable.md"},
        "question": "On64fresh ordinary prime-field curves, can verified monotone reuse of failed Bernstein-Lange endpoints improve complete setup-plus-solve EC group invocation counts under one fixed known-plus-pending endpoint arena?",
        "claims": [
            {"id": "C-correct", "text": "Every claimed scalar answer and every promoted endpoint satisfies the registered public equations and causal verification boundary.", "class": "exact_computation", "decided_by": []},
            {"id": "C-work", "text": "At64targets per cell, harvest uses fewer complete solver-API group_additions than static_filled on the registered paired panel.", "class": "comparative", "decided_by": ["C-growth-filled"],
             "if_supported": "A measured group-invocation improvement at this cohort/reuse/memory scope only; full field/native/RSS costs remain visible.",
             "if_not_supported": "Retain exact costs and uncertainty; revise the implementation/regime without retiring the mechanism family."},
            {"id": "C-scope", "text": "Novelty of the endpoint-reuse family, an overall runtime speedup and an asymptotic exponent improvement are outside this experiment.", "class": "out_of_scope", "decided_by": []}],
        "hypotheses": [{"id": ids["hypothesis"], "statement": "At the registered finite reuse and cap, certified endpoint reuse may reduce complete EC group invocation work relative to the charged distinct-filled staticBL reference while preserving correctness.",
                        "mechanism": "A failed terminal D=Q+[a]G becomes a known scalar endpoint e=x+a mod r only after [x]G=Q verifies; later targets reuse it within a fixed C-slot arena.",
                        "predictions": [{"id": "P-work", "metric": "group_additions_m64", "direction": "lower",
                                         "minimum_effect": "Primary equal-curve geometric mean ratio and its95% cluster-bootstrap upper endpoint below1, with passing exact A/A and witness controls; no runtime inference.",
                                         "provenance": provenance, "role": "decisive"}]}],
        "arms": arms,
        "controls": {
            "aa": {"present": True, "comparison": "C-aa", "not_applicable_reason": None},
            "positive": {"present": False, "arm": None, "expected_detection": None,
                         "not_applicable_reason": "Separate fixed development controls exercise planted scalars, endpoint certification and one actual growth promotion through the same producer/verifier paths before source freeze; every confirmation answer has a public equation check. No extra sampled positive arm is proposed."},
            "negative": {"present": False, "arm": None, "null_population": None,
                         "not_applicable_reason": "The primary estimand is a paired complete-method cost, not anomaly frequency. Disabled-growth A/A, full-static capacity reference, malformed/nonmember/wrongwitness development controls and all uniform-with-replacement target outcomes are retained."}},
        "variable_ledger": variable,
        "randomization": {"arm_order": "randomized", "arm_order_reason": None,
                          "seed_derivation": {"method": "harness_drawn", "seeds": [], "nonce": None,
                                              "note": "Frozen seed_rules.py: SHA256(b'classical.ecdlp.endpoint-reuse.v1\\0'+NULjoinedASCII(protocolhash,post-freeze externalnonce,fixture_id,replicate,purpose)), first8bytes big-endian. solver_cell seed is common acrossBLarms; arm_order/cell_order/curve_generation use separate domains. Custom checker recomputes this law; official harness_drawn lint does not attest it. Private target scalars use a separate post-freeze OSentropy HMACroot/commitment, never the public nonce alone."},
                          "instance_sampling": {"rule": "64 fresh curves,16per12/14/16/18bit subgroup; 2 independent private target-seed replicates,64 uniform scalars withreplacement each. Public sampler and exclusions frozen; target labels withheld until actual outputseal.", "independent_of_arm": True},
                          "blinding": {"analysis_labels_masked": False, "how": "Source/input separation and withheld scalar labels only; arm labels visible and no OS/analyst blindness claimed.", "unmasked_at": None}},
        "sample_size": {"instances": 64, "replicates": 2, "warmups": 0,
                        "power": {"method": "paired_bootstrap", "alpha": .05, "tests_in_family": 1, "correction": "none",
                                  "rank_test_n": None, "min_attainable_two_sided_p": None, "passes": True,
                                  "note": "Precision planning only: under an unmeasured assumed between-curve logratioSD=.5,64clusters give SE=.5/sqrt64=.0625 and nominal95% loghalfwidth=.1225 (~13% ratio). Actual spread/coverage may differ; this is not a power claim or pvalue test. Two replicates remain within clusters. Primary comparison/m64 only is decisive; secondary pointwise intervals have no familywise discovery claim."},
                        "preflight_runtime": {"fixed_seconds": None, "per_sample_seconds": None, "threads": 1,
                                              "estimated_total_seconds": None, "measured_on": None}},
        "metrics": {"primary": primary, "secondary": secondary},
        "measurement": {"isolation_required": "L2", "warmups": 0, "order": "randomized", "clock": "counted",
                        "counters": ["Every native dec::Ops field separately", "Every emitted adapteraux/upstream/reuse counter, including RNG/scalar/sort/comparison/lookup/logging/promotion verification", "Memory arena/pending/known occupancy and actual processRSS"],
                        "record": ["cpu_model", "logical_cpus", "memory_bytes", "kernel", "hypervisor", "governor", "turbo", "SMT", "NUMA", "affinity", "co_tenants", "IRQs", "PSI", "steal", "ASLR", "THP", "binary_sha256", "source_commit", "threads", "isolation.tier", "isolation.blockers", "rusage"],
                        "timed_primary_justification": None},
        "execution": {"backend": "isolab-k8s", "queue": "isolab",
                      "placement": {"required": "Actual source-bound generic worker on an isolated allocation with observed per child receipts; node labels alone do not establish L2.", "maximum_active_cpus": 4, "memory_gib": 12, "child_timeout_seconds": 3600},
                      "measurement_class": "measurement", "timeout_seconds": 3600,
                      "checkpoint": {"policy": "none", "interval_seconds": None, "grace_seconds": None, "restore_validation": "none", "after_restore": {"wall_time": "invalid", "counted_units": "valid"}},
                      "retries": {"infrastructure_only": True, "max_attempts": 1}},
        "stopping_rules": [{"rule": "Fixed64curves*2replicates*6arms=768 fresh child executions,64 target ordinals per child=49152 native target rows over8192 public IDs; no optional extension.", "kind": "fixed_n", "preregistered": True},
                           {"rule": "PerQ upstream workstop256*ceil_sqrt(r)+8192 and per cellbuildstop256*C*(1<<t)+8192, plus unchanged512attempt cap. These are APIreported work units, not full cost bounds; limits and3600s childwatchdog are operational censoring, not mathematical failure.", "kind": "invalidation", "preregistered": True}],
        "invalidation_rules": ["Wrong public witness, unauthorized promotion, cap violation, source/input/seed mismatch or failed mandatory control invalidates affected implementation/measurement; preserve raw records.",
                               "A missing/censored/invalid member of the primary pair makes the full registered paired improvement undefined; do not replace it with a success-only claim.",
                               "Clocks without observedL2/tierB+ or acrossrestore/contended/interrupted rows stay wall_validfalse and do not qualify a runtime comparison.",
                               "The frozen public solver seed law permits zero; the current native parser rejects a zero seed. Retain that child failure and all affected incomplete outcomes as infrastructure/implementation incompletion; never redraw a nonce, replace the seed, retry until favorable, or interpret it as mathematical failure."],
        "decision_rule": {"text": "Report correctness, all counters and memory first. The finite primary group-invocation improvement is eligible only with complete verified primary pairs, public endpoint trace/cap controls and exactA/A equality, and primarym64 harvest/static_filled gmean ratio with95%cluster-bootstrap upper endpoint<1. Other outcomes remain observations for the next revision.",
                          "comparison_ids": ["C-growth-filled"], "threshold": "Complete registered primary panel, passing controls, primary ratioCIupper<1; no hidden fallback.",
                          "statistic": "For eachcurve sum bothreplicate complete group_additions, form candidate/baseline ratio; equal-curve geometricmean and range.",
                          "interval": "10000 bootstrap resamples of64curves withreplacement preserving both replicates/all prefixes/comparisons; pointwise percentile95%, linear quantiles.",
                          "multiple_comparison_correction": "none", "effect_size_measure": "Complete solver-API EC group invocation ratio and absolute counter difference; full native costvector and memory separate.",
                          "verdict_vocabulary": ["supported_within_scope", "within_control_distribution", "invalid_measurement", "inconclusive"]},
        "analysis_plan": {"script": {"path": "../../" + PREFIX + "/protocol/analysis.py", "sha256": sha(HERE / "analysis.py")},
                          "inputs": ["raw-manifest.json", "settings.tsv", "public-targets.tsv", "independent-public-verification/summary.json", "external-nonce.json"],
                          "outputs": ["analysis/summary.json", "analysis/per-cell-index.json", "analysis/per-cell-*.json"], "blinded": False, "frozen_before_data": False},
        "reporting": {"export_schema": "experiment.export/v1", "review_schema": "experiment.review/v1",
                      "graphs": ["Primary completegroup-addition ratios withcurve-clusterCI andA/A", "Cumulative work atnestedreuseprefixes", "Known/pendingarena occupancy andprocessRSS", "Planned/attempted/completed/notcompleted flow"], "report_dir": "reports"},
        "inadmissible": ["Retune C/C0/dpbits, targetcount, seeds, stops or comparisons after confirmation outputs.", "Promote endpoints before a verified public scalar or use uncertified/UF/reselected relations.", "Use public nonce/hash to regenerate private targetlabels or reveal custodianlabels before outputsseal.", "Add nested scalar/doubling counters into group_additions or call a groupcounter saving an overallruntime/exponent improvement.", "Drop duplicateQ, underfilledtables, failed/censored/invalid cases or replace the full panel with favorable cells.", "Claim that a protocol/schema/receipt passing proves runtimeisolation or independent scientific review."],
        "literature": [{"ref": "harness/classical_ecdlp_solver_validation_v2/baselines/vendor-source.json", "provenance": "internal", "claim": "Actual BL/rho vendor source is pinned separately; its setup/online families remain named.", "verified_by": "prior validated source manifest; new provenance audit retained separately"},
                       {"ref": "crypto:LEAD-RHO-advice-table-variants and EXP-ECDLP-1de2ec", "provenance": "internal", "claim": "Prior generic growth/reselection experiments and the existing EC follow-up; no new-family novelty asserted.", "verified_by": "next_mechanism_selection, source audit2026-10-26"}],
        "amendments": [], "freeze": {"status": "draft", "protocol_sha256": None, "commit": None, "frozen_at": None, "filed_before_affected_data": None},
        "extensions": {"native_scope": "classical_ecdlp_endpoint_reuse", "source_prefix": PREFIX,
                       "reuse_prefixes": list(PREFIXES), "primary_prefix": 64, "bootstrap_replicates": 10000,
                       "private_labels": "Custodian OSentropy/HMACroot after source+protocol lock; publish commitments, retainprivate roots/scalars until actualoutputseal.",
                       "arena_contract": "Known+pending<=C in one16Cbyte postbuild arena;16B in-place-sort temporary separate; all other structures/RSS explicit.",
                       "prior_family_scope": "Known endpoint-reuse family including Kuhn2001 context; this is a source-pinned actualEC monotoneappend/cap study, distinct from prior generic UF/reselection/weightedselection. No exponent or novel-family claim."}}
    return protocol

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", type=Path, default=HERE / "ids.json")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-commit")
    parser.add_argument("--binary-sha256")
    parser.add_argument("--image-digest")
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        raise SystemExit("Refusing to overwrite an existing generated protocol; use a fresh preparation directory")
    protocol = build(json.loads(args.ids.read_text()), args.source_commit, args.binary_sha256, args.image_digest)
    args.out.write_text(json.dumps(protocol, indent=2, ensure_ascii=False, allow_nan=False) + "\n")

if __name__ == "__main__":
    main()
