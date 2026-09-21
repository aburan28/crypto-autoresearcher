import { createHash } from "node:crypto";
import { lstatSync, readFileSync, realpathSync, writeFileSync } from "node:fs";
import { dirname, isAbsolute, join, posix, relative } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const protocol = "EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor/9";
const names = {
  selector: "selector-rules-v8.json",
  artifact: "supervised-executor-closed-kernel-v9.json",
  builder: "build_v9_closed_kernel.mjs",
  verifier: "verify_v9_closed_kernel.mjs",
  contract: "supervised-executor-contract-v9.md",
  topology: "supervised-executor-topology-decision-v8.md",
};
const bytes = Object.fromEntries(Object.entries(names).map(([id, name]) => [id, readFileSync(join(here, name))]));
const selectorExpected = "2952bc3c3792eb3d43a4563ab4c6b7afa20922c0846a2a44f8b854bf873d2383";
const artifact = JSON.parse(bytes.artifact.toString("utf8"));
const selector = JSON.parse(bytes.selector.toString("utf8"));
const checks = [];

function stable(value) {
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  if (value !== null && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
}

function digest(value) {
  const input = typeof value === "string" || Buffer.isBuffer(value) ? value : stable(value);
  return createHash("sha256").update(input).digest("hex");
}

function gitHash(type, bytesValue) {
  const body = Buffer.isBuffer(bytesValue) ? bytesValue : Buffer.from(bytesValue, "utf8");
  return createHash("sha1").update(Buffer.concat([Buffer.from(`${type} ${body.length}\0`, "utf8"), body])).digest("hex");
}

function eq(left, right) {
  return stable(left) === stable(right);
}

function clone(value) {
  return structuredClone(value);
}

function reject(code, detail = "") {
  const error = new Error(`${code}${detail ? `: ${detail}` : ""}`);
  error.code = code;
  throw error;
}

function assertCheck(name, condition, detail) {
  if (!condition) reject("CHECK_FAILED", `${name}:${detail}`);
  checks.push({ name, status: "pass", detail });
}

function exactObject(value, fields, code) {
  if (value === null || typeof value !== "object" || Array.isArray(value) || !eq(Object.keys(value).sort(), [...fields].sort())) reject(code);
}

function resolveBundleFile(relativePath) {
  if (
    typeof relativePath !== "string"
    || relativePath.length === 0
    || relativePath.includes("\\")
    || posix.isAbsolute(relativePath)
    || posix.normalize(relativePath) !== relativePath
    || relativePath === "."
    || relativePath.startsWith("../")
  ) reject("NONCANONICAL_EVIDENCE_PATH", String(relativePath));
  const path = join(here, ...relativePath.split("/"));
  if (!lstatSync(path).isFile()) reject("EVIDENCE_NOT_REGULAR_FILE", relativePath);
  const escaped = relative(realpathSync(here), realpathSync(path));
  if (escaped === "" || escaped === ".." || escaped.startsWith(`..${posix.sep}`) || isAbsolute(escaped)) reject("EVIDENCE_PATH_ESCAPE", relativePath);
  return path;
}

function parseSha256Manifest(bytesValue, pathMode) {
  const text = bytesValue.toString("utf8");
  if (!text.endsWith("\n")) reject("MALFORMED_EVIDENCE_MANIFEST", "missing final newline");
  const lines = text.slice(0, -1).split("\n");
  if (lines.length === 0 || lines.some((line) => line.length === 0)) reject("MALFORMED_EVIDENCE_MANIFEST", "empty line");
  return lines.map((line) => {
    const pattern = pathMode === "root" ? /^([0-9a-f]{64})  ([^\r\n]+)$/ : /^([0-9a-f]{64})  \.\/([^\r\n]+)$/;
    const match = pattern.exec(line);
    if (!match) reject("MALFORMED_EVIDENCE_MANIFEST", line);
    return { sha256: match[1], path: match[2] };
  });
}

const phases = ["P0", "P1", "P2", "P3", "P4", "P5", "E0"];
const producer = {
  campaign_config: "bootstrap_controller", root_lock: "bootstrap_controller",
  normal_admission: "root_supervisor", recovery_admission: "root_supervisor", attempt_start: "root_supervisor",
  resource_lifetime: "external_meter", resource_measurement: "external_meter", resource_receipt: "external_meter", attempt_end: "external_meter",
  phase_reservation: "root_supervisor", executable_identity: "capability_guard", capability_receipt: "capability_guard",
  private_map_open_intent: "root_supervisor", private_map_open_observation: "root_supervisor", private_map_opened_receipt: "root_supervisor",
  launch_intent: "root_supervisor", phase_spawn: "root_supervisor", phase_reap: "root_supervisor", phase_result: "root_supervisor", phase_content: "root_supervisor", phase_terminal: "root_supervisor",
  ref_observation_pre: "repository_validator", git_blob_object: "repository_validator", git_tree_object: "repository_validator", commit_intent: "repository_validator", commit_object: "repository_validator", ref_cas_attempt: "repository_validator", ref_observation_post: "repository_validator", committed_phase: "repository_validator",
  closure_request: "root_supervisor", launch_identity: "external_meter", kernel_process_observation: "external_meter", recalculation_receipt: "external_meter", lock_release: "external_meter", campaign_terminal: "external_meter",
  action_receipt: "trusted_reducer", observation_receipt: "observation_gateway",
};

const fields = {
  campaign_config: ["sequence", "campaign_id", "requested_run_mode", "approval_maximum_recovery_bootstraps", "intended_ref", "initial_ref_oid", "capability_descriptor", "capability_descriptor_sha256", "resource_policy"],
  root_lock: ["sequence", "campaign_id", "lock_token", "status"],
  normal_admission: ["sequence", "campaign_id", "ordinal", "predecessor_attempt_end_sha256"], recovery_admission: ["sequence", "campaign_id", "ordinal", "predecessor_attempt_end_sha256"],
  attempt_start: ["sequence", "campaign_id", "ordinal", "admission_sha256"],
  resource_lifetime: ["sequence", "campaign_id", "ordinal", "bootstrap_observed", "bootstrap_cap", "meter_observed_preterminal", "meter_preterminal_cap", "meter_terminal_cap", "wall_cap", "io_charge", "disk_charge", "memory_capacity", "interval_start", "interval_end"],
  resource_measurement: ["sequence", "campaign_id", "closure_ordinal", "input", "input_sha256", "result", "result_sha256"],
  resource_receipt: ["sequence", "campaign_id", "ordinal", "measurement_sha256", "input_sha256", "result_sha256", "result", "admission_sha256", "attempt_start_sha256"],
  attempt_end: ["sequence", "campaign_id", "ordinal", "outcome", "terminal_request", "durable_state", "resource_receipt_sha256"],
  phase_reservation: ["sequence", "campaign_id", "ordinal", "phase", "phase_mode", "predecessor_committed_sha256", "predecessor_commit_oid"],
  executable_identity: ["sequence", "campaign_id", "ordinal", "phase", "executable_path", "executable_sha256", "opened_file_token"],
  capability_receipt: ["sequence", "campaign_id", "ordinal", "phase", "reservation_sha256", "descriptor_sha256", "executable_identity_sha256", "inherited_descriptor_bindings", "decision"],
  private_map_open_intent: ["sequence", "campaign_id", "ordinal", "phase", "reservation_sha256"],
  private_map_open_observation: ["sequence", "campaign_id", "ordinal", "phase", "open_intent_sha256", "outcome", "descriptor_token"],
  private_map_opened_receipt: ["sequence", "campaign_id", "ordinal", "phase", "reservation_sha256", "open_intent_sha256", "open_observation_sha256", "descriptor_token"],
  launch_intent: ["sequence", "campaign_id", "ordinal", "phase", "phase_mode", "reservation_sha256", "capability_receipt_sha256", "executable_identity_sha256", "private_map_receipt_sha256"],
  phase_spawn: ["sequence", "campaign_id", "ordinal", "phase", "launch_intent_sha256", "outcome", "process_token"],
  phase_reap: ["sequence", "campaign_id", "ordinal", "phase", "phase_spawn_sha256", "outcome", "exit_code"],
  phase_result: ["sequence", "campaign_id", "ordinal", "phase", "phase_reap_sha256", "bounded", "valid", "recovery"],
  phase_content: ["sequence", "campaign_id", "ordinal", "phase", "phase_result_sha256", "content_bytes", "content_sha256"],
  phase_terminal: ["sequence", "campaign_id", "ordinal", "phase", "event_kind", "outcome", "predecessor_sha256", "result_sha256", "content_sha256"],
  ref_observation_pre: ["sequence", "campaign_id", "ordinal", "phase", "ref", "observed_oid", "relation"],
  git_blob_object: ["sequence", "campaign_id", "ordinal", "phase", "source_content_sha256", "object_bytes_hex", "oid"],
  git_tree_object: ["sequence", "campaign_id", "ordinal", "phase", "blob_record_sha256", "blob_oid", "object_bytes_hex", "oid"],
  commit_intent: ["sequence", "campaign_id", "ordinal", "phase", "schema", "tree_record_sha256", "tree_oid", "parent_oid", "intended_ref", "message", "result_sha256", "content_sha256", "terminal_sha256", "terminal_outcome", "self_exclusion"],
  commit_object: ["sequence", "campaign_id", "ordinal", "phase", "intent_sha256", "commit_bytes", "oid", "tree_oid", "parent_oid"],
  ref_cas_attempt: ["sequence", "campaign_id", "ordinal", "phase", "ref", "expected_old_oid", "new_oid", "outcome", "commit_object_sha256", "ref_observation_pre_sha256"],
  ref_observation_post: ["sequence", "campaign_id", "ordinal", "phase", "ref", "observed_oid", "cas_sha256"],
  committed_phase: ["sequence", "campaign_id", "ordinal", "phase", "commit_oid", "commit_object_sha256", "ref_cas_sha256", "post_ref_observation_sha256"],
  closure_request: ["sequence", "campaign_id", "ordinal", "last_committed_sha256", "terminal_request"],
  launch_identity: ["sequence", "campaign_id", "ordinal", "executable_sha256", "process_tokens"], kernel_process_observation: ["sequence", "campaign_id", "ordinal", "launch_identity_sha256", "observation"],
  recalculation_receipt: ["sequence", "campaign_id", "ordinal", "campaign_terminal_sha256", "derived_totals_sha256", "status"], lock_release: ["sequence", "campaign_id", "ordinal", "recalculation_receipt_sha256", "status"],
  campaign_terminal: ["sequence", "campaign_id", "ordinal", "kind", "resource_receipt_sha256", "attempt_end_sha256", "closure_request_sha256"],
  action_receipt: ["sequence", "campaign_id", "previous_journal_sha256", "pre_universe_sha256", "source_schema", "source_sha256", "selected_rule", "selected_action", "next_context", "domain_record_sha256s", "post_domain_universe_sha256"],
  observation_receipt: ["sequence", "campaign_id", "previous_journal_sha256", "pre_universe_sha256", "observation_kind", "context", "domain_record_sha256s", "post_domain_universe_sha256"],
};

const descriptorBindings = [{ fd: 0, target: "stdin", rights: ["read"] }, { fd: 1, target: "stdout", rights: ["write"] }, { fd: 2, target: "stderr", rights: ["write"] }];

function suffix(record) {
  const p = record.payload;
  const table = {
    campaign_config: "config.json", root_lock: "root-lock.json", closure_request: "closure-request.json", recalculation_receipt: "recalculation.json", lock_release: "lock-release.json", campaign_terminal: "campaign-terminal.json",
  };
  if (table[record.record_type]) return table[record.record_type];
  if (["normal_admission", "recovery_admission"].includes(record.record_type)) return `admissions/${p.ordinal}.json`;
  if (record.record_type === "attempt_start") return `attempts/${p.ordinal}/start.json`;
  if (record.record_type === "resource_lifetime") return `attempts/${p.ordinal}/lifetime.json`;
  if (record.record_type === "resource_measurement") return `accounting/measurements/${p.closure_ordinal}.json`;
  if (record.record_type === "resource_receipt") return `attempts/${p.ordinal}/resource.json`;
  if (record.record_type === "attempt_end") return `attempts/${p.ordinal}/end.json`;
  if (record.record_type === "launch_identity") return `attempts/${p.ordinal}/launch-identity.json`;
  if (record.record_type === "kernel_process_observation") return `attempts/${p.ordinal}/kernel-observation.json`;
  const phaseNames = { phase_reservation: "reservation", executable_identity: "executable", capability_receipt: "capability", private_map_open_intent: "private-map-intent", private_map_open_observation: "private-map-observation", private_map_opened_receipt: "private-map-receipt", launch_intent: "launch-intent", phase_spawn: "spawn", phase_reap: "reap", phase_result: "result", phase_content: "content", phase_terminal: "terminal", ref_observation_pre: "ref-pre", git_blob_object: "git-blob", git_tree_object: "git-tree", commit_intent: "commit-intent", commit_object: "commit-object", ref_cas_attempt: "ref-cas", ref_observation_post: "ref-post", committed_phase: "committed" };
  if (phaseNames[record.record_type]) return `phases/${p.phase}/${phaseNames[record.record_type]}.json`;
  if (record.record_type === "action_receipt") return `journal/${String(p.sequence).padStart(4, "0")}-action.json`;
  if (record.record_type === "observation_receipt") return `journal/${String(p.sequence).padStart(4, "0")}-observation.json`;
  reject("RECORD_TYPE_UNKNOWN", record.record_type);
}

function ordinalNumber(value) {
  if (typeof value !== "string" || !/^A(?:0|[1-9]|[12][0-9]|3[0-2])$/.test(value)) reject("ORDINAL_OUT_OF_RANGE", String(value));
  return Number(value.slice(1));
}

function inspectRecord(record) {
  exactObject(record, ["schema", "path", "record_type", "payload", "producer", "canonical_bytes", "sha256"], "RECORD_KEYS_MISMATCH");
  const match = record.path.match(/^kernel\/([A-Z0-9-]+)\//);
  if (!match) reject("PATH_TEMPLATE_MISMATCH", record.path);
  const campaign = match[1];
  if (posix.normalize(record.path) !== record.path || posix.isAbsolute(record.path) || record.path.includes("//")) reject("PATH_NONCANONICAL", record.path);
  if (!(record.record_type in producer)) reject("RECORD_TYPE_UNKNOWN", record.record_type);
  if (record.producer !== producer[record.record_type]) reject("PRODUCER_UNAUTHORIZED", `${record.record_type}:${record.producer}`);
  exactObject(record.payload, fields[record.record_type], "PAYLOAD_KEYS_MISMATCH");
  if (!Number.isSafeInteger(record.payload.sequence) || record.payload.sequence < 0) reject("SEQUENCE_INVALID");
  if (record.payload.campaign_id !== campaign) reject("CAMPAIGN_ID_MISMATCH");
  if (record.path !== `kernel/${campaign}/${suffix(record)}`) reject("PATH_TEMPLATE_MISMATCH", record.path);
  const { canonical_bytes: encoded, sha256: claimed, ...body } = record;
  if (stable(body) !== encoded) reject("RECORD_CANONICAL_BYTES_MISMATCH", record.path);
  if (digest(encoded) !== claimed) reject("RECORD_DIGEST_MISMATCH", record.path);
  return campaign;
}

function ordered(records) {
  return clone(records).sort((a, b) => a.path.localeCompare(b.path));
}

function indexUniverse(records) {
  const byType = new Map();
  const paths = new Set();
  let campaign = null;
  for (const record of records) {
    const observedCampaign = inspectRecord(record);
    if (campaign === null) campaign = observedCampaign;
    if (campaign !== observedCampaign) reject("CROSS_CAMPAIGN_RECORD");
    if (paths.has(record.path)) reject("DUPLICATE_DURABLE_PATH", record.path);
    paths.add(record.path);
    if (!byType.has(record.record_type)) byType.set(record.record_type, []);
    byType.get(record.record_type).push(record);
  }
  const all = (type) => byType.get(type) || [];
  const one = (type, predicate = () => true) => all(type).find(predicate);
  return { campaign, all, one };
}

function overlaps(a, b) {
  return a.interval_start < b.interval_end && b.interval_start < a.interval_end;
}

function expectedResourceInput(idx, closureOrdinal) {
  const end = ordinalNumber(closureOrdinal);
  const ordinals = Array.from({ length: end + 1 }, (_, i) => `A${i}`);
  const admissions = [...idx.all("normal_admission"), ...idx.all("recovery_admission")].filter((record) => ordinalNumber(record.payload.ordinal) <= end).map((record) => record.payload.ordinal).sort((a, b) => ordinalNumber(a) - ordinalNumber(b));
  if (!eq(admissions, ordinals)) reject("RESOURCE_ATTEMPT_DOMAIN_INCOMPLETE");
  const attempts = [];
  const vertices = [];
  for (const ordinal of ordinals) {
    const life = idx.one("resource_lifetime", (record) => record.payload.ordinal === ordinal);
    if (!life || !idx.one("attempt_start", (record) => record.payload.ordinal === ordinal)) reject("RESOURCE_LIFETIME_MISSING", ordinal);
    const p = life.payload;
    attempts.push({ id: ordinal, bootstrap_observed: p.bootstrap_observed, bootstrap_cap: p.bootstrap_cap, meter_observed_preterminal: p.meter_observed_preterminal, meter_preterminal_cap: p.meter_preterminal_cap, meter_terminal_cap: p.meter_terminal_cap, wall_cap: p.wall_cap, io_charge: p.io_charge, disk_charge: p.disk_charge });
    vertices.push({ id: ordinal, capacity: p.memory_capacity, interval_start: p.interval_start, interval_end: p.interval_end });
  }
  const maxEnd = Math.max(...vertices.map((vertex) => vertex.interval_end));
  vertices.push({ id: `closure-${closureOrdinal}`, capacity: 5, interval_start: maxEnd - 2, interval_end: maxEnd + 3 });
  const edges = [];
  for (let i = 0; i < vertices.length; i += 1) for (let j = i + 1; j < vertices.length; j += 1) if (overlaps(vertices[i], vertices[j])) edges.push([vertices[i].id, vertices[j].id]);
  return { schema: "tt-supervised-resource-input-v3", closure_ordinal: closureOrdinal, attempts, memory_vertices: vertices, possible_overlap_edges: edges };
}

function resourceTotals(input) {
  const cpu = input.attempts.reduce((sum, row) => sum + (row.bootstrap_observed ?? row.bootstrap_cap) + (row.meter_observed_preterminal ?? row.meter_preterminal_cap) + row.meter_terminal_cap, 0);
  const wall = input.attempts.reduce((sum, row) => sum + row.wall_cap, 0);
  const io = input.attempts.reduce((sum, row) => sum + row.io_charge, 0);
  const disk = input.attempts.reduce((sum, row) => sum + row.disk_charge, 0);
  const adjacency = new Map(input.memory_vertices.map((vertex) => [vertex.id, new Set([vertex.id])]));
  for (const [a, b] of input.possible_overlap_edges) { adjacency.get(a).add(b); adjacency.get(b).add(a); }
  const seen = new Set();
  const components = [];
  for (const vertex of input.memory_vertices) {
    if (seen.has(vertex.id)) continue;
    const stack = [vertex.id]; const members = []; let charge = 0;
    while (stack.length) {
      const id = stack.pop(); if (seen.has(id)) continue; seen.add(id); members.push(id);
      charge += input.memory_vertices.find((row) => row.id === id).capacity;
      for (const neighbor of adjacency.get(id)) stack.push(neighbor);
    }
    components.push({ members: members.sort(), charge });
  }
  return { cpu, memory: Math.max(...components.map((row) => row.charge)), wall, io, disk, memory_components: components };
}

function gitCommitText(intent) {
  const parent = intent.parent_oid === null ? "" : `parent ${intent.parent_oid}\n`;
  return `tree ${intent.tree_oid}\n${parent}author AutoLab <autolab@example.invalid> 0 +0000\ncommitter AutoLab <autolab@example.invalid> 0 +0000\n\n${intent.message}\n`;
}

function semanticAudit(records) {
  const idx = indexUniverse(records);
  if (idx.all("campaign_config").length !== 1 || idx.all("root_lock").length !== 1) reject("ROOT_SINGLETON_CARDINALITY_INVALID");
  const config = idx.one("campaign_config");
  const lock = idx.one("root_lock");
  const cp = config.payload;
  if (cp.sequence !== 0 || !["normal", "recovery"].includes(cp.requested_run_mode) || cp.approval_maximum_recovery_bootstraps < 0 || cp.approval_maximum_recovery_bootstraps > 32) reject("CONFIG_INVALID");
  if (cp.intended_ref !== "refs/autolab/supervised-campaign" || cp.initial_ref_oid !== null || cp.capability_descriptor_sha256 !== digest(cp.capability_descriptor)) reject("CONFIG_REPOSITORY_INVALID");
  if (cp.capability_descriptor_sha256 !== "38f49405406dbbdb2415065635e4d2c202d653d693cd3662e89cd0391b74ed6a" || !eq(cp.capability_descriptor.inherited_descriptor_bindings, descriptorBindings) || cp.capability_descriptor.executable_path !== "candidate/bin/run" || cp.capability_descriptor.executable_sha256 !== "a".repeat(64) || cp.capability_descriptor.network !== "deny" || cp.capability_descriptor.private_artifact_labels !== "deny") reject("CAPABILITY_DESCRIPTOR_INVALID");
  if (lock.payload.sequence !== 0 || lock.payload.status !== "valid_current" || lock.payload.lock_token !== `lock-${idx.campaign}`) reject("ROOT_LOCK_INVALID");

  const admissions = [...idx.all("normal_admission"), ...idx.all("recovery_admission")].sort((a, b) => ordinalNumber(a.payload.ordinal) - ordinalNumber(b.payload.ordinal));
  const seenOrdinals = new Set();
  for (const admission of admissions) {
    const n = ordinalNumber(admission.payload.ordinal);
    if (seenOrdinals.has(n)) reject("ORDINAL_DUPLICATE");
    seenOrdinals.add(n);
    if ((n === 0) !== (admission.record_type === "normal_admission")) reject("ORDINAL_ADMISSION_KIND_MISMATCH");
    if (n > cp.approval_maximum_recovery_bootstraps) reject("ORDINAL_APPROVAL_EXCEEDED");
    if (n === 0 && admission.payload.predecessor_attempt_end_sha256 !== null) reject("ORDINAL_PREDECESSOR_INVALID", admission.payload.ordinal);
    if (n > 0) {
      const end = idx.one("attempt_end", (record) => record.payload.ordinal === `A${n - 1}`);
      if (!end || admission.payload.predecessor_attempt_end_sha256 !== end.sha256) reject("ORDINAL_PREDECESSOR_INVALID", admission.payload.ordinal);
    }
  }
  for (let n = 0; n < admissions.length; n += 1) if (admissions[n].payload.ordinal !== `A${n}`) reject("ORDINAL_HISTORY_NONCONTIGUOUS");
  const startsSeen = new Set();
  for (const start of idx.all("attempt_start")) {
    ordinalNumber(start.payload.ordinal);
    if (startsSeen.has(start.payload.ordinal)) reject("ATTEMPT_START_DUPLICATE");
    startsSeen.add(start.payload.ordinal);
    const admission = admissions.find((record) => record.payload.ordinal === start.payload.ordinal);
    if (!admission || start.payload.admission_sha256 !== admission.sha256) reject("ATTEMPT_START_ADMISSION_MISMATCH");
  }
  for (const life of idx.all("resource_lifetime")) {
    ordinalNumber(life.payload.ordinal);
    if (!Number.isSafeInteger(life.payload.interval_start) || !Number.isSafeInteger(life.payload.interval_end) || life.payload.interval_start >= life.payload.interval_end) reject("RESOURCE_INTERVAL_INVALID");
    for (const key of ["bootstrap_cap", "meter_preterminal_cap", "meter_terminal_cap", "wall_cap", "io_charge", "disk_charge", "memory_capacity"]) if (!Number.isSafeInteger(life.payload[key]) || life.payload[key] < 0) reject("RESOURCE_LIFETIME_VALUE_INVALID");
  }
  for (const measurement of idx.all("resource_measurement")) {
    const expected = expectedResourceInput(idx, measurement.payload.closure_ordinal);
    const actual = measurement.payload.input;
    if (!eq(actual?.attempts?.map((row) => row.id), expected.attempts.map((row) => row.id))) reject("RESOURCE_MEASUREMENT_DOMAIN_MISMATCH");
    if (!eq(actual?.memory_vertices, expected.memory_vertices)) reject("RESOURCE_MEMORY_VERTEX_DOMAIN_MISMATCH");
    if (!eq(actual?.possible_overlap_edges, expected.possible_overlap_edges)) reject("RESOURCE_OVERLAP_GRAPH_MISMATCH");
    if (!eq(actual, expected)) reject("RESOURCE_INPUT_MISMATCH");
    const totals = resourceTotals(expected);
    if (measurement.payload.input_sha256 !== digest(expected) || !eq(measurement.payload.result, totals) || measurement.payload.result_sha256 !== digest(totals)) reject("RESOURCE_MEASUREMENT_ARITHMETIC_MISMATCH");
  }
  for (const receipt of idx.all("resource_receipt")) {
    const p = receipt.payload;
    const measurement = idx.one("resource_measurement", (record) => record.sha256 === p.measurement_sha256);
    const admission = admissions.find((record) => record.payload.ordinal === p.ordinal);
    const start = idx.one("attempt_start", (record) => record.payload.ordinal === p.ordinal);
    if (!measurement || !admission || !start) reject("RESOURCE_RECEIPT_LINK_MISSING");
    if (measurement.payload.closure_ordinal !== p.ordinal || measurement.payload.input.attempts.filter((row) => row.id === p.ordinal).length !== 1) reject("RESOURCE_RECEIPT_ORDINAL_MISMATCH");
    if (p.admission_sha256 !== admission.sha256 || p.attempt_start_sha256 !== start.sha256) reject("RESOURCE_RECEIPT_IDENTITY_MISMATCH");
  }
  for (const end of idx.all("attempt_end")) if (!idx.one("resource_receipt", (record) => record.sha256 === end.payload.resource_receipt_sha256 && record.payload.ordinal === end.payload.ordinal)) reject("ATTEMPT_END_RESOURCE_MISMATCH");

  const committedMap = new Map(idx.all("committed_phase").map((record) => [record.payload.phase, record]));
  for (const reservation of idx.all("phase_reservation")) {
    const p = reservation.payload;
    if (!phases.includes(p.phase) || ordinalNumber(p.ordinal) < 0 || p.phase_mode !== `${p.phase}:${p.phase === "E0" ? "evaluate" : "not_applicable"}`) reject("RESERVATION_IDENTITY_INVALID");
    const priorPhase = phases[phases.indexOf(p.phase) - 1];
    const prior = priorPhase ? committedMap.get(priorPhase) : null;
    if ((prior?.sha256 || null) !== p.predecessor_committed_sha256 || (prior?.payload.commit_oid || null) !== p.predecessor_commit_oid) reject("RESERVATION_PREDECESSOR_MISMATCH", p.phase);
  }
  for (const identity of idx.all("executable_identity")) {
    const p = identity.payload;
    if (p.executable_path !== cp.capability_descriptor.executable_path || p.executable_sha256 !== cp.capability_descriptor.executable_sha256 || p.opened_file_token !== `opened:${p.ordinal}:${p.phase}:${p.executable_sha256}`) reject("EXECUTABLE_IDENTITY_INVALID");
  }
  for (const cap of idx.all("capability_receipt")) {
    const p = cap.payload;
    const reservation = idx.one("phase_reservation", (record) => record.sha256 === p.reservation_sha256);
    const executable = idx.one("executable_identity", (record) => record.sha256 === p.executable_identity_sha256);
    if (!reservation || !executable || reservation.payload.phase !== p.phase || reservation.payload.ordinal !== p.ordinal || executable.payload.phase !== p.phase || executable.payload.ordinal !== p.ordinal) reject("CAPABILITY_RESERVATION_MISMATCH");
    if (p.descriptor_sha256 !== cp.capability_descriptor_sha256) reject("CAPABILITY_DESCRIPTOR_MISMATCH");
    if (!eq(p.inherited_descriptor_bindings, cp.capability_descriptor.inherited_descriptor_bindings)) reject("CAPABILITY_DESCRIPTOR_BINDING_MISMATCH");
    if (p.decision !== "allow") reject("CAPABILITY_DECISION_INVALID");
  }
  for (const mapIntent of idx.all("private_map_open_intent")) if (!idx.one("phase_reservation", (record) => record.sha256 === mapIntent.payload.reservation_sha256 && record.payload.phase === "E0" && record.payload.ordinal === mapIntent.payload.ordinal)) reject("PRIVATE_MAP_RESERVATION_MISMATCH");
  for (const mapObservation of idx.all("private_map_open_observation")) if (!idx.one("private_map_open_intent", (record) => record.sha256 === mapObservation.payload.open_intent_sha256) || mapObservation.payload.outcome !== "opened") reject("PRIVATE_MAP_OBSERVATION_INVALID");
  for (const mapReceipt of idx.all("private_map_opened_receipt")) {
    const reservation = idx.one("phase_reservation", (record) => record.sha256 === mapReceipt.payload.reservation_sha256);
    const intent = idx.one("private_map_open_intent", (record) => record.sha256 === mapReceipt.payload.open_intent_sha256);
    const observation = idx.one("private_map_open_observation", (record) => record.sha256 === mapReceipt.payload.open_observation_sha256);
    if (!reservation || !intent || !observation || mapReceipt.payload.descriptor_token !== observation.payload.descriptor_token) reject("PRIVATE_MAP_RECEIPT_MISMATCH");
  }
  for (const launch of idx.all("launch_intent")) {
    const p = launch.payload;
    const reservation = idx.one("phase_reservation", (record) => record.sha256 === p.reservation_sha256);
    const cap = idx.one("capability_receipt", (record) => record.sha256 === p.capability_receipt_sha256);
    const executable = idx.one("executable_identity", (record) => record.sha256 === p.executable_identity_sha256);
    if (!reservation || !cap || !executable || ![reservation, cap, executable].every((record) => record.payload.phase === p.phase && record.payload.ordinal === p.ordinal)) reject("LAUNCH_IDENTITY_MISMATCH");
    if (p.phase_mode !== reservation.payload.phase_mode) reject("LAUNCH_PHASE_MODE_MISMATCH");
  }
  for (const spawn of idx.all("phase_spawn")) {
    const launch = idx.one("launch_intent", (record) => record.sha256 === spawn.payload.launch_intent_sha256);
    if (!launch || launch.payload.phase !== spawn.payload.phase || launch.payload.ordinal !== spawn.payload.ordinal || spawn.payload.outcome !== "pid_returned") reject("PHASE_SPAWN_INVALID");
  }
  for (const reap of idx.all("phase_reap")) if (!idx.one("phase_spawn", (record) => record.sha256 === reap.payload.phase_spawn_sha256) || reap.payload.outcome !== "exited" || reap.payload.exit_code !== 0) reject("PHASE_REAP_INVALID");
  for (const result of idx.all("phase_result")) if (!idx.one("phase_reap", (record) => record.sha256 === result.payload.phase_reap_sha256) || result.payload.bounded !== true || result.payload.valid !== true) reject("PHASE_RESULT_INVALID");
  for (const content of idx.all("phase_content")) if (!idx.one("phase_result", (record) => record.sha256 === content.payload.phase_result_sha256) || content.payload.content_sha256 !== digest(content.payload.content_bytes)) reject("PHASE_CONTENT_INVALID");
  const eventModel = { valid_outcome: ["TERMINAL_VALID_OUTCOME", "phase_content"], spawn_failure: ["TERMINAL_HARNESS_FAILURE", "phase_spawn"], runtime_failure: ["TERMINAL_HARNESS_FAILURE", "phase_reap"], validation_failure: ["TERMINAL_HARNESS_FAILURE", "phase_content"], quarantine: ["TERMINAL_QUARANTINE", "phase_content"] };
  for (const terminal of idx.all("phase_terminal")) {
    const p = terminal.payload; const predecessor = records.find((record) => record.sha256 === p.predecessor_sha256);
    const expected = eventModel[p.event_kind];
    if (!predecessor || !idx.one("phase_result", (record) => record.sha256 === p.result_sha256) || !idx.one("phase_content", (record) => record.sha256 === p.content_sha256)) reject("TERMINAL_LINKAGE_INVALID");
    if (!expected || p.outcome !== expected[0] || predecessor.record_type !== expected[1]) reject("TERMINAL_EVENT_PREDECESSOR_INVALID");
  }

  for (const pre of idx.all("ref_observation_pre")) {
    const reservation = idx.one("phase_reservation", (record) => record.payload.phase === pre.payload.phase);
    const expectedOid = reservation?.payload.predecessor_commit_oid || null;
    if (pre.payload.ref !== cp.intended_ref || pre.payload.observed_oid !== expectedOid || pre.payload.relation !== (expectedOid === null ? "absent_initial" : "at_parent")) reject("GIT_REF_PRE_MISMATCH");
  }
  for (const blob of idx.all("git_blob_object")) {
    const content = idx.one("phase_content", (record) => record.payload.phase === blob.payload.phase && record.payload.content_sha256 === blob.payload.source_content_sha256);
    const body = Buffer.from(blob.payload.object_bytes_hex, "hex");
    if (!content || body.toString("utf8") !== content.payload.content_bytes || blob.payload.oid !== gitHash("blob", body)) reject("GIT_BLOB_BYTES_MISMATCH");
  }
  for (const tree of idx.all("git_tree_object")) {
    const blob = idx.one("git_blob_object", (record) => record.sha256 === tree.payload.blob_record_sha256);
    const expected = blob && Buffer.concat([Buffer.from("100644 phase.json\0", "utf8"), Buffer.from(blob.payload.oid, "hex")]);
    const actual = Buffer.from(tree.payload.object_bytes_hex, "hex");
    if (!blob || tree.payload.blob_oid !== blob.payload.oid || !actual.equals(expected) || tree.payload.oid !== gitHash("tree", actual)) reject("GIT_TREE_BYTES_MISMATCH");
  }
  const outcomeName = { TERMINAL_VALID_OUTCOME: "valid_outcome", TERMINAL_HARNESS_FAILURE: "harness_failure", TERMINAL_QUARANTINE: "quarantine" };
  for (const intent of idx.all("commit_intent")) {
    const p = intent.payload; const reservation = idx.one("phase_reservation", (record) => record.payload.phase === p.phase);
    const tree = idx.one("git_tree_object", (record) => record.sha256 === p.tree_record_sha256); const terminal = idx.one("phase_terminal", (record) => record.sha256 === p.terminal_sha256);
    if (!reservation || !tree || !terminal || !idx.one("phase_result", (record) => record.sha256 === p.result_sha256) || !idx.one("phase_content", (record) => record.sha256 === p.content_sha256)) reject("GIT_INTENT_LINK_MISSING");
    if (p.schema !== "tt-supervised-git-intent-v3" || p.tree_oid !== tree.payload.oid || p.parent_oid !== reservation.payload.predecessor_commit_oid || p.intended_ref !== cp.intended_ref || p.self_exclusion !== "commit_oid_forbidden") reject("GIT_PARENT_MISMATCH");
    if (p.terminal_outcome !== outcomeName[terminal.payload.outcome]) reject("GIT_TERMINAL_OUTCOME_MISMATCH");
  }
  for (const object of idx.all("commit_object")) {
    const intent = idx.one("commit_intent", (record) => record.sha256 === object.payload.intent_sha256); if (!intent) reject("GIT_COMMIT_INTENT_MISSING");
    const expected = gitCommitText(intent.payload);
    if (object.payload.commit_bytes !== expected || object.payload.oid !== gitHash("commit", Buffer.from(expected, "utf8")) || object.payload.tree_oid !== intent.payload.tree_oid || object.payload.parent_oid !== intent.payload.parent_oid) reject("GIT_COMMIT_BYTES_MISMATCH");
  }
  for (const cas of idx.all("ref_cas_attempt")) {
    const object = idx.one("commit_object", (record) => record.sha256 === cas.payload.commit_object_sha256); const pre = idx.one("ref_observation_pre", (record) => record.sha256 === cas.payload.ref_observation_pre_sha256);
    if (!object || !pre || cas.payload.ref !== cp.intended_ref) reject("GIT_REF_MISMATCH");
    if (cas.payload.expected_old_oid !== pre.payload.observed_oid || cas.payload.new_oid !== object.payload.oid || cas.payload.outcome !== "applied") reject("GIT_CAS_LINKAGE_MISMATCH");
  }
  for (const post of idx.all("ref_observation_post")) {
    const cas = idx.one("ref_cas_attempt", (record) => record.sha256 === post.payload.cas_sha256);
    if (!cas || post.payload.ref !== cp.intended_ref || post.payload.observed_oid !== cas.payload.new_oid) reject("POST_CAS_REF_MISMATCH");
  }
  for (const committed of idx.all("committed_phase")) {
    const object = idx.one("commit_object", (record) => record.sha256 === committed.payload.commit_object_sha256); const post = idx.one("ref_observation_post", (record) => record.sha256 === committed.payload.post_ref_observation_sha256);
    if (!object || !idx.one("ref_cas_attempt", (record) => record.sha256 === committed.payload.ref_cas_sha256) || !post || committed.payload.commit_oid !== object.payload.oid || post.payload.observed_oid !== object.payload.oid) reject("COMMITTED_PHASE_LINKAGE_MISMATCH");
  }
  const commits = idx.all("committed_phase").sort((a, b) => phases.indexOf(a.payload.phase) - phases.indexOf(b.payload.phase));
  for (let i = 0; i < commits.length; i += 1) {
    if (commits[i].payload.phase !== phases[i]) reject("GIT_PHASE_CHAIN_NONCONTIGUOUS");
    if (i > 0) {
      const object = idx.one("commit_object", (record) => record.sha256 === commits[i].payload.commit_object_sha256);
      if (object.payload.parent_oid !== commits[i - 1].payload.commit_oid) reject("GIT_PARENT_MISMATCH");
    }
  }
  for (const identity of idx.all("launch_identity")) {
    const tokens = idx.all("phase_spawn").filter((record) => record.payload.ordinal === identity.payload.ordinal).map((record) => record.payload.process_token).sort();
    if (identity.payload.executable_sha256 !== cp.capability_descriptor.executable_sha256 || !eq(identity.payload.process_tokens, tokens)) reject("METER_LAUNCH_IDENTITY_MISMATCH");
  }
  for (const observation of idx.all("kernel_process_observation")) if (!idx.one("launch_identity", (record) => record.sha256 === observation.payload.launch_identity_sha256 && record.payload.ordinal === observation.payload.ordinal) || observation.payload.observation !== "kernel_confirmed_absent") reject("KERNEL_OBSERVATION_IDENTITY_MISMATCH");
  for (const terminal of idx.all("campaign_terminal")) {
    const resource = idx.one("resource_receipt", (record) => record.sha256 === terminal.payload.resource_receipt_sha256); const end = idx.one("attempt_end", (record) => record.sha256 === terminal.payload.attempt_end_sha256); const closure = idx.one("closure_request", (record) => record.sha256 === terminal.payload.closure_request_sha256);
    if (!resource || !end || !closure || ![resource, end, closure].every((record) => record.payload.ordinal === terminal.payload.ordinal) || terminal.payload.kind !== "valid_attested_closure") reject("CAMPAIGN_TERMINAL_LINKAGE_MISMATCH");
  }
  return idx;
}

function sourceObject(schemaId, values) {
  const schema = selector.source_schemas[schemaId];
  if (!schema) reject("SOURCE_SCHEMA_UNKNOWN", schemaId);
  const source = clone(schema.fixed);
  for (const [field, domain] of Object.entries(schema.domains)) source[field] = clone(domain[0]);
  Object.assign(source, clone(values));
  if (!eq(Object.keys(source).sort(), schema.permitted)) reject("DERIVED_SOURCE_INVALID", `${schemaId}:keys`);
  for (const [field, expected] of Object.entries(schema.fixed)) if (!eq(source[field], expected)) reject("DERIVED_SOURCE_INVALID", `${schemaId}:${field}`);
  for (const [field, domain] of Object.entries(schema.domains)) if (!domain.some((value) => eq(value, source[field]))) reject("DERIVED_SOURCE_INVALID", `${schemaId}:${field}`);
  return source;
}

function select(schemaId, source) {
  const candidates = selector.rules.filter((rule) => rule.source_schema === schemaId && Object.entries(rule.compiled_predicate).every(([field, expected]) => Array.isArray(expected) ? expected.some((value) => eq(value, source[field])) : eq(expected, source[field])));
  if (candidates.length > 1) reject("RULE_OVERLAP", `${schemaId}:${candidates.map((rule) => rule.id).join(",")}`);
  return candidates[0] || { id: "DEFAULT", next_action: "request_infrastructure_failure", next_context: "meter_finalization" };
}

function currentAdmissionFrom(idx) {
  return [...idx.all("normal_admission"), ...idx.all("recovery_admission")].sort((a, b) => ordinalNumber(b.payload.ordinal) - ordinalNumber(a.payload.ordinal))[0] || null;
}

function activeReservationFrom(idx) {
  const done = new Set(idx.all("committed_phase").map((record) => record.payload.phase));
  return idx.all("phase_reservation").filter((record) => !done.has(record.payload.phase)).sort((a, b) => phases.indexOf(b.payload.phase) - phases.indexOf(a.payload.phase))[0] || null;
}

function lastCommitFrom(idx) {
  return idx.all("committed_phase").sort((a, b) => phases.indexOf(b.payload.phase) - phases.indexOf(a.payload.phase))[0] || null;
}

function phaseOne(idx, type, phase) {
  return idx.one(type, (record) => record.payload.phase === phase);
}

function reconstructNext(records, context) {
  const idx = indexUniverse(records);
  const config = idx.one("campaign_config");
  if (!config) reject("CONFIG_MISSING");
  if (idx.one("lock_release")) return { kind: "complete", context, reason: "LOCK_RELEASED" };
  const admission = currentAdmissionFrom(idx);
  const ordinal = admission?.payload.ordinal || (config.payload.requested_run_mode === "normal" ? "A0" : `A${idx.all("recovery_admission").length + 1}`);
  const mode = ordinal === "A0" ? "normal" : "recovery";
  if (context === "entry_preflight") {
    if (config.payload.requested_run_mode === "normal") return { kind: "ready", context, schema_id: "locked_normal_eligible_v3", source: sourceObject("locked_normal_eligible_v3", { recovery_slot: "not_applicable", repository_identity: "valid", phase_chain: "valid", ref_relation: "absent_initial", initial_phase_state: "empty", entry_product_relation: "valid_normal" }) };
    const consumed = idx.all("recovery_admission").length; const maximum = config.payload.approval_maximum_recovery_bootstraps;
    return { kind: "ready", context, schema_id: "locked_recovery_eligible_v3", source: sourceObject("locked_recovery_eligible_v3", { recovery_budget_state: { maximum, consumed, next_ordinal: `A${consumed + 1}`, status: "available" }, recovery_slot: "not_applicable", repository_identity: "valid", phase_chain: "valid", ref_relation: lastCommitFrom(idx) ? "at_last_commit" : "absent_initial", initial_phase_state: "empty", entry_product_relation: "valid_recovery" }) };
  }
  if (!admission) reject("CURRENT_ADMISSION_MISSING");
  const start = idx.one("attempt_start", (record) => record.payload.ordinal === ordinal);
  if (context === "attempt_admission") return { kind: "ready", context, schema_id: "attempt_admission_v2", source: sourceObject("attempt_admission_v2", { run_mode: mode, admission_kind: mode, admission_ordinal: ordinal, linked_attempt_record: start ? "durable" : "absent", normal_consumption_binding: "valid", recovery_budget_binding: mode === "recovery" ? "valid" : "not_applicable" }) };
  if (!start) reject("CURRENT_ATTEMPT_START_MISSING");
  if (context === "recovery_reconstruction") {
    const reservation = activeReservationFrom(idx); const phase = reservation?.payload.phase || "P0";
    return { kind: "ready", context, schema_id: "recovery_reconstruction_v3", source: sourceObject("recovery_reconstruction_v3", { run_mode: "recovery", attempt_ordinal: ordinal, phase_mode: reservation?.payload.phase_mode || `${phase}:not_applicable`, state: reservation ? "RESERVED" : "UNSEEN", private_map_identity: phase === "E0" ? { state: "MAP_OPENED_RECEIPT_DURABLE", binding: "valid_current", relation: "valid" } : { state: "not_applicable", binding: "not_applicable", relation: "valid" }, process_reconciliation: "not_applicable", recoverable_result: "not_applicable" }) };
  }
  if (context === "campaign_progression") {
    const committed = lastCommitFrom(idx); const terminal = committed && phaseOne(idx, "phase_terminal", committed.payload.phase); const post = committed && phaseOne(idx, "ref_observation_post", committed.payload.phase);
    const outcome = terminal ? ({ TERMINAL_VALID_OUTCOME: "valid_outcome", TERMINAL_HARNESS_FAILURE: "harness_failure", TERMINAL_QUARANTINE: "quarantine" })[terminal.payload.outcome] : "none";
    return { kind: "ready", context, schema_id: "campaign_progression_v3", source: sourceObject("campaign_progression_v3", { run_mode: mode, attempt_ordinal: ordinal, trigger: committed ? "phase_committed" : "normal_consumption", last_committed_phase: committed?.payload.phase || "none", last_phase_outcome: outcome, ref_relation: committed && post?.payload.observed_oid === committed.payload.commit_oid ? "at_last_commit" : "absent_initial" }) };
  }
  const reservation = activeReservationFrom(idx);
  if (["live_supervisor", "e0_private_map", "repository_validation"].includes(context) && !reservation) reject("ACTIVE_PHASE_RESERVATION_MISSING");
  const phase = reservation?.payload.phase;
  if (context === "e0_private_map") {
    const intent = idx.one("private_map_open_intent"); const observation = idx.one("private_map_open_observation"); const receipt = idx.one("private_map_opened_receipt");
    const state = !intent ? "MAP_UNSEEN" : !observation ? "MAP_OPEN_INTENT_DURABLE" : !receipt ? "MAP_OPENED_UNRECEIPTED" : "MAP_OPENED_RECEIPT_DURABLE";
    const event = !intent ? "request_open_intent" : !observation ? "open_syscall_success" : !receipt ? "publish_opened_receipt" : "dispatch_live_supervisor";
    return { kind: "ready", context, schema_id: "e0_private_map_v3", source: sourceObject("e0_private_map_v3", { run_mode: mode, attempt_ordinal: ordinal, e0_mode: "evaluate", map_state: state, event, descriptor_state: observation ? "trusted_meter_only" : "absent" }) };
  }
  if (context === "live_supervisor") {
    if (!phaseOne(idx, "capability_receipt", phase)) return { kind: "wait", context, observation_kind: "capability_attestation", ordinal, phase };
    const launch = phaseOne(idx, "launch_intent", phase); const spawn = phaseOne(idx, "phase_spawn", phase); const reap = phaseOne(idx, "phase_reap", phase); const result = phaseOne(idx, "phase_result", phase); const content = phaseOne(idx, "phase_content", phase); const terminal = phaseOne(idx, "phase_terminal", phase);
    let state = "RESERVED"; if (launch) state = "LAUNCH_INTENT_DURABLE"; if (spawn) state = "SPAWNED"; if (reap) state = "REAPED"; if (result) state = "RESULT_RETAINED"; if (content) state = "CONTENT_PUBLISHED"; if (terminal) state = terminal.payload.outcome;
    const values = { run_mode: mode, attempt_ordinal: ordinal, state, result_disposition: state === "REAPED" ? true : "not_applicable", launch_prerequisite: state === "RESERVED" ? "satisfied" : "not_applicable" };
    if (phase === "E0") return { kind: "ready", context, schema_id: "live_e0_evaluate_action_v3", source: sourceObject("live_e0_evaluate_action_v3", values) };
    values.phase_mode = reservation.payload.phase_mode;
    return { kind: "ready", context, schema_id: "live_candidate_action_v3", source: sourceObject("live_candidate_action_v3", values) };
  }
  if (context === "repository_validation") {
    const intent = phaseOne(idx, "commit_intent", phase); const object = phaseOne(idx, "commit_object", phase); const pre = phaseOne(idx, "ref_observation_pre", phase); const cas = phaseOne(idx, "ref_cas_attempt", phase);
    return { kind: "ready", context, schema_id: "git_commit_validation_v2", source: sourceObject("git_commit_validation_v2", { run_mode: mode, attempt_ordinal: ordinal, phase_mode: reservation.payload.phase_mode, commit_intent_relation: intent ? "valid_self_excluding" : "absent", commit_object_state: object ? "exact" : "absent", ref_relation: pre?.payload.relation || (phase === "P0" ? "absent_initial" : "at_parent"), cas_status: cas?.payload.outcome || "not_attempted" }) };
  }
  if (context === "meter_finalization") {
    const identity = idx.one("launch_identity", (record) => record.payload.ordinal === ordinal); const process = idx.one("kernel_process_observation", (record) => record.payload.ordinal === ordinal); const measurement = idx.one("resource_measurement", (record) => record.payload.closure_ordinal === ordinal);
    if (!identity || !process || !measurement) return { kind: "wait", context, observation_kind: "meter_finalization", ordinal };
    const resource = idx.one("resource_receipt", (record) => record.payload.ordinal === ordinal); const end = idx.one("attempt_end", (record) => record.payload.ordinal === ordinal); const terminal = idx.one("campaign_terminal"); const closure = idx.one("closure_request"); const recalculation = idx.one("recalculation_receipt");
    return { kind: "ready", context, schema_id: "meter_finalization_v3", source: sourceObject("meter_finalization_v3", { attempt_identity: { run_mode: mode, admission_kind: mode, ordinal }, process_absence: process.payload.observation, durable_state: end?.payload.durable_state || "valid", terminal_request: closure?.payload.terminal_request || "absent", resource_receipt: resource ? "durable" : "absent", attempt_end: end ? "durable" : "absent", campaign_terminal: terminal?.payload.kind || "absent", recalculation: recalculation ? "complete" : "not_started", lock_release: "held" }) };
  }
  reject("CONTEXT_UNKNOWN", context);
}

const actionDomainTypes = {
  E012: ["normal_admission"], E013: ["recovery_admission"], D001: ["attempt_start"], D002: ["attempt_start"], D003: [], D004: [], R001: [],
  C001: ["phase_reservation"], C002: ["phase_reservation"], C003: ["phase_reservation"], C005: ["closure_request"],
  P001: ["private_map_open_intent"], P002: ["private_map_open_observation"], P004: ["private_map_opened_receipt"], P005: [],
  AN001: ["launch_intent"], AE001: ["launch_intent"], AN002: ["phase_spawn"], AE002: ["phase_spawn"], AN004: ["phase_reap"], AE004: ["phase_reap"], AN005R: ["phase_result"], AE005R: ["phase_result"], AN006: ["phase_content"], AE006: ["phase_content"], AN007: ["phase_terminal"], AE007: ["phase_terminal"], AN008: ["ref_observation_pre"], AE008: ["ref_observation_pre"],
  G000: ["git_blob_object", "git_tree_object", "commit_intent"], G001: ["commit_object"], G003: ["ref_cas_attempt", "ref_observation_post"], G004: ["ref_cas_attempt", "ref_observation_post"], G005I: ["committed_phase"], G005E: ["committed_phase"],
  M002: ["resource_receipt"], M003: ["attempt_end"], M005: ["campaign_terminal"], M008: ["recalculation_receipt"], M009: ["lock_release"],
};

function replayTrace(records) {
  semanticAudit(records);
  const sequenceGroups = new Map();
  for (const record of records) {
    if (!sequenceGroups.has(record.payload.sequence)) sequenceGroups.set(record.payload.sequence, []);
    sequenceGroups.get(record.payload.sequence).push(record);
  }
  let prefix = ordered(sequenceGroups.get(0) || []); let context = "entry_preflight"; let previous = null;
  if (prefix.some((record) => ["action_receipt", "observation_receipt"].includes(record.record_type))) reject("JOURNAL_AT_SEQUENCE_ZERO");
  const baseAllowed = new Set(["campaign_config", "root_lock", "normal_admission", "recovery_admission", "attempt_start", "resource_lifetime", "resource_measurement", "resource_receipt", "attempt_end"]);
  const forbiddenBase = prefix.find((record) => !baseAllowed.has(record.record_type));
  if (forbiddenBase) reject("BASE_RECORD_TYPE_FORBIDDEN", forbiddenBase.record_type);
  const baseConfig = indexUniverse(prefix).one("campaign_config");
  if (baseConfig?.payload.requested_run_mode === "normal" && prefix.some((record) => !["campaign_config", "root_lock"].includes(record.record_type))) reject("BASE_NORMAL_HISTORY_FORBIDDEN");
  const receipts = records.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type)).sort((a, b) => a.payload.sequence - b.payload.sequence);
  for (let i = 0; i < receipts.length; i += 1) {
    const sequence = i + 1; const receipt = receipts[i];
    if (receipt.payload.sequence !== sequence) reject("JOURNAL_SEQUENCE_NONCONTIGUOUS");
    const group = ordered(sequenceGroups.get(sequence) || []); const journals = group.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type));
    if (journals.length !== 1 || journals[0].sha256 !== receipt.sha256) reject("JOURNAL_CARDINALITY_INVALID");
    const domain = group.filter((record) => record.sha256 !== receipt.sha256);
    if (receipt.payload.previous_journal_sha256 !== previous) reject("JOURNAL_PREDECESSOR_MISMATCH");
    if (receipt.payload.pre_universe_sha256 !== digest(prefix)) reject("JOURNAL_PRE_UNIVERSE_MISMATCH");
    if (!eq(receipt.payload.domain_record_sha256s, domain.map((record) => record.sha256))) reject("JOURNAL_DOMAIN_DIGEST_MISMATCH");
    if (receipt.payload.post_domain_universe_sha256 !== digest(ordered([...prefix, ...domain]))) reject("JOURNAL_POST_DOMAIN_MISMATCH");
    if (receipt.record_type === "action_receipt") {
      const next = reconstructNext(prefix, context); if (next.kind !== "ready") reject("ACTION_EXECUTED_WHILE_NOT_READY");
      const chosen = select(next.schema_id, next.source);
      if (receipt.payload.source_schema !== next.schema_id) reject("ACTION_SOURCE_SCHEMA_MISMATCH");
      if (receipt.payload.source_sha256 !== digest(next.source)) reject("ACTION_SOURCE_DIGEST_MISMATCH");
      if (receipt.payload.selected_rule !== chosen.id) reject("ACTION_SELECTED_RULE_MISMATCH");
      if (receipt.payload.selected_action !== chosen.next_action) reject("ACTION_SELECTED_ACTION_MISMATCH");
      if (receipt.payload.next_context !== chosen.next_context) reject("ACTION_NEXT_CONTEXT_MISMATCH");
      const expectedTypes = actionDomainTypes[chosen.id]; if (!expectedTypes) reject("ACTION_SEMANTICS_MISSING", chosen.id);
      if (!eq(domain.map((record) => record.record_type).sort(), [...expectedTypes].sort())) reject("ACTION_RECORD_MISMATCH", chosen.id);
      context = chosen.next_context;
    } else {
      if (receipt.payload.context !== context) reject("OBSERVATION_CONTEXT_MISMATCH");
      const expectedTypes = receipt.payload.observation_kind === "capability_attestation" ? ["executable_identity", "capability_receipt"] : receipt.payload.observation_kind === "meter_finalization" ? ["resource_lifetime", "launch_identity", "kernel_process_observation", "resource_measurement"] : null;
      if (!expectedTypes) reject("OBSERVATION_KIND_UNKNOWN");
      const prefixIndex = indexUniverse(prefix);
      if (receipt.payload.observation_kind === "capability_attestation") {
        const reservation = activeReservationFrom(prefixIndex);
        if (!reservation || !["live_supervisor", "e0_private_map"].includes(context) || phaseOne(prefixIndex, "capability_receipt", reservation.payload.phase)) reject("CAPABILITY_OBSERVATION_NOT_PENDING");
      }
      if (receipt.payload.observation_kind === "meter_finalization") {
        const admission = currentAdmissionFrom(prefixIndex);
        if (context !== "meter_finalization" || !admission || !prefixIndex.one("closure_request") || prefixIndex.one("resource_measurement", (record) => record.payload.closure_ordinal === admission.payload.ordinal)) reject("METER_OBSERVATION_NOT_PENDING");
      }
      if (!eq(domain.map((record) => record.record_type).sort(), expectedTypes.sort())) reject("OBSERVATION_RECORD_MISMATCH");
    }
    prefix = ordered([...prefix, ...domain, receipt]); previous = receipt.sha256;
  }
  const positive = [...sequenceGroups.keys()].filter((value) => value > 0).sort((a, b) => a - b);
  if (!eq(positive, receipts.map((record) => record.payload.sequence))) reject("UNJOURNALED_RECORD_SEQUENCE");
  if (!eq(prefix, ordered(records))) reject("JOURNAL_UNIVERSE_COVERAGE_MISMATCH");
  return { context, final: reconstructNext(prefix, context), journal_count: receipts.length, final_journal_sha256: previous, universe_sha256: digest(prefix) };
}

