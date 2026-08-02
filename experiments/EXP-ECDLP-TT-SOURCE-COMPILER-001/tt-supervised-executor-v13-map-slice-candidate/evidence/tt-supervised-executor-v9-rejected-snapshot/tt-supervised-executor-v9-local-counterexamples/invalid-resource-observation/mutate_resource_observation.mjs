import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

function stable(value) {
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  if (value !== null && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
}
function digest(value) {
  const input = typeof value === "string" || Buffer.isBuffer(value) ? value : stable(value);
  return createHash("sha256").update(input).digest("hex");
}
function ordered(records) { return structuredClone(records).sort((left, right) => left.path.localeCompare(right.path)); }
function rehash(record) {
  const { canonical_bytes: ignoredBytes, sha256: ignoredDigest, ...body } = structuredClone(record);
  const canonicalBytes = stable(body);
  return { ...body, canonical_bytes: canonicalBytes, sha256: digest(canonicalBytes) };
}
function overlaps(left, right) { return left.interval_start < right.interval_end && right.interval_start < left.interval_end; }
function resourceInput(records, closureOrdinal) {
  const end = Number(closureOrdinal.slice(1));
  const ordinals = Array.from({ length: end + 1 }, (_, index) => `A${index}`);
  const attempts = [];
  const memoryVertices = [];
  for (const ordinal of ordinals) {
    const lifetime = records.find((record) => record.record_type === "resource_lifetime" && record.payload.ordinal === ordinal).payload;
    attempts.push({ id: ordinal, bootstrap_observed: lifetime.bootstrap_observed, bootstrap_cap: lifetime.bootstrap_cap, meter_observed_preterminal: lifetime.meter_observed_preterminal, meter_preterminal_cap: lifetime.meter_preterminal_cap, meter_terminal_cap: lifetime.meter_terminal_cap, wall_cap: lifetime.wall_cap, io_charge: lifetime.io_charge, disk_charge: lifetime.disk_charge });
    memoryVertices.push({ id: ordinal, capacity: lifetime.memory_capacity, interval_start: lifetime.interval_start, interval_end: lifetime.interval_end });
  }
  const maximumEnd = Math.max(...memoryVertices.map((vertex) => vertex.interval_end));
  memoryVertices.push({ id: `closure-${closureOrdinal}`, capacity: 5, interval_start: maximumEnd - 2, interval_end: maximumEnd + 3 });
  const edges = [];
  for (let left = 0; left < memoryVertices.length; left += 1) for (let right = left + 1; right < memoryVertices.length; right += 1) if (overlaps(memoryVertices[left], memoryVertices[right])) edges.push([memoryVertices[left].id, memoryVertices[right].id]);
  return { schema: "tt-supervised-resource-input-v3", closure_ordinal: closureOrdinal, attempts, memory_vertices: memoryVertices, possible_overlap_edges: edges };
}
function resourceTotals(input) {
  const cpu = input.attempts.reduce((sum, row) => sum + (row.bootstrap_observed ?? row.bootstrap_cap) + (row.meter_observed_preterminal ?? row.meter_preterminal_cap) + row.meter_terminal_cap, 0);
  const wall = input.attempts.reduce((sum, row) => sum + row.wall_cap, 0);
  const io = input.attempts.reduce((sum, row) => sum + row.io_charge, 0);
  const disk = input.attempts.reduce((sum, row) => sum + row.disk_charge, 0);
  const adjacency = new Map(input.memory_vertices.map((vertex) => [vertex.id, new Set([vertex.id])]));
  for (const [left, right] of input.possible_overlap_edges) { adjacency.get(left).add(right); adjacency.get(right).add(left); }
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
function replaceMapped(value, replacements) {
  if (typeof value === "string") {
    let current = value; const seen = new Set();
    while (replacements.has(current) && !seen.has(current)) { seen.add(current); current = replacements.get(current); }
    return current;
  }
  if (Array.isArray(value)) return value.map((item) => replaceMapped(item, replacements));
  if (value !== null && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, replaceMapped(item, replacements)]));
  return value;
}

