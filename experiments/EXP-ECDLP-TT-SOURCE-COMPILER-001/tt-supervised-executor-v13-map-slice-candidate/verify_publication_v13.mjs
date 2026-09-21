import { createHash } from "node:crypto";
import { lstatSync, readFileSync, readdirSync } from "node:fs";
import { basename, isAbsolute, join, posix, relative, resolve, sep } from "node:path";

const policyName = "publication-payload-policy-v13.json";
const policyExpectedSha256 = "48a1ff20c1d919440f4a201a9b30d336d765565721213019acf236e9d9cabfee";

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function reject(code, detail = "") {
  const error = new Error(`${code}${detail ? `: ${detail}` : ""}`);
  error.code = code;
  throw error;
}

function exactKeys(value, keys, code) {
  if (value === null || typeof value !== "object" || Array.isArray(value) || JSON.stringify(Object.keys(value).sort()) !== JSON.stringify([...keys].sort())) reject(code);
}

function inspectPolicyPath(path) {
  const parts = path.split("/");
  if (parts.some((part) => part.startsWith("._") || part === ".DS_Store")) reject("PUBLICATION_FORBIDDEN_METADATA_PATH", path);
  if (parts.some((part) => part.endsWith("-work"))) reject("PUBLICATION_EXCLUDED_PATH", path);
}

function readPolicy(root) {
  inspectComponents(root, policyName, "file");
  const policyBytes = readFileSync(join(root, policyName));
  const observed = sha256(policyBytes);
  if (observed !== policyExpectedSha256) reject("PUBLICATION_POLICY_DIGEST_MISMATCH", observed);
  let policy;
  try {
    policy = JSON.parse(policyBytes.toString("utf8"));
  } catch {
    reject("PUBLICATION_POLICY_MALFORMED");
  }
  exactKeys(policy, ["schema", "protocol", "status", "required_payload_count", "required_paths", "excluded_path_rule", "forbidden_metadata_rule"], "PUBLICATION_POLICY_SCHEMA_MISMATCH");
  if (policy.schema !== "tt-supervised-executor-publication-payload-policy-v13" || policy.protocol !== "EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor/13" || policy.status !== "PINNED") reject("PUBLICATION_POLICY_IDENTITY_MISMATCH");
  if (!Array.isArray(policy.required_paths) || !Number.isSafeInteger(policy.required_payload_count) || policy.required_payload_count !== policy.required_paths.length) reject("PUBLICATION_POLICY_COUNT_MISMATCH");
  if (new Set(policy.required_paths).size !== policy.required_paths.length || JSON.stringify(policy.required_paths) !== JSON.stringify([...policy.required_paths].sort()) || !policy.required_paths.includes(policyName)) reject("PUBLICATION_POLICY_PATH_SET_INVALID");
  if (policy.excluded_path_rule !== "reject_any_path_component_ending_-work" || policy.forbidden_metadata_rule !== "reject_any_path_component_named_.DS_Store_or_starting._") reject("PUBLICATION_POLICY_RULE_MISMATCH");
  for (const path of policy.required_paths) {
    const canonical = typeof path === "string" && path.length > 0 && !path.includes("\\") && !posix.isAbsolute(path) && posix.normalize(path) === path && path !== "." && !path.startsWith("../") && !path.includes("//") && path !== "SHA256SUMS";
    if (!canonical) reject("PUBLICATION_POLICY_PATH_NONCANONICAL", String(path));
    inspectPolicyPath(path);
  }
  return { policy, sha256: observed };
}

function parseRoot(bytes) {
  const text = bytes.toString("utf8");
  const match = /^([0-9a-f]{64})  ([^\r\n]+)\n$/.exec(text);
  if (!match) reject("PUBLICATION_ROOT_MALFORMED");
  return { sha256: match[1], target: match[2] };
}

function parseManifest(bytes) {
  const text = bytes.toString("utf8");
  if (!text.endsWith("\n")) reject("PUBLICATION_MANIFEST_MALFORMED", "missing final newline");
  const lines = text.slice(0, -1).split("\n");
  if (lines.length === 0 || lines.some((line) => line.length === 0)) reject("PUBLICATION_MANIFEST_MALFORMED", "empty entry");
  return lines.map((line) => {
    const match = /^([0-9a-f]{64})  \.\/([^\r\n]+)$/.exec(line);
    if (!match) reject("PUBLICATION_MANIFEST_MALFORMED", line);
    const path = match[2];
    if (path.includes("\\") || posix.isAbsolute(path) || posix.normalize(path) !== path || path === "." || path.startsWith("../") || path.includes("//")) reject("PUBLICATION_PATH_NONCANONICAL", path);
    return { sha256: match[1], path };
  });
}