function mutate(records, operation) {
  const output = clone(records);
  if (operation.kind === "remove_records") {
    const removals = new Set(operation.paths);
    return ordered(output.filter((record) => !removals.has(record.path)));
  }
  if (operation.kind === "append_record") return ordered([...output, clone(operation.record)]);
  if (operation.kind === "replace_record") {
    const index = output.findIndex((record) => record.path === operation.path);
    if (index < 0) reject("REGRESSION_TARGET_MISSING", operation.path);
    output[index] = clone(operation.after_record);
    return ordered(output);
  }
  reject("REGRESSION_OPERATION_UNKNOWN", operation.kind);
}

function independentRegression(regression) {
  try {
    if (regression.operation.kind === "publication_selector_swap") {
      if (regression.operation.observed_selector_sha256 !== selectorExpected) reject("PUBLICATION_SELECTOR_HASH_MISMATCH");
      return { rejection: null, passed: false };
    }
    const trace = artifact.traces.find((candidate) => candidate.id === regression.target_trace);
    if (!trace) reject("TRACE_UNKNOWN", regression.target_trace);
    replayTrace(mutate(trace.final_record_universe, regression.operation));
    return { rejection: null, passed: false };
  } catch (error) {
    const rejection = error.code || "UNCLASSIFIED_ERROR";
    return { rejection, detail: error.message, passed: rejection === regression.expected_rejection };
  }
}

