"""Write independent dispositions; never changes audited material."""
from pathlib import Path
from .audit_inventory import HERE,C,QUAL,REPO,read,write,ident

def ref(name,line=None):
 path=C/name
 return {'path':str(path),**ident(path),**({'line':line} if line else {})}
def own(name):return {'path':str(HERE/name),**ident(HERE/name)}

f01={
 'status':'ORIGINAL_DOTDOT_EXPLOIT_REJECTED_BUT_FULL_F01_CLOSURE_BLOCKED',
 'original_exploit':'Historical isolation_reproduction.json used QUALIFICATION_ROOT/../../../../errpilot/... to create claims and terminals outside its declared root. Exact retargeted spelling is now rejected by normal Authority.synthetic before any I/O.',
 'independent_checks':own('independent_F01_probes.json'),
 'source_reviews':[ref('qualification_io.py',22),ref('qualification_io.py',75),ref('qualification_io.py',150),ref('qualification_io.py',171),ref('production_provider_remediated_candidate.py',137),ref('production_provider_remediated_candidate.py',506)],
 'mechanisms':{'canonical_spelling':'Rejects dot/dotdot, empty components, relative and outside paths. Path.resolve adds a symlink alias check.','root_identity':'Fixture parent must equal qualification_root; scope anchor pins device/inode. Caller-supplied outside roots cannot become authority.','traversal':'Absolute componentwise O_DIRECTORY|O_NOFOLLOW traversal, dirfd-relative leaf operations and macOS F_GETPATH verification.','exclusive_publication':'O_EXCL on raw/receipt/association/claim leaves; terminal uses exclusive os.link.','protected_paths':'ConfinedPath and fs(authority) route claims, terminal, lock, raw, receipt, association and synthetic scientific outputs through candidate I/O.','legitimate_nested':'Existing nested result independently read; actual write supported by sealed run_4 trace/source/output, not repeated by audit.'},
 'counterexample_coverage':{'direct_parent':'independently rejected','nested_traversal':'independently rejected','absolute_outside':'independently rejected','intermediate_symlink':'existing sealed symlink independently rejected read-only','outside_symlink_target':'existing sealed outbound leaves independently rejected without reading target','dangling_symlink':'existing sealed dangling path independently rejected','path_alias':'independently rejected','replacement_between_validation_and_write':'three sealed controlled replacement probes inspected; after-final-check relocation remains unresolved','claim_terminal_receipt_raw_association_escape':'sealed real methods reviewed, all corresponding existing symlink paths rejected independently read-only'},
 'remaining_limitation':'No atomic relationship between final F_GETPATH and os.open/os.write/os.link. A held directory can move after the name check. File creation occurs before the new fd name check and can leave an empty artifact; terminal linking has no subsequent confinement check.',
 'independent_OS_evidence':own('relocation_primitive_probe.json'),
 'threat_model_disposition':'Separate Human-PI authority decision required. The proposed V3 F01_limit exclusion is candidate-only, HUMAN_PI_ACCEPTED=NO; the construction request required rejection or demonstrated confinement of TOCTOU redirection. No accepted waiver found. Treat unresolved mandatory invariant as MATERIAL assurance failure.',
 'candidate_constructor_race_executed':False,
 'boundary':'No candidate operation was redirected into an audit-owned alternative root. No existing qualification files were created, renamed, rewritten or deleted.'}
write('F01_root_confinement_reaudit.json',f01)

write('F02_endpoint_correlation_reaudit.json',{
 'status':'ORIGINAL_F02_FIXED_IN_EXACT_CANDIDATE_SOURCE_AND_SYNTHETIC_EVIDENCE',
 'sources':[ref('socket_endpoint_binding.py',51),ref('production_provider_remediated_candidate.py',997),ref('production_provider_remediated_candidate.py',1049)],
 'independent_probes':own('independent_F02_probes.json'),
 'preclaim_call_chain':'ProductionController.claim -> ReceiptBoundLedger.claim -> permit.revalidate -> prepare(PRECLAIM) -> Authority.observe -> verify_raw_security -> verify_clients -> verify_endpoint_binding; before association/lock/claim publication.',
 'provider_call_chain':'ProductionProvider constructor, execute_synthetic/execute, and build -> verify_claim -> Authority.observe(PROVIDER_PREBUILD) -> mandatory verify_raw_security chain; before solve.',
 'original_contradiction':'Connected inode 3697 with actual Path /tmp/unknown-control.sock versus claimed unix:///run/buildkit/buildkitd.sock rejects with F02 actual socket Path/endpoint conflict.',
 'covered_relations':['single observed connected inode mapping','Protocol/Type/Flags/State','actual Path versus strictly normalized endpoint','session/process identity and proof original bytes/SHA','principal and independently observed namespace','complete census and connected inode multiset','independent endpoint-access body bound to observed access identity'],
 'anonymous_socket':'Empty actual Path remains empty. Independent pathless flag, peer endpoint and exact full session/socket provenance body are mandatory. Passing sealed pathless fixture was independently reverified.',
 'optional_parameters':'synthetic/accepted_principals/stage do not disable endpoint binding; V3 contract name is mandatory in SECURITY_CONTRACT_NAMES.',
 'independent_execution_limit':'Pure gate calls independently run at both stage values. Entire write-capable preclaim/prebuild flows reviewed in sealed run_4; not claimed as freshly rerun.',
 'preclaim_new_real_attempts':0,'unauthorized_builds':0,'historical_execs':'ORIGIN_NOT_ESTABLISHED','real_world_authorization_inferred':False,'real_observer':'ABSENT; future separate acceptance required'})

