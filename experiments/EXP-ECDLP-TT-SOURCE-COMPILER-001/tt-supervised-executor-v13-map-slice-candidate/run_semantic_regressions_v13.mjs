import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const protocol = "EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor/13";
const artifactPath = "supervised-executor-closed-kernel-v13.json";
const workDirectory = "semantic-regression-inputs-v13";

function stable(value) {
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  if (value !== null && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
}

function digest(value) {
  const input = typeof value === "string" || Buffer.isBuffer(value) ? value : stable(value);
  return createHash("sha256").update(input).digest("hex");
}

function gitHash(type, value) {
  const bytes = Buffer.isBuffer(value) ? value : Buffer.from(value, "utf8");
  return createHash("sha1").update(Buffer.concat([Buffer.from(`${type} ${bytes.length}\0`, "utf8"), bytes])).digest("hex");
}

function commitText(intent) {
  const parent = intent.parent_oid === null ? "" : `parent ${intent.parent_oid}\n`;
  return `tree ${intent.tree_oid}\n${parent}author AutoLab <autolab@example.invalid> 0 +0000\ncommitter AutoLab <autolab@example.invalid> 0 +0000\n\n${intent.message}\n`;
}

function ordered(records) {
  return structuredClone(records).sort((left, right) => left.path.localeCompare(right.path));
}

function rehash(record) {
  const { canonical_bytes: ignoredBytes, sha256: ignoredDigest, ...body } = structuredClone(record);
  const canonicalBytes = stable(body);
  return { ...body, canonical_bytes: canonicalBytes, sha256: digest(canonicalBytes) };
}

function replaceRecord(records, path, editor) {
  const index = records.findIndex((record) => record.path === path);
  if (index < 0) throw new Error(`record not found: ${path}`);
  const edited = structuredClone(records[index]);
  editor(edited);
  const replacement = rehash(edited);
  records[index] = replacement;
  return replacement;
}

function replaceTracked(records, path, editor, replacements) {
  const original = records.find((record) => record.path === path);
  const replacement = replaceRecord(records, path, editor);
  replacements.set(original.sha256, replacement.sha256);
  return replacement;
}

function replaceMapped(value, replacements) {
  if (typeof value === "string") {
    let current = value;
    const seen = new Set();
    while (replacements.has(current) && !seen.has(current)) {
      seen.add(current);
      current = replacements.get(current);
    }
    return current;
  }
  if (Array.isArray(value)) return value.map((item) => replaceMapped(item, replacements));
  if (value !== null && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, replaceMapped(item, replacements)]));
  return value;
}

function propagateDigestReferences(records, replacements) {
  for (let round = 0; round < 128; round += 1) {
    let changed = false;
    for (const record of [...records]) {
      if (["action_receipt", "observation_receipt"].includes(record.record_type)) continue;
      const payload = replaceMapped(record.payload, replacements);
      if (stable(payload) === stable(record.payload)) continue;
      replaceTracked(records, record.path, (edited) => { edited.payload = payload; }, replacements);
      changed = true;
    }
    if (!changed) return records;
  }
  throw new Error("digest-reference propagation did not converge");
}