assertCheck("protocol", artifact.protocol === protocol, artifact.protocol);
assertCheck("artifact schema", artifact.schema === "tt-supervised-executor-closed-kernel-v9", artifact.schema);
assertCheck("selector bytes", digest(bytes.selector) === selectorExpected && artifact.selector_sha256 === selectorExpected, selectorExpected);
assertCheck("builder bytes", artifact.builder_sha256 === digest(bytes.builder), artifact.builder_sha256);
assertCheck("selector conservation", artifact.selector_rule_count === 153 && artifact.selector_symbolic_case_count === 1584249 && artifact.selector_partition_count === 179, `${artifact.selector_rule_count}/${artifact.selector_symbolic_case_count}/${artifact.selector_partition_count}`);
assertCheck("status boundary", ["HYPOTHESIS", "MODEL-BOUND", "ZERO-RUN", "NOVELTY-UNVERIFIED"].every((status) => artifact.status.includes(status)) && artifact.ecdlp_claim === false, stable(artifact.status));
assertCheck("authorization boundary", artifact.implementation_authorized === false && artifact.campaign_authorized === false && artifact.gates.implementation_gate === false && artifact.gates.campaign_gate === false, "implementation and campaign remain closed");
assertCheck("closed architecture", artifact.architecture.source_snapshots_permitted === false && artifact.architecture.unknown_records_rejected === true && artifact.architecture.producer_authority_closed === true && artifact.architecture.post_cas_ref_observation_required === true, stable(artifact.architecture));
assertCheck("record vocabulary", eq(Object.keys(artifact.record_schema_registry).sort(), Object.keys(producer).sort()), `${Object.keys(producer).length} types`);
for (const type of Object.keys(producer)) {
  const row = artifact.record_schema_registry[type];
  assertCheck(`registry ${type}`, row.allowed_producer === producer[type] && row.additional_payload_properties === false && eq(row.payload_required, fields[type]), type);
}