write('F03_test_semantics_reaudit.json',{
 'status':'ORIGINAL_F03_FIXED','field':'client_evidence.sessions[0].authenticated_source',
 'source':ref('socket_endpoint_binding.py',44),'test_source':ref('remediation_regressions.py',93),
 'Boolean_false':{'category':'runtime_authority_false','reason':'F03 client authenticated_source authority false'},
 'integer_zero':{'category':'runtime_authority_integer_zero','reason':'F03 client authenticated_source exact Boolean type required'},
 'independent_probes':own('independent_F03_probes.json'),'final_source_bytes_verified':True,
 'obsolete_V1_field_reintroduced':False,'synthetic_receipt_runtime_authority_false':'Correct and preserved; not the failing authority leaf.',
 'inherited_126_names_preserved':True,'mandatory_category_drop':False})

write('receipt_association_audit.json',{
 'status':'PASS_SOURCE_AND_RETAINED_BYTE_BINDINGS_WITH_DECLARED_DURABILITY_LIMIT',
 'source_reviews':[ref('production_provider_remediated_candidate.py',464),ref('production_provider_remediated_candidate.py',534),ref('production_provider_remediated_candidate.py',561),ref('production_provider_remediated_candidate.py',592),ref('production_provider_remediated_candidate.py',1119),ref('production_provider_remediated_candidate.py',1164)],
 'independent_readback':own('independent_receipt_probes.json'),
 'invariants':{'receipt':'Exact canonical field set and canonical bytes compared to regenerated expected attempt/work/source/effectivity/projection/client identity.','claim':'Immutable original raw and receipt association completed/fsynced/read back before lock; exclusive claim contains exact receipt and association SHAs.','provider':'Durable claim bytes/state, both original raw observations, receipt, association fields, approved principals and fresh prebuild projection independently checked.','NONE':'No receipt bytes; null receipt SHA in claim/association; exact null behavior reverified.','terminal':'Exact claim digest, owner lock and state checked; immutable hardlink publication. Publication failure is outside provider catch, preventing second terminal attempt.','reentry':'Existing claim/terminal/orphan/partial evidence blocks new attempt; no reclaim or automatic retry.','incomplete_sidecar':'Orphan preclaim directory blocks new claim; missing/corrupt association rejects provider before build.'},
 'terminal_cases':['RESTRICTED MATERIALIZED','NONE MATERIALIZED','provider RAISE INTERRUPTED'],
 'fresh_full_E2E':False,'source_fault_scope':'10 crash boundaries and four empty-write faults inspected at actual final synthetic methods; PHYSICAL_POWER_LOSS_DURABILITY_NOT_ESTABLISHED',
 'uncovered_relocation':'F01 affects underlying synthetic I/O confinement; no acceptance of its exclusion.'})

