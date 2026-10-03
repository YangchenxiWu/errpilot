# V5 oracle execution readiness lifecycle closure V1

Transaction: `OPEN_V5_ORACLE_EXECUTION_READINESS_LIFECYCLE_CLOSURE`.
Component: `V5_ORACLE_EXECUTION_READINESS_BRIDGE_V1`.

## Human-PI authority and effective lifecycle

The Human PI explicitly accepted the seven readiness-bridge candidate artifacts,
accepted the five prior preflight artifacts as historical supporting evidence,
and authorized this single closure record, bounded non-executing validation,
readiness freeze, exact thirteen-path staging, exactly one local commit and
post-commit read-only verification.

```text
HUMAN_PI_V5_ORACLE_PLAN_STORAGE_DECISION_V1 = ADOPTED
V5_ORACLE_EXECUTION_READINESS_BRIDGE_V1 = HUMAN_PI_ACCEPTED
PRIOR_V5_ORACLE_PREFLIGHT_EVIDENCE = HUMAN_PI_ACCEPTED_AS_HISTORICAL_SUPPORTING_EVIDENCE
```

Only this closure record is newly authored. All twelve previously accepted
repository artifacts retain their exact bytes. Their candidate-only lifecycle
fields and historical next-gate declarations remain immutable historical
representations. This closure supplies the subsequent effective acceptance and
freeze when read from its verified enclosing commit. It does not activate or
alter the candidate execution-authority JSON; actual execution remains denied.

The lifecycle below is effective only if the enclosing local commit has exactly
the required parent, message and thirteen-path inventory and all bounded checks
pass. The enclosing commit identity is deliberately not embedded here.

```text
V5_ORACLE_EXECUTION_READINESS_BRIDGE_V1 = HUMAN_PI_ACCEPTED = FROZEN
PERSISTED = YES
COMMITTED = YES
REMOTE_PUBLISHED = NO
REAL_ORACLE_SCREENING_EXECUTED = NO
```

## Entry state and preservation

Canonical root: `/Users/wuyangchenxi/errpilot`; branch: `main`.
Required starting HEAD, verified live `origin/main`, and enclosing commit parent:
`86fb1021e2504f00fa2a9dfcdc25ab95a307e41c`.
Commit message: `benchmark: freeze V5 oracle execution readiness`.
Entry index and tracked diff were empty; the untracked set was exactly the twelve
accepted paths below. The initial sandbox live query failed DNS resolution;
the authorized elevated read-only `git ls-remote --exit-code origin refs/heads/main`
succeeded before lifecycle writes. No fetch or remote-ref write occurred.
No repository or ancestor AGENTS.md, `.airos/current_state.md`, or `.airos/contracts/`
was present; the supplied global rules and Human-PI transaction control this work.
No active non-sample Git hook was present at inspection.

All 472 original tracked file bytes and Git modes were preserved and
compared with parent blobs. The SHA-256 of the sorted compact JSON map with
repository-relative paths and values {sha256,mode} is
`689deb31d9600e3a57907d70a0f14d1d06fd75d1dad25f3f4b739dff6fcf2a47`.
The 123 distinct historical/current input paths (28 original
plans, frozen oracle scripts, protected manifests and environment identities)
were captured for repeated preservation checks; their sorted compact path/hash
map SHA-256 is `ef5ff8b68854e01295919b012d9678404ebe8db9c8d997bf6ad4a72eee50b1db`.

## Five accepted historical preflight supporting-evidence artifacts

| Exact repository path | Accepted SHA-256 |
| --- | --- |
| `evaluation/downstream_benchmark/evidence/v5_3x3_oracle_screening_preflight_20261003/RUN_REPORT.md` | `15a79d45d7d7a2ff6f2ed5905aef4f33e41ec6f9cb100c7fcc56dab553003d06` |
| `evaluation/downstream_benchmark/evidence/v5_3x3_oracle_screening_preflight_20261003/docker_image_inventory.json` | `11e7b9d34f3f2e184f57a20fda02382f378603dfaaefd176770a2213ea458086` |
| `evaluation/downstream_benchmark/evidence/v5_3x3_oracle_screening_preflight_20261003/evidence_sha256.json` | `50cec525498a51910fc1dffbdecbe121591ba278d1dec9a23e55b295c0c53ba5` |
| `evaluation/downstream_benchmark/evidence/v5_3x3_oracle_screening_preflight_20261003/population_environment_bindings.csv` | `2e7e495b3372310b577e503e5d75f56ec4b38082d1565cba67bb91d036be9dc8` |
| `evaluation/downstream_benchmark/evidence/v5_3x3_oracle_screening_preflight_20261003/preflight.json` | `43af1307cb03b1f6305307009799e2113024008cec8d89a96142ef9687a6fe4d` |

## Seven accepted readiness-candidate artifacts

| Exact repository path | Accepted SHA-256 |
| --- | --- |
| `evaluation/downstream_benchmark/V5_ORACLE_EXECUTION_READINESS_BRIDGE_V1_CANDIDATE_REPORT.md` | `9a7a839c8db6b3a2ec49f5d94b44381a50d07dc69f3d52ccfc903cbcff072d49` |
| `evaluation/downstream_benchmark/evidence/v5_oracle_execution_readiness_bridge_v1/artifact_sha256.json` | `857c720590ad49a28b3a93400e292e6588a2787cd49ec69401dff250844a284c` |
| `evaluation/downstream_benchmark/screening/docker_oracle_backend_v1.py` | `aff923b6bd9f0001b4805ce5d6a9e9cf7281b63893f62541b0d3604e0a18e0f3` |
| `evaluation/downstream_benchmark/screening/oracle_trial_driver_v1.py` | `f7d3a27fb398ca02af95c97112b6e3e0ea6cf5a61880a1ef3c98186c935b3e12` |
| `evaluation/downstream_benchmark/screening/v5_oracle_executor.py` | `3f9d4f79d382f062416b20bf7c754f9d3dc8dd7aef3c7fdfa14807c7a88b1256` |
| `evaluation/downstream_benchmark/tests/test_v5_oracle_readiness_bridge.py` | `8153ac9cca69b4e19cca0ecc836559b84d29f1240bc82ce7df9dd5a46428edf2` |
| `evaluation/downstream_benchmark/v5_oracle_execution_readiness_bridge_v1.json` | `34f28bcb9b1218fe21f8ca5da71be2e764ee84721de309dd19d582a75ef207e3` |

## Exact twenty-four external artifact identities

External artifacts remain external; none is copied into Git. The accepted
repository inventory and report independently agree on these exact twenty-four
paths/hashes; the external inventory binds the other twenty-three payloads and
is itself bound below without a circular self-hash.