function relinkDerivedGraph(records, replacements) {
  for (let round = 0; round < 128; round += 1) {
    propagateDigestReferences(records, replacements);
    let changed = false;
    for (const tree of records.filter((record) => record.record_type === "git_tree_object")) {
      const blob = records.find((record) => record.record_type === "git_blob_object" && record.sha256 === tree.payload.blob_record_sha256);
      if (!blob) continue;
      const objectBytes = Buffer.concat([Buffer.from("100644 phase.json\0", "utf8"), Buffer.from(blob.payload.oid, "hex")]);
      const payload = { ...tree.payload, blob_oid: blob.payload.oid, object_bytes_hex: objectBytes.toString("hex"), oid: gitHash("tree", objectBytes) };
      if (stable(payload) === stable(tree.payload)) continue;
      const oldOid = tree.payload.oid;
      const changedTree = replaceTracked(records, tree.path, (record) => { record.payload = payload; }, replacements);
      if (oldOid !== changedTree.payload.oid) replacements.set(oldOid, changedTree.payload.oid);
      changed = true;
    }
    propagateDigestReferences(records, replacements);
    for (const object of records.filter((record) => record.record_type === "commit_object")) {
      const intent = records.find((record) => record.record_type === "commit_intent" && record.sha256 === object.payload.intent_sha256);
      if (!intent) continue;
      const bytes = commitText(intent.payload);
      const payload = { ...object.payload, commit_bytes: bytes, oid: gitHash("commit", bytes), tree_oid: intent.payload.tree_oid, parent_oid: intent.payload.parent_oid };
      if (stable(payload) === stable(object.payload)) continue;
      const oldOid = object.payload.oid;
      const changedObject = replaceTracked(records, object.path, (record) => { record.payload = payload; }, replacements);
      if (oldOid !== changedObject.payload.oid) replacements.set(oldOid, changedObject.payload.oid);
      changed = true;
    }
    if (!changed) {
      propagateDigestReferences(records, replacements);
      return records;
    }
  }
  throw new Error("derived Git graph relinking did not converge");
}

function overlaps(left, right) {
  return left.interval_start < right.interval_end && right.interval_start < left.interval_end;
}

function resourceInput(records, closureOrdinal) {
  const end = Number(closureOrdinal.slice(1));
  const ordinals = Array.from({ length: end + 1 }, (_, index) => `A${index}`);
  const attempts = [];
  const memoryVertices = [];
  for (const ordinal of ordinals) {
    const lifetime = records.find((record) => record.record_type === "resource_lifetime" && record.payload.ordinal === ordinal).payload;
    attempts.push({
      id: ordinal,
      bootstrap_observed: lifetime.bootstrap_observed,
      bootstrap_cap: lifetime.bootstrap_cap,
      meter_observed_preterminal: lifetime.meter_observed_preterminal,
      meter_preterminal_cap: lifetime.meter_preterminal_cap,
      meter_terminal_cap: lifetime.meter_terminal_cap,
      wall_cap: lifetime.wall_cap,
      io_charge: lifetime.io_charge,
      disk_charge: lifetime.disk_charge,
    });
    memoryVertices.push({ id: ordinal, capacity: lifetime.memory_capacity, interval_start: lifetime.interval_start, interval_end: lifetime.interval_end });
  }
  const maximumEnd = Math.max(...memoryVertices.map((vertex) => vertex.interval_end));
  memoryVertices.push({ id: `closure-${closureOrdinal}`, capacity: 5, interval_start: maximumEnd - 2, interval_end: maximumEnd + 3 });
  const possibleOverlapEdges = [];
  for (let left = 0; left < memoryVertices.length; left += 1) {
    for (let right = left + 1; right < memoryVertices.length; right += 1) {
      if (overlaps(memoryVertices[left], memoryVertices[right])) possibleOverlapEdges.push([memoryVertices[left].id, memoryVertices[right].id]);
    }
  }
  return { schema: "tt-supervised-resource-input-v3", closure_ordinal: closureOrdinal, attempts, memory_vertices: memoryVertices, possible_overlap_edges: possibleOverlapEdges };
}

function resourceTotals(input) {
  const cpu = input.attempts.reduce((sum, row) => sum + (row.bootstrap_observed ?? row.bootstrap_cap) + (row.meter_observed_preterminal ?? row.meter_preterminal_cap) + row.meter_terminal_cap, 0);
  const wall = input.attempts.reduce((sum, row) => sum + row.wall_cap, 0);
  const io = input.attempts.reduce((sum, row) => sum + row.io_charge, 0);
  const disk = input.attempts.reduce((sum, row) => sum + row.disk_charge, 0);
  const adjacency = new Map(input.memory_vertices.map((vertex) => [vertex.id, new Set([vertex.id])]));
  for (const [left, right] of input.possible_overlap_edges) {
    adjacency.get(left).add(right);
    adjacency.get(right).add(left);
  }
  const seen = new Set();
  const components = [];
  for (const vertex of input.memory_vertices) {
    if (seen.has(vertex.id)) continue;
    const stack = [vertex.id];
    const members = [];
    let charge = 0;
    while (stack.length > 0) {
      const id = stack.pop();
      if (seen.has(id)) continue;
      seen.add(id);
      members.push(id);
      charge += input.memory_vertices.find((row) => row.id === id).capacity;
      for (const neighbor of adjacency.get(id)) stack.push(neighbor);
    }
    components.push({ members: members.sort(), charge });
  }
  return { cpu, memory: Math.max(...components.map((row) => row.charge)), wall, io, disk, memory_components: components };
}