findings=[{
 'ID':'R01','SEVERITY':'MATERIAL','SOURCE_PATH':str(C/'qualification_io.py'),'FUNCTION_OR_FIELD':'QualificationIO.exclusive_write / atomic_publish; V3 F01_limit',
 'TITLE':'Full F01 closure relies on an unaccepted directory-relocation exclusion',
 'EXACT_EVIDENCE':{'source':[ref('qualification_io.py',150),ref('qualification_io.py',171),ref('client_socket_endpoint_binding_contract_v3_candidate.json',3),ref('raw_human_pi_request.txt',311)],'audit_probe':own('relocation_primitive_probe.json'),'construction_probes':ref('additional_security_regressions.py',58)},
 'REPRODUCTION_RESULT':'Original traversal attack is rejected. Exact candidate full-race constructor execution was not attempted because its guarded root is sealed. Two independent Darwin primitive probes, all within the new audit namespace, show current euid 501 can rename its owned open directory after F_GETPATH and then create an empty file or publish a hardlink via its still-held dirfd. This is an OS mechanism reproduction, not a candidate-constructor exploit. Source ordering exposes the same unguarded intervals.',
 'CONSEQUENCE':'Mandatory protected-write containment/check-use assurance remains unsupported. Post-open checking can detect a relocation only after a reserved file exists; terminal link may publish after the last name check. The label privileged is not an established root-only boundary: observed qualification parents are owned by uid 501 with owner write/search permissions.',
 'DISPOSITION':'BLOCK F01 full closure. Human-PI must explicitly adjudicate the filesystem attacker/relocation threat model, or authorize a separate candidate remediation and adversarial test boundary. The candidate-only V3 exclusion is not authority. No waiver inferred and no candidate changed.'
},{
 'ID':'R02','SEVERITY':'MINOR','SOURCE_PATH':str(C/'package_final_candidate.py'),'FUNCTION_OR_FIELD':'qualification -> F01_replace_component_before_open.fixture_root',
 'TITLE':'One aggregated F01 record names the run directory instead of its actual fixture',
 'EXACT_EVIDENCE':{'source':ref('package_final_candidate.py',83),'record':ref('rejection_matrix.json'),'raw_probe':ref('construction_history/qualification_run_4/root_confinement_regressions.json'),'actual_fixture':str(QUAL/'run_4/fixture_76')},
 'REPRODUCTION_RESULT':'Recorded fixture_root ends in run_4, while before/after keys and mutation trace concern fixture_76. The sealed legitimate/nested output and mutable/retained_mutable/owned_redirect symlinks resolve the actual fixture. All recorded bytes and source hashes remain intact.',
 'CONSEQUENCE':'Consumers resolving this category inventory relative to recorded fixture_root locate the wrong paths; the exact fixture identity needs the raw regression evidence. This does not negate its recorded no-follow rejection.',
 'DISPOSITION':'Record the locator defect; correct only in a separately authorized successor or erratum. Existing sealed candidate preserved.'
}]
write('findings.json',{'status':'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_BLOCKED','counts':{'MATERIAL':1,'MINOR':1,'OPTIONAL':0},'original_findings':{'F01':'Original lexical exploit fixed; full mandated race-confinement closure blocked by R01','F02':'Fixed at source/pure verifier and sealed preclaim/prebuild boundaries','F03':'Precise Boolean-versus-integer semantics fixed'},'findings':findings,'fixes_performed':False})

write('validation_results.json',{
 'STATUS':'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_BLOCKED',
 'TRANSACTION':'INDEPENDENT_REMEDIATION_REAUDIT_ONLY',
 'HUMAN_PI_ACCEPTED':'NO','candidate_only':True,'runtime_effective':'NO','execute_now':False,
 'gates':{'A_entry_canonical':'PASS','B_1780_file_integrity':'PASS','C_final_source_SHAs':'PASS','D_F01_original_exploit':'REJECTED; FULL_CLOSURE_BLOCKED_R01','E_F02_original_exploit':'FIXED_WITH_STATED_EXECUTION_SCOPE','F_F03':'PASS','G_receipt_sidecar_once_only':'PASS_SOURCE_AND_RETAINED_EVIDENCE','H_crash_partial_write':'SOURCE_LEVEL_FAULT_INJECTION_PASS_REVIEWED_ONLY','I_source_isolation':'PASS_WITH_F01_LIMIT','J_188_and_A_X':'PASS_RECORDED_COVERAGE_WITH_MINOR_R02','K_641_replay':'PASS_IMPLEMENTATION_EQUIVALENCE_ONLY','L_graph':'PASS_11_18_739','M_synthetic_inventory':'PASS_4089_FILES_3081_DIRECTORIES_40_SYMLINKS','N_findings':'1_MATERIAL_1_MINOR_0_OPTIONAL','O_audit_seal':'REQUIRED_SEPARATE_FINAL_READBACK','P_preservation':'REQUIRED_EXIT_COMPARISON','Q_production_gates':'REMAIN_CLOSED'},
 'unsupported_assertion':'Full F01 confinement including relevant check/use races without accepted relocation exclusion.',
 'recommended_next_action':'Human-PI adjudicate R01 before any acceptance or separately authorize bounded successor remediation; preserve this blocked audit and the exact candidate.',
 'next_production_gate_authorized':False,'PHYSICAL_POWER_LOSS_DURABILITY_NOT_ESTABLISHED':True,
 'audit_harness_failure':'Initial process guard blocked the owning adapter read-only git cat-file call. Preserved failure and source revision; allowed exact argv only and final offline probes passed.'})

