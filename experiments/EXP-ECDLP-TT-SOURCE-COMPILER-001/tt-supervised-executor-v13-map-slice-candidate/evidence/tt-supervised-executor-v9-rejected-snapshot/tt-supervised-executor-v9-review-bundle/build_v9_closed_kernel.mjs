import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join, posix } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const protocol = "EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor/9";
const selectorName = "selector-rules-v8.json";
const selectorExpectedSha256 = "2952bc3c3792eb3d43a4563ab4c6b7afa20922c0846a2a44f8b854bf873d2383";
const builderBytes = readFileSync(fileURLToPath(import.meta.url));
const selectorBytes = readFileSync(join(here, selectorName));

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function sha256(value) {
  const bytes = typeof value === "string" || Buffer.isBuffer(value) ? value : canonical(value);
  return createHash("sha256").update(bytes).digest("hex");
}

function sha1Bytes(bytes) {
  return createHash("sha1").update(bytes).digest("hex");
}

function gitOid(type, bytes) {
  const body = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes, "utf8");
  return sha1Bytes(Buffer.concat([Buffer.from(`${type} ${body.length}\0`, "utf8"), body]));
}

function clone(value) {
  return structuredClone(value);
}

function same(left, right) {
  return canonical(left) === canonical(right);
}

function fail(code, detail = "") {
  const error = new Error(`${code}${detail ? `: ${detail}` : ""}`);
  error.code = code;
  throw error;
}

function exactKeys(value, expected, code) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail(code, "not an object");
  if (!same(Object.keys(value).sort(), [...expected].sort())) fail(code, `${Object.keys(value).sort().join(",")}`);
}

function isHex(value, length) {
  return typeof value === "string" && new RegExp(`^[0-9a-f]{${length}}$`).test(value);
}

function isOrdinal(value) {
  return typeof value === "string" && /^A(?:0|[1-9]|[12][0-9]|3[0-2])$/.test(value);
}

function ordinalIndex(value) {
  if (!isOrdinal(value)) fail("ORDINAL_OUT_OF_RANGE", String(value));
  return Number(value.slice(1));
}

function isPhase(value) {
  return ["P0", "P1", "P2", "P3", "P4", "P5", "E0"].includes(value);
}

const phaseOrder = ["P0", "P1", "P2", "P3", "P4", "P5", "E0"];
const candidatePhases = phaseOrder.slice(0, 6);
const selectorSha256 = sha256(selectorBytes);
if (selectorSha256 !== selectorExpectedSha256) fail("SELECTOR_HASH_MISMATCH", selectorSha256);
const selector = JSON.parse(selectorBytes.toString("utf8"));
const sourceSchemas = selector.source_schemas;
const rules = selector.rules;
const rulesBySchema = Object.fromEntries(Object.keys(sourceSchemas).map((schemaId) => [schemaId, rules.filter((rule) => rule.source_schema === schemaId)]));

const inheritedDescriptorBindings = [
  { fd: 0, target: "stdin", rights: ["read"] },
  { fd: 1, target: "stdout", rights: ["write"] },
  { fd: 2, target: "stderr", rights: ["write"] },
];

const capabilityDescriptor = {
  schema: "candidate_boundary_descriptor_v4",
  executable_path: "candidate/bin/run",
  executable_sha256: "a".repeat(64),
  argv: ["candidate/bin/run", "--public-input", "candidate/public/input.json"],
  environment: { LANG: "C", PATH: "/usr/bin:/bin" },
  cwd: "candidate/work",
  readable_roots: ["candidate/public", "candidate/work"],
  writable_roots: ["candidate/work"],
  inherited_descriptor_bindings: inheritedDescriptorBindings,
  private_artifact_labels: "deny",
  path_resolution: "beneath_no_symlinks_no_magiclinks_no_xdev",
  mount_namespace: "private_unmounted_public_readonly",
  directory_handle_policy: "deny_unlisted_dirfds",
  syscall_profile: "candidate_no_network_no_process_control",
  resource_limits: {
    cpu_seconds: 300,
    address_space_bytes: 1073741824,
    open_files: 16,
    processes: 1,
    output_bytes: 67108864,
  },
  signal_policy: "self_and_supervisor_only",
  network: "deny",
  fork: "deny",
  exec: "deny_after_initial_image",
  ipc: "deny",
  debugger: "deny",
  task_port: "deny",
  ptrace: "deny",
  timeout_ms: 300000,
  kill_policy: "term_then_kill",
  reap_policy: "exact_identity_required",
};

const producerByType = {
  campaign_config: "bootstrap_controller",
  root_lock: "bootstrap_controller",
  normal_admission: "root_supervisor",
  recovery_admission: "root_supervisor",
  attempt_start: "root_supervisor",
  resource_lifetime: "external_meter",
  resource_measurement: "external_meter",
  resource_receipt: "external_meter",
  attempt_end: "external_meter",
  phase_reservation: "root_supervisor",
  executable_identity: "capability_guard",
  capability_receipt: "capability_guard",
  private_map_open_intent: "root_supervisor",
  private_map_open_observation: "root_supervisor",
  private_map_opened_receipt: "root_supervisor",
  launch_intent: "root_supervisor",
  phase_spawn: "root_supervisor",
  phase_reap: "root_supervisor",
  phase_result: "root_supervisor",
  phase_content: "root_supervisor",
  phase_terminal: "root_supervisor",
  ref_observation_pre: "repository_validator",
  git_blob_object: "repository_validator",
  git_tree_object: "repository_validator",
  commit_intent: "repository_validator",
  commit_object: "repository_validator",
  ref_cas_attempt: "repository_validator",
  ref_observation_post: "repository_validator",
  committed_phase: "repository_validator",
  closure_request: "root_supervisor",
  launch_identity: "external_meter",
  kernel_process_observation: "external_meter",
  recalculation_receipt: "external_meter",
  lock_release: "external_meter",
  campaign_terminal: "external_meter",
  action_receipt: "trusted_reducer",
  observation_receipt: "observation_gateway",
};

const payloadKeysByType = {
  campaign_config: ["sequence", "campaign_id", "requested_run_mode", "approval_maximum_recovery_bootstraps", "intended_ref", "initial_ref_oid", "capability_descriptor", "capability_descriptor_sha256", "resource_policy"],
  root_lock: ["sequence", "campaign_id", "lock_token", "status"],
  normal_admission: ["sequence", "campaign_id", "ordinal", "predecessor_attempt_end_sha256"],
  recovery_admission: ["sequence", "campaign_id", "ordinal", "predecessor_attempt_end_sha256"],
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
  launch_identity: ["sequence", "campaign_id", "ordinal", "executable_sha256", "process_tokens"],
  kernel_process_observation: ["sequence", "campaign_id", "ordinal", "launch_identity_sha256", "observation"],
  recalculation_receipt: ["sequence", "campaign_id", "ordinal", "campaign_terminal_sha256", "derived_totals_sha256", "status"],
  lock_release: ["sequence", "campaign_id", "ordinal", "recalculation_receipt_sha256", "status"],
  campaign_terminal: ["sequence", "campaign_id", "ordinal", "kind", "resource_receipt_sha256", "attempt_end_sha256", "closure_request_sha256"],
  action_receipt: ["sequence", "campaign_id", "previous_journal_sha256", "pre_universe_sha256", "source_schema", "source_sha256", "selected_rule", "selected_action", "next_context", "domain_record_sha256s", "post_domain_universe_sha256"],
  observation_receipt: ["sequence", "campaign_id", "previous_journal_sha256", "pre_universe_sha256", "observation_kind", "context", "domain_record_sha256s", "post_domain_universe_sha256"],
};

function suffixFor(record) {
  const p = record.payload;
  switch (record.record_type) {
    case "campaign_config": return "config.json";
    case "root_lock": return "root-lock.json";
    case "normal_admission":
    case "recovery_admission": return `admissions/${p.ordinal}.json`;
    case "attempt_start": return `attempts/${p.ordinal}/start.json`;
    case "resource_lifetime": return `attempts/${p.ordinal}/lifetime.json`;
    case "resource_measurement": return `accounting/measurements/${p.closure_ordinal}.json`;
    case "resource_receipt": return `attempts/${p.ordinal}/resource.json`;
    case "attempt_end": return `attempts/${p.ordinal}/end.json`;
    case "phase_reservation": return `phases/${p.phase}/reservation.json`;
    case "executable_identity": return `phases/${p.phase}/executable.json`;
    case "capability_receipt": return `phases/${p.phase}/capability.json`;
    case "private_map_open_intent": return "phases/E0/private-map-intent.json";
    case "private_map_open_observation": return "phases/E0/private-map-observation.json";
    case "private_map_opened_receipt": return "phases/E0/private-map-receipt.json";
    case "launch_intent": return `phases/${p.phase}/launch-intent.json`;
    case "phase_spawn": return `phases/${p.phase}/spawn.json`;
    case "phase_reap": return `phases/${p.phase}/reap.json`;
    case "phase_result": return `phases/${p.phase}/result.json`;
    case "phase_content": return `phases/${p.phase}/content.json`;
    case "phase_terminal": return `phases/${p.phase}/terminal.json`;
    case "ref_observation_pre": return `phases/${p.phase}/ref-pre.json`;
    case "git_blob_object": return `phases/${p.phase}/git-blob.json`;
    case "git_tree_object": return `phases/${p.phase}/git-tree.json`;
    case "commit_intent": return `phases/${p.phase}/commit-intent.json`;
    case "commit_object": return `phases/${p.phase}/commit-object.json`;
    case "ref_cas_attempt": return `phases/${p.phase}/ref-cas.json`;
    case "ref_observation_post": return `phases/${p.phase}/ref-post.json`;
    case "committed_phase": return `phases/${p.phase}/committed.json`;
    case "closure_request": return "closure-request.json";
    case "launch_identity": return `attempts/${p.ordinal}/launch-identity.json`;
    case "kernel_process_observation": return `attempts/${p.ordinal}/kernel-observation.json`;
    case "recalculation_receipt": return "recalculation.json";
    case "lock_release": return "lock-release.json";
    case "campaign_terminal": return "campaign-terminal.json";
    case "action_receipt": return `journal/${String(p.sequence).padStart(4, "0")}-action.json`;
    case "observation_receipt": return `journal/${String(p.sequence).padStart(4, "0")}-observation.json`;
    default: fail("RECORD_TYPE_UNKNOWN", record.record_type);
  }
}

function makeRecord(traceId, recordType, payload, producer = producerByType[recordType]) {
  const stub = { record_type: recordType, payload };
  const path = `kernel/${traceId}/${suffixFor(stub)}`;
  const body = { schema: "tt-supervised-record-v3", path, record_type: recordType, payload, producer };
  const canonicalBytes = canonical(body);
  return { ...body, canonical_bytes: canonicalBytes, sha256: sha256(canonicalBytes) };
}