function relinkJournals(input, initialReplacements = new Map()) {
  const records = ordered(input);
  const replacements = new Map(initialReplacements);
  let previous = null;
  const receiptPaths = records
    .filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type))
    .sort((left, right) => left.payload.sequence - right.payload.sequence)
    .map((record) => record.path);
  for (const receiptPath of receiptPaths) {
    relinkDerivedGraph(records, replacements);
    const oldReceipt = records.find((record) => record.path === receiptPath);
    const sequence = oldReceipt.payload.sequence;
    const prefix = ordered(records.filter((record) => record.payload.sequence < sequence));
    const group = ordered(records.filter((record) => record.payload.sequence === sequence));
    const domain = group.filter((record) => !["action_receipt", "observation_receipt"].includes(record.record_type));
    const edited = structuredClone(oldReceipt);
    edited.payload = replaceMapped(edited.payload, replacements);
    edited.payload.previous_journal_sha256 = previous;
    edited.payload.pre_universe_sha256 = digest(prefix);
    edited.payload.domain_record_sha256s = domain.map((record) => record.sha256);
    edited.payload.post_domain_universe_sha256 = digest(ordered([...prefix, ...domain]));
    const receipt = rehash(edited);
    records[records.findIndex((record) => record.path === oldReceipt.path)] = receipt;
    replacements.set(oldReceipt.sha256, receipt.sha256);
    previous = receipt.sha256;
  }
  return ordered(records);
}

function mutateConfig(records, editor) {
  const config = records.find((record) => record.record_type === "campaign_config");
  replaceRecord(records, config.path, (record) => editor(record.payload));
  return relinkJournals(records);
}

function mutateRecalculation(records, editor) {
  const recalculation = records.find((record) => record.record_type === "recalculation_receipt");
  const changed = replaceRecord(records, recalculation.path, (record) => editor(record.payload));
  const release = records.find((record) => record.record_type === "lock_release");
  replaceRecord(records, release.path, (record) => { record.payload.recalculation_receipt_sha256 = changed.sha256; });
  return relinkJournals(records);
}

function mutateResourceObservation(records, editor) {
  const replacements = new Map();
  const lifetime = records.find((record) => record.record_type === "resource_lifetime" && record.payload.ordinal === "A2");
  replaceTracked(records, lifetime.path, (record) => editor(record.payload), replacements);

  const input = resourceInput(records, "A2");
  const result = resourceTotals(input);
  const measurement = records.find((record) => record.record_type === "resource_measurement" && record.payload.closure_ordinal === "A2");
  const changedMeasurement = replaceTracked(records, measurement.path, (record) => {
    record.payload.input = input;
    record.payload.input_sha256 = digest(input);
    record.payload.result = result;
    record.payload.result_sha256 = digest(result);
  }, replacements);
  const receipt = records.find((record) => record.record_type === "resource_receipt" && record.payload.ordinal === "A2");
  replaceTracked(records, receipt.path, (record) => {
    record.payload.measurement_sha256 = changedMeasurement.sha256;
    record.payload.input_sha256 = changedMeasurement.payload.input_sha256;
    record.payload.result_sha256 = changedMeasurement.payload.result_sha256;
    record.payload.result = structuredClone(changedMeasurement.payload.result);
  }, replacements);
  const recalculation = records.find((record) => record.record_type === "recalculation_receipt");
  replaceTracked(records, recalculation.path, (record) => { record.payload.derived_totals_sha256 = changedMeasurement.payload.result_sha256; }, replacements);
  propagateDigestReferences(records, replacements);
  return relinkJournals(records, replacements);
}

