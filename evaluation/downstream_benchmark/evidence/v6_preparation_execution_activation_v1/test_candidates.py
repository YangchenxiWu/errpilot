"""Non-executing V6 admission and journal tests; all observations are mocks."""
import copy
import unittest

from evaluation.downstream_benchmark.evidence.v6_preparation_execution_activation_v1 import (
    adapter_candidate as a, controller_candidate as c,
)

REJECTIONS = []
POSITIVE = []


class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.descriptor, cls.manifest = a.load_inputs()
        cls.population = a.derive_population(cls.manifest)
        cls.items = cls.population["items"]
        cls.item = cls.items[0]
        cls.authorities = a.loads((a.ROOT / __file__).with_name("authority_candidates.json").read_bytes())
        cls.common = cls.authorities["common_binding"]

    def route_args(self, item=None):
        item = item or self.item
        snapshot = None if item["variant"] == "SOURCE_INDEPENDENT" else {
            "sha256": "0" * 64, "source_revision_sha": item["source_revision_sha"],
            "source": f"snapshots/{item['base_attempt_id']}"}
        proposal = a.engine_call_proposal(self.manifest, item, snapshot=snapshot)
        scopes = c.PERMISSIONS if proposal["network_required"] else (
            x for x in c.PERMISSIONS if x != "BUILD_NETWORK")
        receipts = {x: {"namespace": c.TEST_NAMESPACE, "scope": x,
                        "common_binding_sha256": a.identity(self.common), "HUMAN_PI_ACCEPTED": "YES",
                        "authority_candidate_record_sha256": a.identity(self.authorities["separate_permissions"][x])}
                    for x in scopes}
        return dict(manifest=self.manifest, population=self.population, item=item, receipts=receipts,
                    common_binding=self.common, policy=copy.deepcopy(c.ROUTE_POLICY),
                    runtime_gates={"namespace": c.TEST_NAMESPACE,
                                   "implementation_accepted_frozen_persisted_committed": True,
                                   "remote_publication_verified": True, "clean_committed_head": True,
                                   "exact_execution_descriptor_pin_and_full_chain": True,
                                   "source_objects_present": True, "base_runtime_verified_without_pull": True,
                                   "restricted_default_build_network_verified": proposal["network_required"],
                                   "persistent_output_binding_accepted": True},
                    sentinel=c.ReviewSentinel(), snapshot=snapshot)

    def reject(self, name, callback):
        with self.subTest(name=name):
            try:
                callback()
            except a.Rejected as exc:
                REJECTIONS.append({"name": name, "result": "PASS", "reason": str(exc)})
            else:
                self.fail("accepted forbidden candidate: " + name)

    def test_exact_population_and_all_shared_engine_proposals(self):
        self.assertEqual(self.population["counts"], {
            "SOURCE_INDEPENDENT": 221, "BUGGY": 210, "FIXED": 210,
            "dispatchable_cases": 431, "blocked_cases": 2, "total_base_attempts": 641})
        self.assertEqual(a.canonical(self.population), a.canonical(a.derive_population(self.manifest)))
        networks, source_reuse, engine_sha = 0, 0, []
        for item in self.items:
            args = self.route_args(item)
            result = c.review_route(**args)
            self.assertFalse(result["engine_called"])
            self.assertFalse(result["source_exported"])
            self.assertFalse(result["attempt_consumed"])
            proposal = args["sentinel"].calls[0]
            engine_sha.append(proposal["dockerfile_sha256"])
            networks += proposal["network_required"]
            self.assertEqual(proposal["single_identity"], True)
            if item["variant"] != "SOURCE_INDEPENDENT":
                fn = c.source_function_candidate(self.manifest, item)
                self.assertIs(fn.__code__, c.snapshots.source_snapshot_identity.__code__)
                source_reuse += 1
        self.assertEqual(source_reuse, 420)
        self.assertEqual(networks, 583)
        POSITIVE.append({"name": "all_641_items_reach_only_nonexecuting_sentinel", "result": "PASS",
                         "network_required_work_items": networks, "shared_source_code_bindings": source_reuse,
                         "ordered_dockerfile_sha256_list_sha256": a.identity(engine_sha)})

    def test_entry_selection_and_input_rejections(self):
        self.reject("wrong_current_descriptor", lambda: a.load_inputs(current_sha="0" * 64))
        self.reject("wrong_manifest_sha", lambda: a.load_inputs(manifest_sha="0" * 64))
        self.reject("wrong_manifest_path_latest_fallback", lambda: a.load_inputs(manifest_path="latest"))
        for ordinal in (67, 121):
            p = self.manifest["plans"][ordinal - 1]
            self.reject("blocked_case_" + p["case_id"], lambda p=p: a.select(
                self.manifest, ordinal=p["census_order"], case_id=p["case_id"], plan_sha=p["plan_sha256"]))
        self.reject("wrong_ordinal", lambda: a.select(self.manifest, ordinal=2,
                    case_id=self.item["case_id"], plan_sha=self.item["plan_sha256"]))
        self.reject("ordinal_bool_type", lambda: a.select(self.manifest, ordinal=True,
                    case_id=self.item["case_id"], plan_sha=self.item["plan_sha256"]))
        self.reject("wrong_plan_sha", lambda: a.select(self.manifest, ordinal=1,
                    case_id=self.item["case_id"], plan_sha="0" * 64))
        def mutate_manifest(name, mutation):
            altered = copy.deepcopy(self.manifest)
            mutation(altered)
            self.reject(name, lambda: a.validate_manifest(altered))
        mutate_manifest("reordered_case", lambda m: m["plans"].reverse())
        mutate_manifest("stale_recipe", lambda m: m["plans"][0]["recipe_candidate"].__setitem__("setup_sha256", "0" * 64))
        mutate_manifest("hidden_recipe_mutation", lambda m: m["plans"][0]["recipe_candidate"].__setitem__("rescue", True))
        mutate_manifest("setup_normalization", lambda m: m["plans"][0]["recipe_candidate"]["setup_actions"][0].__setitem__("exact_source_text", "pip install Cython"))
        def wrong_item(key, value):
            item = {**self.item, key: value}
            return a.engine_call_proposal(self.manifest, item, snapshot=self.route_args()["snapshot"])
        self.reject("wrong_revision", lambda: wrong_item("source_revision_sha", "0" * 40))
        self.reject("wrong_variant", lambda: wrong_item("variant", "SOURCE_INDEPENDENT"))
        altered = copy.deepcopy(self.population)
        altered["items"].append(copy.deepcopy(altered["items"][0]))
        self.reject("duplicate_work_item", lambda: a.validate_population(self.manifest, altered))
        self.reject("real_dispatch_candidate_only", c.real_dispatch)
        self.reject("retry_without_authority", c.request_retry)

    def test_authority_policy_and_publication_rejections(self):
        for permission in c.PERMISSIONS:
            args = self.route_args()
            args["receipts"].pop(permission)
            self.reject("missing_" + permission.lower() + "_authority", lambda args=args: c.review_route(**args))
        args = self.route_args()
        args["receipts"] = {"predecessor_token": a.shared.EXPANSION_03_AUTHORITY_TOKEN}
        self.reject("predecessor_block_03_token", lambda: c.review_route(**args))
        args = self.route_args()
        args["receipts"]["IMAGE_BUILD"]["HUMAN_PI_ACCEPTED"] = "NO"
        self.reject("unaccepted_candidate_permission", lambda: c.review_route(**args))
        args = self.route_args()
        args["common_binding"] = {**self.common, "entry_current_descriptor": {"path": a.CURRENT, "sha256": "0" * 64}}
        self.reject("wrong_runtime_descriptor_binding", lambda: c.review_route(**args))
        args = self.route_args()
        args["receipts"]["BUILD_NETWORK"]["authority_candidate_record_sha256"] = "0" * 64
        self.reject("wrong_independent_authority_scope_sha", lambda: c.review_route(**args))
        for name, key, value in (
            ("source_acquisition_attempt", "source_acquisition", True),
            ("oracle_execution", "oracle_execution", True),
            ("stop_at_capacity_behavior", "stop_at_capacity", True),
            ("governed_chunk_batch_semantics", "governed_batches", True),
            ("chunk_membership_authority", "runtime_chunk_membership_authority", "V6_BATCH"),
            ("chunk_stopping_authority", "runtime_chunk_stopping_authority", "CAPACITY"),
            ("latest_selector", "fallback", "latest"),
            ("mtime_selector", "fallback", "mtime"),
            ("lexical_selector", "fallback", "lexical"),
            ("directory_scan_selector", "fallback", "directory_scan"),
            ("automatic_retry", "automatic_retry", True),
            ("silent_rescue", "automatic_rescue", True),
        ):
            args = self.route_args()
            args["policy"][key] = value
            self.reject(name, lambda args=args: c.review_route(**args))
        for key in ("remote_publication_verified", "clean_committed_head", "source_objects_present",
                    "base_runtime_verified_without_pull", "restricted_default_build_network_verified",
                    "exact_execution_descriptor_pin_and_full_chain"):
            args = self.route_args()
            args["runtime_gates"][key] = False
            self.reject("missing_" + key, lambda args=args: c.review_route(**args))
        args = self.route_args()
        args["prior_claims"] = [self.item["base_attempt_id"]]
        self.reject("repeated_base_attempt_at_dispatch", lambda: c.review_route(**args))
        args = self.route_args()
        args["sentinel"] = a.shared._materialize_checked
        self.reject("real_engine_as_sentinel", lambda: c.review_route(**args))

    def test_once_only_terminal_no_overwrite(self):
        initial = c.ledger_template(self.population)
        c.validate_journal(initial, self.population)
        self.assertFalse(any(x["attempt_consumed"] for x in initial["entries"]))
        def append(ledger, **kwargs):
            return c.append_test_event(ledger, self.population, self.item,
                                       namespace=c.TEST_NAMESPACE, **kwargs)
        claim = append(initial, operation="CLAIM")
        self.reject("repeated_base_attempt_claim", lambda: append(claim, operation="CLAIM"))
        self.reject("terminal_without_claim", lambda: append(initial, operation="TERMINAL", state="BUILD_FAILED", reason="mock failure"))
        self.reject("materialized_without_evidence", lambda: append(claim, operation="TERMINAL", state="MATERIALIZED"))
        for status in ("BUILD_FAILED", "BLOCKED_INPUT_IDENTITY", "INTERRUPTED", "MATERIALIZED"):
            terminal = append(claim, operation="TERMINAL", state=status,
                              reason="mock first-pass observation",
                              evidence={x: "0" * 64 for x in c.REQUIRED_SUCCESS_EVIDENCE} if status == "MATERIALIZED" else {})
            self.reject("successful_overwrite_" + status, lambda terminal=terminal: append(
                terminal, operation="TERMINAL", state="MATERIALIZED",
                evidence={x: "0" * 64 for x in c.REQUIRED_SUCCESS_EVIDENCE}))
            self.reject("retry_claim_after_" + status, lambda terminal=terminal: append(terminal, operation="CLAIM"))
        altered = copy.deepcopy(claim)
        altered["journal"][0]["prior_event_sha256"] = "0" * 64
        self.reject("ledger_lineage_drift", lambda: c.validate_journal(altered, self.population))
        self.assertEqual(initial["journal"], [])
        POSITIVE.append({"name": "unstarted_to_unique_terminal_fixture_and_original_template_unchanged", "result": "PASS"})


if __name__ == "__main__":
    unittest.main()