const requiredObligations = ["V9-REDUCER-01", "V9-SCHEMA-01", "V9-PATH-01", "V9-ORDINAL-01", "V9-IDENTITY-01", "V9-PHASE-01", "V9-TRACE-01", "V9-POST-01", "V9-EVENT-01", "V9-AUTHORITY-01", "V9-CLOSURE-01", "V9-GIT-01", "V9-GIT-02", "V9-OUTCOME-01", "V9-CAPABILITY-01", "V9-RESOURCE-01", "V9-RESOURCE-02", "V9-CONTEXT-01", "V9-PUBLISH-01", "V9-DIFFERENTIAL-01"];
assertCheck("repair obligations", eq(artifact.repair_obligations, requiredObligations), `${requiredObligations.length} obligations`);

for (const [id, evidence] of Object.entries(artifact.evidence_manifest)) {
  exactObject(evidence, ["relative_path", "sha256"], "EVIDENCE_MANIFEST_SCHEMA_MISMATCH");
  if (!evidence.relative_path.startsWith("evidence/")) reject("EVIDENCE_OUTSIDE_BUNDLE", evidence.relative_path);
  const observed = digest(readFileSync(resolveBundleFile(evidence.relative_path)));
  assertCheck(`evidence ${id}`, observed === evidence.sha256, observed);
}