| Exact external path | Accepted SHA-256 |
| --- | --- |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/black-16/execution_plan.json` | `ecd7fcb0503f80f545c038f8ae72219b8747cf86dc8a319d386c758cd68e6210` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/black-17/execution_plan.json` | `23b04aa7d65e16a182c3bc833f97e90f3be85db39411e43152af23bf155198dd` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/current_plan_manifest_v1.json` | `dd2c097fec150a991c2e5fcddbc2bd21619c34744edd939c549d99df6b1bf7cd` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/fastapi-11/execution_plan.json` | `3432aeaac346e022b1e776d6ee13097cc8bc464e3523df17badb1a8f45df4410` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/fastapi-13/execution_plan.json` | `69b659041867531d2640704e20253d39cd71f08389f27104f405d99ed636875d` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/fastapi-2/execution_plan.json` | `3ba834d47d8ba7f3c14c8f6c0f5e25bea59b2fc73e5a5f2d5aa2869a4ce99672` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/httpie-1/execution_plan.json` | `9d0ae333694feea3695b18ea8be3869aef694311edcec953938a42f6960c9ba1` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/httpie-3/execution_plan.json` | `f5ed620c46fec2f6c9a2a35adff846924113c12193e7c70de60a1163aa7bc97e` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/httpie-4/execution_plan.json` | `745aceebfdd739972cb867fcea0418497e0ec854ce535b029547cc7d90d8ff15` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/keras-28/execution_plan.json` | `cca350415fe8d3c6d0f6578d1a4ec5b03fe2c8d82050f527ec16c75c1958faa4` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/matplotlib-11/execution_plan.json` | `de65825672b4f335a0ce0ced5c2db5ca8a611bcbd7164dc7d8fe2dea5390ca0d` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/matplotlib-17/execution_plan.json` | `076b3284c6b90b4a7e98662a126ee2184ffbc9570d2a732562de9488fc199696` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/matplotlib-29/execution_plan.json` | `c5365a2f981168fc0487b45758aec05d04d04838e3f735378b5cfbcb704f1c8d` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/pandas-102/execution_plan.json` | `230ee1686d142fcbdb0d8815adc6d0289df47b89ae8ad1236afd78ad96815140` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/pandas-4/execution_plan.json` | `c9e3307fc62f264dfcad5a40484468f2ac15daee167dae487c1c451de0337ba2` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/pandas-45/execution_plan.json` | `bdd1b3d95cfe014d011987e7e83fe6bee4c3dcb136b0046868145003b0da680e` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/pandas-78/execution_plan.json` | `2bc1f4eb3713f9c27b16df13d160a8f8822e84a6e4820072cbdfa093d1a66fc6` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/readiness/artifact_sha256.json` | `b136be34a1c5faf290a7084d01577e37f006328864aca26b1e26cb01d1c6785c` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/readiness/docker_readiness_v1.json` | `8a148a593c479cc4f3ea2fe8f75bb923837ef34b61233c7bf4b0efe54917fc68` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/readiness/dry_validation_v1.json` | `c54577bdd64b49a457984adc1948c47871d96adb7a90486c4fa011e7c3793400` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/readiness/plan_lineage_v1.csv` | `4c1a70abf1f0380b8dbb34748c67268b676ce97ecf022a1d9cb4fa01dc8e135b` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/youtube-dl-18/execution_plan.json` | `f86737809a178d1cb2dd8397b1db0251361564479a8ea8b773955560e7bcee02` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/youtube-dl-37/execution_plan.json` | `d86930329de4dd5b68ce64db6cb468c13fea10cec4ae50a97a8aabf3314de36b` |
| `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/youtube-dl-7/execution_plan.json` | `498d54ebce062a4650b5d82eebb67299a215b9b0c4f5ef6f18f611da0a26a449` |

## Exclusive current-plan selection and lineage

The sole current selector is
`/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/current_plan_manifest_v1.json`.
Its raw SHA-256 is
`dd2c097fec150a991c2e5fcddbc2bd21619c34744edd939c549d99df6b1bf7cd`.
Resolution is frozen V5 population -> explicit manifest -> exact selected
path/raw hash/version -> exact bound variant environment. Latest, mtime,
lexical selection, directory selection and predecessor fallback are forbidden.

Exactly nineteen per-case v1.1 successors are selected for the initial cases;
the nineteen predecessors remain byte-identical and are never selected as
current. Each successor preserves the committed composite core and binds its
predecessor raw/canonical identity, V5 baseline, both environments and frozen
contracts. Materialized environments retain their original committed-core
identities; no environment identity was rewritten.

| Initial case | Immutable predecessor path | Predecessor raw SHA-256 | Predecessor canonical SHA-256 | Selected successor path | Successor raw SHA-256 | Successor canonical SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| `pandas::102` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/pandas-102/preparation/execution_plan.json` | `c51770fe183a7512ef09ebd91405f1cc9ec044d9320872377a7096bc212eda5a` | `0f9acc47fed2787a7e14d7d423868871b4b028c19ce7c136a1ee2b7a1dc59c8c` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/pandas-102/execution_plan.json` | `230ee1686d142fcbdb0d8815adc6d0289df47b89ae8ad1236afd78ad96815140` | `f8fd81287794679ad77e418b8fa66bb47710684bec07e8dddf6a739f14199654` |
| `pandas::78` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/pandas-78/preparation/execution_plan.json` | `d78960ea79df5b0d75ea272e23fb0337eb6b58a6aa4e79c77ae9ec13aefb1dfb` | `05e9d0d3045608d43657d931ca03b3fe2a9830dc1fe4a3097e2ecd2e0eda3da1` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/pandas-78/execution_plan.json` | `2bc1f4eb3713f9c27b16df13d160a8f8822e84a6e4820072cbdfa093d1a66fc6` | `1dbb52f0911f3e2cf3c24c686ea15685a361f21500051797c46b1549b97180c8` |
| `pandas::4` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/pandas-4/preparation/execution_plan.json` | `289051b4c140e20438d57f99d9a26b1ec62912087d20e34d5d6c891316fbf66b` | `06045e1127da6587b591a88d2b3a7676d04dd719d848ef5b50780ff746ca7339` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/pandas-4/execution_plan.json` | `c9e3307fc62f264dfcad5a40484468f2ac15daee167dae487c1c451de0337ba2` | `16323f0b9ade21349ae8cb5fa9ddb87c5a182500683b48aad9934eab5b3edb75` |
| `pandas::45` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/pandas-45/preparation/execution_plan.json` | `bf0c922a06b8ce3a05a8d28f6f283b3271f9334974636014a2a1fd5055f387a6` | `f68465abacd2aa8989b9a6aeb9b8a61c14b27a11d5795e8ec3273e6f3db1b26d` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/pandas-45/execution_plan.json` | `bdd1b3d95cfe014d011987e7e83fe6bee4c3dcb136b0046868145003b0da680e` | `3355ac9c7494a39db71c4916515d85aee2dde2c2417d17d02e8aacc29f433579` |
| `matplotlib::17` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/matplotlib-17/preparation/execution_plan.json` | `13ba226042b11e5a2dfd39412345ea378d174985583b6d0892105c35e776350e` | `86939c6b1914e506e6989238300f4d85094b3ead0b2fbc124957951727d651ef` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/matplotlib-17/execution_plan.json` | `076b3284c6b90b4a7e98662a126ee2184ffbc9570d2a732562de9488fc199696` | `ef4baad5a74852f447aadde901f586b002817144ab5bda3bc490794fa6697d6f` |
| `matplotlib::11` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/matplotlib-11/preparation/execution_plan.json` | `2777e81a09476b5d3e2e19b8e394d90570f438ec12c7b09326b1640974c271b7` | `93f677f03dfc6fdf27ebce67b69cb0ac4cb567bf1d2615fd1b0033cd39702d1c` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/matplotlib-11/execution_plan.json` | `de65825672b4f335a0ce0ced5c2db5ca8a611bcbd7164dc7d8fe2dea5390ca0d` | `41ceac469c669dbbec8ef9d629b4510ba2e67d5ba1da7ef1595686f5aaa6a0f6` |
| `keras::28` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/keras-28/preparation/execution_plan.json` | `1941d44af653f4be2e5ef2ad860cb308a24b6626eb5a0a1b348165fb18b4a611` | `c2f99d34118ac9b29a2534875a98caa58a864aa535a63822550fa347e93b51db` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/keras-28/execution_plan.json` | `cca350415fe8d3c6d0f6578d1a4ec5b03fe2c8d82050f527ec16c75c1958faa4` | `2bb8b5fac1e54f88b27f0cb1038519fd3c8cdc0d049a4b609f5052c2930c7a81` |
| `youtube-dl::7` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/youtube-dl-7/preparation/execution_plan.json` | `d9f124ea8fc76dd60d2a6855ff2140ad3437e55efb1c1ca9a686a90032b595fc` | `e6adc1ecb648180a49057112febae1dc3cdad23b3a4243913f0b444f45638e72` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/youtube-dl-7/execution_plan.json` | `498d54ebce062a4650b5d82eebb67299a215b9b0c4f5ef6f18f611da0a26a449` | `a7d82291c4f2f3ff54aebcd350f5f0a347e793252c5f0f6bec8ac423fc95b9e8` |
| `black::17` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/black-17/preparation/execution_plan.json` | `abd669b75a7d72c8559d9c3b266644b84926fa3959c8f400c672ddfb2fccd4cc` | `9eeeeb88cb6757204e2341eaa35ef1f3dff8a242af7b6bdfe2b3bda298118ed1` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/black-17/execution_plan.json` | `23b04aa7d65e16a182c3bc833f97e90f3be85db39411e43152af23bf155198dd` | `99555c822885bc64cc567476fc66e15fc24dea4cba375ba9f49f2ecaed7cc764` |
| `httpie::1` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/httpie-1/preparation/execution_plan.json` | `1fdc77da3a14039fc540e1a593627e5b7fc399b619037bca7563a037f5617d57` | `8a40bd53c8ec9b8b666ff0fb07e4ad3c1e74fd8831ac7e788adb7cdf16566932` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/httpie-1/execution_plan.json` | `9d0ae333694feea3695b18ea8be3869aef694311edcec953938a42f6960c9ba1` | `c17a19318694e1a672e7b8a319dc8e19ddfd415602e5a899b8caf3d18f0832c2` |
| `fastapi::2` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/fastapi-2/preparation/execution_plan.json` | `b055ba3a544e413eed4adcb263831a8026acf90ec05e1800aff55c5b4a201f56` | `52074248ae4f088943b34a680a9bf354c26522e19a1c0cafadfe93df1634899f` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/fastapi-2/execution_plan.json` | `3ba834d47d8ba7f3c14c8f6c0f5e25bea59b2fc73e5a5f2d5aa2869a4ce99672` | `a42c24c91ed79fd359c2472ad55ed0a85eb7463ea049b34661d873361afea312` |
| `youtube-dl::37` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/youtube-dl-37/preparation/execution_plan.json` | `0635e34d5855c36362ca89716df03155da3b03347478c263314b8fdbab8d6270` | `ea3a10d8a8d75258a75d12d0bb294d68de859c3dc0cd1566a72045d332e1accb` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/youtube-dl-37/execution_plan.json` | `d86930329de4dd5b68ce64db6cb468c13fea10cec4ae50a97a8aabf3314de36b` | `5a9044568020d74b57def412161ca1451392c0dcbc3dafa7924ace426d948b49` |
| `youtube-dl::18` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/youtube-dl-18/preparation/execution_plan.json` | `040a58ac300614d59dea4535f4158d7c0f59013ffb07459d3a61e7368ea4e582` | `0d6304c235330174e1ce31d7ed041e09643597a13d3436d566cccc94e37c9294` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/youtube-dl-18/execution_plan.json` | `f86737809a178d1cb2dd8397b1db0251361564479a8ea8b773955560e7bcee02` | `5b3e40a5b96ec5441a1e398753d80d2779e372c0761eeb61f72d1542daedc4be` |
| `fastapi::13` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/fastapi-13/preparation/execution_plan.json` | `6f627b459ceeb8d2f2e7e7b095d6bb201b990401aa5f886abd75e10d6b9c1e6b` | `09679daa81f44895e49d854d39fed8482f263a7d897df71a0144e55d2234f580` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/fastapi-13/execution_plan.json` | `69b659041867531d2640704e20253d39cd71f08389f27104f405d99ed636875d` | `4be2208795217c69ef0663007b8d3f81810385481ad5bbafde501dac1f4fc852` |
| `black::16` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/black-16/preparation/execution_plan.json` | `e6679210c506550b8c64a32aa83c21c40fc2970ba0f7e97d7c5343bb1670272b` | `46c0441c56d3021bd98153810a18502b4add13a5aecb6b56c023480105a37c32` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/black-16/execution_plan.json` | `ecd7fcb0503f80f545c038f8ae72219b8747cf86dc8a319d386c758cd68e6210` | `85a66fdd229dc4d8e2792d7730373b03064ceff2272132c8a7477be62de88177` |
| `httpie::3` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/httpie-3/preparation/execution_plan.json` | `6db57769c02991a9c1ce7ca8592688f69e735c0d6b972e2b6bddf61202946399` | `08ac42cbd0c379ddf6ae2201097759e58d1687d9b575df4777682b968a84dd02` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/httpie-3/execution_plan.json` | `f5ed620c46fec2f6c9a2a35adff846924113c12193e7c70de60a1163aa7bc97e` | `89587fd376e4079041b1f305a2c0f7a2c0ef86e7da500cd450d7e4979c44b1cb` |
| `matplotlib::29` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/matplotlib-29/preparation/execution_plan.json` | `f3eb85f7e176c442a89f0cb6737377f76996329b41bede76ead0c9f9e951dfc2` | `315f9147b2053623de22d87612f649af0f1bbc2c0e4b7272e249ddf4f5d2e647` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/matplotlib-29/execution_plan.json` | `c5365a2f981168fc0487b45758aec05d04d04838e3f735378b5cfbcb704f1c8d` | `e22b3e8b0a02ba6faed5cbc22552f07ed1aa61e7e209b5b7940ed01f47742c48` |
| `fastapi::11` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/fastapi-11/preparation/execution_plan.json` | `b5b960c6ad798f951a1f1a702cfe48b405887e16f839832d8b6c5d4b4d4499c7` | `217e624886986e3b7bcd0ea59f5f4cc1ab97b8709e9d736acb2acc3380899398` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/fastapi-11/execution_plan.json` | `3432aeaac346e022b1e776d6ee13097cc8bc464e3523df17badb1a8f45df4410` | `ce63833ca55e4997e0aefccbb9abcb35497e57aeed263c2cf3841758464f4676` |
| `httpie::4` | `/Users/wuyangchenxi/errpilot-benchmark-work/screening_workspaces/httpie-4/preparation/execution_plan.json` | `6c543e2d4af30fbd660d63211b64296117366702bf2ce4c825ce5e7a3edd49bf` | `9ea58a40c0c27e03dba86924dca4141ed476050523adc12ee2633cff921e45a7` | `/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/httpie-4/execution_plan.json` | `745aceebfdd739972cb867fcea0418497e0ec854ce535b029547cc7d90d8ff15` | `e551315276ed2b75ac1a87c31b83d21dc3aed4628265a0716c785ba7a61d22a1` |

## Newer-nine preservation

All nine newer plans retain their exact historical paths, bytes and canonical
plan identities. No successor is created for them; their manifest predecessor
is null and their lineage predecessor fields are empty. All twenty-eight
original historical plans were verified unchanged.

| Case | Preserved and selected path | Raw SHA-256 | Canonical SHA-256 | Selected version |
| --- | --- | --- | --- | --- |
| `matplotlib::21` | `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_01_preparation/matplotlib__21/preparation_plan.json` | `aaa4aa648e323e5e0249e40987e70967099f2a2955363f85df443523736f87eb` | `7146d43a882b6b0d1c8814f65994c66a1cc0fb5c071392cefc49b7e3f21df3bf` | `EXPANSION_BLOCK_01_PREPARATION_PLAN_V1` |
| `youtube-dl::24` | `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_01_preparation/youtube-dl__24/preparation_plan.json` | `0c1a2b9f0dda9475aa157274a4bb004418ba0c82621ab9e4ac9ffac7b6dda743` | `bfc7053572235f965c28e9a1b293bda097538b470d7dfb417710958723103a2c` | `EXPANSION_BLOCK_01_PREPARATION_PLAN_V1` |
| `black::6` | `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_01_preparation/black__6/preparation_plan.json` | `0db3c193115b1e9e3b02ccc53a55ff7881a0a93732922358385bb52fad4fafdb` | `f21af95424035163ec177cfe3a5e699a6c23494f67f09e7a7f38050547a5519e` | `EXPANSION_BLOCK_01_PREPARATION_PLAN_V1` |
| `black::15` | `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_01_preparation/black__15/preparation_plan.json` | `ddb9d636213dda8498d26a3be452341a72b7d7f8476ca041626202d8d5282adf` | `49fcb4be9b93812a1e0c1262cb70c012ad6c818523c9691ba62f8fa65513d63c` | `EXPANSION_BLOCK_01_PREPARATION_PLAN_V1` |
| `fastapi::12` | `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_02_preparation/fastapi__12/preparation_plan.json` | `86f748ec60b67d2b0e318606f2c43143073fa5aaaa2affae875595d4d5002cd4` | `3e468cebb67766d7b4a39d1f1b816cd0d03952f64ab107fd2210d5c0d0d94526` | `EXPANSION_BLOCK_02_PREPARATION_PLAN_V1` |
| `httpie::5` | `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_02_preparation/httpie__5/preparation_plan.json` | `2284bb655524fc205c355a34eaa0c4c00fc51b50ce31232e793d2b21a342d3b7` | `38847bbb7875602256cbb92bd6f181f027355623423e14caa5d854d2258dbaf2` | `EXPANSION_BLOCK_02_PREPARATION_PLAN_V1` |
| `PySnooper::1` | `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_02_preparation/PySnooper__1/preparation_plan.json` | `d3bc12b735a05273932fc1653ce025372bafc09417e4908e036e9a8de5ceee6d` | `6e7e01099933e797550c8e59743ba1fb8107251aaf4652915ec9eb15cbffb828` | `EXPANSION_BLOCK_02_PREPARATION_PLAN_V1` |
| `PySnooper::3` | `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_03_preparation/PySnooper__3/preparation_plan.json` | `e001534de9e932700ad64874f70acbd5276d8c4989deeffed0cd84f93e54d0dd` | `7284c3b552eac65340346e8682b9c7fd98320765a35959c86af1e21ab60401b5` | `EXPANSION_BLOCK_03_PREPARATION_PLAN_V1` |
| `PySnooper::2` | `/Users/wuyangchenxi/errpilot-benchmark-work/expansion_block_03_preparation/PySnooper__2/preparation_plan.json` | `35a137616e94094f71fcbe5a3bd3d77299e496879e0d2e24330b5731f78c4e0f` | `5e029faa4a5a007cf4d7bed73f125903927c4e537153c1e2dbd64eff1938062c` | `EXPANSION_BLOCK_03_PREPARATION_PLAN_V1` |

## Exact twenty-eight-case / fifty-six-environment population

Order is the nineteen initial cases, four Block-01 cases, three Block-02 cases
and two Block-03 cases in the tables above. Membership is unique and complete;
no exclusion/NON_RETRY case or stale initial plan is selected. Seventeen cases
share one source-independent image between variants, and eleven cases use
revision-specific pairs: thirty-nine distinct required immutable image IDs.
The fifty-six variant bindings are exact below; shared identities intentionally
repeat for BUGGY and FIXED.

| Case | Variant | Source revision | Materialized label | Environment identity path | Environment identity SHA-256 | Immutable image ID |
| --- | --- | --- | --- | --- | --- | --- |
| `pandas::102` | `BUGGY` | `efaadd502aba9af6322e7938b7034740fcca753b` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_01_pandas_102/BUGGY/environment_identity.json` | `eb11ecdde8023cb83de9295f52042314842fdc43bbe796ef10268e8f8bd4ff34` | `sha256:1c99db06103ab9af43c4a6650955a7daabd644bebe1dbf94c10616dcfa8506a3` |
| `pandas::102` | `FIXED` | `765d8db7eef1befef33f4c99d3e206d26e8444c8` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_01_pandas_102/FIXED/environment_identity.json` | `c618c39283c9ac7481dae12165f88012e61f5e7b7d2ab34fa027087eccae4f63` | `sha256:12c66972e5aaa9df50a12bddc8c3886aec481fd3786a00db171d2239797b3fec` |
| `pandas::78` | `BUGGY` | `f5aa5425549c5b39e7bc0a154b4d585a9375a571` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_02_pandas_78/BUGGY/environment_identity.json` | `e4b155b06140952a2d2ae861321f9c52f889ee04530b804c08740c1dda3df3bb` | `sha256:81bb0da00af36fb0846dd51b53681ebc4916d346d9f52fea8590c2a49cadb885` |
| `pandas::78` | `FIXED` | `bd6b395a1e8fb7d099fa17a0e24f8fe3b628822c` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_02_pandas_78/FIXED/environment_identity.json` | `6ef6fc93d9363a98ec4b7ee6001d5ec2d5ff9049efab69cf74435c8afd3e4eb3` | `sha256:9bc94f938f34aa864141a8841c6be1aea16c9b081d8e74d2ac64e6afea49f87d` |
| `pandas::4` | `BUGGY` | `cca710b42455664b44022e49f760ef790e9a3320` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_03_pandas_4/BUGGY/environment_identity.json` | `277a86337bd1f3e1fbcab93f2899430f7cb6046b186fe641b2484a2340de0d3f` | `sha256:79cfe477121afa51b167bb819e32babf7c461ba0e05aa04fcabb8359b6268a8c` |
| `pandas::4` | `FIXED` | `2250ddfaff92abaff20a5bcd78315f5d4bd44981` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_03_pandas_4/FIXED/environment_identity.json` | `24d54f83746906949794899cc0e205c35b3fda576da7943983b96bd1d44f46cf` | `sha256:7053928b670cb4c0117be2c8a0e2b07c2fdeae4f3ada8f1d1f8a40fd7ea8b911` |
| `pandas::45` | `BUGGY` | `74c530642c11308df6162b4040ab04ac4e07db9f` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_04_pandas_45/BUGGY/environment_identity.json` | `280be799d1496d99fe0d11a23bf0212c8d9b10b36aaf78e35706c4dc2adebba5` | `sha256:71992b697357c10002b4b59612160e4cad9506ed27b11329013f404bb29875d9` |
| `pandas::45` | `FIXED` | `74f6579941fbe71cf7c033f53977047ac872e469` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_04_pandas_45/FIXED/environment_identity.json` | `c23515288228f5df978698a34d80903eff82f22a34f8afbc1e66719571f70d41` | `sha256:51cf86ad40a2e4bcd9f0da7140c41882c78c2152e49a21c2eda0a8a0bda9e30b` |
| `matplotlib::17` | `BUGGY` | `58c66982d98851c56b045137ced803fd62c6c5e8` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_07_matplotlib_17/SOURCE_INDEPENDENT/environment_identity.json` | `fe52603d57dcc9b13826e6d30fccbeb99f58726a2e5e9bc2de68890354837c93` | `sha256:5496b2af549a70dd5fff579c029d61cdbb63cbb6a8309044b2963a50d5e069e0` |
| `matplotlib::17` | `FIXED` | `05a5db0fec2eced55076736f0b9520641b279ad6` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_07_matplotlib_17/SOURCE_INDEPENDENT/environment_identity.json` | `fe52603d57dcc9b13826e6d30fccbeb99f58726a2e5e9bc2de68890354837c93` | `sha256:5496b2af549a70dd5fff579c029d61cdbb63cbb6a8309044b2963a50d5e069e0` |
| `matplotlib::11` | `BUGGY` | `f8459a513c3f67447ceb1a07c29760d504517ff2` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_09_matplotlib_11/SOURCE_INDEPENDENT/environment_identity.json` | `d4e34b79d8b8bab198301e9b838c8b97aa097ddff4d14f7aee84cbd97824a852` | `sha256:024ebec9dedadfffc48b4c6e125e159dfcd1b921acb42e9490c2ef788709b483` |
| `matplotlib::11` | `FIXED` | `af745264376a10782bd0d8b96d255f958c2950f3` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_01/batch01_09_matplotlib_11/SOURCE_INDEPENDENT/environment_identity.json` | `d4e34b79d8b8bab198301e9b838c8b97aa097ddff4d14f7aee84cbd97824a852` | `sha256:024ebec9dedadfffc48b4c6e125e159dfcd1b921acb42e9490c2ef788709b483` |
| `keras::28` | `BUGGY` | `6171b3656ebd9b6038f709ba83f7475de284ba4e` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/evidence/batch_01_keras28_identity_completion/environment_identity.json` | `36070fd6869dac8ef60046ad32ebc1500a4fa190ca0f3f3c83cde2922683a8cf` | `sha256:f9b214bdeeb7fa29722bdd95226d1aa6600d89f73ca8e6b5627d989f2d7546d3` |
| `keras::28` | `FIXED` | `5422fdd38baad36730cb6aeb946e17eeae6a551c` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot/evaluation/downstream_benchmark/evidence/batch_01_keras28_identity_completion/environment_identity.json` | `36070fd6869dac8ef60046ad32ebc1500a4fa190ca0f3f3c83cde2922683a8cf` | `sha256:f9b214bdeeb7fa29722bdd95226d1aa6600d89f73ca8e6b5627d989f2d7546d3` |
| `youtube-dl::7` | `BUGGY` | `63a64948342ebfe46db8c258765e698a04a61904` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_02/batch02_12_youtube-dl_7/SOURCE_INDEPENDENT/environment_identity.json` | `37274c1a999de2358d504a21acf07ff8c3099807f7c940206bb15ec4af976092` | `sha256:d64fd5798a01d4596f7e2e386335077fcd7ae173413fd9cf5ebf97d54e3ca70f` |
| `youtube-dl::7` | `FIXED` | `d01949dc89feb2441f251e42e8a6bfa4711b9715` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_02/batch02_12_youtube-dl_7/SOURCE_INDEPENDENT/environment_identity.json` | `37274c1a999de2358d504a21acf07ff8c3099807f7c940206bb15ec4af976092` | `sha256:d64fd5798a01d4596f7e2e386335077fcd7ae173413fd9cf5ebf97d54e3ca70f` |
| `black::17` | `BUGGY` | `bbc09a4f013f2a584f143f3f5e3f76f6082367d4` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_02/batch02_16_black_17/BUGGY/environment_identity.json` | `81da4de52ddb030c72095a3f63cc9c73d0913dd3dbbe00fcc1a52e9e48c7833b` | `sha256:17953aa7de810232d03f990e9fea528c7f4d2ca63833a224b6c46be40e7e5de6` |
| `black::17` | `FIXED` | `7fc6ce990669464f5172b63fafa3724f5f308be3` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_02/batch02_16_black_17/FIXED/environment_identity.json` | `458b6cfdae2569261864d45edc4b6e2f0f1113e6d3bc5fef0cfbf508def7ed7f` | `sha256:b2afadf182432ecbe817dac772df3cae7bfae06bde80daa430a02d49570a5080` |
| `httpie::1` | `BUGGY` | `001bda19450ad85c91345eea3cfa3991e1d492ba` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_02/batch02_19_httpie_1/SOURCE_INDEPENDENT/environment_identity.json` | `602c9325960d394a5a2f8237640b7ade05643bdc68d9120470ada6056e12661d` | `sha256:293cd8b11fc20605c85af3b396bf89940b4a175ec806aab31f71fa8ca0d8b5ad` |
| `httpie::1` | `FIXED` | `5300b0b490b8db48fac30b5e32164be93dc574b7` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_02/batch02_19_httpie_1/SOURCE_INDEPENDENT/environment_identity.json` | `602c9325960d394a5a2f8237640b7ade05643bdc68d9120470ada6056e12661d` | `sha256:293cd8b11fc20605c85af3b396bf89940b4a175ec806aab31f71fa8ca0d8b5ad` |
| `fastapi::2` | `BUGGY` | `210af1fd3dc0f612a08fa02a0cb3f5adb81e5bfb` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_03/batch03_23_fastapi_2/SOURCE_INDEPENDENT/environment_identity.json` | `631508608de41e5acfc54c419cc0dc1092eb460cc13f86b45df5e179c7b31371` | `sha256:076d63249117b9270dd9bfcf596572d153668088afbdeca5d406a588cb360176` |
| `fastapi::2` | `FIXED` | `02441ff0313d5b471b662293244c53e712f1243f` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_03/batch03_23_fastapi_2/SOURCE_INDEPENDENT/environment_identity.json` | `631508608de41e5acfc54c419cc0dc1092eb460cc13f86b45df5e179c7b31371` | `sha256:076d63249117b9270dd9bfcf596572d153668088afbdeca5d406a588cb360176` |
| `youtube-dl::37` | `BUGGY` | `98b7cf1acefe398f792ca6ff4c5f84f1b7785fcb` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_03/batch03_24_youtube-dl_37/SOURCE_INDEPENDENT/environment_identity.json` | `437de85532de95d528bf0048f9117b0249a286a718d4fb81fdfdd1d3263db2b9` | `sha256:822c98af2f3e140cdd895042aac9b035eb14487eb453322f3ca58fa19478f509` |
| `youtube-dl::37` | `FIXED` | `676eb3f2dd542be3e84780b18388253382d3e465` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_03/batch03_24_youtube-dl_37/SOURCE_INDEPENDENT/environment_identity.json` | `437de85532de95d528bf0048f9117b0249a286a718d4fb81fdfdd1d3263db2b9` | `sha256:822c98af2f3e140cdd895042aac9b035eb14487eb453322f3ca58fa19478f509` |
| `youtube-dl::18` | `BUGGY` | `dc6520aa3d1fe7afc52613e392f15dde90af4844` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_03/batch03_25_youtube-dl_18/SOURCE_INDEPENDENT/environment_identity.json` | `0b5f1ef92792560a314b969110c583ef7b32e72eb06aadaf71d918ae9602ec58` | `sha256:c432fba647d1b87035d9581ee231dc3f14201a5a7d8e65bf194f7676b08889b3` |
| `youtube-dl::18` | `FIXED` | `0396806f671e5828c2abdeb8048acf8b654507b6` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_03/batch03_25_youtube-dl_18/SOURCE_INDEPENDENT/environment_identity.json` | `0b5f1ef92792560a314b969110c583ef7b32e72eb06aadaf71d918ae9602ec58` | `sha256:c432fba647d1b87035d9581ee231dc3f14201a5a7d8e65bf194f7676b08889b3` |
| `fastapi::13` | `BUGGY` | `6f7f9268f6b03f42831dcfeaa5c15ba9813333ec` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_31_fastapi_13_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `ab1915e81b943a86147c181a474061aad6d3b302da2b63f564eb52d94cc3edf6` | `sha256:a59ad53068f67bdb147252a9a9b50e9d568a36f3b3a7ae2993ccba86260ef595` |
| `fastapi::13` | `FIXED` | `c8df3ae57c57e119d115dd3c1f44efa78de1022a` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_31_fastapi_13_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `ab1915e81b943a86147c181a474061aad6d3b302da2b63f564eb52d94cc3edf6` | `sha256:a59ad53068f67bdb147252a9a9b50e9d568a36f3b3a7ae2993ccba86260ef595` |
| `black::16` | `BUGGY` | `fb34c9e19589d05f92084a28940837151251ebd6` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_33_black_16_buggy/BUGGY/environment_identity.json` | `8a12e4c39f6bc96c3e49561878807f0c8fefc48e83b7b75b18f690f0b5c54757` | `sha256:9b9afc87ee4c2bb0a61c9983bbc10416250de106c90f3f40b9d76c43c2f388f1` |
| `black::16` | `FIXED` | `42a3fe53319a8c02858c2a96989ed1339f84515a` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_33_black_16_fixed/FIXED/environment_identity.json` | `8f2359fa36394f8526ba2082740286ff6199f1757173718d71e6d259a63fe47b` | `sha256:72adfd17b7ccdc6d2c3c00c925fa5ad9e13a2e41d36d88b35d1028c134cc90e9` |
| `httpie::3` | `BUGGY` | `8c33e5e3d31d3cd6476c4d9bc963a4c529f883d2` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_35_httpie_3_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `540b2ff94bac78c7b6852c4958635fb4f8b8e667b8cb77cfce73555b330ce170` | `sha256:153166915f9cd6e9e5b5fea6cdc96bf027b109b672ada1a1f3d6cb0860714043` |
| `httpie::3` | `FIXED` | `589887939507ff26d36ec74bd2c045819cfa3d56` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_35_httpie_3_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `540b2ff94bac78c7b6852c4958635fb4f8b8e667b8cb77cfce73555b330ce170` | `sha256:153166915f9cd6e9e5b5fea6cdc96bf027b109b672ada1a1f3d6cb0860714043` |
| `matplotlib::29` | `BUGGY` | `cdf9e30e4f3fb7747b178ee9c3849dfdebee7bd0` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_36_matplotlib_29_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `2059511b2b5b332b57be567a350f44449a47838854eacc277c2e99b61667055b` | `sha256:61967bee132f4c25e6962e56ce846558b299e8d4978208bc76530743be8ddd20` |
| `matplotlib::29` | `FIXED` | `fc51b411ba5d0984544ecff97e0a28ea4b6a6d03` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_36_matplotlib_29_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `2059511b2b5b332b57be567a350f44449a47838854eacc277c2e99b61667055b` | `sha256:61967bee132f4c25e6962e56ce846558b299e8d4978208bc76530743be8ddd20` |
| `fastapi::11` | `BUGGY` | `bf229ad5d830eb5320f966d51a55e590e8d57008` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_38_fastapi_11_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `e50f1ebab53df1b0ca686d525d5f5eb54364395bd83d041505c760ed6742057f` | `sha256:e75585e97ca91c95024210e9c27591888aa4f9e80105d4595c946ed9d4ad31c8` |
| `fastapi::11` | `FIXED` | `06eb4219345a77d23484528c9d164eb8d2097fec` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_38_fastapi_11_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `e50f1ebab53df1b0ca686d525d5f5eb54364395bd83d041505c760ed6742057f` | `sha256:e75585e97ca91c95024210e9c27591888aa4f9e80105d4595c946ed9d4ad31c8` |
| `httpie::4` | `BUGGY` | `8c892edd4fe700a7ca5cc733dcb4817831d253e2` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_40_httpie_4_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `bee8ddd433be0677ce00fd66a255215d22b61dc1d4d42e5327c2f909b9339e55` | `sha256:1f96c0d1952ae56c5da0f1464a0e9162d32bd13ce0b0c4a457d391c8753fb7ec` |
| `httpie::4` | `FIXED` | `040d981f00c3f6830b2d0db3daf3c64c080e96e3` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_batch_04/batch04_40_httpie_4_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `bee8ddd433be0677ce00fd66a255215d22b61dc1d4d42e5327c2f909b9339e55` | `sha256:1f96c0d1952ae56c5da0f1464a0e9162d32bd13ce0b0c4a457d391c8753fb7ec` |
| `matplotlib::21` | `BUGGY` | `e240493a899ac05cb992cdb88f5487386586090e` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_01/attempts/02_matplotlib__21_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `056fab150b9d06ea4a145be5c054de7510d28fbd804becfffaa135da157c7cdd` | `sha256:ff21817de1e2ce11e23e024ce8089c5e274ea17657b3c72f12ce4be6d6d35eb0` |
| `matplotlib::21` | `FIXED` | `6fceb054369445d0b20d2864957e8bcfd8d2cb87` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_01/attempts/02_matplotlib__21_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `056fab150b9d06ea4a145be5c054de7510d28fbd804becfffaa135da157c7cdd` | `sha256:ff21817de1e2ce11e23e024ce8089c5e274ea17657b3c72f12ce4be6d6d35eb0` |
| `youtube-dl::24` | `BUGGY` | `2c6da7df4a4d69ec933688e3c53795fd3436a1c6` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_01/attempts/03_youtube-dl__24_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `929ef806ed782d2b7a26243f3886120d6e5014ced4b6ead95fae16fc68500bbe` | `sha256:733c286fefed8fbf678c80d3eddfa657caf1a987e5afc2c4c8593d74ea7cad88` |
| `youtube-dl::24` | `FIXED` | `e5a088dc4be4fdcc96927a9f1b7284d4cd49c415` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_01/attempts/03_youtube-dl__24_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `929ef806ed782d2b7a26243f3886120d6e5014ced4b6ead95fae16fc68500bbe` | `sha256:733c286fefed8fbf678c80d3eddfa657caf1a987e5afc2c4c8593d74ea7cad88` |
| `black::6` | `BUGGY` | `8c8adedc2a74a494c24f93e405b6418ac32f54cd` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_01/attempts/05_black__6_buggy/BUGGY/environment_identity.json` | `514ecb53b403f7e9710f307a8d97d9dda26fab7aa5b17e39b051eb8068446d3f` | `sha256:71fd8391021dbdd01c01def245b8a80aa16f1c8da27f3c8cd47d738a601ade02` |
| `black::6` | `FIXED` | `f8617f975d56e81cfb4070ce65584f7b29a77e7a` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_01/attempts/05_black__6_fixed/FIXED/environment_identity.json` | `252d6ec81bc5bf8a638ac6c674622909091e53025adccf380a726bffdd0edd06` | `sha256:bec4af6facc284c921a91e11b2730a152b568259700c9f3eac0cdbfc07b4e02c` |
| `black::15` | `BUGGY` | `8a8c58252cc023ae250d6febd24f50a8166450d4` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_01/attempts/07_black__15_buggy/BUGGY/environment_identity.json` | `ae90b3b04621049e47ac719bbdba7f0a96c619e6eaa7f2b209089e7b10f9a55d` | `sha256:ba9e9b1e1459f959da5e9ffbd2485ca1eab8fbca3762b59ededa0b581884d9cc` |
| `black::15` | `FIXED` | `df2ae3bbe6c45298aabb6c04e85cb353205626f1` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_01/attempts/07_black__15_fixed/FIXED/environment_identity.json` | `14425b6bfdfe94dd690363451588d2b54bd93f1197ba19fd090f829d1b5a2f9a` | `sha256:239fe4798426c4cac10464fabc68eef70df453460d66df68b7ed23bc34437b78` |
| `fastapi::12` | `BUGGY` | `d61f5e4b555b123bf222503fc0e076cbae6a7ebc` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2/attempts/04_fastapi__12_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `57c7e3108f6ffa3b3148a4aadc3fec6e0b75200b08494b36556c3732fb350029` | `sha256:b4ff6cd46d6ddbe550d07a7c8c6fc0a979429e779219cc0874931f5fca0611d3` |
| `fastapi::12` | `FIXED` | `d262f6e9296993e528e2327f0a73f7bf5514e7c6` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2/attempts/04_fastapi__12_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `57c7e3108f6ffa3b3148a4aadc3fec6e0b75200b08494b36556c3732fb350029` | `sha256:b4ff6cd46d6ddbe550d07a7c8c6fc0a979429e779219cc0874931f5fca0611d3` |
| `httpie::5` | `BUGGY` | `16df8848e81eefac830f407e4b985f42b52970da` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2/attempts/09_httpie__5_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `2b572aca9815d3ab92a905308c3aa70bda3d78f9c60b7029cde66b2a6fa34682` | `sha256:c8eaac5f6d9477a4d8c29ad0ea4c316f6fe055117cc86b375c5bd19a1c47964c` |
| `httpie::5` | `FIXED` | `90af1f742230831792d74d303d1e7ce56c96d4bd` | `SOURCE_INDEPENDENT` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2/attempts/09_httpie__5_source_independent/SOURCE_INDEPENDENT/environment_identity.json` | `2b572aca9815d3ab92a905308c3aa70bda3d78f9c60b7029cde66b2a6fa34682` | `sha256:c8eaac5f6d9477a4d8c29ad0ea4c316f6fe055117cc86b375c5bd19a1c47964c` |
| `PySnooper::1` | `BUGGY` | `e21a31162f4c54be693d8ca8260e42393b39abd3` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2/attempts/10_PySnooper__1_buggy/BUGGY/environment_identity.json` | `eef8f200f720e10eb34980f237e05c6f66827b8d72a44e934b2a1f5f8da3cab0` | `sha256:cf8249aab08653c2708da5e0711ac664b4ee13f7f23d2f13f3cba629e10b44cb` |
| `PySnooper::1` | `FIXED` | `56f22f8ffe1c6b2be4d2cf3ad1987fdb66113da2` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_02_v2/attempts/10_PySnooper__1_fixed/FIXED/environment_identity.json` | `dea8d322942ab4c29bdb8df814f7667c824823d82bb6760a4b82248befe589da` | `sha256:fe5ca7b562e829421a8a45040b7a5ee9b05802c3c5b04f2f7cdc71de2b8366f8` |
| `PySnooper::3` | `BUGGY` | `6e3d797be3fa0a746fb5b1b7c7fea78eb926c208` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_03_v1/attempts/block03_02_PySnooper__3_buggy/BUGGY/environment_identity.json` | `4f0e9a26c3c4eafbb61d0ac68e4442ea1f04b57154c7c564802d9ed9ccc9c418` | `sha256:20cbe7b0328ee56c00b0c798744881501626794782fd0213ff307e66ff9a887f` |
| `PySnooper::3` | `FIXED` | `15555ed760000b049aff8fecc79d29339c1224c3` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_03_v1/attempts/block03_02_PySnooper__3_fixed/FIXED/environment_identity.json` | `378597002e80d60360404245ba0242c28f2666cb33345d9f8336101c48f0257b` | `sha256:d659d9b5b73c18762a0be797757257bcc2c7c35b8043700958894d7a33d3d889` |
| `PySnooper::2` | `BUGGY` | `e21a31162f4c54be693d8ca8260e42393b39abd3` | `BUGGY` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_03_v1/attempts/block03_05_PySnooper__2_buggy/BUGGY/environment_identity.json` | `d78b699ee726aa7e17480d3e8f2e745c8930d72cea66d4dd6238e57098e93ee7` | `sha256:9a254be8e406239b8198652ab7b5cf3ab5827c7281c4cbaed752465856085ac7` |
| `PySnooper::2` | `FIXED` | `814abc34a098c1b98cb327105ac396f985d2413e` | `FIXED` | `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_03_v1/attempts/block03_05_PySnooper__2_fixed/FIXED/environment_identity.json` | `06662fbc4dabc67111166893dacf4857629c379beeeaf7acb242adaa41b45562` | `sha256:64e176622d16315edd552c680127e84c0bece749493da32dd879ce4799bc7d95` |

## Frozen runtime, timeout gate and implementation identity

Six trials per case, ordered BUGGY 1, 2, 3 then FIXED 1, 2, 3. The required
scientific pattern remains BUGGY FAIL/FAIL/FAIL and FIXED PASS/PASS/PASS.
Ordered oracle commands use direct argv, shell=False, subject-root cwd and
fresh repository/workspace state per trial. No oracle command is executed here.
Incomplete, infrastructure-failed, interrupted or evidence-incomplete trials
cannot establish eligibility.

Timeout is exactly 300 seconds per subcommand and 900 seconds per complete
trial, including startup and teardown. The trial budget never resets between
commands. Workspace preparation precedes timing; post-trial evidence hashing
follows it. A timeout is OTHER_INFRASTRUCTURE_FAILURE /
INFRASTRUCTURE_ERROR_NOT_ELIGIBILITY, never scientific FAIL. Termination must
stop and reap the process group or complete daemon-owned container. No retry.
`PRE_EXECUTION_TIMEOUT_GATE_REQUIRED` remains True. Exact manifest/plan/runtime
hash validation satisfies the gate; absent, altered, non-integer or mismatched
300/900 authority fails closed.

Production backend identity:
`evaluation/downstream_benchmark/screening/docker_oracle_backend_v1.py`
SHA-256 `aff923b6bd9f0001b4805ce5d6a9e9cf7281b63893f62541b0d3604e0a18e0f3`.
Timeout-gate and dispatch identity:
`evaluation/downstream_benchmark/screening/v5_oracle_executor.py`
SHA-256 `3f9d4f79d382f062416b20bf7c754f9d3dc8dd7aef3c7fdfa14807c7a88b1256`.
Container-driver identity:
`evaluation/downstream_benchmark/screening/oracle_trial_driver_v1.py`
SHA-256 `f7d3a27fb398ca02af95c97112b6e3e0ea6cf5a61880a1ef3c98186c935b3e12`.

Docker semantics remain linux/amd64, exact immutable governed image ID,
--network=none, read-only rootfs, and fresh HOME/TMP/cache/workspace. Each
future trial has unique container and evidence namespaces, exact raw stream
capture and hashes. No real runner is constructed during production dry validation.
Candidate execution authority remains false, including its historical lifecycle
fields. Closure freeze alone does not authorize, publish or activate execution.

Frozen contract identities:

| Contract path relative to evaluation/downstream_benchmark | SHA-256 |
| --- | --- |
| `ORACLE_REPRESENTATION_V1.md` | `625b656495b5f1174ea1f4a07f872a42112a0be839b47c3db884dcd103a87f52` |
| `PROTOCOL.md` | `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93` |
| `RUN_SPEC_V1.md` | `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406` |
| `SCREENING_RUNTIME_V1.md` | `235b404dd32da91f28c303922ce7acfc8f58611cd78f3c365d583cb2572bb41f` |
| `SCREENING_SPEC_V1.md` | `a7f3cd5e73d6c733f560456d9f3949be18deca9b295ffb4ef2ae087af7e89db3` |

## Exact 168-slot non-executing namespace

The accepted dry evidence is
`/Users/wuyangchenxi/errpilot-benchmark-work/oracle_plans/v1_1/readiness/dry_validation_v1.json`
SHA-256 `c54577bdd64b49a457984adc1948c47871d96adb7a90486c4fa011e7c3793400`.
Execution ID is exactly `v5-readiness-dry-v1`.
The namespace is the ordered manifest's 28 case IDs crossed with exactly
[(BUGGY,1),(BUGGY,2),(BUGGY,3),(FIXED,1),(FIXED,2),(FIXED,3)].
For each case, evidence is
`/Users/wuyangchenxi/errpilot-benchmark-work/screening_evidence/<case-slug>/v5-readiness-dry-v1/runs/<schedule-index:02>-<variant-lower>-<ordinal>`.
Case-slug is canonical case ID with `::` replaced by `-`. Container name is
`ep-oracle-` plus the first 32 lowercase hex SHA-256 characters of the UTF-8
string `<case-id>|<variant>|<ordinal>|v5-readiness-dry-v1`.
All 168 concrete unique evidence paths and container names are bound by the
accepted dry evidence above. Their ordered namespace projection
{case_id,revision_label,ordinal,execution_id,evidence_path,container_name}
has compact sorted-key JSON SHA-256
`7258bcd4a2cebcb03f8f4feb057d83800bb92d73c27ba1366024d89f45e48dc9`.
Every record has boundary NON_EXECUTING_SENTINEL and executed=false.
No governed attempt/workspace/checkpoint/trial/stream path exists for this namespace.
Planned ordered command invocations = 210.

```text
PRODUCTION_DOCKER_ORACLE_BACKEND_READY = YES
PRE_EXECUTION_TIMEOUT_GATE_READY = YES
CURRENT_ORACLE_PLAN_POPULATION_READY = YES
INITIAL_19_SUCCESSOR_PLANS_READY = YES
CURRENT_28_CASE_PLAN_MANIFEST_READY = YES
ALL_28_CASES_DRY_VALIDATED = YES
PLANNED_ORACLE_REPETITIONS = 168
DRY_VALIDATED_ORACLE_REPETITIONS = 168
EXECUTED_ORACLE_REPETITIONS = 0
```

## Bounded validation evidence

Validation result: PASS. Accepted candidate/preflight bytes were not repaired or
rewritten. Repository validation remains separate from scientific validation.

- Accepted bounded suite: 173 test items passed, 0 failed; 190 subtests passed,
  0 failed; 0 errors and 0 skipped, in 4.97 seconds. Per-file item counts:
  readiness bridge 66; executor 30; environment audit 2; V5 regression 75.
  JUnit recorded 363 total outcomes including subtests; 173 testcase nodes.
- Command:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q --tb=short -p no:cacheprovider --junitxml=/private/tmp/errpilot-v5-readiness-closure-20261003-tests.xml evaluation/downstream_benchmark/tests/test_v5_oracle_readiness_bridge.py evaluation/downstream_benchmark/tests/test_screening_executor.py evaluation/downstream_benchmark/tests/test_screening_environment_audit.py evaluation/downstream_benchmark/tests/test_pre_eligibility_state_v5.py`.
- Readiness tests include fail-closed selected-plan/manifest/environment/image/
  command/cwd/timeout/lineage/repetition/evidence checks; default-deny execution;
  synthetic startup/subcommand/trial timeout accounting, termination/reaping,
  raw-stream preservation, ordered argv/no-shell semantics, Docker infrastructure
  failure classification and the common non-executing dispatch boundary.
  Existing executor tests use isolated synthetic temporary Git/process fixtures;
  bridge tests use process tripwires and fake process/Git adapters. They do not
  execute governed subjects, governed containers or real oracle repetitions.
