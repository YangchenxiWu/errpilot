# Section-M Expansion Block 01

Status: `SECTION_M_EXPANSION_BLOCK_01_FROZEN`.

## A. Authority and controlling identities

The Human PI's 2026-09-26 instruction authorizes exactly ten additional metadata candidate identities for Block 01 and the versioned timing supplement `EXPANSION_TRIGGER_SUPPLEMENT_V1.md`. This freeze is metadata-only. `SCREENING_SPEC_V1.md` section M controls selection. The 21 accepted `NON_RETRY` exclusions establish the expansion trigger only; no environment, failure, oracle, or repair information enters candidate selection.

- Pinned BugsInPy commit: `11c5f1eea954a42132cfd06bf257766a7963e0fd`.
- Pinned BugsInPy tree: `d00ce0495ba73abe50317599f48bced3c9afe4b3`.
- Authoritative census and rank ledger: `candidate_universe.csv`, SHA-256 `78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c`.
- Sampling seed: `20260922`; rank digest: SHA-256 of `20260922|candidate|<project>::<bug_id>`, ascending digest then ascending canonical ID.
- Cumulative project cap: 4 admissions. The 40 original cases remain counted after their later disposition.

## B. Initial-40 cursor reconstruction

The 500 metadata-eligible rows were re-ranked from their frozen digests and canonical-ID tie-breaker, and their `candidate_rank` values were checked against positions 1–500. A fresh first-pass traversal from rank 1 admitted each case unless its project had already reached four admissions, stopping on admission 40. The reconstructed admission order matched every frozen `initial_selection_order` and exactly the frozen initial-40 membership. It represented 15 projects, so the conditional diversity pass in section D of `SCREENING_SPEC_V1.md` was not invoked.

The 40th admission is `httpie::4` at **global candidate rank 71**. The first traversal examined ranks 1–71 and skipped 31 capped rows, with ranks: 10, 15, 16, 17, 18, 20, 24, 28, 29, 34, 36, 37, 39, 41, 42, 44, 46, 47, 48, 52, 53, 55, 57, 60, 61, 62, 63, 64, 66, 69, 70. The expansion cursor begins strictly after rank 71; none of those earlier skipped cases is revisited. The first Block-01 row examined is rank **72**.

## C. Cumulative project counts

Counts include every original admission, including cases later excluded for environment failure. They were derived before Block-01 traversal.

| Project | Initial 40 count | After Block 01 |
| --- | ---: | ---: |
| `ansible` | 4 | 4 |
| `black` | 2 | 4 |
| `fastapi` | 3 | 3 |
| `httpie` | 3 | 3 |
| `keras` | 4 | 4 |
| `luigi` | 2 | 4 |
| `matplotlib` | 3 | 4 |
| `pandas` | 4 | 4 |
| `sanic` | 1 | 2 |
| `scrapy` | 4 | 4 |
| `spacy` | 2 | 2 |
| `thefuck` | 3 | 4 |
| `tornado` | 1 | 2 |
| `tqdm` | 1 | 2 |
| `youtube-dl` | 3 | 4 |

Initial total: **40**. Post-block total: **50**. No project exceeds four.

## D. Complete Block-01 traversal

All 31 rows from rank **72** through rank **102** were examined. `ADMIT` means metadata-eligible, outside the initial 40, and the project count before admission was below four. `SKIP_PROJECT_CAP` means the metadata-eligible row's project already had four cumulative admissions. No row in this range was previously skipped or already selected, and no metadata-ineligible row has a global candidate rank in the range. The detailed rank digests and metadata statuses are frozen in `expansion_block_01_traversal.csv`.

| Rank | Case | Project count before | Decision | Exact reason | Block order |
| ---: | --- | ---: | --- | --- | ---: |
| 72 | `tornado::11` | 1 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 1 |
| 73 | `pandas::148` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 74 | `pandas::92` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 75 | `matplotlib::21` | 3 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 2 |
| 76 | `keras::31` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 77 | `youtube-dl::24` | 3 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 3 |
| 78 | `matplotlib::30` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 79 | `pandas::36` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 80 | `pandas::147` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 81 | `tqdm::1` | 1 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 4 |
| 82 | `scrapy::38` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 83 | `pandas::106` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 84 | `pandas::8` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 85 | `matplotlib::10` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 86 | `black::6` | 2 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 5 |
| 87 | `luigi::6` | 2 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 6 |
| 88 | `black::15` | 3 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 7 |
| 89 | `thefuck::8` | 3 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 8 |
| 90 | `matplotlib::25` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 91 | `pandas::64` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 92 | `keras::20` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 93 | `youtube-dl::31` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 94 | `matplotlib::16` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 95 | `pandas::108` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 96 | `scrapy::10` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 97 | `matplotlib::5` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 98 | `thefuck::11` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 99 | `sanic::2` | 1 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 9 |
| 100 | `pandas::165` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 101 | `keras::21` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 102 | `luigi::20` | 3 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 10 |

Decision counts: `ADMIT=10`, `SKIP_PROJECT_CAP=21`, `SKIP_PREVIOUSLY_SKIPPED=0`, `SKIP_ALREADY_SELECTED=0`, `SKIP_METADATA_INELIGIBLE=0`. The ten admissions follow the frozen rank order with no replacement or feasibility optimization.

## E. Ordered admitted identities

`expansion_block_01.csv` preserves the exact selected metadata fields from `candidate_universe.csv`. Each row has `metadata_status=METADATA_ELIGIBLE`, `initial_40_member=false`, and `admission_reason=SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP`.