const rejectedRoot = artifact.evidence_manifest.rejected_snapshot_root;
const rootEntries = parseSha256Manifest(readFileSync(resolveBundleFile(rejectedRoot.relative_path)), "root");
assertCheck("rejected evidence root cardinality", rootEntries.length === 1, `${rootEntries.length}`);
const rootEntry = rootEntries[0];
assertCheck("rejected evidence root target", rootEntry.path === "tt-supervised-executor-v8-rejected-snapshot/SHA256SUMS", rootEntry.path);
const rootBase = posix.dirname(rejectedRoot.relative_path);
const rejectedManifestRelativePath = posix.join(rootBase, rootEntry.path);
const rejectedManifestBytes = readFileSync(resolveBundleFile(rejectedManifestRelativePath));
assertCheck("rejected evidence root pin", digest(rejectedManifestBytes) === rootEntry.sha256, digest(rejectedManifestBytes));
const rejectedEntries = parseSha256Manifest(rejectedManifestBytes, "nested");
const rejectedBase = posix.dirname(rejectedManifestRelativePath);
const rejectedPaths = rejectedEntries.map((entry) => entry.path);
assertCheck("rejected evidence paths unique", new Set(rejectedPaths).size === rejectedPaths.length, `${rejectedPaths.length}`);
for (const entry of rejectedEntries) {
  if (
    entry.path.length === 0
    || entry.path.includes("\\")
    || posix.isAbsolute(entry.path)
    || posix.normalize(entry.path) !== entry.path
    || entry.path === "."
    || entry.path.startsWith("../")
  ) reject("NONCANONICAL_REJECTED_EVIDENCE_PATH", entry.path);
  const memberRelativePath = posix.join(rejectedBase, entry.path);
  const observed = digest(readFileSync(resolveBundleFile(memberRelativePath)));
  assertCheck(`rejected evidence member ${entry.path}`, observed === entry.sha256, observed);
}