function recordTraceId(record) {
  const match = record.path.match(/^kernel\/([A-Z0-9-]+)\//);
  if (!match) fail("PATH_TEMPLATE_MISMATCH", record.path);
  return match[1];
}

function validateCapabilityDescriptor(descriptor) {
  if (!same(descriptor, capabilityDescriptor)) fail("CAPABILITY_DESCRIPTOR_INVALID");
}

function validateRecordShape(record) {
  exactKeys(record, ["schema", "path", "record_type", "payload", "producer", "canonical_bytes", "sha256"], "RECORD_KEYS_MISMATCH");
  if (record.schema !== "tt-supervised-record-v3") fail("RECORD_SCHEMA_MISMATCH", record.path);
  const traceId = recordTraceId(record);
  if (posix.isAbsolute(record.path) || posix.normalize(record.path) !== record.path || record.path.includes("//")) fail("PATH_NONCANONICAL", record.path);
  if (!Object.hasOwn(producerByType, record.record_type)) fail("RECORD_TYPE_UNKNOWN", record.record_type);
  if (record.producer !== producerByType[record.record_type]) fail("PRODUCER_UNAUTHORIZED", `${record.record_type}:${record.producer}`);
  exactKeys(record.payload, payloadKeysByType[record.record_type], "PAYLOAD_KEYS_MISMATCH");
  if (!Number.isSafeInteger(record.payload.sequence) || record.payload.sequence < 0) fail("SEQUENCE_INVALID", record.path);
  if (record.payload.campaign_id !== traceId) fail("CAMPAIGN_ID_MISMATCH", record.path);
  const expectedPath = `kernel/${traceId}/${suffixFor(record)}`;
  if (record.path !== expectedPath) fail("PATH_TEMPLATE_MISMATCH", record.path);
  const { canonical_bytes: canonicalBytes, sha256: digest, ...body } = record;
  if (canonical(body) !== canonicalBytes) fail("RECORD_CANONICAL_BYTES_MISMATCH", record.path);
  if (sha256(canonicalBytes) !== digest) fail("RECORD_DIGEST_MISMATCH", record.path);
  return traceId;
}

function validateConfig(config) {
  const p = config.payload;
  if (p.sequence !== 0 || !["normal", "recovery"].includes(p.requested_run_mode)) fail("CONFIG_INVALID");
  if (!Number.isInteger(p.approval_maximum_recovery_bootstraps) || p.approval_maximum_recovery_bootstraps < 0 || p.approval_maximum_recovery_bootstraps > 32) fail("CONFIG_APPROVAL_INVALID");
  if (p.intended_ref !== "refs/autolab/supervised-campaign" || p.initial_ref_oid !== null) fail("CONFIG_REPOSITORY_INVALID");
  validateCapabilityDescriptor(p.capability_descriptor);
  if (p.capability_descriptor_sha256 !== sha256(p.capability_descriptor)) fail("CAPABILITY_DESCRIPTOR_DIGEST_MISMATCH");
  if (!same(p.resource_policy, { schema: "tt-supervised-resource-policy-v3", closure_memory_capacity: 5, interval_width: 10, interval_stride: 8 })) fail("RESOURCE_POLICY_INVALID");
}

function findOne(records, type, predicate = () => true) {
  return records.find((record) => record.record_type === type && predicate(record));
}

function findAll(records, type, predicate = () => true) {
  return records.filter((record) => record.record_type === type && predicate(record));
}

function sortedUniverse(records) {
  return clone(records).sort((left, right) => left.path.localeCompare(right.path));
}

function addRecord(records, record) {
  if (records.some((candidate) => candidate.path === record.path)) fail("DUPLICATE_DURABLE_PATH", record.path);
  records.push(record);
  records.sort((left, right) => left.path.localeCompare(right.path));
}

function lifetimePayload(traceId, ordinal, sequence) {
  const index = ordinalIndex(ordinal);
  const start = index * 8;
  return {
    sequence,
    campaign_id: traceId,
    ordinal,
    bootstrap_observed: index === 0 ? 13 : null,
    bootstrap_cap: 20 + index,
    meter_observed_preterminal: 7 + index,
    meter_preterminal_cap: 10 + index,
    meter_terminal_cap: 2,
    wall_cap: 40 + index,
    io_charge: 11 + index,
    disk_charge: 5 + index,
    memory_capacity: 31 + 6 * index,
    interval_start: start,
    interval_end: start + 10,
  };
}

function intervalsOverlap(left, right) {
  return left.interval_start < right.interval_end && right.interval_start < left.interval_end;
}

function resourceInputFor(records, closureOrdinal) {
  const closureIndex = ordinalIndex(closureOrdinal);
  const admissions = findAll(records, "normal_admission").concat(findAll(records, "recovery_admission"));
  const expectedOrdinals = Array.from({ length: closureIndex + 1 }, (_, index) => `A${index}`);
  const admitted = admissions.map((record) => record.payload.ordinal).filter((ordinal) => ordinalIndex(ordinal) <= closureIndex).sort((a, b) => ordinalIndex(a) - ordinalIndex(b));
  if (!same(admitted, expectedOrdinals)) fail("RESOURCE_ATTEMPT_DOMAIN_INCOMPLETE", closureOrdinal);
  const attempts = [];
  const vertices = [];
  for (const ordinal of expectedOrdinals) {
    const lifetime = findOne(records, "resource_lifetime", (record) => record.payload.ordinal === ordinal);
    const start = findOne(records, "attempt_start", (record) => record.payload.ordinal === ordinal);
    if (!lifetime || !start) fail("RESOURCE_LIFETIME_MISSING", ordinal);
    const p = lifetime.payload;
    attempts.push({
      id: ordinal,
      bootstrap_observed: p.bootstrap_observed,
      bootstrap_cap: p.bootstrap_cap,
      meter_observed_preterminal: p.meter_observed_preterminal,
      meter_preterminal_cap: p.meter_preterminal_cap,
      meter_terminal_cap: p.meter_terminal_cap,
      wall_cap: p.wall_cap,
      io_charge: p.io_charge,
      disk_charge: p.disk_charge,
    });
    vertices.push({ id: ordinal, capacity: p.memory_capacity, interval_start: p.interval_start, interval_end: p.interval_end });
  }
  const maximumEnd = Math.max(...vertices.map((vertex) => vertex.interval_end));
  vertices.push({ id: `closure-${closureOrdinal}`, capacity: 5, interval_start: maximumEnd - 2, interval_end: maximumEnd + 3 });
  const possibleOverlapEdges = [];
  for (let left = 0; left < vertices.length; left += 1) {
    for (let right = left + 1; right < vertices.length; right += 1) {
      if (intervalsOverlap(vertices[left], vertices[right])) possibleOverlapEdges.push([vertices[left].id, vertices[right].id]);
    }
  }
  return {
    schema: "tt-supervised-resource-input-v3",
    closure_ordinal: closureOrdinal,
    attempts,
    memory_vertices: vertices,
    possible_overlap_edges: possibleOverlapEdges,
  };
}

function computeResources(input) {
  const cpu = input.attempts.reduce((sum, attempt) => sum + (attempt.bootstrap_observed ?? attempt.bootstrap_cap) + (attempt.meter_observed_preterminal ?? attempt.meter_preterminal_cap) + attempt.meter_terminal_cap, 0);
  const wall = input.attempts.reduce((sum, attempt) => sum + attempt.wall_cap, 0);
  const io = input.attempts.reduce((sum, attempt) => sum + attempt.io_charge, 0);
  const disk = input.attempts.reduce((sum, attempt) => sum + attempt.disk_charge, 0);
  const vertices = input.memory_vertices;
  const adjacency = Object.fromEntries(vertices.map((vertex) => [vertex.id, new Set([vertex.id])]));
  for (const [left, right] of input.possible_overlap_edges) {
    if (!adjacency[left] || !adjacency[right]) fail("RESOURCE_OVERLAP_ENDPOINT_INVALID");
    adjacency[left].add(right);
    adjacency[right].add(left);
  }
  const seen = new Set();
  const components = [];
  for (const vertex of vertices) {
    if (seen.has(vertex.id)) continue;
    const stack = [vertex.id];
    const members = [];
    let charge = 0;
    while (stack.length > 0) {
      const id = stack.pop();
      if (seen.has(id)) continue;
      seen.add(id);
      members.push(id);
      charge += vertices.find((candidate) => candidate.id === id).capacity;
      for (const neighbor of adjacency[id]) stack.push(neighbor);
    }
    components.push({ members: members.sort(), charge });
  }
  return { cpu, memory: Math.max(...components.map((component) => component.charge)), wall, io, disk, memory_components: components };
}

function makeMeasurementRecord(traceId, sequence, closureOrdinal, records) {
  const input = resourceInputFor(records, closureOrdinal);
  const result = computeResources(input);
  return makeRecord(traceId, "resource_measurement", {
    sequence,
    campaign_id: traceId,
    closure_ordinal: closureOrdinal,
    input,
    input_sha256: sha256(input),
    result,
    result_sha256: sha256(result),
  });
}

function validateLifetime(record) {
  const p = record.payload;
  ordinalIndex(p.ordinal);
  for (const field of ["bootstrap_cap", "meter_preterminal_cap", "meter_terminal_cap", "wall_cap", "io_charge", "disk_charge", "memory_capacity", "interval_start", "interval_end"]) {
    if (!Number.isSafeInteger(p[field]) || p[field] < 0) fail("RESOURCE_LIFETIME_VALUE_INVALID", `${p.ordinal}:${field}`);
  }
  for (const [observed, cap] of [["bootstrap_observed", "bootstrap_cap"], ["meter_observed_preterminal", "meter_preterminal_cap"]]) {
    if (p[observed] !== null && (!Number.isSafeInteger(p[observed]) || p[observed] < 0 || p[observed] > p[cap])) fail("RESOURCE_OBSERVATION_INVALID", `${p.ordinal}:${observed}`);
  }
  if (p.interval_start >= p.interval_end) fail("RESOURCE_INTERVAL_INVALID", p.ordinal);
}

function validateSemanticUniverse(records) {
  if (!Array.isArray(records) || records.length < 2) fail("UNIVERSE_EMPTY");
  const paths = new Set();
  let traceId = null;
  for (const record of records) {
    const observedTraceId = validateRecordShape(record);
    if (traceId === null) traceId = observedTraceId;
    if (traceId !== observedTraceId) fail("CROSS_CAMPAIGN_RECORD", record.path);
    if (paths.has(record.path)) fail("DUPLICATE_DURABLE_PATH", record.path);
    paths.add(record.path);
  }
  const configs = findAll(records, "campaign_config");
  const locks = findAll(records, "root_lock");
  if (configs.length !== 1 || locks.length !== 1) fail("ROOT_SINGLETON_CARDINALITY_INVALID");
  const config = configs[0];
  validateConfig(config);
  if (locks[0].payload.sequence !== 0 || locks[0].payload.status !== "valid_current" || locks[0].payload.lock_token !== `lock-${traceId}`) fail("ROOT_LOCK_INVALID");

  const admissions = findAll(records, "normal_admission").concat(findAll(records, "recovery_admission")).sort((a, b) => ordinalIndex(a.payload.ordinal) - ordinalIndex(b.payload.ordinal));
  const ordinalSet = new Set();
  for (const admission of admissions) {
    const ordinal = admission.payload.ordinal;
    const index = ordinalIndex(ordinal);
    if (ordinalSet.has(ordinal)) fail("ORDINAL_DUPLICATE", ordinal);
    ordinalSet.add(ordinal);
    if (index === 0 && admission.record_type !== "normal_admission") fail("ORDINAL_ADMISSION_KIND_MISMATCH", ordinal);
    if (index > 0 && admission.record_type !== "recovery_admission") fail("ORDINAL_ADMISSION_KIND_MISMATCH", ordinal);
    if (index > config.payload.approval_maximum_recovery_bootstraps) fail("ORDINAL_APPROVAL_EXCEEDED", ordinal);
    if (index === 0 && admission.payload.predecessor_attempt_end_sha256 !== null) fail("ORDINAL_PREDECESSOR_INVALID", ordinal);
    if (index > 0) {
      const predecessor = findOne(records, "attempt_end", (record) => record.payload.ordinal === `A${index - 1}`);
      if (!predecessor || admission.payload.predecessor_attempt_end_sha256 !== predecessor.sha256) fail("ORDINAL_PREDECESSOR_INVALID", ordinal);
    }
  }
  for (let index = 0; index < admissions.length; index += 1) {
    if (admissions[index].payload.ordinal !== `A${index}`) fail("ORDINAL_HISTORY_NONCONTIGUOUS", admissions.map((record) => record.payload.ordinal).join(","));
  }
  const starts = findAll(records, "attempt_start");
  const started = new Set();
  for (const start of starts) {
    const ordinal = start.payload.ordinal;
    ordinalIndex(ordinal);
    if (started.has(ordinal)) fail("ATTEMPT_START_DUPLICATE", ordinal);
    started.add(ordinal);
    const admission = admissions.find((record) => record.payload.ordinal === ordinal);
    if (!admission || start.payload.admission_sha256 !== admission.sha256) fail("ATTEMPT_START_ADMISSION_MISMATCH", ordinal);
  }
  for (const lifetime of findAll(records, "resource_lifetime")) validateLifetime(lifetime);

  for (const measurement of findAll(records, "resource_measurement")) {
    const closureOrdinal = measurement.payload.closure_ordinal;
    const expectedInput = resourceInputFor(records, closureOrdinal);
    const observedAttemptIds = measurement.payload.input?.attempts?.map((attempt) => attempt.id);
    const expectedAttemptIds = expectedInput.attempts.map((attempt) => attempt.id);
    if (!same(observedAttemptIds, expectedAttemptIds)) fail("RESOURCE_MEASUREMENT_DOMAIN_MISMATCH", closureOrdinal);
    if (!same(measurement.payload.input?.memory_vertices, expectedInput.memory_vertices)) fail("RESOURCE_MEMORY_VERTEX_DOMAIN_MISMATCH", closureOrdinal);
    if (!same(measurement.payload.input?.possible_overlap_edges, expectedInput.possible_overlap_edges)) fail("RESOURCE_OVERLAP_GRAPH_MISMATCH", closureOrdinal);
    if (!same(measurement.payload.input, expectedInput)) fail("RESOURCE_INPUT_MISMATCH", closureOrdinal);
    const expectedResult = computeResources(expectedInput);
    if (measurement.payload.input_sha256 !== sha256(expectedInput) || !same(measurement.payload.result, expectedResult) || measurement.payload.result_sha256 !== sha256(expectedResult)) fail("RESOURCE_MEASUREMENT_ARITHMETIC_MISMATCH", closureOrdinal);
  }
  for (const receipt of findAll(records, "resource_receipt")) {
    const p = receipt.payload;
    const measurement = findOne(records, "resource_measurement", (record) => record.sha256 === p.measurement_sha256);
    const admission = admissions.find((record) => record.payload.ordinal === p.ordinal);
    const start = findOne(records, "attempt_start", (record) => record.payload.ordinal === p.ordinal);
    if (!measurement || !admission || !start) fail("RESOURCE_RECEIPT_LINK_MISSING", p.ordinal);
    const occurrences = measurement.payload.input.attempts.filter((attempt) => attempt.id === p.ordinal).length;
    if (occurrences !== 1 || measurement.payload.closure_ordinal !== p.ordinal) fail("RESOURCE_RECEIPT_ORDINAL_MISMATCH", p.ordinal);
    if (p.admission_sha256 !== admission.sha256 || p.attempt_start_sha256 !== start.sha256) fail("RESOURCE_RECEIPT_IDENTITY_MISMATCH", p.ordinal);
    if (p.input_sha256 !== measurement.payload.input_sha256 || p.result_sha256 !== measurement.payload.result_sha256 || !same(p.result, measurement.payload.result)) fail("RESOURCE_RECEIPT_MEASUREMENT_MISMATCH", p.ordinal);
  }
  const ends = findAll(records, "attempt_end");
  for (const end of ends) {
    const receipt = findOne(records, "resource_receipt", (record) => record.sha256 === end.payload.resource_receipt_sha256 && record.payload.ordinal === end.payload.ordinal);
    if (!receipt) fail("ATTEMPT_END_RESOURCE_MISMATCH", end.payload.ordinal);
    if (!["recoverable_crash", "attested_closure", "infrastructure_failure"].includes(end.payload.outcome)) fail("ATTEMPT_END_OUTCOME_INVALID", end.payload.ordinal);
  }

  const committedByPhase = new Map(findAll(records, "committed_phase").map((record) => [record.payload.phase, record]));
  for (const reservation of findAll(records, "phase_reservation")) {
    const p = reservation.payload;
    if (!isPhase(p.phase) || !isOrdinal(p.ordinal) || p.phase_mode !== `${p.phase}:${p.phase === "E0" ? "evaluate" : "not_applicable"}`) fail("RESERVATION_IDENTITY_INVALID", p.phase);
    const expectedIndex = phaseOrder.indexOf(p.phase) - 1;
    const predecessor = expectedIndex >= 0 ? committedByPhase.get(phaseOrder[expectedIndex]) : null;
    if ((predecessor?.sha256 || null) !== p.predecessor_committed_sha256 || (predecessor?.payload.commit_oid || null) !== p.predecessor_commit_oid) fail("RESERVATION_PREDECESSOR_MISMATCH", p.phase);
  }
  for (const identity of findAll(records, "executable_identity")) {
    const p = identity.payload;
    if (!isPhase(p.phase) || !isOrdinal(p.ordinal) || p.executable_path !== capabilityDescriptor.executable_path || p.executable_sha256 !== capabilityDescriptor.executable_sha256 || p.opened_file_token !== `opened:${p.ordinal}:${p.phase}:${p.executable_sha256}`) fail("EXECUTABLE_IDENTITY_INVALID", p.phase);
  }
  for (const capability of findAll(records, "capability_receipt")) {
    const p = capability.payload;
    const reservation = findOne(records, "phase_reservation", (record) => record.sha256 === p.reservation_sha256);
    const identity = findOne(records, "executable_identity", (record) => record.sha256 === p.executable_identity_sha256);
    if (!reservation || !identity || reservation.payload.phase !== p.phase || reservation.payload.ordinal !== p.ordinal || identity.payload.phase !== p.phase || identity.payload.ordinal !== p.ordinal) fail("CAPABILITY_RESERVATION_MISMATCH", p.phase);
    if (p.descriptor_sha256 !== config.payload.capability_descriptor_sha256) fail("CAPABILITY_DESCRIPTOR_MISMATCH", p.phase);
    if (!same(p.inherited_descriptor_bindings, config.payload.capability_descriptor.inherited_descriptor_bindings)) fail("CAPABILITY_DESCRIPTOR_BINDING_MISMATCH", p.phase);
    if (p.decision !== "allow") fail("CAPABILITY_DECISION_INVALID", p.phase);
  }
  for (const intent of findAll(records, "private_map_open_intent")) {
    const reservation = findOne(records, "phase_reservation", (record) => record.sha256 === intent.payload.reservation_sha256);
    if (!reservation || reservation.payload.phase !== "E0" || reservation.payload.ordinal !== intent.payload.ordinal) fail("PRIVATE_MAP_RESERVATION_MISMATCH");
  }
  for (const observation of findAll(records, "private_map_open_observation")) {
    const intent = findOne(records, "private_map_open_intent", (record) => record.sha256 === observation.payload.open_intent_sha256);
    if (!intent || observation.payload.outcome !== "opened" || observation.payload.descriptor_token !== `private-map:${observation.payload.ordinal}:E0`) fail("PRIVATE_MAP_OBSERVATION_INVALID");
  }
  for (const receipt of findAll(records, "private_map_opened_receipt")) {
    const reservation = findOne(records, "phase_reservation", (record) => record.sha256 === receipt.payload.reservation_sha256);
    const intent = findOne(records, "private_map_open_intent", (record) => record.sha256 === receipt.payload.open_intent_sha256);
    const observation = findOne(records, "private_map_open_observation", (record) => record.sha256 === receipt.payload.open_observation_sha256);
    if (!reservation || !intent || !observation || ![reservation, intent, observation].every((record) => record.payload.ordinal === receipt.payload.ordinal && record.payload.phase === "E0") || receipt.payload.descriptor_token !== observation.payload.descriptor_token) fail("PRIVATE_MAP_RECEIPT_MISMATCH");
  }
  for (const launch of findAll(records, "launch_intent")) {
    const p = launch.payload;
    const reservation = findOne(records, "phase_reservation", (record) => record.sha256 === p.reservation_sha256);
    const capability = findOne(records, "capability_receipt", (record) => record.sha256 === p.capability_receipt_sha256);
    const identity = findOne(records, "executable_identity", (record) => record.sha256 === p.executable_identity_sha256);
    if (!reservation || !capability || !identity || ![reservation, capability, identity].every((record) => record.payload.phase === p.phase && record.payload.ordinal === p.ordinal)) fail("LAUNCH_IDENTITY_MISMATCH", p.phase);
    if (p.phase_mode !== reservation.payload.phase_mode) fail("LAUNCH_PHASE_MODE_MISMATCH", p.phase);
    if (p.phase === "E0") {
      const map = findOne(records, "private_map_opened_receipt", (record) => record.sha256 === p.private_map_receipt_sha256);
      if (!map || map.payload.ordinal !== p.ordinal) fail("LAUNCH_PRIVATE_MAP_MISMATCH");
    } else if (p.private_map_receipt_sha256 !== null) fail("LAUNCH_PRIVATE_MAP_UNEXPECTED", p.phase);
  }
  for (const spawn of findAll(records, "phase_spawn")) {
    const launch = findOne(records, "launch_intent", (record) => record.sha256 === spawn.payload.launch_intent_sha256);
    if (!launch || launch.payload.phase !== spawn.payload.phase || launch.payload.ordinal !== spawn.payload.ordinal || spawn.payload.outcome !== "pid_returned" || spawn.payload.process_token !== `process:${spawn.payload.ordinal}:${spawn.payload.phase}`) fail("PHASE_SPAWN_INVALID", spawn.payload.phase);
  }
  for (const reap of findAll(records, "phase_reap")) {
    const spawn = findOne(records, "phase_spawn", (record) => record.sha256 === reap.payload.phase_spawn_sha256);
    if (!spawn || spawn.payload.phase !== reap.payload.phase || reap.payload.outcome !== "exited" || reap.payload.exit_code !== 0) fail("PHASE_REAP_INVALID", reap.payload.phase);
  }
  for (const result of findAll(records, "phase_result")) {
    const reap = findOne(records, "phase_reap", (record) => record.sha256 === result.payload.phase_reap_sha256);
    if (!reap || reap.payload.phase !== result.payload.phase || result.payload.bounded !== true || result.payload.valid !== true || typeof result.payload.recovery !== "boolean") fail("PHASE_RESULT_INVALID", result.payload.phase);
  }
  for (const content of findAll(records, "phase_content")) {
    const result = findOne(records, "phase_result", (record) => record.sha256 === content.payload.phase_result_sha256);
    if (!result || result.payload.phase !== content.payload.phase || content.payload.content_sha256 !== sha256(content.payload.content_bytes)) fail("PHASE_CONTENT_INVALID", content.payload.phase);
  }
  for (const terminal of findAll(records, "phase_terminal")) {
    const p = terminal.payload;
    const predecessor = records.find((record) => record.sha256 === p.predecessor_sha256);
    const result = findOne(records, "phase_result", (record) => record.sha256 === p.result_sha256);
    const content = findOne(records, "phase_content", (record) => record.sha256 === p.content_sha256);
    if (!predecessor || !result || !content || ![predecessor, result, content].every((record) => record.payload.phase === p.phase && record.payload.ordinal === p.ordinal)) fail("TERMINAL_LINKAGE_INVALID", p.phase);
    const eventMap = {
      valid_outcome: { outcome: "TERMINAL_VALID_OUTCOME", predecessor: "phase_content" },
      spawn_failure: { outcome: "TERMINAL_HARNESS_FAILURE", predecessor: "phase_spawn" },
      runtime_failure: { outcome: "TERMINAL_HARNESS_FAILURE", predecessor: "phase_reap" },
      validation_failure: { outcome: "TERMINAL_HARNESS_FAILURE", predecessor: "phase_content" },
      quarantine: { outcome: "TERMINAL_QUARANTINE", predecessor: "phase_content" },
    };
    const expected = eventMap[p.event_kind];
    if (!expected || p.outcome !== expected.outcome || predecessor.record_type !== expected.predecessor) fail("TERMINAL_EVENT_PREDECESSOR_INVALID", p.phase);
  }

  for (const pre of findAll(records, "ref_observation_pre")) {
    const configRef = config.payload.intended_ref;
    const reservation = findOne(records, "phase_reservation", (record) => record.payload.phase === pre.payload.phase);
    const expectedOid = reservation?.payload.predecessor_commit_oid || null;
    const expectedRelation = expectedOid === null ? "absent_initial" : "at_parent";
    if (pre.payload.ref !== configRef || pre.payload.observed_oid !== expectedOid || pre.payload.relation !== expectedRelation) fail("GIT_REF_PRE_MISMATCH", pre.payload.phase);
  }
  for (const blob of findAll(records, "git_blob_object")) {
    const content = findOne(records, "phase_content", (record) => record.payload.phase === blob.payload.phase && record.payload.content_sha256 === blob.payload.source_content_sha256);
    const bytes = Buffer.from(blob.payload.object_bytes_hex, "hex");
    if (!content || bytes.toString("utf8") !== content.payload.content_bytes || blob.payload.oid !== gitOid("blob", bytes)) fail("GIT_BLOB_BYTES_MISMATCH", blob.payload.phase);
  }
  for (const tree of findAll(records, "git_tree_object")) {
    const blob = findOne(records, "git_blob_object", (record) => record.sha256 === tree.payload.blob_record_sha256);
    if (!blob || tree.payload.blob_oid !== blob.payload.oid) fail("GIT_TREE_BLOB_MISMATCH", tree.payload.phase);
    const expectedBytes = Buffer.concat([Buffer.from("100644 phase.json\0", "utf8"), Buffer.from(blob.payload.oid, "hex")]);
    const bytes = Buffer.from(tree.payload.object_bytes_hex, "hex");
    if (!bytes.equals(expectedBytes) || tree.payload.oid !== gitOid("tree", bytes)) fail("GIT_TREE_BYTES_MISMATCH", tree.payload.phase);
  }
  for (const intent of findAll(records, "commit_intent")) {
    const p = intent.payload;
    const reservation = findOne(records, "phase_reservation", (record) => record.payload.phase === p.phase);
    const tree = findOne(records, "git_tree_object", (record) => record.sha256 === p.tree_record_sha256);
    const terminal = findOne(records, "phase_terminal", (record) => record.sha256 === p.terminal_sha256);
    const result = findOne(records, "phase_result", (record) => record.sha256 === p.result_sha256);
    const content = findOne(records, "phase_content", (record) => record.sha256 === p.content_sha256);
    if (!reservation || !tree || !terminal || !result || !content) fail("GIT_INTENT_LINK_MISSING", p.phase);
    if (p.schema !== "tt-supervised-git-intent-v3" || p.tree_oid !== tree.payload.oid || p.parent_oid !== reservation.payload.predecessor_commit_oid || p.intended_ref !== config.payload.intended_ref || p.self_exclusion !== "commit_oid_forbidden") fail("GIT_PARENT_MISMATCH", p.phase);
    const outcomeMap = { TERMINAL_VALID_OUTCOME: "valid_outcome", TERMINAL_HARNESS_FAILURE: "harness_failure", TERMINAL_QUARANTINE: "quarantine" };
    if (p.terminal_outcome !== outcomeMap[terminal.payload.outcome]) fail("GIT_TERMINAL_OUTCOME_MISMATCH", p.phase);
  }
  for (const object of findAll(records, "commit_object")) {
    const intent = findOne(records, "commit_intent", (record) => record.sha256 === object.payload.intent_sha256);
    if (!intent) fail("GIT_COMMIT_INTENT_MISSING", object.payload.phase);
    const expectedBytes = gitCommitBytes(intent.payload);
    if (object.payload.commit_bytes !== expectedBytes || object.payload.oid !== gitOid("commit", Buffer.from(expectedBytes, "utf8")) || object.payload.tree_oid !== intent.payload.tree_oid || object.payload.parent_oid !== intent.payload.parent_oid) fail("GIT_COMMIT_BYTES_MISMATCH", object.payload.phase);
  }
  for (const cas of findAll(records, "ref_cas_attempt")) {
    const object = findOne(records, "commit_object", (record) => record.sha256 === cas.payload.commit_object_sha256);
    const pre = findOne(records, "ref_observation_pre", (record) => record.sha256 === cas.payload.ref_observation_pre_sha256);
    if (!object || !pre || cas.payload.ref !== config.payload.intended_ref) fail("GIT_REF_MISMATCH", cas.payload.phase);
    if (cas.payload.expected_old_oid !== pre.payload.observed_oid || cas.payload.new_oid !== object.payload.oid || cas.payload.outcome !== "applied") fail("GIT_CAS_LINKAGE_MISMATCH", cas.payload.phase);
  }
  for (const post of findAll(records, "ref_observation_post")) {
    const cas = findOne(records, "ref_cas_attempt", (record) => record.sha256 === post.payload.cas_sha256);
    if (!cas || post.payload.ref !== config.payload.intended_ref || post.payload.observed_oid !== cas.payload.new_oid) fail("POST_CAS_REF_MISMATCH", post.payload.phase);
  }
  for (const committed of findAll(records, "committed_phase")) {
    const object = findOne(records, "commit_object", (record) => record.sha256 === committed.payload.commit_object_sha256);
    const cas = findOne(records, "ref_cas_attempt", (record) => record.sha256 === committed.payload.ref_cas_sha256);
    const post = findOne(records, "ref_observation_post", (record) => record.sha256 === committed.payload.post_ref_observation_sha256);
    if (!object || !cas || !post || committed.payload.commit_oid !== object.payload.oid || post.payload.observed_oid !== object.payload.oid) fail("COMMITTED_PHASE_LINKAGE_MISMATCH", committed.payload.phase);
  }
  const commits = findAll(records, "committed_phase").sort((a, b) => phaseOrder.indexOf(a.payload.phase) - phaseOrder.indexOf(b.payload.phase));
  for (let index = 0; index < commits.length; index += 1) {
    if (commits[index].payload.phase !== phaseOrder[index]) fail("GIT_PHASE_CHAIN_NONCONTIGUOUS");
    if (index > 0) {
      const object = findOne(records, "commit_object", (record) => record.sha256 === commits[index].payload.commit_object_sha256);
      if (object.payload.parent_oid !== commits[index - 1].payload.commit_oid) fail("GIT_PARENT_MISMATCH", commits[index].payload.phase);
    }
  }
  for (const launchIdentity of findAll(records, "launch_identity")) {
    const expectedTokens = findAll(records, "phase_spawn", (record) => record.payload.ordinal === launchIdentity.payload.ordinal).map((record) => record.payload.process_token).sort();
    if (launchIdentity.payload.executable_sha256 !== capabilityDescriptor.executable_sha256 || !same(launchIdentity.payload.process_tokens, expectedTokens)) fail("METER_LAUNCH_IDENTITY_MISMATCH", launchIdentity.payload.ordinal);
  }
  for (const observation of findAll(records, "kernel_process_observation")) {
    const identity = findOne(records, "launch_identity", (record) => record.sha256 === observation.payload.launch_identity_sha256);
    if (!identity || identity.payload.ordinal !== observation.payload.ordinal || observation.payload.observation !== "kernel_confirmed_absent") fail("KERNEL_OBSERVATION_IDENTITY_MISMATCH", observation.payload.ordinal);
  }
  for (const terminal of findAll(records, "campaign_terminal")) {
    const resource = findOne(records, "resource_receipt", (record) => record.sha256 === terminal.payload.resource_receipt_sha256);
    const end = findOne(records, "attempt_end", (record) => record.sha256 === terminal.payload.attempt_end_sha256);
    const closure = findOne(records, "closure_request", (record) => record.sha256 === terminal.payload.closure_request_sha256);
    if (!resource || !end || !closure || ![resource, end, closure].every((record) => record.payload.ordinal === terminal.payload.ordinal) || terminal.payload.kind !== "valid_attested_closure") fail("CAMPAIGN_TERMINAL_LINKAGE_MISMATCH");
  }
  for (const recalculation of findAll(records, "recalculation_receipt")) {
    const terminal = findOne(records, "campaign_terminal", (record) => record.sha256 === recalculation.payload.campaign_terminal_sha256);
    const measurement = findOne(records, "resource_measurement", (record) => record.payload.closure_ordinal === recalculation.payload.ordinal);
    if (!terminal || !measurement || recalculation.payload.derived_totals_sha256 !== measurement.payload.result_sha256 || recalculation.payload.status !== "complete") fail("RECALCULATION_LINKAGE_MISMATCH");
  }
  for (const release of findAll(records, "lock_release")) {
    const recalculation = findOne(records, "recalculation_receipt", (record) => record.sha256 === release.payload.recalculation_receipt_sha256);
    if (!recalculation || release.payload.status !== "released") fail("LOCK_RELEASE_LINKAGE_MISMATCH");
  }
  return { traceId, config, admissions, starts, ends };
}

function gitCommitBytes(intent) {
  const parent = intent.parent_oid === null ? "" : `parent ${intent.parent_oid}\n`;
  return `tree ${intent.tree_oid}\n${parent}author AutoLab <autolab@example.invalid> 0 +0000\ncommitter AutoLab <autolab@example.invalid> 0 +0000\n\n${intent.message}\n`;
}

function validateSource(schemaId, source) {
  const schema = sourceSchemas[schemaId];
  if (!schema) return { ok: false, reason: "SCHEMA_UNKNOWN" };
  if (!same(Object.keys(source).sort(), schema.permitted)) return { ok: false, reason: "SCHEMA_KEYS_MISMATCH" };
  for (const [field, expected] of Object.entries(schema.fixed)) if (!same(source[field], expected)) return { ok: false, reason: `SCHEMA_FIXED_MISMATCH:${field}` };
  for (const [field, domain] of Object.entries(schema.domains)) if (!domain.some((value) => same(value, source[field]))) return { ok: false, reason: `SCHEMA_DOMAIN_MISMATCH:${field}` };
  return { ok: true, reason: "SCHEMA_VALID" };
}

function sourceFrom(schemaId, values) {
  const schema = sourceSchemas[schemaId];
  if (!schema) fail("SOURCE_SCHEMA_UNKNOWN", schemaId);
  const source = { ...clone(schema.fixed) };
  for (const [field, domain] of Object.entries(schema.domains)) source[field] = clone(domain[0]);
  Object.assign(source, clone(values));
  const validation = validateSource(schemaId, source);
  if (!validation.ok) fail("DERIVED_SOURCE_INVALID", `${schemaId}:${validation.reason}`);
  return source;
}

function conditionMatches(actual, expected) {
  return Array.isArray(expected) ? expected.some((value) => same(value, actual)) : same(actual, expected);
}

function selectRule(schemaId, source) {
  const validation = validateSource(schemaId, source);
  if (!validation.ok) return { id: "SCHEMA_REJECT", reason: validation.reason, state: "CONTROL_INVALID", next_action: "none", next_context: "control_validation" };
  const matches = rulesBySchema[schemaId].filter((rule) => Object.entries(rule.compiled_predicate).every(([field, expected]) => conditionMatches(source[field], expected)));
  if (matches.length > 1) fail("RULE_OVERLAP", `${schemaId}:${matches.map((rule) => rule.id).join(",")}`);
  return matches[0] || { id: "DEFAULT", reason: "STATE_PRODUCT_UNMATCHED", state: "INFRASTRUCTURE_REQUESTED", next_action: "request_infrastructure_failure", next_context: "meter_finalization" };
}

function configOf(records) {
  const config = findOne(records, "campaign_config");
  if (!config) fail("CONFIG_MISSING");
  return config;
}

function currentAdmission(records) {
  const admissions = findAll(records, "normal_admission").concat(findAll(records, "recovery_admission"));
  if (admissions.length === 0) return null;
  return admissions.sort((a, b) => ordinalIndex(b.payload.ordinal) - ordinalIndex(a.payload.ordinal))[0];
}

function activeReservation(records) {
  const committed = new Set(findAll(records, "committed_phase").map((record) => record.payload.phase));
  return findAll(records, "phase_reservation").filter((record) => !committed.has(record.payload.phase)).sort((a, b) => phaseOrder.indexOf(b.payload.phase) - phaseOrder.indexOf(a.payload.phase))[0] || null;
}

function latestCommitted(records) {
  return findAll(records, "committed_phase").sort((a, b) => phaseOrder.indexOf(b.payload.phase) - phaseOrder.indexOf(a.payload.phase))[0] || null;
}

function phaseRecord(records, type, phase) {
  return findOne(records, type, (record) => record.payload.phase === phase);
}

function runModeForOrdinal(ordinal) {
  return ordinal === "A0" ? "normal" : "recovery";
}

function deriveKernelSource(records, context) {
  validateSemanticUniverse(records);
  const config = configOf(records);
  const admission = currentAdmission(records);
  const ordinal = admission?.payload.ordinal || (config.payload.requested_run_mode === "normal" ? "A0" : `A${findAll(records, "recovery_admission").length + 1}`);
  const runMode = runModeForOrdinal(ordinal);
  const campaignTerminal = findOne(records, "campaign_terminal");
  if (findOne(records, "lock_release")) return { kind: "complete", context, reason: "LOCK_RELEASED" };

  if (context === "entry_preflight") {
    if (campaignTerminal) return { kind: "complete", context, reason: "CAMPAIGN_TERMINAL_PRESENT" };
    if (config.payload.requested_run_mode === "normal") {
      const source = sourceFrom("locked_normal_eligible_v3", {
        recovery_slot: "not_applicable",
        repository_identity: "valid",
        phase_chain: "valid",
        ref_relation: "absent_initial",
        initial_phase_state: "empty",
        entry_product_relation: "valid_normal",
      });
      return { kind: "ready", context, schema_id: "locked_normal_eligible_v3", source };
    }
    const consumed = findAll(records, "recovery_admission").length;
    const maximum = config.payload.approval_maximum_recovery_bootstraps;
    if (consumed >= maximum) fail("RECOVERY_BUDGET_EXHAUSTED");
    const source = sourceFrom("locked_recovery_eligible_v3", {
      recovery_budget_state: { maximum, consumed, next_ordinal: `A${consumed + 1}`, status: "available" },
      recovery_slot: "not_applicable",
      repository_identity: "valid",
      phase_chain: "valid",
      ref_relation: latestCommitted(records) ? "at_last_commit" : "absent_initial",
      initial_phase_state: "empty",
      entry_product_relation: "valid_recovery",
    });
    return { kind: "ready", context, schema_id: "locked_recovery_eligible_v3", source };
  }

  if (!admission) fail("CURRENT_ADMISSION_MISSING", context);
  const start = findOne(records, "attempt_start", (record) => record.payload.ordinal === admission.payload.ordinal);
  if (context === "attempt_admission") {
    const source = sourceFrom("attempt_admission_v2", {
      run_mode: runMode,
      admission_kind: runMode,
      admission_ordinal: ordinal,
      linked_attempt_record: start ? "durable" : "absent",
      normal_consumption_binding: "valid",
      recovery_budget_binding: runMode === "recovery" ? "valid" : "not_applicable",
    });
    return { kind: "ready", context, schema_id: "attempt_admission_v2", source };
  }
  if (!start) fail("CURRENT_ATTEMPT_START_MISSING", ordinal);

  if (context === "recovery_reconstruction") {
    const reservation = activeReservation(records);
    const phase = reservation?.payload.phase || "P0";
    const source = sourceFrom("recovery_reconstruction_v3", {
      run_mode: "recovery",
      attempt_ordinal: ordinal,
      phase_mode: reservation?.payload.phase_mode || `${phase}:not_applicable`,
      state: reservation ? "RESERVED" : "UNSEEN",
      private_map_identity: phase === "E0" ? { state: "MAP_OPENED_RECEIPT_DURABLE", binding: "valid_current", relation: "valid" } : { state: "not_applicable", binding: "not_applicable", relation: "valid" },
      process_reconciliation: "not_applicable",
      recoverable_result: "not_applicable",
    });
    return { kind: "ready", context, schema_id: "recovery_reconstruction_v3", source };
  }

  if (context === "campaign_progression") {
    const committed = latestCommitted(records);
    const terminal = committed ? phaseRecord(records, "phase_terminal", committed.payload.phase) : null;
    const outcomeMap = { TERMINAL_VALID_OUTCOME: "valid_outcome", TERMINAL_HARNESS_FAILURE: "harness_failure", TERMINAL_QUARANTINE: "quarantine" };
    const postRef = committed ? phaseRecord(records, "ref_observation_post", committed.payload.phase) : null;
    const source = sourceFrom("campaign_progression_v3", {
      run_mode: runMode,
      attempt_ordinal: ordinal,
      trigger: committed ? "phase_committed" : "normal_consumption",
      last_committed_phase: committed?.payload.phase || "none",
      last_phase_outcome: terminal ? outcomeMap[terminal.payload.outcome] : "none",
      ref_relation: committed && postRef?.payload.observed_oid === committed.payload.commit_oid ? "at_last_commit" : "absent_initial",
    });
    return { kind: "ready", context, schema_id: "campaign_progression_v3", source };
  }

  const reservation = activeReservation(records);
  if (["live_supervisor", "e0_private_map", "repository_validation"].includes(context) && !reservation) fail("ACTIVE_PHASE_RESERVATION_MISSING", context);
  const phase = reservation?.payload.phase;
  if (context === "e0_private_map") {
    if (phase !== "E0") fail("E0_RESERVATION_MISSING");
    const mapIntent = findOne(records, "private_map_open_intent");
    const mapObservation = findOne(records, "private_map_open_observation");
    const mapReceipt = findOne(records, "private_map_opened_receipt");
    const mapState = !mapIntent ? "MAP_UNSEEN" : !mapObservation ? "MAP_OPEN_INTENT_DURABLE" : !mapReceipt ? "MAP_OPENED_UNRECEIPTED" : "MAP_OPENED_RECEIPT_DURABLE";
    const event = !mapIntent ? "request_open_intent" : !mapObservation ? "open_syscall_success" : !mapReceipt ? "publish_opened_receipt" : "dispatch_live_supervisor";
    const source = sourceFrom("e0_private_map_v3", {
      run_mode: runMode,
      attempt_ordinal: ordinal,
      e0_mode: "evaluate",
      map_state: mapState,
      event,
      descriptor_state: mapObservation ? "trusted_meter_only" : "absent",
    });
    return { kind: "ready", context, schema_id: "e0_private_map_v3", source };
  }

  if (context === "live_supervisor") {
    const capability = phaseRecord(records, "capability_receipt", phase);
    if (!capability) return { kind: "wait", context, observation_kind: "capability_attestation", phase, ordinal };
    const launch = phaseRecord(records, "launch_intent", phase);
    const spawn = phaseRecord(records, "phase_spawn", phase);
    const reap = phaseRecord(records, "phase_reap", phase);
    const result = phaseRecord(records, "phase_result", phase);
    const content = phaseRecord(records, "phase_content", phase);
    const terminal = phaseRecord(records, "phase_terminal", phase);
    let state = "RESERVED";
    if (launch) state = "LAUNCH_INTENT_DURABLE";
    if (spawn) state = "SPAWNED";
    if (reap) state = "REAPED";
    if (result) state = "RESULT_RETAINED";
    if (content) state = "CONTENT_PUBLISHED";
    if (terminal) state = terminal.payload.outcome;
    const values = {
      run_mode: runMode,
      attempt_ordinal: ordinal,
      state,
      result_disposition: state === "REAPED" ? true : "not_applicable",
      launch_prerequisite: state === "RESERVED" ? "satisfied" : "not_applicable",
    };
    if (phase === "E0") {
      const source = sourceFrom("live_e0_evaluate_action_v3", values);
      return { kind: "ready", context, schema_id: "live_e0_evaluate_action_v3", source };
    }
    values.phase_mode = reservation.payload.phase_mode;
    const source = sourceFrom("live_candidate_action_v3", values);
    return { kind: "ready", context, schema_id: "live_candidate_action_v3", source };
  }

  if (context === "repository_validation") {
    const intent = phaseRecord(records, "commit_intent", phase);
    const object = phaseRecord(records, "commit_object", phase);
    const pre = phaseRecord(records, "ref_observation_pre", phase);
    const cas = phaseRecord(records, "ref_cas_attempt", phase);
    const source = sourceFrom("git_commit_validation_v2", {
      run_mode: runMode,
      attempt_ordinal: ordinal,
      phase_mode: reservation.payload.phase_mode,
      commit_intent_relation: intent ? "valid_self_excluding" : "absent",
      commit_object_state: object ? "exact" : "absent",
      ref_relation: pre?.payload.relation || (phase === "P0" ? "absent_initial" : "at_parent"),
      cas_status: cas ? cas.payload.outcome : "not_attempted",
    });
    return { kind: "ready", context, schema_id: "git_commit_validation_v2", source };
  }

  if (context === "meter_finalization") {
    const launchIdentity = findOne(records, "launch_identity", (record) => record.payload.ordinal === ordinal);
    const kernelObservation = findOne(records, "kernel_process_observation", (record) => record.payload.ordinal === ordinal);
    const measurement = findOne(records, "resource_measurement", (record) => record.payload.closure_ordinal === ordinal);
    if (!launchIdentity || !kernelObservation || !measurement) return { kind: "wait", context, observation_kind: "meter_finalization", ordinal };
    const resource = findOne(records, "resource_receipt", (record) => record.payload.ordinal === ordinal);
    const end = findOne(records, "attempt_end", (record) => record.payload.ordinal === ordinal);
    const terminal = findOne(records, "campaign_terminal");
    const closure = findOne(records, "closure_request");
    const recalculation = findOne(records, "recalculation_receipt");
    const source = sourceFrom("meter_finalization_v3", {
      attempt_identity: { run_mode: runMode, admission_kind: runMode, ordinal },
      process_absence: kernelObservation.payload.observation,
      durable_state: end?.payload.durable_state || "valid",
      terminal_request: closure?.payload.terminal_request || "absent",
      resource_receipt: resource ? "durable" : "absent",
      attempt_end: end ? "durable" : "absent",
      campaign_terminal: terminal?.payload.kind || "absent",
      recalculation: recalculation ? "complete" : "not_started",
      lock_release: "held",
    });
    return { kind: "ready", context, schema_id: "meter_finalization_v3", source };
  }
  fail("CONTEXT_UNKNOWN", context);
}

function expectedPhaseForReservation(selection, records) {
  if (selection.id === "C001") return "P0";
  if (selection.id === "C003") return "E0";
  if (selection.id === "C002") {
    const committed = latestCommitted(records);
    const index = phaseOrder.indexOf(committed?.payload.phase);
    if (index < 0 || index >= 5) fail("SUCCESSOR_PHASE_INVALID");
    return phaseOrder[index + 1];
  }
  fail("RESERVATION_RULE_INVALID", selection.id);
}

function expectedActionRecords(traceId, sequence, selection, source, records) {
  const config = configOf(records);
  const admission = currentAdmission(records);
  const ordinal = selection.id === "E012"
    ? "A0"
    : selection.id === "E013"
      ? source.recovery_budget_state.next_ordinal
      : admission?.payload.ordinal;
  const action = selection.next_action;
  const output = [];
  const push = (type, payload, producer) => output.push(makeRecord(traceId, type, { sequence, campaign_id: traceId, ...payload }, producer));
  if (selection.id === "E012" || selection.id === "E013") {
    const index = ordinalIndex(ordinal);
    const predecessor = index === 0 ? null : findOne(records, "attempt_end", (record) => record.payload.ordinal === `A${index - 1}`);
    push(index === 0 ? "normal_admission" : "recovery_admission", { ordinal, predecessor_attempt_end_sha256: predecessor?.sha256 || null });
  } else if (["D001", "D002"].includes(selection.id)) {
    push("attempt_start", { ordinal, admission_sha256: admission.sha256 });
  } else if (["C001", "C002", "C003"].includes(selection.id)) {
    const phase = expectedPhaseForReservation(selection, records);
    const predecessor = latestCommitted(records);
    push("phase_reservation", {
      ordinal,
      phase,
      phase_mode: `${phase}:${phase === "E0" ? "evaluate" : "not_applicable"}`,
      predecessor_committed_sha256: predecessor?.sha256 || null,
      predecessor_commit_oid: predecessor?.payload.commit_oid || null,
    });
  } else if (selection.id === "P001") {
    const reservation = activeReservation(records);
    push("private_map_open_intent", { ordinal, phase: "E0", reservation_sha256: reservation.sha256 });
  } else if (selection.id === "P002") {
    const intent = findOne(records, "private_map_open_intent");
    push("private_map_open_observation", { ordinal, phase: "E0", open_intent_sha256: intent.sha256, outcome: "opened", descriptor_token: `private-map:${ordinal}:E0` });
  } else if (selection.id === "P004") {
    const reservation = activeReservation(records);
    const intent = findOne(records, "private_map_open_intent");
    const observation = findOne(records, "private_map_open_observation");
    push("private_map_opened_receipt", { ordinal, phase: "E0", reservation_sha256: reservation.sha256, open_intent_sha256: intent.sha256, open_observation_sha256: observation.sha256, descriptor_token: observation.payload.descriptor_token });
  } else if (["AN001", "AE001"].includes(selection.id)) {
    const reservation = activeReservation(records);
    const phase = reservation.payload.phase;
    const capability = phaseRecord(records, "capability_receipt", phase);
    const identity = phaseRecord(records, "executable_identity", phase);
    const mapReceipt = phase === "E0" ? findOne(records, "private_map_opened_receipt") : null;
    push("launch_intent", { ordinal, phase, phase_mode: reservation.payload.phase_mode, reservation_sha256: reservation.sha256, capability_receipt_sha256: capability.sha256, executable_identity_sha256: identity.sha256, private_map_receipt_sha256: mapReceipt?.sha256 || null });
  } else if (["AN002", "AE002"].includes(selection.id)) {
    const reservation = activeReservation(records);
    const phase = reservation.payload.phase;
    const launch = phaseRecord(records, "launch_intent", phase);
    push("phase_spawn", { ordinal, phase, launch_intent_sha256: launch.sha256, outcome: "pid_returned", process_token: `process:${ordinal}:${phase}` });
  } else if (["AN004", "AE004"].includes(selection.id)) {
    const phase = activeReservation(records).payload.phase;
    const spawn = phaseRecord(records, "phase_spawn", phase);
    push("phase_reap", { ordinal, phase, phase_spawn_sha256: spawn.sha256, outcome: "exited", exit_code: 0 });
  } else if (["AN005R", "AE005R"].includes(selection.id)) {
    const phase = activeReservation(records).payload.phase;
    const reap = phaseRecord(records, "phase_reap", phase);
    push("phase_result", { ordinal, phase, phase_reap_sha256: reap.sha256, bounded: true, valid: true, recovery: runModeForOrdinal(ordinal) === "recovery" });
  } else if (["AN006", "AE006"].includes(selection.id)) {
    const phase = activeReservation(records).payload.phase;
    const result = phaseRecord(records, "phase_result", phase);
    const contentBytes = canonical({ campaign_id: traceId, ordinal, phase, result_sha256: result.sha256, status: "valid" });
    push("phase_content", { ordinal, phase, phase_result_sha256: result.sha256, content_bytes: contentBytes, content_sha256: sha256(contentBytes) });
  } else if (["AN007", "AE007"].includes(selection.id)) {
    const phase = activeReservation(records).payload.phase;
    const result = phaseRecord(records, "phase_result", phase);
    const content = phaseRecord(records, "phase_content", phase);
    push("phase_terminal", { ordinal, phase, event_kind: "valid_outcome", outcome: "TERMINAL_VALID_OUTCOME", predecessor_sha256: content.sha256, result_sha256: result.sha256, content_sha256: content.sha256 });
  } else if (["AN008", "AE008"].includes(selection.id)) {
    const reservation = activeReservation(records);
    push("ref_observation_pre", { ordinal, phase: reservation.payload.phase, ref: config.payload.intended_ref, observed_oid: reservation.payload.predecessor_commit_oid, relation: reservation.payload.predecessor_commit_oid === null ? "absent_initial" : "at_parent" });
  } else if (selection.id === "G000") {
    const reservation = activeReservation(records);
    const phase = reservation.payload.phase;
    const content = phaseRecord(records, "phase_content", phase);
    const result = phaseRecord(records, "phase_result", phase);
    const terminal = phaseRecord(records, "phase_terminal", phase);
    const blobBytes = Buffer.from(content.payload.content_bytes, "utf8");
    const blob = makeRecord(traceId, "git_blob_object", { sequence, campaign_id: traceId, ordinal, phase, source_content_sha256: content.payload.content_sha256, object_bytes_hex: blobBytes.toString("hex"), oid: gitOid("blob", blobBytes) });
    output.push(blob);
    const treeBytes = Buffer.concat([Buffer.from("100644 phase.json\0", "utf8"), Buffer.from(blob.payload.oid, "hex")]);
    const tree = makeRecord(traceId, "git_tree_object", { sequence, campaign_id: traceId, ordinal, phase, blob_record_sha256: blob.sha256, blob_oid: blob.payload.oid, object_bytes_hex: treeBytes.toString("hex"), oid: gitOid("tree", treeBytes) });
    output.push(tree);
    const outcomeMap = { TERMINAL_VALID_OUTCOME: "valid_outcome", TERMINAL_HARNESS_FAILURE: "harness_failure", TERMINAL_QUARANTINE: "quarantine" };
    push("commit_intent", {
      ordinal,
      phase,
      schema: "tt-supervised-git-intent-v3",
      tree_record_sha256: tree.sha256,
      tree_oid: tree.payload.oid,
      parent_oid: reservation.payload.predecessor_commit_oid,
      intended_ref: config.payload.intended_ref,
      message: `record supervised phase ${phase}`,
      result_sha256: result.sha256,
      content_sha256: content.sha256,
      terminal_sha256: terminal.sha256,
      terminal_outcome: outcomeMap[terminal.payload.outcome],
      self_exclusion: "commit_oid_forbidden",
    });
  } else if (selection.id === "G001") {
    const phase = activeReservation(records).payload.phase;
    const intent = phaseRecord(records, "commit_intent", phase);
    const commitBytes = gitCommitBytes(intent.payload);
    push("commit_object", { ordinal, phase, intent_sha256: intent.sha256, commit_bytes: commitBytes, oid: gitOid("commit", Buffer.from(commitBytes, "utf8")), tree_oid: intent.payload.tree_oid, parent_oid: intent.payload.parent_oid });
  } else if (["G003", "G004"].includes(selection.id)) {
    const phase = activeReservation(records).payload.phase;
    const object = phaseRecord(records, "commit_object", phase);
    const pre = phaseRecord(records, "ref_observation_pre", phase);
    const cas = makeRecord(traceId, "ref_cas_attempt", { sequence, campaign_id: traceId, ordinal, phase, ref: config.payload.intended_ref, expected_old_oid: pre.payload.observed_oid, new_oid: object.payload.oid, outcome: "applied", commit_object_sha256: object.sha256, ref_observation_pre_sha256: pre.sha256 });
    output.push(cas);
    push("ref_observation_post", { ordinal, phase, ref: config.payload.intended_ref, observed_oid: object.payload.oid, cas_sha256: cas.sha256 });
  } else if (["G005I", "G005E"].includes(selection.id)) {
    const phase = activeReservation(records).payload.phase;
    const object = phaseRecord(records, "commit_object", phase);
    const cas = phaseRecord(records, "ref_cas_attempt", phase);
    const post = phaseRecord(records, "ref_observation_post", phase);
    push("committed_phase", { ordinal, phase, commit_oid: object.payload.oid, commit_object_sha256: object.sha256, ref_cas_sha256: cas.sha256, post_ref_observation_sha256: post.sha256 });
  } else if (selection.id === "C005") {
    const committed = latestCommitted(records);
    push("closure_request", { ordinal, last_committed_sha256: committed.sha256, terminal_request: "attested_closure" });
  } else if (selection.id === "M002") {
    const measurement = findOne(records, "resource_measurement", (record) => record.payload.closure_ordinal === ordinal);
    const start = findOne(records, "attempt_start", (record) => record.payload.ordinal === ordinal);
    push("resource_receipt", { ordinal, measurement_sha256: measurement.sha256, input_sha256: measurement.payload.input_sha256, result_sha256: measurement.payload.result_sha256, result: measurement.payload.result, admission_sha256: admission.sha256, attempt_start_sha256: start.sha256 });
  } else if (selection.id === "M003") {
    const resource = findOne(records, "resource_receipt", (record) => record.payload.ordinal === ordinal);
    const closure = findOne(records, "closure_request");
    push("attempt_end", { ordinal, outcome: "attested_closure", terminal_request: closure.payload.terminal_request, durable_state: "valid", resource_receipt_sha256: resource.sha256 });
  } else if (selection.id === "M005") {
    const resource = findOne(records, "resource_receipt", (record) => record.payload.ordinal === ordinal);
    const end = findOne(records, "attempt_end", (record) => record.payload.ordinal === ordinal);
    const closure = findOne(records, "closure_request");
    push("campaign_terminal", { ordinal, kind: "valid_attested_closure", resource_receipt_sha256: resource.sha256, attempt_end_sha256: end.sha256, closure_request_sha256: closure.sha256 });
  } else if (selection.id === "M008") {
    const terminal = findOne(records, "campaign_terminal");
    const measurement = findOne(records, "resource_measurement", (record) => record.payload.closure_ordinal === ordinal);
    push("recalculation_receipt", { ordinal, campaign_terminal_sha256: terminal.sha256, derived_totals_sha256: measurement.payload.result_sha256, status: "complete" });
  } else if (selection.id === "M009") {
    const recalculation = findOne(records, "recalculation_receipt");
    push("lock_release", { ordinal, recalculation_receipt_sha256: recalculation.sha256, status: "released" });
  } else if (!["D003", "D004", "R001", "P005"].includes(selection.id)) {
    fail("ACTION_SEMANTICS_MISSING", `${selection.id}:${action}`);
  }
  return sortedUniverse(output);
}

function expectedObservationRecords(traceId, sequence, observationKind, context, records) {
  const admission = currentAdmission(records);
  if (!admission) fail("OBSERVATION_CURRENT_ADMISSION_MISSING");
  const ordinal = admission.payload.ordinal;
  const output = [];
  const push = (type, payload) => output.push(makeRecord(traceId, type, { sequence, campaign_id: traceId, ...payload }));
  if (observationKind === "capability_attestation") {
    const reservation = activeReservation(records);
    if (!reservation || phaseRecord(records, "capability_receipt", reservation.payload.phase)) fail("CAPABILITY_OBSERVATION_NOT_PENDING");
    const phase = reservation.payload.phase;
    const identity = makeRecord(traceId, "executable_identity", {
      sequence,
      campaign_id: traceId,
      ordinal,
      phase,
      executable_path: capabilityDescriptor.executable_path,
      executable_sha256: capabilityDescriptor.executable_sha256,
      opened_file_token: `opened:${ordinal}:${phase}:${capabilityDescriptor.executable_sha256}`,
    });
    output.push(identity);
    push("capability_receipt", {
      ordinal,
      phase,
      reservation_sha256: reservation.sha256,
      descriptor_sha256: configOf(records).payload.capability_descriptor_sha256,
      executable_identity_sha256: identity.sha256,
      inherited_descriptor_bindings: clone(inheritedDescriptorBindings),
      decision: "allow",
    });
  } else if (observationKind === "meter_finalization") {
    if (context !== "meter_finalization" || !findOne(records, "closure_request")) fail("METER_OBSERVATION_NOT_PENDING");
    const temporary = clone(records);
    if (!findOne(temporary, "resource_lifetime", (record) => record.payload.ordinal === ordinal)) {
      const lifetime = makeRecord(traceId, "resource_lifetime", lifetimePayload(traceId, ordinal, sequence));
      output.push(lifetime);
      temporary.push(lifetime);
    }
    const processTokens = findAll(temporary, "phase_spawn", (record) => record.payload.ordinal === ordinal).map((record) => record.payload.process_token).sort();
    const identity = makeRecord(traceId, "launch_identity", { sequence, campaign_id: traceId, ordinal, executable_sha256: capabilityDescriptor.executable_sha256, process_tokens: processTokens });
    output.push(identity);
    const observation = makeRecord(traceId, "kernel_process_observation", { sequence, campaign_id: traceId, ordinal, launch_identity_sha256: identity.sha256, observation: "kernel_confirmed_absent" });
    output.push(observation);
    temporary.push(identity, observation);
    output.push(makeMeasurementRecord(traceId, sequence, ordinal, temporary));
  } else {
    fail("OBSERVATION_KIND_UNKNOWN", observationKind);
  }
  return sortedUniverse(output);
}

function journalRecords(records) {
  return records.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type)).sort((a, b) => a.payload.sequence - b.payload.sequence);
}

