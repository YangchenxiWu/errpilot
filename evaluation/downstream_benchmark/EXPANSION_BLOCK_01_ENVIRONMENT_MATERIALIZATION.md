# Expansion Block 01 environment materialization

Status: `EXPANSION_BLOCK_01_MATERIALIZATION_FIRST_PASS_COMPLETE`.

This is the first governed real environment materialization pass only. `MATERIALIZED != ELIGIBLE`; no screening or oracle was authorized or run.

## Entry and authority

- Human-PI token: `BUGSINPY_EXPANSION_BLOCK_01_MATERIALIZATION_AUTHORIZED_V1` for exactly one attempt per required identity.
- Entry repository root/branch/HEAD: `/Users/wuyangchenxi/errpilot`, `main`, `ed1e42448bc1b2661e935671102c4f6b2f5ae4f8`; live `origin/main` matched, ahead/behind `0/0`, index/worktree clean.
- Frozen block identity: `8a478d475066ab94afccf80472aa031e141ec8639296487fdd7fa572308ae02c`.
- Frozen ten-recipe ledger SHA-256: `8a9efeb613f6f175322a6c52b899efc30ddb8654b0856e5145ec92c018fc1bf1`. All ten were `BUILD_RECIPE_READY` / `UNBUILT` at entry; the expansion validator and preparation verifier passed.
- The independent-revision bridge was committed. Docker was operational. All five required frozen linux/amd64 base images passed digest, Python-version, architecture, and executable-SHA checks. Neither a previous production attempt root nor a repository result ledger existed.

## Ordered identity outcomes

| Order | Case | Identity | Outcome | Docker exit | Final image ID |
| ---: | --- | --- | --- | ---: | --- |
| 1 | `tornado::11` | SOURCE_INDEPENDENT | BUILD_FAILED | 1 | NA |
| 2 | `matplotlib::21` | SOURCE_INDEPENDENT | MATERIALIZED | 0 | `sha256:ff21817de1e2ce11e23e024ce8089c5e274ea17657b3c72f12ce4be6d6d35eb0` |
| 3 | `youtube-dl::24` | SOURCE_INDEPENDENT | MATERIALIZED | 0 | `sha256:733c286fefed8fbf678c80d3eddfa657caf1a987e5afc2c4c8593d74ea7cad88` |
| 4 | `tqdm::1` | BUGGY | BUILD_FAILED | 1 | NA |
| 4 | `tqdm::1` | FIXED | BUILD_FAILED | 1 | NA |
| 5 | `black::6` | BUGGY | MATERIALIZED | 0 | `sha256:71fd8391021dbdd01c01def245b8a80aa16f1c8da27f3c8cd47d738a601ade02` |
| 5 | `black::6` | FIXED | MATERIALIZED | 0 | `sha256:bec4af6facc284c921a91e11b2730a152b568259700c9f3eac0cdbfc07b4e02c` |
| 6 | `luigi::6` | SOURCE_INDEPENDENT | BUILD_FAILED | 1 | NA |
| 7 | `black::15` | BUGGY | MATERIALIZED | 0 | `sha256:ba9e9b1e1459f959da5e9ffbd2485ca1eab8fbca3762b59ededa0b581884d9cc` |
| 7 | `black::15` | FIXED | MATERIALIZED | 0 | `sha256:239fe4798426c4cac10464fabc68eef70df453460d66df68b7ed23bc34437b78` |
| 8 | `thefuck::8` | SOURCE_INDEPENDENT | BUILD_FAILED | 1 | NA |
| 9 | `sanic::2` | BUGGY | BUILD_FAILED | 1 | NA |
| 9 | `sanic::2` | FIXED | BUILD_FAILED | 1 | NA |
| 10 | `luigi::20` | SOURCE_INDEPENDENT | BUILD_FAILED | 1 | NA |