assertCheck("trace cardinality", artifact.trace_count === 2 && artifact.traces.length === 2, `${artifact.traces.length}`);
let independentStepCount = 0;
for (const trace of artifact.traces) {
  const replay = replayTrace(trace.final_record_universe);
  independentStepCount += replay.journal_count;
  assertCheck(`trace ${trace.id} completion`, replay.final.kind === "complete" && replay.final.reason === "LOCK_RELEASED", replay.final.reason);
  assertCheck(`trace ${trace.id} step count`, replay.journal_count === trace.step_count && trace.steps.length === trace.step_count, `${replay.journal_count}`);
  assertCheck(`trace ${trace.id} universe`, replay.universe_sha256 === trace.final_universe_sha256 && replay.final_journal_sha256 === trace.final_journal_sha256, replay.universe_sha256);
  const reversedReplay = replayTrace([...trace.final_record_universe].reverse());
  assertCheck(`trace ${trace.id} order invariance`, reversedReplay.universe_sha256 === replay.universe_sha256 && reversedReplay.final_journal_sha256 === replay.final_journal_sha256, reversedReplay.universe_sha256);
  const actionRows = trace.steps.filter((step) => step.kind === "action");
  const receiptRules = trace.final_record_universe.filter((record) => record.record_type === "action_receipt").map((record) => record.payload.selected_rule);
  assertCheck(`trace ${trace.id} summaries`, eq(actionRows.map((step) => step.selected_rule), receiptRules), `${actionRows.length} actions`);
}
assertCheck("aggregate step count", independentStepCount === artifact.trace_step_count, `${independentStepCount}`);