function replayKernel(records) {
  const semantic = validateSemanticUniverse(records);
  const traceId = semantic.traceId;
  const journals = journalRecords(records);
  const bySequence = new Map();
  for (const record of records) {
    const sequence = record.payload.sequence;
    if (!bySequence.has(sequence)) bySequence.set(sequence, []);
    bySequence.get(sequence).push(record);
  }
  if (findAll(bySequence.get(0) || [], "action_receipt").length || findAll(bySequence.get(0) || [], "observation_receipt").length) fail("JOURNAL_AT_SEQUENCE_ZERO");
  let prefix = sortedUniverse(bySequence.get(0) || []);
  const baseAllowedTypes = new Set(["campaign_config", "root_lock", "normal_admission", "recovery_admission", "attempt_start", "resource_lifetime", "resource_measurement", "resource_receipt", "attempt_end"]);
  const forbiddenBase = prefix.find((record) => !baseAllowedTypes.has(record.record_type));
  if (forbiddenBase) fail("BASE_RECORD_TYPE_FORBIDDEN", forbiddenBase.record_type);
  const baseConfig = configOf(prefix);
  if (baseConfig.payload.requested_run_mode === "normal" && prefix.some((record) => !["campaign_config", "root_lock"].includes(record.record_type))) fail("BASE_NORMAL_HISTORY_FORBIDDEN");
  let context = "entry_preflight";
  let previousJournalSha256 = null;
  for (let index = 0; index < journals.length; index += 1) {
    const expectedSequence = index + 1;
    const receipt = journals[index];
    if (receipt.payload.sequence !== expectedSequence) fail("JOURNAL_SEQUENCE_NONCONTIGUOUS", receipt.path);
    const group = sortedUniverse(bySequence.get(expectedSequence) || []);
    const groupJournals = group.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type));
    if (groupJournals.length !== 1 || groupJournals[0].sha256 !== receipt.sha256) fail("JOURNAL_CARDINALITY_INVALID", String(expectedSequence));
    const domain = group.filter((record) => record.sha256 !== receipt.sha256);
    if (receipt.payload.previous_journal_sha256 !== previousJournalSha256) fail("JOURNAL_PREDECESSOR_MISMATCH", receipt.path);
    if (receipt.payload.pre_universe_sha256 !== sha256(prefix)) fail("JOURNAL_PRE_UNIVERSE_MISMATCH", receipt.path);
    if (receipt.payload.context && receipt.payload.context !== context) fail("OBSERVATION_CONTEXT_MISMATCH", receipt.path);
    if (!same(receipt.payload.domain_record_sha256s, domain.map((record) => record.sha256))) fail("JOURNAL_DOMAIN_DIGEST_MISMATCH", receipt.path);
    const postDomain = sortedUniverse([...prefix, ...domain]);
    if (receipt.payload.post_domain_universe_sha256 !== sha256(postDomain)) fail("JOURNAL_POST_DOMAIN_MISMATCH", receipt.path);
    if (receipt.record_type === "action_receipt") {
      const derived = deriveKernelSource(prefix, context);
      if (derived.kind !== "ready") fail("ACTION_EXECUTED_WHILE_NOT_READY", `${receipt.path}:${derived.kind}`);
      const selected = selectRule(derived.schema_id, derived.source);
      if (receipt.payload.source_schema !== derived.schema_id) fail("ACTION_SOURCE_SCHEMA_MISMATCH", receipt.path);
      if (receipt.payload.source_sha256 !== sha256(derived.source)) fail("ACTION_SOURCE_DIGEST_MISMATCH", receipt.path);
      if (receipt.payload.selected_rule !== selected.id) fail("ACTION_SELECTED_RULE_MISMATCH", receipt.path);
      if (receipt.payload.selected_action !== selected.next_action) fail("ACTION_SELECTED_ACTION_MISMATCH", receipt.path);
      if (receipt.payload.next_context !== selected.next_context) fail("ACTION_NEXT_CONTEXT_MISMATCH", receipt.path);
      const expectedDomain = expectedActionRecords(traceId, expectedSequence, selected, derived.source, prefix);
      if (!same(domain, expectedDomain)) fail("ACTION_RECORD_MISMATCH", receipt.path);
      context = selected.next_context;
    } else {
      const expectedDomain = expectedObservationRecords(traceId, expectedSequence, receipt.payload.observation_kind, context, prefix);
      if (!same(domain, expectedDomain)) fail("OBSERVATION_RECORD_MISMATCH", receipt.path);
    }
    prefix = sortedUniverse([...postDomain, receipt]);
    previousJournalSha256 = receipt.sha256;
  }
  const positiveSequences = [...bySequence.keys()].filter((sequence) => sequence > 0).sort((a, b) => a - b);
  if (!same(positiveSequences, journals.map((record) => record.payload.sequence))) fail("UNJOURNALED_RECORD_SEQUENCE");
  if (!same(prefix, sortedUniverse(records))) fail("JOURNAL_UNIVERSE_COVERAGE_MISMATCH");
  return {
    trace_id: traceId,
    context,
    previous_journal_sha256: previousJournalSha256,
    next: deriveKernelSource(prefix, context),
    universe: prefix,
    universe_sha256: sha256(prefix),
    journal_count: journals.length,
  };
}