function mutateResourceReceipt(records, editor) {
  const replacements = new Map();
  const receipt = records.find((record) => record.record_type === "resource_receipt" && record.payload.ordinal === "A2");
  replaceTracked(records, receipt.path, (record) => editor(record.payload), replacements);
  propagateDigestReferences(records, replacements);
  return relinkJournals(records, replacements);
}

function mutateTrackedGraphRecord(records, type, predicate, editor) {
  const replacements = new Map();
  const record = records.find((candidate) => candidate.record_type === type && predicate(candidate));
  if (!record) throw new Error(`tracked mutation record missing: ${type}`);
  replaceTracked(records, record.path, (changed) => editor(changed.payload, changed), replacements);
  propagateDigestReferences(records, replacements);
  return relinkJournals(records, replacements);
}

function replay(validatorPath, inputPath) {
  const run = spawnSync(process.execPath, [validatorPath, "--replay-file", inputPath], { encoding: "utf8" });
  const lines = run.stdout.trim().split("\n").filter(Boolean);
  if (lines.length !== 1) throw new Error(`${validatorPath} emitted invalid replay output: ${run.stdout}${run.stderr}`);
  return { ...JSON.parse(lines[0]), exit_code: run.status };
}

const artifactBytes = readFileSync(artifactPath);
const artifact = JSON.parse(artifactBytes);
const trace = artifact.traces.find((candidate) => candidate.id === "SEC13-TRACE-A2-END-TO-END");
if (!trace) throw new Error("A2 trace missing");
const cleanRecords = trace.final_record_universe;