const a2 = artifact.traces.find((trace) => trace.id === "SEC9-TRACE-A2-END-TO-END");
const a2Measurement = a2.final_record_universe.find((record) => record.record_type === "resource_measurement" && record.payload.closure_ordinal === "A2");
const a2Receipt = a2.final_record_universe.find((record) => record.record_type === "resource_receipt" && record.payload.ordinal === "A2");
assertCheck("A2 measurement domain", eq(a2Measurement.payload.input.attempts.map((row) => row.id), ["A0", "A1", "A2"]), stable(a2Measurement.payload.input.attempts.map((row) => row.id)));
assertCheck("A2 receipt binding", a2Receipt.payload.measurement_sha256 === a2Measurement.sha256 && a2Measurement.payload.input.attempts.filter((row) => row.id === "A2").length === 1, a2Receipt.sha256);
const a2Commits = a2.final_record_universe.filter((record) => record.record_type === "committed_phase").sort((a, b) => phases.indexOf(a.payload.phase) - phases.indexOf(b.payload.phase));
for (let i = 1; i < a2Commits.length; i += 1) {
  const object = a2.final_record_universe.find((record) => record.record_type === "commit_object" && record.payload.phase === a2Commits[i].payload.phase);
  assertCheck(`Git parent ${a2Commits[i].payload.phase}`, object.payload.parent_oid === a2Commits[i - 1].payload.commit_oid, object.payload.parent_oid);
}