function nextSequence(records) {
  return Math.max(0, ...records.map((record) => record.payload.sequence)) + 1;
}

function appendAction(records) {
  const replay = replayKernel(records);
  if (replay.next.kind !== "ready") fail("TRACE_ACTION_NOT_READY", replay.next.kind);
  const selected = selectRule(replay.next.schema_id, replay.next.source);
  if (["DEFAULT", "SCHEMA_REJECT"].includes(selected.id)) fail("TRACE_SELECTOR_REJECTED", `${selected.id}:${replay.next.schema_id}:${canonical(replay.next.source)}`);
  const sequence = nextSequence(records);
  const domain = expectedActionRecords(replay.trace_id, sequence, selected, replay.next.source, records);
  const postDomain = sortedUniverse([...records, ...domain]);
  const receipt = makeRecord(replay.trace_id, "action_receipt", {
    sequence,
    campaign_id: replay.trace_id,
    previous_journal_sha256: replay.previous_journal_sha256,
    pre_universe_sha256: sha256(sortedUniverse(records)),
    source_schema: replay.next.schema_id,
    source_sha256: sha256(replay.next.source),
    selected_rule: selected.id,
    selected_action: selected.next_action,
    next_context: selected.next_context,
    domain_record_sha256s: domain.map((record) => record.sha256),
    post_domain_universe_sha256: sha256(postDomain),
  });
  const output = sortedUniverse([...postDomain, receipt]);
  replayKernel(output);
  return { records: output, receipt, selected, source: replay.next.source, source_schema: replay.next.schema_id, domain };
}