const cases = [
  {
    id: "alternate_record_schema_literal",
    expected_rejection: "RECORD_SCHEMA_MISMATCH",
    mutate(records) {
      const finalReceipt = records.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type)).sort((left, right) => right.payload.sequence - left.payload.sequence)[0];
      replaceRecord(records, finalReceipt.path, (record) => { record.schema = "attacker-selected-record-schema-v0"; });
      return relinkJournals(records);
    },
  },
  {
    id: "noninteger_recovery_approval",
    expected_rejection: "CONFIG_APPROVAL_INVALID",
    mutate: (records) => mutateConfig(records, (payload) => { payload.approval_maximum_recovery_bootstraps = 31.5; }),
  },
  {
    id: "alternate_resource_policy",
    expected_rejection: "RESOURCE_POLICY_INVALID",
    mutate: (records) => mutateConfig(records, (payload) => { payload.resource_policy.interval_stride = 9; }),
  },
  {
    id: "sequence_zero_unconsumed_known_type",
    expected_rejection: "BASE_REACHABILITY_MISMATCH",
    mutate(records) {
      const template = structuredClone(records.find((record) => record.record_type === "recovery_admission" && record.payload.ordinal === "A2"));
      const currentEnd = records.find((record) => record.record_type === "attempt_end" && record.payload.ordinal === "A2");
      template.path = `kernel/${trace.id}/admissions/A3.json`;
      template.payload.sequence = 0;
      template.payload.ordinal = "A3";
      template.payload.predecessor_attempt_end_sha256 = currentEnd.sha256;
      records.push(rehash(template));
      return relinkJournals(records);
    },
  },
  {
    id: "sequence_zero_A3_resource_lifetime",
    expected_rejection: "BASE_REACHABILITY_MISMATCH",
    mutate(records) {
      const template = structuredClone(records.find((record) => record.record_type === "resource_lifetime" && record.payload.ordinal === "A2"));
      template.path = `kernel/${trace.id}/attempts/A3/lifetime.json`;
      Object.assign(template.payload, {
        sequence: 0,
        ordinal: "A3",
        bootstrap_observed: null,
        bootstrap_cap: 23,
        meter_observed_preterminal: 10,
        meter_preterminal_cap: 13,
        meter_terminal_cap: 2,
        wall_cap: 43,
        io_charge: 14,
        disk_charge: 8,
        memory_capacity: 49,
        interval_start: 24,
        interval_end: 34,
      });
      records.push(rehash(template));
      return relinkJournals(records);
    },
  },
  {
    id: "observed_resource_value_above_cap",
    expected_rejection: "RESOURCE_OBSERVATION_INVALID",
    mutate: (records) => mutateResourceObservation(records, (payload) => { payload.bootstrap_observed = payload.bootstrap_cap + 1; }),
  },
  {
    id: "observed_resource_value_negative",
    expected_rejection: "RESOURCE_OBSERVATION_INVALID",
    mutate: (records) => mutateResourceObservation(records, (payload) => { payload.meter_observed_preterminal = -1; }),
  },
  {
    id: "fabricated_resource_receipt_input",
    expected_rejection: "RESOURCE_RECEIPT_MEASUREMENT_MISMATCH",
    mutate: (records) => mutateResourceReceipt(records, (payload) => { payload.input_sha256 = "0".repeat(64); }),
  },
  {
    id: "fabricated_resource_receipt_result",
    expected_rejection: "RESOURCE_RECEIPT_MEASUREMENT_MISMATCH",
    mutate: (records) => mutateResourceReceipt(records, (payload) => {
      payload.result_sha256 = "f".repeat(64);
      payload.result.memory += 1;
    }),
  },
  {
    id: "invalid_attempt_end_outcome",
    expected_rejection: "ATTEMPT_END_OUTCOME_INVALID",
    mutate: (records) => mutateTrackedGraphRecord(records, "attempt_end", (record) => record.payload.ordinal === "A2", (payload) => { payload.outcome = "attacker_selected"; }),
  },
  {
    id: "stale_attempt_end_terminal_request",
    expected_rejection: "ATTEMPT_END_STATE_INVALID",
    mutate: (records) => mutateTrackedGraphRecord(records, "attempt_end", (record) => record.payload.ordinal === "A2", (payload) => { payload.terminal_request = "absent"; }),
  },
  {
    id: "e0_missing_private_map_receipt",
    expected_rejection: "LAUNCH_PRIVATE_MAP_MISMATCH",
    mutate: (records) => mutateTrackedGraphRecord(records, "launch_intent", (record) => record.payload.phase === "E0", (payload) => { payload.private_map_receipt_sha256 = null; }),
  },
  {
    id: "e0_cross_ordinal_private_map_receipt",
    expected_rejection: "PRIVATE_MAP_RECEIPT_MISMATCH",
    mutate: (records) => mutateTrackedGraphRecord(records, "private_map_opened_receipt", () => true, (payload) => { payload.ordinal = "A1"; }),
  },
  {
    id: "non_e0_unexpected_private_map_receipt",
    expected_rejection: "LAUNCH_PRIVATE_MAP_UNEXPECTED",
    mutate: (records) => mutateTrackedGraphRecord(records, "launch_intent", (record) => record.payload.phase === "P0", (payload) => { payload.private_map_receipt_sha256 = "0".repeat(64); }),
  },
  {
    id: "arbitrary_process_token",
    expected_rejection: "PHASE_SPAWN_INVALID",
    mutate(records) {
      const replacements = new Map();
      const spawn = records.find((record) => record.record_type === "phase_spawn" && record.payload.phase === "P0");
      const oldToken = spawn.payload.process_token;
      replaceTracked(records, spawn.path, (record) => { record.payload.process_token = "process:attacker-selected"; }, replacements);
      const identity = records.find((record) => record.record_type === "launch_identity" && record.payload.ordinal === "A2");
      replaceTracked(records, identity.path, (record) => { record.payload.process_tokens = record.payload.process_tokens.map((token) => token === oldToken ? "process:attacker-selected" : token); }, replacements);
      propagateDigestReferences(records, replacements);
      return relinkJournals(records, replacements);
    },
  },
  {
    id: "alternate_private_map_descriptor_token",
    expected_rejection: "PRIVATE_MAP_OBSERVATION_INVALID",
    mutate(records) {
      const replacements = new Map();
      const observation = records.find((record) => record.record_type === "private_map_open_observation");
      const changedObservation = replaceTracked(records, observation.path, (record) => { record.payload.descriptor_token = "private-map:attacker-selected"; }, replacements);
      const receipt = records.find((record) => record.record_type === "private_map_opened_receipt");
      replaceTracked(records, receipt.path, (record) => {
        record.payload.open_observation_sha256 = changedObservation.sha256;
        record.payload.descriptor_token = changedObservation.payload.descriptor_token;
      }, replacements);
      propagateDigestReferences(records, replacements);
      return relinkJournals(records, replacements);
    },
  },
  {
    id: "cross_phase_reap_result_content_terminal",
    expected_rejection: "PHASE_REAP_INVALID",
    mutate(records) {
      const replacements = new Map();
      const p0Spawn = records.find((record) => record.record_type === "phase_spawn" && record.payload.phase === "P0");
      const p1Reap = records.find((record) => record.record_type === "phase_reap" && record.payload.phase === "P1");
      replaceTracked(records, p1Reap.path, (record) => { record.payload.phase_spawn_sha256 = p0Spawn.sha256; }, replacements);
      relinkDerivedGraph(records, replacements);
      return relinkJournals(records, replacements);
    },
  },
  {
    id: "cross_ordinal_phase_chain",
    expected_rejection: "PHASE_SPAWN_INVALID",
    mutate(records) {
      const replacements = new Map();
      const spawn = records.find((record) => record.record_type === "phase_spawn" && record.payload.phase === "P1");
      replaceTracked(records, spawn.path, (record) => {
        record.payload.ordinal = "A1";
        record.payload.process_token = "process:A1:P1";
      }, replacements);
      relinkDerivedGraph(records, replacements);
      return relinkJournals(records, replacements);
    },
  },
  {
    id: "cross_phase_git_intent_components",
    expected_rejection: "GIT_INTENT_LINK_MISSING",
    mutate(records) {
      const replacements = new Map();
      const p0Tree = records.find((record) => record.record_type === "git_tree_object" && record.payload.phase === "P0");
      const p0Result = records.find((record) => record.record_type === "phase_result" && record.payload.phase === "P0");
      const p0Content = records.find((record) => record.record_type === "phase_content" && record.payload.phase === "P0");
      const p0Terminal = records.find((record) => record.record_type === "phase_terminal" && record.payload.phase === "P0");
      const p1Intent = records.find((record) => record.record_type === "commit_intent" && record.payload.phase === "P1");
      replaceTracked(records, p1Intent.path, (record) => {
        record.payload.tree_record_sha256 = p0Tree.sha256;
        record.payload.tree_oid = p0Tree.payload.oid;
        record.payload.result_sha256 = p0Result.sha256;
        record.payload.content_sha256 = p0Content.sha256;
        record.payload.terminal_sha256 = p0Terminal.sha256;
      }, replacements);
      relinkDerivedGraph(records, replacements);
      return relinkJournals(records, replacements);
    },
  },
  {
    id: "cross_phase_git_blob_tree",
    expected_rejection: "GIT_TREE_BYTES_MISMATCH",
    mutate(records) {
      const replacements = new Map();
      const p0Blob = records.find((record) => record.record_type === "git_blob_object" && record.payload.phase === "P0");
      const p1Tree = records.find((record) => record.record_type === "git_tree_object" && record.payload.phase === "P1");
      const objectBytes = Buffer.concat([Buffer.from("100644 phase.json\0", "utf8"), Buffer.from(p0Blob.payload.oid, "hex")]);
      const oldOid = p1Tree.payload.oid;
      const changedTree = replaceTracked(records, p1Tree.path, (record) => {
        record.payload.blob_record_sha256 = p0Blob.sha256;
        record.payload.blob_oid = p0Blob.payload.oid;
        record.payload.object_bytes_hex = objectBytes.toString("hex");
        record.payload.oid = gitHash("tree", objectBytes);
      }, replacements);
      replacements.set(oldOid, changedTree.payload.oid);
      relinkDerivedGraph(records, replacements);
      return relinkJournals(records, replacements);
    },
  },
  {
    id: "cross_phase_terminal_result_content",
    expected_rejection: "TERMINAL_LINKAGE_INVALID",
    mutate(records) {
      const replacements = new Map();
      const p0Result = records.find((record) => record.record_type === "phase_result" && record.payload.phase === "P0");
      const p0Content = records.find((record) => record.record_type === "phase_content" && record.payload.phase === "P0");
      const p1Terminal = records.find((record) => record.record_type === "phase_terminal" && record.payload.phase === "P1");
      replaceTracked(records, p1Terminal.path, (record) => {
        record.payload.predecessor_sha256 = p0Content.sha256;
        record.payload.result_sha256 = p0Result.sha256;
        record.payload.content_sha256 = p0Content.sha256;
      }, replacements);
      relinkDerivedGraph(records, replacements);
      return relinkJournals(records, replacements);
    },
  },
  {
    id: "spawn_failure_over_successful_spawn",
    expected_rejection: "TERMINAL_EVENT_EVIDENCE_INVALID",
    mutate: (records) => mutateTrackedGraphRecord(records, "phase_terminal", (record) => record.payload.phase === "P0", (payload) => {
      const spawn = records.find((record) => record.record_type === "phase_spawn" && record.payload.phase === "P0");
      payload.event_kind = "spawn_failure";
      payload.outcome = "TERMINAL_HARNESS_FAILURE";
      payload.predecessor_sha256 = spawn.sha256;
      payload.result_sha256 = null;
      payload.content_sha256 = null;
    }),
  },
  {
    id: "runtime_failure_over_zero_exit",
    expected_rejection: "TERMINAL_EVENT_EVIDENCE_INVALID",
    mutate: (records) => mutateTrackedGraphRecord(records, "phase_terminal", (record) => record.payload.phase === "P0", (payload) => {
      const reap = records.find((record) => record.record_type === "phase_reap" && record.payload.phase === "P0");
      payload.event_kind = "runtime_failure";
      payload.outcome = "TERMINAL_HARNESS_FAILURE";
      payload.predecessor_sha256 = reap.sha256;
      payload.result_sha256 = null;
      payload.content_sha256 = null;
    }),
  },
  {
    id: "opened_receipt_over_failed_map",
    expected_rejection: "PRIVATE_MAP_RECEIPT_MISMATCH",
    mutate(records) {
      const replacements = new Map();
      const observation = records.find((record) => record.record_type === "private_map_open_observation");
      replaceTracked(records, observation.path, (record) => {
        record.payload.outcome = "open_failed";
        record.payload.descriptor_token = null;
      }, replacements);
      propagateDigestReferences(records, replacements);
      const receipt = records.find((record) => record.record_type === "private_map_opened_receipt");
      replaceTracked(records, receipt.path, (record) => { record.payload.descriptor_token = null; }, replacements);
      propagateDigestReferences(records, replacements);
      relinkDerivedGraph(records, replacements);
      return relinkJournals(records, replacements);
    },
  },
  {
    id: "forged_recalculation_terminal_digest",
    expected_rejection: "RECALCULATION_LINKAGE_MISMATCH",
    mutate: (records) => mutateRecalculation(records, (payload) => { payload.campaign_terminal_sha256 = "0".repeat(64); }),
  },
  {
    id: "forged_recalculation_totals_digest",
    expected_rejection: "RECALCULATION_LINKAGE_MISMATCH",
    mutate: (records) => mutateRecalculation(records, (payload) => { payload.derived_totals_sha256 = "f".repeat(64); }),
  },
  {
    id: "stale_lock_release_recalculation",
    expected_rejection: "LOCK_RELEASE_LINKAGE_MISMATCH",
    mutate(records) {
      const release = records.find((record) => record.record_type === "lock_release");
      replaceRecord(records, release.path, (record) => { record.payload.recalculation_receipt_sha256 = "0".repeat(64); });
      return relinkJournals(records);
    },
  },
  {
    id: "stale_lock_release_attempt_end",
    expected_rejection: "LOCK_RELEASE_LINKAGE_MISMATCH",
    mutate(records) {
      const release = records.find((record) => record.record_type === "lock_release");
      replaceRecord(records, release.path, (record) => { record.payload.attempt_end_sha256 = "0".repeat(64); });
      return relinkJournals(records);
    },
  },
  {
    id: "invalid_lock_release_kind",
    expected_rejection: "LOCK_RELEASE_LINKAGE_MISMATCH",
    mutate(records) {
      const release = records.find((record) => record.record_type === "lock_release");
      replaceRecord(records, release.path, (record) => { record.payload.release_kind = "attacker_selected"; });
      return relinkJournals(records);
    },
  },
  {
    id: "release_without_held_lock",
    expected_rejection: "LOCK_RELEASE_ROOT_STATE_INVALID",
    mutate(records) {
      const root = records.find((record) => record.record_type === "root_lock");
      replaceRecord(records, root.path, (record) => { record.payload.status = "released"; });
      return relinkJournals(records);
    },
  },
];