assertCheck("regression cardinality", artifact.regression_count === 26 && artifact.regressions.length === 26, `${artifact.regressions.length}`);
const independentResults = artifact.regressions.map((regression) => ({ id: regression.id, expected_rejection: regression.expected_rejection, ...independentRegression(regression) }));
for (const result of independentResults) assertCheck(`regression ${result.id}`, result.passed, `${result.rejection}/${result.expected_rejection}`);
assertCheck("builder verdicts untrusted parity", artifact.regressions.every((regression) => regression.builder_result.passed === true) && independentResults.every((result) => result.passed), "builder and independent outcomes agree after separate execution");

assertCheck("contract labels", bytes.contract.toString("utf8").includes("V9") && bytes.contract.toString("utf8").includes("ZERO-RUN"), names.contract);
assertCheck("topology labels", bytes.topology.toString("utf8").includes("V9") && bytes.topology.toString("utf8").includes("deriveState"), names.topology);

const receipt = {
  schema: "tt-supervised-executor-local-verification-v9",
  protocol,
  status: "PASS",
  evidence_status: ["MODEL-BOUND", "ZERO-RUN"],
  ecdlp_claim: false,
  implementation_authorized: false,
  campaign_authorized: false,
  byte_snapshots: Object.fromEntries(Object.entries(bytes).map(([id, value]) => [id, { name: names[id], sha256: digest(value), byte_length: value.length }])),
  artifact_sha256: digest(bytes.artifact),
  selector_sha256: digest(bytes.selector),
  independent_trace_count: artifact.traces.length,
  independent_step_count: independentStepCount,
  independent_regression_count: independentResults.length,
  independent_regression_pass_count: independentResults.filter((result) => result.passed).length,
  independent_regression_results: independentResults,
  checks,
  check_count: checks.length,
  limitations: [
    "Local verification is not an independent Theory or Red Team GO decision.",
    "The finite model does not establish OS enforcement or filesystem durability.",
    "No campaign or cryptanalytic workload was executed.",
  ],
};

const receiptName = "local-verification-v9.json";
const receiptBytes = Buffer.from(`${JSON.stringify(receipt, null, 2)}\n`, "utf8");
writeFileSync(join(here, receiptName), receiptBytes);
process.stdout.write(`${JSON.stringify({ status: "PASS", receipt: receiptName, receipt_sha256: digest(receiptBytes), checks: checks.length, traces: artifact.traces.length, steps: independentStepCount, regressions: independentResults.length })}\n`);