- Non-executing production dry validation: PASS, fresh report exactly equals
  the accepted frozen dry evidence, including every one of the 168 records.
  PLANNED=168; DRY_VALIDATED=168; EXECUTED=0; sentinel arrivals=168;
  failed=0; skipped=0; 210 planned ordered command invocations.
  Popen, subprocess.run, check_output and DockerProcessRunner construction were
  denied during dry validation. No governed attempt/evidence path was created.
- Docker read-only reconciliation: PASS. Client/server version 29.4.1; all 39
  required exact immutable images present; missing=0; identity conflicts=0;
  each image linux/amd64; RootFS observations exactly equal accepted readiness
  observations and every environment identity. All 56 variant bindings pass.
  Initial sandbox metadata access was denied at the Docker socket; the explicit
  authorized elevated metadata-only query succeeded. The verifier audit hook
  permitted only docker version and docker image inspect subprocesses: two
  successful metadata calls, zero run/create/exec/build/pull calls.
- Exact frozen timeout authority 300/900 and required gate True: PASS.
- Changed-source Ruff: PASS, using
  `python3 -B -m ruff check --no-cache evaluation/downstream_benchmark/screening/v5_oracle_executor.py evaluation/downstream_benchmark/screening/docker_oracle_backend_v1.py evaluation/downstream_benchmark/screening/oracle_trial_driver_v1.py evaluation/downstream_benchmark/tests/test_v5_oracle_readiness_bridge.py`.