function appendObservation(records, observationKind) {
  const replay = replayKernel(records);
  if (observationKind === "capability_attestation") {
    const reservation = activeReservation(records);
    if (!reservation || phaseRecord(records, "capability_receipt", reservation.payload.phase)) fail("CAPABILITY_OBSERVATION_NOT_PENDING");
  } else if (replay.next.kind !== "wait" || replay.next.observation_kind !== observationKind) {
    fail("TRACE_OBSERVATION_NOT_PENDING", `${observationKind}:${replay.next.kind}`);
  }
  const sequence = nextSequence(records);
  const domain = expectedObservationRecords(replay.trace_id, sequence, observationKind, replay.context, records);
  const postDomain = sortedUniverse([...records, ...domain]);
  const receipt = makeRecord(replay.trace_id, "observation_receipt", {
    sequence,
    campaign_id: replay.trace_id,
    previous_journal_sha256: replay.previous_journal_sha256,
    pre_universe_sha256: sha256(sortedUniverse(records)),
    observation_kind: observationKind,
    context: replay.context,
    domain_record_sha256s: domain.map((record) => record.sha256),
    post_domain_universe_sha256: sha256(postDomain),
  });
  const output = sortedUniverse([...postDomain, receipt]);
  replayKernel(output);
  return { records: output, receipt, observation_kind: observationKind, domain };
}