function inspectComponents(root, relativePath, finalKind) {
  let current = root;
  const components = relativePath.split("/");
  for (let index = 0; index < components.length; index += 1) {
    current = join(current, components[index]);
    const stat = lstatSync(current);
    if (stat.isSymbolicLink()) reject("EVIDENCE_PATH_COMPONENT_SYMLINK", relativePath);
    if (index < components.length - 1 && !stat.isDirectory()) reject("PUBLICATION_PATH_COMPONENT_NOT_DIRECTORY", relativePath);
    if (index === components.length - 1 && finalKind === "file" && !stat.isFile()) reject("PUBLICATION_PAYLOAD_NOT_REGULAR_FILE", relativePath);
  }
}

function walk(root, current = root, output = []) {
  for (const name of readdirSync(current).sort()) {
    const path = join(current, name);
    const stat = lstatSync(path);
    const relativePath = relative(root, path).split(sep).join("/");
    if (stat.isSymbolicLink()) reject("EVIDENCE_PATH_COMPONENT_SYMLINK", relativePath);
    if (stat.isDirectory()) walk(root, path, output);
    else if (stat.isFile()) output.push(relativePath);
    else reject("PUBLICATION_PAYLOAD_NOT_REGULAR_FILE", relativePath);
  }
  return output;
}

function verify(rootArgument, externalRootArgument) {
  const root = resolve(rootArgument);
  const externalRoot = resolve(externalRootArgument);
  if (!isAbsolute(root) || !lstatSync(root).isDirectory() || lstatSync(root).isSymbolicLink()) reject("PUBLICATION_ROOT_NOT_DIRECTORY");
  if (!lstatSync(externalRoot).isFile() || lstatSync(externalRoot).isSymbolicLink()) reject("PUBLICATION_EXTERNAL_ROOT_NOT_REGULAR_FILE");
  const rootEntry = parseRoot(readFileSync(externalRoot));
  const expectedTarget = `${basename(root)}/SHA256SUMS`;
  if (rootEntry.target !== expectedTarget) reject("PUBLICATION_ROOT_TARGET_MISMATCH", rootEntry.target);
  inspectComponents(root, "SHA256SUMS", "file");
  const policyRecord = readPolicy(root);
  const manifestBytes = readFileSync(join(root, "SHA256SUMS"));
  if (sha256(manifestBytes) !== rootEntry.sha256) reject("PUBLICATION_ROOT_DIGEST_MISMATCH");
  const entries = parseManifest(manifestBytes);
  const listed = entries.map((entry) => entry.path);
  if (new Set(listed).size !== listed.length) reject("PUBLICATION_MANIFEST_DUPLICATE_PATH");
  if (listed.includes("SHA256SUMS")) reject("PUBLICATION_MANIFEST_SELF_REFERENCE");
  for (const entry of entries) {
    inspectPolicyPath(entry.path);
    inspectComponents(root, entry.path, "file");
  }
  const required = policyRecord.policy.required_paths;
  if (listed.length !== policyRecord.policy.required_payload_count || JSON.stringify([...listed].sort()) !== JSON.stringify(required)) reject("PUBLICATION_REQUIRED_PATHS_MISMATCH", JSON.stringify({ listed: listed.length, required: required.length }));
  const actual = walk(root).filter((path) => path !== "SHA256SUMS").sort();
  for (const path of actual) inspectPolicyPath(path);
  const expected = [...listed].sort();
  if (JSON.stringify(actual) !== JSON.stringify(expected)) reject("PUBLICATION_DIRECTORY_MISMATCH", JSON.stringify({ actual, expected }));
  for (const entry of entries) {
    const observed = sha256(readFileSync(join(root, ...entry.path.split("/"))));
    if (observed !== entry.sha256) reject("PUBLICATION_PAYLOAD_DIGEST_MISMATCH", entry.path);
  }
  return {
    decision: "ACCEPT",
    rejection: null,
    root,
    external_root: externalRoot,
    manifest_sha256: rootEntry.sha256,
    payload_count: entries.length,
    policy_sha256: policyRecord.sha256,
    required_payload_count: policyRecord.policy.required_payload_count,
  };
}

try {
  const result = verify(process.argv[2], process.argv[3]);
  process.stdout.write(`${JSON.stringify(result)}\n`);
} catch (error) {
  process.stdout.write(`${JSON.stringify({ decision: "REJECT", rejection: error.code || "UNCLASSIFIED_ERROR", detail: error.message })}\n`);
  process.exitCode = 2;
}