request=Path('/Users/wuyangchenxi/.codex/attachments/f8b0d850-5553-4b4b-89af-28a39896a0a3/已粘贴的文本.txt')
with (HERE/'raw_user_request.txt').open('xb') as stream:stream.write(request.read_bytes())

write('commands_run.json',{'record_basis':'Tool invocations in this audit plus reviewed script source; no constructor command log was relabeled as independently executed.',
 'commands':[
 {'command':'pwd; repository/ancestor AGENTS.md and .airos/current_state.md existence checks; scoped source listings','kind':'read-only discovery','result':'No on-disk AGENTS.md or .airos/current_state.md found; pasted global instructions and attached transaction applied'},
 {'command':'rg --files -g AGENTS.md -g !node_modules -g !.git /Users/wuyangchenxi','kind':'read-only initial instruction discovery','result':'Over-broad filename scan interrupted with Ctrl-C; no file contents or mutations'},
 {'command':'git status --porcelain=v1; git branch --show-current; git rev-parse HEAD; git ls-files','kind':'read-only entry','result':'main / e492d159daf188323efcfe121aa019d5b098bfb2; eight existing untracked evidence namespaces'},
 {'command':'git ls-remote --exit-code origin refs/heads/main','attempt':1,'exit_code':128,'result':'Sandbox DNS failure'},
 {'command':'git ls-remote --exit-code origin refs/heads/main','attempt':2,'context':'approved read-only network escalation','exit_code':0,'result':'e492d159daf188323efcfe121aa019d5b098bfb2 refs/heads/main'},
 {'command':'cat attached request; sed/cat source and contract ranges; Python strict-JSON summaries; rg threat/relocation/F01 references','kind':'read-only source and evidence inspection','files':'Final controller/provider, qualification_io, socket_endpoint_binding, qualifier/regressions/package builder/scientific qualifier, original independent findings/isolation reproduction, ledger/adapter, Human-PI request/decision and V2/V3 contracts; exact reviewed references in domain reports'},
 {'command':'.venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_remediation_independent_reaudit_v1.audit_inventory','exit_code':0,'result':'All eight inventories, persistent outputs and tracked/index baseline measured'},
 {'command':'.venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_remediation_independent_reaudit_v1.audit_probes','attempt':1,'exit_code':1,'result':'AUDIT_HARNESS_GUARD_STOP at read-only git cat-file; first four probe reports retained'},
 {'command':'.venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_remediation_independent_reaudit_v1.audit_probes','attempt':2,'exit_code':0,'result':'9 F01 lexical/factory checks, 16 existing symlink checks, legitimate nested read, 76 F02 negative stage calls, reconstructed original contradiction twice, four F03 calls, pathless positive, 3 terminal/association readbacks, 641 exact pure replays'},
 {'command':'git cat-file blob 5c007fbfbfc5b3529105a14f87127f50e1eab6d7:evaluation/downstream_benchmark/v6_current_state.json','kind':'owning adapter invoked this exact read-only command during pure scientific replay','result':'Accepted planning baseline byte pin verified; no Git write'},
 {'command':'.venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_remediation_independent_reaudit_v1.audit_review','exit_code':0,'result':'Strict seal/text/AST, 188 records and both A-X, 14 final fault traces/output inventories, 739 graph references, preserved contracts and source history'},
 {'command':'.venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_remediation_independent_reaudit_v1.audit_relocation_primitives','exit_code':0,'result':'2 same-owner Darwin syscall probes wholly inside new audit namespace; no candidate protected-write invocation'},
 {'command':'apply_patch and exclusive Python report writes','kind':'authorized new audit namespace only','result':'No candidate, predecessor, tracked file or existing output edited'},
 {'command':'.venv/bin/python -B -m evaluation.downstream_benchmark.evidence.v6_production_runtime_topology_stability_successor_remediation_independent_reaudit_v1.assemble_report','kind':'report assembly','result_record':'Report presence and final seal; exit command separately reported'},
 ],'not_executed':['Docker command/API/exec','live topology recertification','candidate qualifier or constructor write rerun','source acquisition','real preparation','oracle/allocation/repair','dependency installation','git add/commit/push','GUI launch'],
 'finalization':'Exit snapshot comparison and evidence seal are performed by finalize_audit.py after report creation; their actual diagnostics are preserved in preservation_verification.json and seal_readback.json.'})
print({'status':'V6_SUCCESSOR_REMEDIATION_INDEPENDENT_REAUDIT_BLOCKED','material':1,'minor':1})
