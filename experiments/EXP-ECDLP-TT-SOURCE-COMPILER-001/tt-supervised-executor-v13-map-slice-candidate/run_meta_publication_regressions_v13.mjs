import { createHash } from "node:crypto";
import { basename, dirname, join } from "node:path";
import { copyFileSync, lstatSync, mkdirSync, readFileSync, readdirSync, renameSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";

const work = "meta-publication-regressions-v13-work";
const policyPath = "publication-payload-policy-v13.json";

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function reset(path) {
  rmSync(path, { recursive: true, force: true });
  mkdirSync(path, { recursive: true });
}

function removeAppleDouble(path) {
  for (const name of readdirSync(path)) {
    const child = join(path, name);
    if (name.startsWith("._")) {
      rmSync(child, { recursive: true, force: true });
      continue;
    }
    const stat = lstatSync(child);
    if (stat.isDirectory() && !stat.isSymbolicLink()) removeAppleDouble(child);
  }
}

function writeBundle(root, listedPaths) {
  const lines = listedPaths.slice().sort().map((path) => `${sha256(readFileSync(join(root, ...path.split("/"))))}  ./${path}`);
  const manifestBytes = Buffer.from(`${lines.join("\n")}\n`, "utf8");
  writeFileSync(join(root, "SHA256SUMS"), manifestBytes);
  const externalPath = `${root}.sha256`;
  writeFileSync(externalPath, `${sha256(manifestBytes)}  ${basename(root)}/SHA256SUMS\n`);
  return externalPath;
}

function copyRequiredPayloads(root, requiredPaths) {
  for (const path of requiredPaths) {
    const destination = join(root, ...path.split("/"));
    mkdirSync(dirname(destination), { recursive: true });
    copyFileSync(join(...path.split("/")), destination);
  }
}

function run(command, args) {
  const result = spawnSync(command, args, { encoding: "utf8" });
  const lines = result.stdout.trim().split("\n").filter(Boolean);
  if (lines.length !== 1) throw new Error(`invalid command output: ${result.stdout}${result.stderr}`);
  return { ...JSON.parse(lines[0]), exit_code: result.status };
}

function compareDecisions(builderDecision, verifierDecision) {
  if (builderDecision.decision !== verifierDecision.decision || builderDecision.rejection !== verifierDecision.rejection) {
    const error = new Error("DECISION_PARITY_MISMATCH");
    error.code = "DECISION_PARITY_MISMATCH";
    throw error;
  }
  return { decision: builderDecision.decision, rejection: builderDecision.rejection };
}

function injectedParityCase(id, builderDecision, verifierDecision) {
  try {
    compareDecisions(builderDecision, verifierDecision);
    return { id, expected_rejection: "DECISION_PARITY_MISMATCH", observed_rejection: null, pass: false };
  } catch (error) {
    const rejection = error.code || "UNCLASSIFIED_ERROR";
    return { id, expected_rejection: "DECISION_PARITY_MISMATCH", observed_rejection: rejection, pass: rejection === "DECISION_PARITY_MISMATCH", injection: { builderDecision, verifierDecision } };
  }
}

reset(work);
const publicationPolicy = JSON.parse(readFileSync(policyPath, "utf8"));
const requiredPaths = publicationPolicy.required_paths;
const clean = join(work, "clean-bundle");
mkdirSync(clean, { recursive: true });
copyRequiredPayloads(clean, requiredPaths);
const cleanRoot = writeBundle(clean, requiredPaths);
removeAppleDouble(clean);
const cleanDecision = run(process.execPath, ["verify_publication_v13.mjs", clean, cleanRoot]);

const unlisted = join(work, "unlisted-bundle");
mkdirSync(unlisted, { recursive: true });
copyRequiredPayloads(unlisted, requiredPaths);
writeFileSync(join(unlisted, "UNLISTED-PAYLOAD.bin"), "not-in-manifest\n");
const unlistedRoot = writeBundle(unlisted, requiredPaths);
removeAppleDouble(unlisted);
const unlistedDecision = run(process.execPath, ["verify_publication_v13.mjs", unlisted, unlistedRoot]);

const symlinked = join(work, "symlink-bundle");
mkdirSync(symlinked, { recursive: true });
copyRequiredPayloads(symlinked, requiredPaths);
renameSync(join(symlinked, "evidence"), join(symlinked, "real-evidence"));
symlinkSync("real-evidence", join(symlinked, "evidence"), "dir");
const symlinkRoot = writeBundle(symlinked, requiredPaths);
removeAppleDouble(symlinked);
const symlinkDecision = run(process.execPath, ["verify_publication_v13.mjs", symlinked, symlinkRoot]);

const missing = join(work, "missing-required-bundle");
mkdirSync(missing, { recursive: true });
copyRequiredPayloads(missing, requiredPaths);
rmSync(join(missing, "mandatory-regressions-v13.json"));
const missingPaths = requiredPaths.filter((path) => path !== "mandatory-regressions-v13.json");
const missingRoot = writeBundle(missing, missingPaths);
removeAppleDouble(missing);
const missingDecision = run(process.execPath, ["verify_publication_v13.mjs", missing, missingRoot]);

const listedAppleDouble = join(work, "listed-appledouble-bundle");
mkdirSync(listedAppleDouble, { recursive: true });
copyRequiredPayloads(listedAppleDouble, requiredPaths);
writeFileSync(join(listedAppleDouble, "._LISTED-PAYLOAD"), "forbidden-metadata\n");
const listedAppleDoubleRoot = writeBundle(listedAppleDouble, [...requiredPaths, "._LISTED-PAYLOAD"]);
const listedAppleDoubleDecision = run(process.execPath, ["verify_publication_v13.mjs", listedAppleDouble, listedAppleDoubleRoot]);

const mandatory = JSON.parse(readFileSync("mandatory-regressions-v13.json", "utf8"));
mandatory.tests[0].id = "substituted_trivial_control";
const substitutedPath = join(work, "mandatory-regressions-substituted.json");
writeFileSync(substitutedPath, `${JSON.stringify(mandatory, null, 2)}\n`);
const substitutionDecision = run(process.execPath, ["verify_v13_closed_kernel.mjs", "--check-regression-manifest", substitutedPath]);

const results = [
  injectedParityCase("builder_accepts_verifier_rejects", { decision: "ACCEPT", rejection: null }, { decision: "REJECT", rejection: "INJECTED_VERIFIER_REJECTION" }),
  injectedParityCase("verifier_accepts_builder_rejects", { decision: "REJECT", rejection: "INJECTED_BUILDER_REJECTION" }, { decision: "ACCEPT", rejection: null }),
  {
    id: "mandatory_regression_suite_substitution",
    expected_rejection: "PINNED_REGRESSION_SUITE_MISMATCH",
    observed_rejection: substitutionDecision.rejection,
    decision: substitutionDecision,
    pass: substitutionDecision.decision === "REJECT" && substitutionDecision.rejection === "PINNED_REGRESSION_SUITE_MISMATCH",
  },
  {
    id: "unlisted_publication_payload",
    expected_rejection: "PUBLICATION_DIRECTORY_MISMATCH",
    observed_rejection: unlistedDecision.rejection,
    decision: unlistedDecision,
    pass: unlistedDecision.decision === "REJECT" && unlistedDecision.rejection === "PUBLICATION_DIRECTORY_MISMATCH",
  },
  {
    id: "intermediate_evidence_symlink_alias",
    expected_rejection: "EVIDENCE_PATH_COMPONENT_SYMLINK",
    observed_rejection: symlinkDecision.rejection,
    decision: symlinkDecision,
    pass: symlinkDecision.decision === "REJECT" && symlinkDecision.rejection === "EVIDENCE_PATH_COMPONENT_SYMLINK",
  },
  {
    id: "missing_required_publication_payload",
    expected_rejection: "PUBLICATION_REQUIRED_PATHS_MISMATCH",
    observed_rejection: missingDecision.rejection,
    decision: missingDecision,
    pass: missingDecision.decision === "REJECT" && missingDecision.rejection === "PUBLICATION_REQUIRED_PATHS_MISMATCH",
  },
  {
    id: "listed_appledouble_publication_payload",
    expected_rejection: "PUBLICATION_FORBIDDEN_METADATA_PATH",
    observed_rejection: listedAppleDoubleDecision.rejection,
    decision: listedAppleDoubleDecision,
    pass: listedAppleDoubleDecision.decision === "REJECT" && listedAppleDoubleDecision.rejection === "PUBLICATION_FORBIDDEN_METADATA_PATH",
  },
];
const receipt = {
  schema: "tt-supervised-executor-meta-publication-regressions-v13",
  protocol: "EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor/13",
  status: results.every((result) => result.pass) && cleanDecision.decision === "ACCEPT" ? "PASS" : "FAIL",
  evidence_status: ["MODEL-BOUND", "ZERO-RUN"],
  positive_control: { id: "clean_publication_bundle", decision: cleanDecision, pass: cleanDecision.decision === "ACCEPT" },
  case_count: results.length,
  pass_count: results.filter((result) => result.pass).length,
  results,
  byte_snapshots: {
    harness: { path: "run_meta_publication_regressions_v13.mjs", sha256: sha256(readFileSync("run_meta_publication_regressions_v13.mjs")) },
    mandatory_regressions: { path: "mandatory-regressions-v13.json", sha256: sha256(readFileSync("mandatory-regressions-v13.json")) },
    verifier: { path: "verify_v13_closed_kernel.mjs", sha256: sha256(readFileSync("verify_v13_closed_kernel.mjs")) },
    publication_verifier: { path: "verify_publication_v13.mjs", sha256: sha256(readFileSync("verify_publication_v13.mjs")) },
    publication_policy: { path: policyPath, sha256: sha256(readFileSync(policyPath)) },
  },
  limitations: [
    "The two parity cases are fault injections into the comparator, not naturally occurring validator disagreements.",
    "Publication tests copy the complete pinned V13 payload path set into synthetic bundles; the immutable checkpoint itself remains to be staged and frozen.",
    "No runtime or cryptanalytic campaign was executed."
  ]
};
writeFileSync("meta-publication-regressions-v13.json", `${JSON.stringify(receipt, null, 2)}\n`);
process.stdout.write(`${JSON.stringify({ status: receipt.status, receipt: "meta-publication-regressions-v13.json", receipt_sha256: sha256(readFileSync("meta-publication-regressions-v13.json")), cases: results.length, passes: receipt.pass_count, positive_control: receipt.positive_control.pass })}\n`);
if (receipt.status !== "PASS") process.exitCode = 1;
