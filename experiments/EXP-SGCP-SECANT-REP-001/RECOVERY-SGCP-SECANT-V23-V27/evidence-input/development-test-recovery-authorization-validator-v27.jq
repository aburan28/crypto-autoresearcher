def exact_keys($expected):
  (keys | sort) == ($expected | sort);

def uuid_string:
  type == "string"
  and length == 36
  and test("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\z")
  and . != "00000000-0000-0000-0000-000000000000";

def receipt_ok($receipt; $role; $id; $p; $expected; $excluded):
  ($receipt | type == "object")
  and ($receipt | exact_keys($p.review_receipt_schema.exact_keys))
  and ($receipt.id == $id)
  and ($receipt.experiment_id == $p.experiment_id)
  and ($receipt.role == $role)
  and ($receipt.reviewer_principal_kind == "multi_agent_orchestrator_agent_id")
  and ($receipt.reviewer_principal_id | uuid_string)
  and ($receipt.reviewer_principal_id
       == $p.review_receipt_schema.pinned_principal_ids_by_role[$role])
  and (($excluded | index($receipt.reviewer_principal_id)) == null)
  and ($receipt.verdict == "GO")
  and ($receipt.observed_head_sha1 == $expected.protocol_commit_sha1)
  and ($receipt.observed_tree_sha1 == $expected.protocol_tree_sha1)
  and ($receipt.observed_parent_sha1 == $expected.base_commit_sha1)
  and ($receipt.observed_parent_tree_sha1 == $expected.base_tree_sha1)
  and ($receipt.observed_delta == $p.review_target.expected_delta)
  and ($receipt.execution_protocol_sha256 == $expected.protocol_sha256)
  and ($receipt.host_runner_sha256 == $expected.host_runner_sha256)
  and ($receipt.authorization_validator_sha256
       == $expected.authorization_validator_sha256)
  and ($receipt.result_validator_sha256
       == $expected.result_validator_sha256)
  and ($receipt.source_manifest_sha256 == $expected.source_manifest_sha256)
  and ($receipt.shell_control_runner_sha256
       == $expected.shell_control_runner_sha256)
  and ($receipt.shell_control_receipt_sha256
       == $expected.shell_control_receipt_sha256)
  and ($receipt.source_consumption_commit_sha1
       == $expected.source_consumption_commit_sha1)
  and ($receipt.source_stdout_sha256 == $expected.source_stdout_sha256)
  and ($receipt.findings == [])
  and ($receipt.findings_sha256
       == "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945");

($protocol | length == 1) and
($decision | length == 1) and
($theory | length == 1) and
($accounting | length == 1) and
($red_team | length == 1) and
($excluded_source | length == 1) and

($protocol[0].recovery_protocol) as $p |
($excluded_source[0].development_test_execution_protocol) as $prior |
($decision[0]) as $d |
($theory[0]) as $t |
($accounting[0]) as $a |
($red_team[0]) as $r |
(
  $prior.excluded_reviewer_principal_ids
  + $p.excluded_reviewer_source.appended_principal_ids
) as $excluded |

($p.excluded_reviewer_source.commit_sha1
 == $expected.source_protocol_commit_sha1) and
($p.excluded_reviewer_source.sha256
 == $expected.source_protocol_sha256) and
($prior.id
 == "EXP-SGCP-SECANT-REP-001-DEVELOPMENT-TEST-EXECUTION-PROTOCOL-V23") and
($prior.excluded_reviewer_principal_ids | length == 102) and
($excluded | unique | length == 114) and

receipt_ok(
  $t;
  "theory";
  $p.review_receipt_schema.ids_by_role.theory;
  $p;
  $expected;
  $excluded
) and
receipt_ok(
  $a;
  "accounting";
  $p.review_receipt_schema.ids_by_role.accounting;
  $p;
  $expected;
  $excluded
) and
receipt_ok(
  $r;
  "red_team";
  $p.review_receipt_schema.ids_by_role.red_team;
  $p;
  $expected;
  $excluded
) and
([$t.reviewer_principal_id, $a.reviewer_principal_id, $r.reviewer_principal_id]
 | unique | length == 3) and

($d | type == "object") and
($d | exact_keys($p.authorization_decision_schema.exact_keys)) and
($d.id == $p.authorization_decision_schema.required_id) and
($d.experiment_id == $p.experiment_id) and
($d.status == "approved_for_one_read_only_recovery") and
($d.maximum_runs == 1) and
($d.protocol_commit_sha1 == $expected.protocol_commit_sha1) and
($d.protocol_tree_sha1 == $expected.protocol_tree_sha1) and
($d.execution_protocol_sha256 == $expected.protocol_sha256) and
($d.host_runner_sha256 == $expected.host_runner_sha256) and
($d.authorization_validator_sha256
 == $expected.authorization_validator_sha256) and
($d.result_validator_sha256 == $expected.result_validator_sha256) and
($d.source_manifest_sha256 == $expected.source_manifest_sha256) and
($d.shell_control_runner_sha256
 == $expected.shell_control_runner_sha256) and
($d.shell_control_receipt_sha256
 == $expected.shell_control_receipt_sha256) and
($d.source_protocol_commit_sha1 == $expected.source_protocol_commit_sha1) and
($d.source_authorization_commit_sha1
 == $expected.source_authorization_commit_sha1) and
($d.source_consumption_commit_sha1
 == $expected.source_consumption_commit_sha1) and
($d.source_original_result_ref == $p.source.original_result_ref) and
($d.recovery_consumption_ref == $p.recovery.recovery_consumption_ref) and
($d.recovery_result_ref == $p.recovery.recovery_result_ref) and
($d.recovery_directory == $p.recovery.recovery_directory) and
($d.review_receipt_sha256 == {
  "accounting": $accounting_receipt_sha256,
  "red_team": $red_team_receipt_sha256,
  "theory": $theory_receipt_sha256
}) and
($d.reviewer_principal_ids == {
  "accounting": $a.reviewer_principal_id,
  "red_team": $r.reviewer_principal_id,
  "theory": $t.reviewer_principal_id
}) and
($d.authority == $p.authorization_decision_schema.required_authority) and
($d.interpretation == $p.authorization_decision_schema.required_interpretation)