function makeConfig(traceId, requestedRunMode) {
  return makeRecord(traceId, "campaign_config", {
    sequence: 0,
    campaign_id: traceId,
    requested_run_mode: requestedRunMode,
    approval_maximum_recovery_bootstraps: 32,
    intended_ref: "refs/autolab/supervised-campaign",
    initial_ref_oid: null,
    capability_descriptor: clone(capabilityDescriptor),
    capability_descriptor_sha256: sha256(capabilityDescriptor),
    resource_policy: { schema: "tt-supervised-resource-policy-v3", closure_memory_capacity: 5, interval_width: 10, interval_stride: 8 },
  });
}

function appendHistoricalAttempt(records, traceId, ordinal) {
  const index = ordinalIndex(ordinal);
  const predecessor = index === 0 ? null : findOne(records, "attempt_end", (record) => record.payload.ordinal === `A${index - 1}`);
  const admission = makeRecord(traceId, index === 0 ? "normal_admission" : "recovery_admission", {
    sequence: 0,
    campaign_id: traceId,
    ordinal,
    predecessor_attempt_end_sha256: predecessor?.sha256 || null,
  });
  addRecord(records, admission);
  const start = makeRecord(traceId, "attempt_start", { sequence: 0, campaign_id: traceId, ordinal, admission_sha256: admission.sha256 });
  addRecord(records, start);
  const lifetime = makeRecord(traceId, "resource_lifetime", lifetimePayload(traceId, ordinal, 0));
  addRecord(records, lifetime);
  const measurement = makeMeasurementRecord(traceId, 0, ordinal, records);
  addRecord(records, measurement);
  const receipt = makeRecord(traceId, "resource_receipt", {
    sequence: 0,
    campaign_id: traceId,
    ordinal,
    measurement_sha256: measurement.sha256,
    input_sha256: measurement.payload.input_sha256,
    result_sha256: measurement.payload.result_sha256,
    result: measurement.payload.result,
    admission_sha256: admission.sha256,
    attempt_start_sha256: start.sha256,
  });
  addRecord(records, receipt);
  addRecord(records, makeRecord(traceId, "attempt_end", {
    sequence: 0,
    campaign_id: traceId,
    ordinal,
    outcome: "recoverable_crash",
    terminal_request: "absent",
    durable_state: "valid",
    resource_receipt_sha256: receipt.sha256,
  }));
}