| Block order | Candidate rank | Case | Rank SHA-256 | Project count after admission |
| ---: | ---: | --- | --- | ---: |
| 1 | 72 | `tornado::11` | `20cefbbc68949acd4ba8cbaf2c735174237084cd46cd826e94d9fe30a0c6ba80` | 2 |
| 2 | 75 | `matplotlib::21` | `23096a597287456764902ebdc3786a11bd185c774e0a82241a7a5a4e4aafa574` | 4 |
| 3 | 77 | `youtube-dl::24` | `253c2e3c5d4d094a5b1ed618b96d698372f77e7ab3a5945509501ce166943c46` | 4 |
| 4 | 81 | `tqdm::1` | `297e68ec5df78bcd049012dbdf92ac3fbe16b3b8c98e1a91a49ac29ac1b047d9` | 2 |
| 5 | 86 | `black::6` | `2c2dd67dbdb81423708301c2ec71bcf281e089eb216d049c9d3d1aaee5ef2c76` | 3 |
| 6 | 87 | `luigi::6` | `2c8926f331aae02b41c83d3e07e61f056b8cb39365b8adef7fd4ed80a2eff080` | 3 |
| 7 | 88 | `black::15` | `2d5a1e6f4cafd1afe55ac2cdf7fc9a6f6900f408989538b993996f4bfa417314` | 4 |
| 8 | 89 | `thefuck::8` | `2d77c76c721a19af78a933730b26b139aaafe7ba02320b1183a0109caac08d4d` | 4 |
| 9 | 99 | `sanic::2` | `3378a09311b7063bb4a4b6cc609a309801ab32cde860ff6811628f61add7c3ae` | 2 |
| 10 | 102 | `luigi::20` | `33f6b35ecab0fcfa08514ac74f9d624257e71f94f61d8ba543dfeab5986ebe02` | 4 |

## F. Canonical block identity and next cursor

Canonical identity is UTF-8 JSON with lexicographically sorted keys, no spaces (`separators=(',', ':')`), JSON integer values for counts/ranks/seed, and ordered arrays as shown. No timestamp is included. The exact canonical JSON byte string is:

```json
{"block_number":1,"bugsinpy_commit":"11c5f1eea954a42132cfd06bf257766a7963e0fd","candidate_universe_sha256":"78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c","expansion_admitted_count":10,"first_examined_rank":72,"initial_admitted_count":40,"initial_cursor_rank":71,"next_cursor_rank":102,"ordered_10_candidate_ranks":[72,75,77,81,86,87,88,89,99,102],"ordered_10_case_ids":["tornado::11","matplotlib::21","youtube-dl::24","tqdm::1","black::6","luigi::6","black::15","thefuck::8","sanic::2","luigi::20"],"ordered_10_rank_sha256":["20cefbbc68949acd4ba8cbaf2c735174237084cd46cd826e94d9fe30a0c6ba80","23096a597287456764902ebdc3786a11bd185c774e0a82241a7a5a4e4aafa574","253c2e3c5d4d094a5b1ed618b96d698372f77e7ab3a5945509501ce166943c46","297e68ec5df78bcd049012dbdf92ac3fbe16b3b8c98e1a91a49ac29ac1b047d9","2c2dd67dbdb81423708301c2ec71bcf281e089eb216d049c9d3d1aaee5ef2c76","2c8926f331aae02b41c83d3e07e61f056b8cb39365b8adef7fd4ed80a2eff080","2d5a1e6f4cafd1afe55ac2cdf7fc9a6f6900f408989538b993996f4bfa417314","2d77c76c721a19af78a933730b26b139aaafe7ba02320b1183a0109caac08d4d","3378a09311b7063bb4a4b6cc609a309801ab32cde860ff6811628f61add7c3ae","33f6b35ecab0fcfa08514ac74f9d624257e71f94f61d8ba543dfeab5986ebe02"],"project_cap":4,"sampling_seed":20260922,"schema":"SECTION_M_EXPANSION_BLOCK_IDENTITY_V1","traversal_terminal_rank":102}
```

**Block identity SHA-256:** `8a478d475066ab94afccf80472aa031e141ec8639296487fdd7fa572308ae02c`.

The tenth admission and traversal terminal are at rank **102**. Block 01's next cursor is rank **102**; any separately authorized next traversal would begin strictly after it, at rank 103. This freeze authorizes no second block.

## G. Independent reproduction

A separate derivation read the frozen `candidate_rank` column as a rank-to-row map, built the starting project counts from the 40 `initial_selection_order` records, and traversed ranks 72 onward. It did not use the first derivation's digest-sort loop or its generated decisions as selection inputs. Mechanical comparison against both CSV outputs found identical ten case IDs and order, all 31 traversal decisions and reasons, terminal rank 102, and canonical block identity SHA-256 `8a478d475066ab94afccf80472aa031e141ec8639296487fdd7fa572308ae02c`.

## H. Zero-outcome and future authority boundary

No Block-01 subject repository was acquired, checked out, built, imported, or tested in this transaction. No oracle, 3/3 eligibility, pilot/final allocation, repair experiment, ErrPilot, or downstream model/API was run. The 19 environment-ready initial cases still require their separately authorized 3/3 screening; this block records no eligibility outcome. The admitted identities are metadata candidates only.

Subject acquisition, revision identity resolution, environment materialization, oracle/eligibility execution, and later allocation each require the applicable separate Human-PI authorization and controlling identity gates. Automatic repository CI after an approved push, if triggered, is classified only under `CI_SIDE_EFFECT_BOUNDARY_V1.md` as `CI_TRIGGERED_REPOSITORY_VERIFICATION` when its stated conditions hold.