mkdirSync(workDirectory, { recursive: true });
const results = [];
for (const spec of cases) {
  const records = spec.mutate(structuredClone(cleanRecords));
  const input = { schema: "tt-supervised-executor-replay-input-v13", protocol, mutation_id: spec.id, records };
  const inputPath = join(workDirectory, `${spec.id}.json`);
  const bytes = Buffer.from(`${JSON.stringify(input, null, 2)}\n`, "utf8");
  writeFileSync(inputPath, bytes);
  const builderDecision = replay("build_v13_closed_kernel.mjs", inputPath);
  const verifierDecision = replay("verify_v13_closed_kernel.mjs", inputPath);
  const decisionsMatch = builderDecision.decision === verifierDecision.decision && builderDecision.rejection === verifierDecision.rejection;
  const expectedMatch = builderDecision.decision === "REJECT" && builderDecision.rejection === spec.expected_rejection && verifierDecision.rejection === spec.expected_rejection;
  results.push({
    id: spec.id,
    expected_rejection: spec.expected_rejection,
    requirement_rejection: spec.requirement_rejection || spec.expected_rejection,
    input_artifact: inputPath,
    input_sha256: digest(bytes),
    record_universe_sha256: digest(ordered(records)),
    record_count: records.length,
    journal_count: records.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type)).length,
    relinking: "all_journal_predecessors_and_universe_roots_recomputed",
    builder_decision: builderDecision,
    verifier_decision: verifierDecision,
    decisions_match: decisionsMatch,
    expected_rejection_match: expectedMatch,
    pass: decisionsMatch && expectedMatch,
  });
}

