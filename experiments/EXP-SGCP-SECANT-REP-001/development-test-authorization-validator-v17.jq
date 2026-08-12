def exact_keys($expected):
  (keys | sort) == ($expected | sort);

def uuid_string:
  type == "string"
  and length == 36
  and test("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\z")
  and . != "00000000-0000-0000-0000-000000000000";

def receipt_ok($receipt; $role; $receipt_id; $protocol; $expected):
  ($receipt | type == "object")
  and ($receipt | exact_keys($protocol.review_receipt_schema.exact_keys))
  and ($receipt.id == $receipt_id)
  and ($receipt.experiment_id == $protocol.experiment_id)
  and ($receipt.role == $role)
  and ($receipt.reviewer_principal_kind == "multi_agent_orchestrator_agent_id")
  and ($receipt.reviewer_principal_id | uuid_string)
  and (($protocol.excluded_reviewer_principal_ids
        | index($receipt.reviewer_principal_id)) == null)
  and ($receipt.verdict == "GO")
  and ($receipt.observed_head_sha1 == $expected.protocol_commit_sha1)
  and ($receipt.observed_tree_sha1 == $expected.protocol_tree_sha1)
  and ($receipt.observed_parent_sha1 == $expected.base_commit_sha1)
  and ($receipt.observed_parent_tree_sha1 == $expected.base_tree_sha1)
  and ($receipt.observed_delta == $protocol.review_container.expected_delta)
  and ($receipt.execution_protocol_sha256 == $expected.protocol_sha256)
  and ($receipt.host_runner_sha256 == $expected.host_runner_sha256)
  and ($receipt.authorization_validator_sha256
       == $expected.authorization_validator_sha256)
  and ($receipt.result_validator_sha256
       == $expected.result_validator_sha256)
  and ($receipt.container_runner_sha256 == $expected.container_runner_sha256)
  and ($receipt.protected_source_sha256 == $expected.protected_source_sha256)
  and ($receipt.test_source_sha256 == $expected.test_source_sha256)
  and ($receipt.container_image == $expected.container_image)
  and ($receipt.container_image_id == $expected.container_image_id)
  and ($receipt.ignored_ambient_paths == [])
  and ($receipt.ancestor_sidecars_present == [])
  and ($receipt.cache_paths_present == [])
  and ($receipt.findings == [])
  and ($receipt.findings_sha256
       == "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945");

($protocol | length == 1) and
($decision | length == 1) and
($theory | length == 1) and
($accounting | length == 1) and
($red_team | length == 1) and

($protocol[0].development_test_execution_protocol) as $p |
($decision[0]) as $d |
($theory[0]) as $t |
($accounting[0]) as $a |
($red_team[0]) as $r |

receipt_ok(
  $t;
  "theory";
  $p.review_receipt_schema.ids_by_role.theory;
  $p;
  $expected
) and
receipt_ok(
  $a;
  "accounting";
  $p.review_receipt_schema.ids_by_role.accounting;
  $p;
  $expected
) and
receipt_ok(
  $r;
  "red_team";
  $p.review_receipt_schema.ids_by_role.red_team;
  $p;
  $expected
) and
([$t.reviewer_principal_id, $a.reviewer_principal_id, $r.reviewer_principal_id]
 | unique | length == 3) and

($d | type == "object") and
($d | exact_keys($p.authorization_decision_schema.exact_keys)) and
($d.id == $p.authorization_decision_schema.required_id) and
($d.experiment_id == $p.experiment_id) and
($d.status == "approved_for_one_development_test") and
($d.maximum_runs == 1) and
($d.protocol_commit_sha1 == $expected.protocol_commit_sha1) and
($d.protocol_tree_sha1 == $expected.protocol_tree_sha1) and
($d.execution_protocol_sha256 == $expected.protocol_sha256) and
($d.host_runner_sha256 == $expected.host_runner_sha256) and
($d.authorization_validator_sha256
 == $expected.authorization_validator_sha256) and
($d.result_validator_sha256 == $expected.result_validator_sha256) and
($d.container_runner_sha256 == $expected.container_runner_sha256) and
($d.protected_source_sha256 == $expected.protected_source_sha256) and
($d.test_source_sha256 == $expected.test_source_sha256) and
($d.container_image == $expected.container_image) and
($d.container_image_id == $expected.container_image_id) and
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
($d.run_id == $p.host_runner.run_id) and
($d.run_directory == $p.host_runner.run_directory) and
($d.consumption_ref == $p.host_runner.consumption_ref) and
($d.result_ref == $p.host_runner.result_ref) and
($d.container_name ==
  ($p.host_runner.container_name_prefix + $expected.protocol_commit_sha1)) and
($d.authority == $p.authorization_decision_schema.required_authority) and
($d.interpretation == $p.authorization_decision_schema.required_interpretation)