- Container driver AST parse with feature_version=(3,6): PASS; this is syntax
  compatibility evidence, not a historical-Python container execution test.
- V5 production-evidence validator: PASS, using
  `PYTHONDONTWRITEBYTECODE=1 python3 -m evaluation.downstream_benchmark.screening.validate_pre_eligibility_state_v5 --verify-production-evidence`.
  V4 historical relation, V5 exclusions 39 (11/26/2), capacity 28/28, admissions
  67, oracle outcomes 0, header-only cases_manifest and eligibility NO all pass.
- git diff --check: PASS. Added-file whitespace check of the exact thirteen
  approved untracked paths: PASS, including no trailing whitespace or blank EOF.
  git diff --cached --check is a mandatory later staging gate for this record.
- Preservation: PASS for all twelve accepted repository hashes, all twenty-four
  external hashes, all 472 original tracked hashes/modes, all 28 historical plan
  bytes, nine unchanged selected plans, 123 distinct preserved input paths,
  nineteen successor lineages, unique exact 28-case manifest and 56 bindings.
- Two verification-scaffolding assumptions were corrected without accepted-byte
  changes: newer-nine lineage predecessor fields are intentionally empty, and
  no-index diff status 1 with no diagnostic means added content differs from
  /dev/null. Closure inventory table ordering was made deterministic in this
  sole newly authored record. No accepted test or candidate implementation failed.