The order is the frozen `expansion_order` 1–10; each revision-specific case ran BUGGY then FIXED as independent production identities. A failed BUGGY build did not suppress FIXED. Every `BUILD_FAILED` was a nonzero exit from its frozen Docker dependency/setup build. In particular, tornado::11 reached the frozen `pip install unittest` action and failed; it was not skipped or rescued. The other seven failed identities stopped at frozen dependency installation. No retry, alternate index, version, Python, base image, setup, or case-specific rescue was used. Failed post-build-unobservable CSV fields are `NA`.

## Counts and case readiness

- Required identities: **14**; distinct attempted identities: **14**; duplicates: **0**; unattempted: **0**.
- `MATERIALIZED`: **6**. `BUILD_FAILED`: **8**. Other blockers: **0**.
- Environment-ready cases, requiring all their identities to materialize: **4/10** — `matplotlib::21`, `youtube-dl::24`, `black::6`, `black::15`.
- The other six cases are not environment-ready under this first pass. No eligibility classification was made.

## Evidence and audit

- External evidence root: `/Users/wuyangchenxi/errpilot-benchmark-work/environment_materialization_expansion_block_01`. The durable controller ledger, exact requests, materializer attempts, build definitions, build contexts, raw logs, probes, and audit files remain there. Controller SHA-256: `004965b6fe992b0a785b319b6c9491720b589946b40823d11841c4341dacaf84`. Audit JSON SHA-256: `cd104b6b491b031ecc183f5c87844ae63e1ad0c411fa5e9c6a723690fc703a54`.
- Every attempt has a request and recipe hash, exact frozen input hashes, build definition and `BUILD_CONTEXT_MANIFEST_V2`, raw build-log SHA-256, timestamps, Docker exit code, network policy, and materializer version/commit (`ENVIRONMENT_MATERIALIZER_V1_5` / `ed1e42448bc1b2661e935671102c4f6b2f5ae4f8`). The controller wrote `PENDING`, request, then `ATTEMPTED` durably before each dispatch and closed the result durably before advancing. Restart logic never redispatches an attempted identity.
- All eight revision-specific snapshots are history-free exact Git revisions. `SOURCE_SNAPSHOT_MANIFEST_V2` and tracked Git blob bytes/modes match; 54 safe tracked symlinks were retained as symlinks with exact target bytes across the four black snapshots. Source-independent build contexts contain zero subject source. No unsafe or escaping symlink entered a snapshot.
- All six successful final image IDs and RootFS layer sets matched saved image inspection, and current Docker inspection found those six linux/amd64 IDs. Observed Python/executable SHA, installed distribution manifest, system package manifest, and environment identity were recorded. Distribution Probe V2 used `PIP_LIST_JSON` once (Python 3.7.4) and `STDLIB_IMPORTLIB_METADATA` five times (Python 3.8.x); each probe used `--network=none` and returned exit 0. Build networking was `NETWORK_ALLOWED_RECORDED` for 12 identities and `NONE` for two, according to frozen dependency/setup requirements. Future execution network policy remains `NONE`.
- The controller compared SHA-256 manifests of all four initial-40 historical evidence directories and the Expansion Block 01 preparation directory before and after the batch; they matched. The post-build read-only audit verified all fourteen requests, recipe/log hashes, frozen Dockerfiles, source/context manifests, successful identities, and one-attempt counts. Neither `cases_manifest.csv` nor `exclusions.csv` was modified.
- The audited build definitions contain only frozen environment-construction steps. This transaction ran zero subject pytest/unittest, `run_test.sh`, `bugsinpy-test`, oracle, eligibility, ErrPilot, repair-agent, or downstream model/API commands.

## Repository validation

- `python3 -m pytest evaluation/downstream_benchmark/tests -q`: **123 passed, 2 skipped, 87 subtests passed**.
- `python3 -m evaluation.downstream_benchmark.screening.prepare_expansion_block_01 verify`: **10 ready, 0 blocked**; preparation evidence unchanged.
- Full pytest and Ruff were not required: no repository code or Python file was changed.

## Boundary and next gate

This pass establishes environment evidence only. The Human PI must decide the next governed action for the six cases without complete environments and separately authorize any screening or eligibility work. This report creates no such authority.