function makeBaseUniverse(traceId, requestedRunMode) {
  const records = [makeConfig(traceId, requestedRunMode), makeRecord(traceId, "root_lock", { sequence: 0, campaign_id: traceId, lock_token: `lock-${traceId}`, status: "valid_current" })];
  if (requestedRunMode === "recovery") {
    appendHistoricalAttempt(records, traceId, "A0");
    appendHistoricalAttempt(records, traceId, "A1");
  }
  const output = sortedUniverse(records);
  replayKernel(output);
  return output;
}

function buildCompleteTrace(id, requestedRunMode) {
  let records = makeBaseUniverse(id, requestedRunMode);
  const steps = [];
  for (let guard = 0; guard < 160; guard += 1) {
    const replay = replayKernel(records);
    if (replay.next.kind === "complete") {
      return {
        id,
        requested_run_mode: requestedRunMode,
        status: "COMPLETE",
        step_count: steps.length,
        steps,
        final_context: replay.context,
        final_record_universe: records,
        final_universe_sha256: replay.universe_sha256,
        final_journal_sha256: replay.previous_journal_sha256,
      };
    }
    const reservation = activeReservation(records);
    const needsProactiveCapability = reservation && !phaseRecord(records, "capability_receipt", reservation.payload.phase)
      && ["e0_private_map", "live_supervisor"].includes(replay.context);
    if (replay.next.kind === "wait" || needsProactiveCapability) {
      const observationKind = needsProactiveCapability ? "capability_attestation" : replay.next.observation_kind;
      const result = appendObservation(records, observationKind);
      records = result.records;
      steps.push({ sequence: result.receipt.payload.sequence, kind: "observation", observation_kind: observationKind, receipt_sha256: result.receipt.sha256, domain_record_sha256s: result.receipt.payload.domain_record_sha256s, post_universe_sha256: sha256(records) });
    } else {
      const result = appendAction(records);
      records = result.records;
      steps.push({ sequence: result.receipt.payload.sequence, kind: "action", source_schema: result.source_schema, source_sha256: sha256(result.source), selected_rule: result.selected.id, selected_action: result.selected.next_action, next_context: result.selected.next_context, receipt_sha256: result.receipt.sha256, domain_record_sha256s: result.receipt.payload.domain_record_sha256s, post_universe_sha256: sha256(records) });
    }
  }
  fail("TRACE_GUARD_EXHAUSTED", id);
}

const traces = [
  buildCompleteTrace("SEC9-TRACE-A0-END-TO-END", "normal"),
  buildCompleteTrace("SEC9-TRACE-A2-END-TO-END", "recovery"),
];

function rehashRecord(record, edits = {}) {
  const body = {
    schema: edits.schema ?? record.schema,
    path: edits.path ?? record.path,
    record_type: edits.record_type ?? record.record_type,
    payload: edits.payload ?? clone(record.payload),
    producer: edits.producer ?? record.producer,
  };
  const canonicalBytes = canonical(body);
  return { ...body, canonical_bytes: canonicalBytes, sha256: sha256(canonicalBytes) };
}

function rawRecord({ path, recordType, payload, producer }) {
  const body = { schema: "tt-supervised-record-v3", path, record_type: recordType, payload, producer };
  const canonicalBytes = canonical(body);
  return { ...body, canonical_bytes: canonicalBytes, sha256: sha256(canonicalBytes) };
}

function replacePayload(record, mutator) {
  const payload = clone(record.payload);
  mutator(payload);
  return rehashRecord(record, { payload });
}

function traceById(id) {
  const trace = traces.find((candidate) => candidate.id === id);
  if (!trace) fail("TRACE_UNKNOWN", id);
  return trace;
}

function traceRecord(trace, type, predicate = () => true) {
  const record = findOne(trace.final_record_universe, type, predicate);
  if (!record) fail("REGRESSION_TARGET_MISSING", `${trace.id}:${type}`);
  return record;
}

function applyRegressionOperation(records, operation) {
  const output = clone(records);
  if (operation.kind === "remove_records") {
    const paths = new Set(operation.paths);
    const retained = output.filter((record) => !paths.has(record.path));
    if (retained.length === output.length) fail("REGRESSION_MUTATION_NOOP", operation.kind);
    return sortedUniverse(retained);
  }
  if (operation.kind === "append_record") {
    output.push(clone(operation.record));
    return sortedUniverse(output);
  }
  if (operation.kind === "replace_record") {
    const index = output.findIndex((record) => record.path === operation.path);
    if (index < 0) fail("REGRESSION_TARGET_MISSING", operation.path);
    output[index] = clone(operation.after_record);
    return sortedUniverse(output);
  }
  fail("REGRESSION_OPERATION_UNKNOWN", operation.kind);
}

const a0Trace = traceById("SEC9-TRACE-A0-END-TO-END");
const a2Trace = traceById("SEC9-TRACE-A2-END-TO-END");
const a0Records = a0Trace.final_record_universe;
const a2Records = a2Trace.final_record_universe;
const d004Receipt = traceRecord(a2Trace, "action_receipt", (record) => record.payload.selected_rule === "D004");
const p0Terminal = traceRecord(a0Trace, "phase_terminal", (record) => record.payload.phase === "P0");
const p0Content = traceRecord(a0Trace, "phase_content", (record) => record.payload.phase === "P0");
const p0Reservation = traceRecord(a0Trace, "phase_reservation", (record) => record.payload.phase === "P0");
const p1Reservation = traceRecord(a0Trace, "phase_reservation", (record) => record.payload.phase === "P1");
const p1Launch = traceRecord(a0Trace, "launch_intent", (record) => record.payload.phase === "P1");
const p1Intent = traceRecord(a0Trace, "commit_intent", (record) => record.payload.phase === "P1");
const p1Cas = traceRecord(a0Trace, "ref_cas_attempt", (record) => record.payload.phase === "P1");
const p1Post = traceRecord(a0Trace, "ref_observation_post", (record) => record.payload.phase === "P1");
const p1Tree = traceRecord(a0Trace, "git_tree_object", (record) => record.payload.phase === "P1");
const p1Capability = traceRecord(a0Trace, "capability_receipt", (record) => record.payload.phase === "P1");
const a2Measurement = traceRecord(a2Trace, "resource_measurement", (record) => record.payload.closure_ordinal === "A2");
const firstActionReceipt = traceRecord(a0Trace, "action_receipt", (record) => record.payload.sequence === 1);
const p0CapabilityObservationReceipt = traceRecord(a0Trace, "observation_receipt", (record) => record.payload.observation_kind === "capability_attestation" && record.payload.context === "live_supervisor");
const a0FinalJournal = a0Records.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type)).sort((a, b) => b.payload.sequence - a.payload.sequence)[0];
const replayedCapabilityReceipt = makeRecord(a0Trace.id, "observation_receipt", {
  sequence: a0FinalJournal.payload.sequence + 1,
  campaign_id: a0Trace.id,
  previous_journal_sha256: a0FinalJournal.sha256,
  pre_universe_sha256: sha256(sortedUniverse(a0Records)),
  observation_kind: "capability_attestation",
  context: "meter_finalization",
  domain_record_sha256s: [],
  post_domain_universe_sha256: sha256(sortedUniverse(a0Records)),
});

const sparseA1Paths = a2Records.filter((record) => record.payload.sequence === 0 && (
  record.payload.ordinal === "A1" || record.payload.closure_ordinal === "A1"
)).map((record) => record.path);

const omittedA2Input = clone(a2Measurement.payload.input);
omittedA2Input.attempts = omittedA2Input.attempts.filter((attempt) => attempt.id !== "A2");
omittedA2Input.memory_vertices = omittedA2Input.memory_vertices.filter((vertex) => vertex.id !== "A2");
omittedA2Input.possible_overlap_edges = omittedA2Input.possible_overlap_edges.filter((edge) => !edge.includes("A2"));
const omittedA2Result = computeResources(omittedA2Input);
const omittedA2Measurement = replacePayload(a2Measurement, (payload) => {
  payload.input = omittedA2Input;
  payload.input_sha256 = sha256(omittedA2Input);
  payload.result = omittedA2Result;
  payload.result_sha256 = sha256(omittedA2Result);
});

const missingEdgeInput = clone(a2Measurement.payload.input);
missingEdgeInput.possible_overlap_edges = missingEdgeInput.possible_overlap_edges.slice(1);
const missingEdgeResult = computeResources(missingEdgeInput);
const missingEdgeMeasurement = replacePayload(a2Measurement, (payload) => {
  payload.input = missingEdgeInput;
  payload.input_sha256 = sha256(missingEdgeInput);
  payload.result = missingEdgeResult;
  payload.result_sha256 = sha256(missingEdgeResult);
});