const artifactPath = process.argv[2] || "supervised-executor-closed-kernel-v9.json";
const artifact = JSON.parse(readFileSync(artifactPath, "utf8"));
const trace = artifact.traces.find((candidate) => candidate.id === "SEC9-TRACE-A2-END-TO-END");
let records = structuredClone(trace.final_record_universe);
const replacements = new Map();
function replaceRecord(index, payload) {
  const original = records[index]; const edited = rehash({ ...original, payload }); records[index] = edited; replacements.set(original.sha256, edited.sha256); return edited;
}

const lifetimeIndex = records.findIndex((record) => record.record_type === "resource_lifetime" && record.payload.ordinal === "A2");
const lifetimePayload = structuredClone(records[lifetimeIndex].payload);
lifetimePayload.bootstrap_observed = lifetimePayload.bootstrap_cap + 1;
lifetimePayload.meter_observed_preterminal = -1;
const forgedLifetime = replaceRecord(lifetimeIndex, lifetimePayload);

const input = resourceInput(records, "A2");
const result = resourceTotals(input);
const measurementIndex = records.findIndex((record) => record.record_type === "resource_measurement" && record.payload.closure_ordinal === "A2");
const measurementPayload = { ...records[measurementIndex].payload, input, input_sha256: digest(input), result, result_sha256: digest(result) };
const measurement = replaceRecord(measurementIndex, measurementPayload);

const receiptIndex = records.findIndex((record) => record.record_type === "resource_receipt" && record.payload.ordinal === "A2");
const receiptPayload = { ...records[receiptIndex].payload, measurement_sha256: measurement.sha256, input_sha256: measurement.payload.input_sha256, result_sha256: measurement.payload.result_sha256, result: measurement.payload.result };
replaceRecord(receiptIndex, receiptPayload);

const recalculationIndex = records.findIndex((record) => record.record_type === "recalculation_receipt");
const recalculationPayload = { ...records[recalculationIndex].payload, derived_totals_sha256: measurement.payload.result_sha256 };
replaceRecord(recalculationIndex, recalculationPayload);

for (let round = 0; round < 100; round += 1) {
  let changed = false;
  for (let index = 0; index < records.length; index += 1) {
    const record = records[index];
    if (["action_receipt", "observation_receipt"].includes(record.record_type)) continue;
    const payload = replaceMapped(record.payload, replacements);
    if (stable(payload) === stable(record.payload)) continue;
    replaceRecord(index, payload); changed = true;
  }
  if (!changed) break;
  if (round === 99) throw new Error("dependency relink did not converge");
}

records = ordered(records);
let prefix = ordered(records.filter((record) => record.payload.sequence === 0));
let previous = null;
const receipts = records.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type)).sort((left, right) => left.payload.sequence - right.payload.sequence);
for (const oldReceipt of receipts) {
  const group = ordered(records.filter((record) => record.payload.sequence === oldReceipt.payload.sequence));
  const domain = group.filter((record) => !["action_receipt", "observation_receipt"].includes(record.record_type));
  const edited = structuredClone(oldReceipt);
  edited.payload.previous_journal_sha256 = previous;
  edited.payload.pre_universe_sha256 = digest(prefix);
  edited.payload.domain_record_sha256s = domain.map((record) => record.sha256);
  edited.payload.post_domain_universe_sha256 = digest(ordered([...prefix, ...domain]));
  const receipt = rehash(edited);
  records[records.findIndex((record) => record.path === oldReceipt.path)] = receipt;
  prefix = ordered([...prefix, ...domain, receipt]); previous = receipt.sha256;
}

trace.final_record_universe = ordered(records);
trace.final_universe_sha256 = digest(trace.final_record_universe);
trace.final_journal_sha256 = previous;
const summary = {
  mutation: "A2 observations exceed cap and are negative, with measurement arithmetic and all downstream links recomputed",
  forged_lifetime_sha256: forgedLifetime.sha256,
  lifetime: forgedLifetime.payload,
  measurement_sha256: measurement.sha256,
  measurement_result: result,
  final_universe_sha256: trace.final_universe_sha256,
  final_journal_sha256: trace.final_journal_sha256,
};
writeFileSync(artifactPath, `${JSON.stringify(artifact, null, 2)}\n`);
writeFileSync("resource-observation-summary.json", `${JSON.stringify(summary, null, 2)}\n`);