Commands also included bounded cat/sed/rg and Python -B reads, parent-blob and
SHA-256 checks, branch/HEAD/status/index/path enumeration, live read-only
ls-remote, local hook inspection and temporary verification helpers under
/private/tmp. Temporary diagnostic/helper files are excluded from the exact
repository commit inventory. No dependency installation, environment rebuilding,
subject setup, oracle/eligibility/repair/allocation or remote mutation occurred.

## Exact repository commit inventory and freeze scope

Exact repository inventory = the five historical evidence paths + the seven
accepted candidate paths listed above + this one closure record at
`evaluation/downstream_benchmark/V5_ORACLE_EXECUTION_READINESS_LIFECYCLE_CLOSURE_V1.md`.
Exact committed path count = 13; all are additions. No unrelated path enters
the commit. External artifacts remain external. The record does not include
its own hash or the future enclosing commit SHA.

Freeze fixes the production Docker backend, timeout gate, adopted plan-storage
decision, nineteen successors, current manifest, exclusive current-plan
resolution semantics, fifty-six environment bindings, 168-slot repetition
namespace and non-executing readiness evidence. Freeze makes no scientific
result, survivor, eligibility or allocation decision.

## Unchanged scientific state and execution firewall

```text
V5 = CURRENT_CANONICAL_PRE_ELIGIBILITY_STATE
cumulative metadata admissions = 67
accepted exclusions = 39
UNSUPPORTED_ENVIRONMENT = 11
DEPENDENCY_SETUP_FAILURE = 26
ORACLE_COMMAND_INVALID = 2
environment-ready = 28
required slots = 28
oracle outcomes = 0
cases_manifest = header-only
eligibility established = NO
REAL_ORACLE_COMMAND_EXECUTED = NO
TOTAL_ORACLE_REPETITIONS_EXECUTED = 0
DOCKER_RUN_EXECUTED = NO
DOCKER_CREATE_EXECUTED = NO
DOCKER_EXEC_EXECUTED = NO
DOCKER_BUILD_EXECUTED = NO
DOCKER_PULL_EXECUTED = NO
ENVIRONMENT_REBUILD_EXECUTED = NO
DEPENDENCY_INSTALLATION_EXECUTED = NO
SUBJECT_SETUP_EXECUTED = NO
ORACLE_RULE_CHANGED = NO
TIMEOUT_RULE_CHANGED = NO
PLAN_SELECTION_RULE_CHANGED = NO
ELIGIBILITY_CLASSIFICATION_PERFORMED = NO
PILOT_FINAL_ALLOCATION_PERFORMED = NO
RAW_REPAIR_EXECUTED = NO
ERRPILOT_REPAIR_EXECUTED = NO
BLOCK_04_CONSTRUCTED = NO
GIT_PUSH_PERFORMED = NO
GIT_TAG_PERFORMED = NO
```

## Risks, unknowns and next Human-PI gate

Tests and dry validation establish bounded mechanical readiness. Actual Docker
startup/mounts, historical Python execution, source restoration in governed
images, process termination and subject oracle behavior remain unexercised.
Eligibility and oracle-surviving population remain unknown. No scientific
validation or finished screening is claimed.

```text
NEXT_GATE = HUMAN_PI_REVIEW_OF_COMMITTED_V5_ORACLE_EXECUTION_READINESS_BASELINE
REMOTE_PUBLISH_NOT_AUTHORIZED
REAL_ORACLE_SCREENING_EXECUTION_REMAINS_BLOCKED_PENDING_REMOTE_PUBLISH
```

Human-PI review of the committed baseline is the recommended next action.
Publication and any real screening remain separate authority gates.