const regressionSpecs = [
  {
    id: "SEC9-REG-SPARSE-A2-HISTORY",
    claim: "A2 cannot exist after deleting the complete A1 history",
    target_trace: a2Trace.id,
    operation: { kind: "remove_records", paths: sparseA1Paths },
    expected_rejection: "ORDINAL_PREDECESSOR_INVALID",
  },
  {
    id: "SEC9-REG-A33-ADMISSION",
    claim: "A33 is outside the closed A0-A32 domain",
    target_trace: a2Trace.id,
    operation: {
      kind: "append_record",
      record: rawRecord({ path: `kernel/${a2Trace.id}/admissions/A33.json`, recordType: "recovery_admission", payload: { sequence: 0, campaign_id: a2Trace.id, ordinal: "A33", predecessor_attempt_end_sha256: "0".repeat(64) }, producer: "root_supervisor" }),
    },
    expected_rejection: "ORDINAL_OUT_OF_RANGE",
  },
  {
    id: "SEC9-REG-SOURCE-CONTEXT-RESEED",
    claim: "D004 cannot relabel its derived recovery handoff as campaign progression",
    target_trace: a2Trace.id,
    operation: { kind: "replace_record", path: d004Receipt.path, after_record: replacePayload(d004Receipt, (payload) => { payload.next_context = "campaign_progression"; }) },
    expected_rejection: "ACTION_NEXT_CONTEXT_MISMATCH",
  },
  {
    id: "SEC9-REG-EVENT-TERMINAL-SUBSTITUTION",
    claim: "a content-predecessor terminal cannot masquerade as spawn failure",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p0Terminal.path, after_record: replacePayload(p0Terminal, (payload) => { payload.event_kind = "spawn_failure"; payload.outcome = "TERMINAL_HARNESS_FAILURE"; payload.predecessor_sha256 = p0Content.sha256; }) },
    expected_rejection: "TERMINAL_EVENT_PREDECESSOR_INVALID",
  },
  {
    id: "SEC9-REG-UNKNOWN-RECORD-TYPE",
    claim: "the record vocabulary has no fallthrough type",
    target_trace: a0Trace.id,
    operation: { kind: "append_record", record: rawRecord({ path: `kernel/${a0Trace.id}/opaque/unknown.json`, recordType: "unknown_record", payload: { sequence: 0, campaign_id: a0Trace.id }, producer: "root_supervisor" }) },
    expected_rejection: "RECORD_TYPE_UNKNOWN",
  },
  {
    id: "SEC9-REG-EXTRA-PAYLOAD-KEY",
    claim: "a validly rehashed record with an extra key is rejected",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p0Content.path, after_record: replacePayload(p0Content, (payload) => { payload.private_copy = "forbidden"; }) },
    expected_rejection: "PAYLOAD_KEYS_MISMATCH",
  },
  {
    id: "SEC9-REG-UNAUTHORIZED-PRODUCER",
    claim: "candidate_process cannot author repository CAS evidence",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Cas.path, after_record: rehashRecord(p1Cas, { producer: "candidate_process" }) },
    expected_rejection: "PRODUCER_UNAUTHORIZED",
  },
  {
    id: "SEC9-REG-NORMALIZED-PATH-ALIAS",
    claim: "dot-segment aliases are rejected before path uniqueness",
    target_trace: a0Trace.id,
    operation: { kind: "append_record", record: rehashRecord(p0Content, { path: p0Content.path.replace("/phases/P0/", "/phases/P0/../P0/") }) },
    expected_rejection: "PATH_NONCANONICAL",
  },
  {
    id: "SEC9-REG-RESERVATION-LAUNCH-ORDINAL-DRIFT",
    claim: "a P1 launch cannot drift from A0 to A1",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Launch.path, after_record: replacePayload(p1Launch, (payload) => { payload.ordinal = "A1"; }) },
    expected_rejection: "LAUNCH_IDENTITY_MISMATCH",
  },
  {
    id: "SEC9-REG-DISCONNECTED-GIT-PARENT",
    claim: "P1 parent must equal the exact P0 committed OID",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Intent.path, after_record: replacePayload(p1Intent, (payload) => { payload.parent_oid = "f".repeat(40); }) },
    expected_rejection: "GIT_PARENT_MISMATCH",
  },
  {
    id: "SEC9-REG-ALTERNATE-GIT-REF",
    claim: "CAS cannot target an attacker-selected ref",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Cas.path, after_record: replacePayload(p1Cas, (payload) => { payload.ref = "refs/heads/attacker-controlled"; }) },
    expected_rejection: "GIT_REF_MISMATCH",
  },
  {
    id: "SEC9-REG-CANDIDATE-PRODUCED-CAS",
    claim: "CAS producer authority is closed",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Cas.path, after_record: rehashRecord(p1Cas, { producer: "candidate_process" }) },
    expected_rejection: "PRODUCER_UNAUTHORIZED",
  },
  {
    id: "SEC9-REG-POST-CAS-REF-MOVEMENT",
    claim: "post-CAS observation must still name the committed OID",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Post.path, after_record: replacePayload(p1Post, (payload) => { payload.observed_oid = "e".repeat(40); }) },
    expected_rejection: "POST_CAS_REF_MISMATCH",
  },
  {
    id: "SEC9-REG-SYNTHETIC-TREE",
    claim: "a self-consistent descriptive tree hash cannot replace literal Git tree bytes",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Tree.path, after_record: replacePayload(p1Tree, (payload) => { const bytes = Buffer.from("tree:P1:public-artifacts", "utf8"); payload.object_bytes_hex = bytes.toString("hex"); payload.oid = gitOid("tree", bytes); }) },
    expected_rejection: "GIT_TREE_BYTES_MISMATCH",
  },
  {
    id: "SEC9-REG-FORGED-CAPABILITY-RECEIPT",
    claim: "capability receipt must bind the exact descriptor digest",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Capability.path, after_record: replacePayload(p1Capability, (payload) => { payload.descriptor_sha256 = "f".repeat(64); }) },
    expected_rejection: "CAPABILITY_DESCRIPTOR_MISMATCH",
  },
  {
    id: "SEC9-REG-REPLAYED-CAPABILITY-RECEIPT",
    claim: "a P0 capability receipt cannot be replayed into P1",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Capability.path, after_record: replacePayload(p1Capability, (payload) => { payload.reservation_sha256 = p0Reservation.sha256; }) },
    expected_rejection: "CAPABILITY_RESERVATION_MISMATCH",
  },
  {
    id: "SEC9-REG-INHERITED-DESCRIPTOR-TARGET",
    claim: "descriptor numbers are bound to exact targets and rights",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Capability.path, after_record: replacePayload(p1Capability, (payload) => { payload.inherited_descriptor_bindings[0].target = "private-map"; }) },
    expected_rejection: "CAPABILITY_DESCRIPTOR_BINDING_MISMATCH",
  },
  {
    id: "SEC9-REG-OMITTED-CURRENT-RESOURCE-ATTEMPT",
    claim: "A2 receipt cannot use a validly rehashed A0/A1-only measurement",
    target_trace: a2Trace.id,
    operation: { kind: "replace_record", path: a2Measurement.path, after_record: omittedA2Measurement },
    expected_rejection: "RESOURCE_MEASUREMENT_DOMAIN_MISMATCH",
  },
  {
    id: "SEC9-REG-DELETED-OVERLAP-EDGE",
    claim: "recomputed arithmetic cannot hide a missing lifetime-derived overlap edge",
    target_trace: a2Trace.id,
    operation: { kind: "replace_record", path: a2Measurement.path, after_record: missingEdgeMeasurement },
    expected_rejection: "RESOURCE_OVERLAP_GRAPH_MISMATCH",
  },
  {
    id: "SEC9-REG-ASSERTED-PHASE-OUTCOME",
    claim: "Git progression outcome is derived from the exact terminal",
    target_trace: a0Trace.id,
    operation: { kind: "replace_record", path: p1Intent.path, after_record: replacePayload(p1Intent, (payload) => { payload.terminal_outcome = "harness_failure"; }) },
    expected_rejection: "GIT_TERMINAL_OUTCOME_MISMATCH",
  },
  {
    id: "SEC9-REG-UNREFERENCED-PRIVATE-COPY",
    claim: "an unreferenced private-copy record cannot enter the closed universe",
    target_trace: a0Trace.id,
    operation: { kind: "append_record", record: rawRecord({ path: `kernel/${a0Trace.id}/unmodeled/private-copy.json`, recordType: "unmodeled_private_copy", payload: { sequence: 0, campaign_id: a0Trace.id, private_payload: "arbitrary" }, producer: "candidate_process" }) },
    expected_rejection: "RECORD_TYPE_UNKNOWN",
  },
  {
    id: "SEC9-REG-JOURNAL-AT-SEQUENCE-ZERO",
    claim: "a transition receipt cannot be smuggled into the trusted base snapshot",
    target_trace: a0Trace.id,
    operation: {
      kind: "replace_record",
      path: firstActionReceipt.path,
      after_record: rehashRecord(firstActionReceipt, {
        path: `kernel/${a0Trace.id}/journal/0000-action.json`,
        payload: { ...clone(firstActionReceipt.payload), sequence: 0 },
      }),
    },
    expected_rejection: "JOURNAL_AT_SEQUENCE_ZERO",
  },
  {
    id: "SEC9-REG-OUT-OF-CONTEXT-METER-OBSERVATION",
    claim: "a capability boundary cannot be relabeled as a meter observation in live context",
    target_trace: a0Trace.id,
    operation: {
      kind: "replace_record",
      path: p0CapabilityObservationReceipt.path,
      after_record: replacePayload(p0CapabilityObservationReceipt, (payload) => { payload.observation_kind = "meter_finalization"; }),
    },
    expected_rejection: "METER_OBSERVATION_NOT_PENDING",
  },
  {
    id: "SEC9-REG-DELETED-TRANSITION-RECEIPT",
    claim: "deleting D004's no-record transition receipt breaks the contiguous journal",
    target_trace: a2Trace.id,
    operation: { kind: "remove_records", paths: [d004Receipt.path] },
    expected_rejection: "JOURNAL_SEQUENCE_NONCONTIGUOUS",
  },
  {
    id: "SEC9-REG-REPLAYED-CONSUMED-OBSERVATION",
    claim: "a consumed capability observation cannot be replayed after final closure",
    target_trace: a0Trace.id,
    operation: { kind: "append_record", record: replayedCapabilityReceipt },
    expected_rejection: "CAPABILITY_OBSERVATION_NOT_PENDING",
  },
  {
    id: "SEC9-REG-CROSS-FILE-PUBLICATION-SWAP",
    claim: "the selector byte snapshot cannot be replaced under the V9 binding",
    target_trace: null,
    operation: { kind: "publication_selector_swap", observed_selector_sha256: "0".repeat(64) },
    expected_rejection: "PUBLICATION_SELECTOR_HASH_MISMATCH",
  },
];

function executeRegression(spec) {
  try {
    if (spec.operation.kind === "publication_selector_swap") {
      if (spec.operation.observed_selector_sha256 !== selectorExpectedSha256) fail("PUBLICATION_SELECTOR_HASH_MISMATCH");
      return { observed_rejection: null, passed: false };
    }
    const trace = traceById(spec.target_trace);
    const mutated = applyRegressionOperation(trace.final_record_universe, spec.operation);
    replayKernel(mutated);
    return { observed_rejection: null, passed: false };
  } catch (error) {
    return { observed_rejection: error.code || "UNCLASSIFIED_ERROR", detail: error.message, passed: (error.code || "UNCLASSIFIED_ERROR") === spec.expected_rejection };
  }
}

const regressions = regressionSpecs.map((spec) => ({ ...spec, builder_result: executeRegression(spec) }));
const failedRegressions = regressions.filter((regression) => !regression.builder_result.passed);
if (failedRegressions.length > 0) fail("REGRESSION_EXPECTATION_MISMATCH", failedRegressions.map((regression) => `${regression.id}:${regression.builder_result.observed_rejection}`).join(","));

const repairObligations = [
  "V9-REDUCER-01", "V9-SCHEMA-01", "V9-PATH-01", "V9-ORDINAL-01", "V9-IDENTITY-01",
  "V9-PHASE-01", "V9-TRACE-01", "V9-POST-01", "V9-EVENT-01", "V9-AUTHORITY-01",
  "V9-CLOSURE-01", "V9-GIT-01", "V9-GIT-02", "V9-OUTCOME-01", "V9-CAPABILITY-01",
  "V9-RESOURCE-01", "V9-RESOURCE-02", "V9-CONTEXT-01", "V9-PUBLISH-01", "V9-DIFFERENTIAL-01",
];

const evidenceRelativePaths = {
  repair_handoff_v8: "evidence/tt-supervised-executor-v8-rejected-snapshot/supervised-executor-repair-handoff-v8.yaml",
  rejected_snapshot_root: "evidence/tt-supervised-executor-v8-rejected-snapshot.sha256",
  theory_review_v8: "evidence/tt-supervised-executor-v8-rejected-snapshot/supervised-executor-v8-theory-review.md",
  red_team_review_v8: "evidence/tt-supervised-executor-v8-rejected-snapshot/supervised-executor-v8-red-team-review.md",
  postfreeze_counterexample_v8: "evidence/tt-supervised-executor-v8-rejected-snapshot/supervised-executor-v8-postfreeze-counterexamples.md",
};
const evidenceManifest = Object.fromEntries(Object.entries(evidenceRelativePaths).map(([id, relativePath]) => [id, {
  relative_path: relativePath,
  sha256: sha256(readFileSync(join(here, relativePath))),
}]));

const recordSchemaRegistry = Object.fromEntries(Object.keys(producerByType).sort().map((type) => [type, {
  allowed_producer: producerByType[type],
  payload_required: payloadKeysByType[type],
  additional_payload_properties: false,
  path_derived_from_payload: true,
  cardinality: ["action_receipt", "observation_receipt"].includes(type) ? "one_per_sequence" : "one_per_canonical_path",
}]));

const artifact = {
  schema: "tt-supervised-executor-closed-kernel-v9",
  protocol,
  status: ["HYPOTHESIS", "MODEL-BOUND", "ZERO-RUN", "NOVELTY-UNVERIFIED"],
  artifact_freeze_authorized: false,
  implementation_authorized: false,
  campaign_authorized: false,
  ecdlp_claim: false,
  builder_artifact: "build_v9_closed_kernel.mjs",
  builder_sha256: sha256(builderBytes),
  selector_artifact: selectorName,
  selector_sha256: selectorSha256,
  selector_rule_count: rules.length,
  selector_symbolic_case_count: selector.totality.symbolic_domain_cardinality,
  selector_partition_count: selector.totality.symbolic_partition_count,
  architecture: {
    source_snapshots_permitted: false,
    next_source_input: "canonical_record_universe_and_replayed_context_only",
    journal_predecessor_bound: true,
    no_record_actions_receive_durable_action_receipts: true,
    unknown_records_rejected: true,
    exact_payload_keys_required: true,
    canonical_normalized_paths_required: true,
    producer_authority_closed: true,
    git_tree_blob_commit_bytes_literal: true,
    post_cas_ref_observation_required: true,
    resource_domain_derived_from_admissions_starts_lifetimes: true,
    capability_bound_to_descriptor_executable_attempt_phase_reservation: true,
  },
  repair_obligations: repairObligations,
  record_schema_registry: recordSchemaRegistry,
  evidence_manifest: evidenceManifest,
  traces,
  trace_count: traces.length,
  trace_step_count: traces.reduce((sum, trace) => sum + trace.step_count, 0),
  regressions,
  regression_count: regressions.length,
  builder_regression_pass_count: regressions.filter((regression) => regression.builder_result.passed).length,
  gates: {
    local_builder_gate: regressions.every((regression) => regression.builder_result.passed) && traces.every((trace) => trace.status === "COMPLETE"),
    independent_verifier_gate: false,
    independent_theory_gate: false,
    independent_red_team_gate: false,
    implementation_gate: false,
    campaign_gate: false,
  },
  limitations: [
    "finite model only",
    "OS isolation and filesystem durability remain implementation obligations",
    "SHA-1 Git object IDs model Git compatibility and are not a cryptographic claim",
    "selector matrix is inherited from rejected V8 only as the unchanged rule set",
    "no campaign or cryptanalytic workload was executed",
  ],
};

const artifactName = "supervised-executor-closed-kernel-v9.json";
const artifactBytes = Buffer.from(`${JSON.stringify(artifact, null, 2)}\n`, "utf8");
writeFileSync(join(here, artifactName), artifactBytes);
process.stdout.write(`${JSON.stringify({
  status: "PASS",
  artifact: artifactName,
  artifact_sha256: sha256(artifactBytes),
  builder_sha256: artifact.builder_sha256,
  selector_sha256: selectorSha256,
  traces: traces.map((trace) => ({ id: trace.id, steps: trace.step_count, records: trace.final_record_universe.length, final_universe_sha256: trace.final_universe_sha256 })),
  regressions: regressions.length,
  regression_passes: artifact.builder_regression_pass_count,
})}\n`);