const failed = results.filter((result) => !result.pass);
const receipt = {
  schema: "tt-supervised-executor-semantic-regressions-v13",
  protocol,
  status: failed.length === 0 ? "PASS" : "FAIL",
  evidence_status: ["MODEL-BOUND", "ZERO-RUN"],
  source_artifact: { path: artifactPath, sha256: digest(artifactBytes), trace_id: trace.id, universe_sha256: trace.final_universe_sha256 },
  validator_snapshots: {
    harness: { path: "run_semantic_regressions_v13.mjs", sha256: digest(readFileSync("run_semantic_regressions_v13.mjs")) },
    builder: { path: "build_v13_closed_kernel.mjs", sha256: digest(readFileSync("build_v13_closed_kernel.mjs")) },
    verifier: { path: "verify_v13_closed_kernel.mjs", sha256: digest(readFileSync("verify_v13_closed_kernel.mjs")) },
  },
  case_count: results.length,
  pass_count: results.filter((result) => result.pass).length,
  results,
  limitations: [
    "These 30 cases cover the semantic subset of the 35 mandatory controls; five comparator and publication controls are executed separately.",
    "Each mutation establishes its preregistered first rejection; downstream selector sources and actions are not causally regenerated and may contain secondary rejection causes.",
    "Passing negative mutations does not supply positive reachability evidence for selector rules outside the three V13 traces.",
    "No runtime or cryptanalytic campaign was executed.",
  ],
};
writeFileSync("semantic-regressions-v13.json", `${JSON.stringify(receipt, null, 2)}\n`);
process.stdout.write(`${JSON.stringify({
  status: receipt.status,
  receipt: "semantic-regressions-v13.json",
  receipt_sha256: digest(readFileSync("semantic-regressions-v13.json")),
  cases: results.length,
  passes: receipt.pass_count,
  failed: failed.map((result) => result.id),
})}\n`);
if (failed.length > 0) process.exitCode = 1;
