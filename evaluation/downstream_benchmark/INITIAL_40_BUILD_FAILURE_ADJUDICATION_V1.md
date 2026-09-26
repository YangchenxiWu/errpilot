# Initial-40 build-failure adjudication V1

Status: `INITIAL_40_BUILD_FAILURE_ADJUDICATION_V1_FROZEN`. Authority: the Human PI's 2026-09-26 normative decision for exactly the 21 first-pass build-failed initial-40 cases. This V1 and its companion CSV supersede the proposal for adjudication authority; the proposal remains unchanged historical decision support.

## A. Authority and first-pass accounting

The Human PI accepts all 21 first-pass materialization failures as exclusions with `NON_RETRY`. The governed frozen environment construction policy supplied one first-pass attempt per required identity. The four frozen batch ledgers record 54 required identities across 40 initial cases. Applying the Batch-01 `keras::28` identity-completion supplement gives 25 effective `MATERIALIZED` identities, 29 `BUILD_FAILED` identities, and no other unresolved identity. At case level, 19 have every required environment identity materialized; 21 have failed required builds. Neither this decision nor a materialized environment establishes oracle eligibility.

## B. Proposal evidence and frozen records

| Historical proposal artifact | Entry SHA-256 |
| --- | --- |
| `INITIAL_40_BUILD_FAILURE_ADJUDICATION_PROPOSAL.md` | `61978c7705a7321ee34f02210df81fe9e0ded1a54b211134dd2a5901e6285fd7` |
| `initial_40_build_failure_adjudication_proposal.csv` | `a52fda84006bf8c926fa0677e153a39c4f875441672e12f976d191541f3d2bbd` |

The two proposal artifacts are committed byte-identically as proposal-only evidence. Their prior `NEEDS_HUMAN_PI_ADJUDICATION` rows remain historical, not operative. The V1 CSV and `exclusions.csv` are the normative disposition. The frozen first-pass batch ledgers, reports, Batch-01 identity-completion supplement, build logs, and attempts remain historical evidence and are not rewritten by this adjudication. Entry SHA-256 values for protected repository evidence are:

| Frozen repository artifact | Entry SHA-256 |
| --- | --- |
| `PROTOCOL.md` | `34e014a07821dc9dca52178874eef0b847aee7f048071fb4920864ae5d3bee93` |
| `RUN_SPEC_V1.md` | `29ab6f78739d0eeea1c2a774e62e2d133f173e160c3d247407970a80726f4406` |
| `SCREENING_SPEC_V1.md` | `a7f3cd5e73d6c733f560456d9f3949be18deca9b295ffb4ef2ae087af7e89db3` |
| `environment_build_recipes.csv` | `2addaf1830e61350e46583ec27b1403b43ffb0f8475b48e4bfc7d62b068b663e` |
| `ENVIRONMENT_MATERIALIZATION_BATCH_01.md` | `184fa568a6cb59685047f868799fcd012869d53d5a7409cbc8d3af68fc665f13` |
| `environment_materialization_batch_01.csv` | `d898ee0bb6d26f6b46ad387292a39df93d438e683947ff6500229b0922a1088b` |
| `ENVIRONMENT_MATERIALIZATION_BATCH_02.md` | `1aa8654030b7c026c6312828a80176a73c8d6391a6a4f9a788a5c8ed6f781a32` |
| `environment_materialization_batch_02.csv` | `fe791fc87892cc706bc0e92bdf915f17fed6e0c112fa3f542b2801ad4dfd9a62` |
| `ENVIRONMENT_MATERIALIZATION_BATCH_03.md` | `48e990f10243f4f7d29b113c897b1f6f0b826f5d11803be7fdcd02545c954adf` |
| `environment_materialization_batch_03.csv` | `2a6eb3abf0b1ef762dcca7273a329119869503d9d1aba5d484556d33afee2ebf` |
| `ENVIRONMENT_MATERIALIZATION_BATCH_04.md` | `359d832bc467b75e7f087e8f244f34e39dd915464163ec5d3de14830eefe9353` |
| `environment_materialization_batch_04.csv` | `250ae3398ab9a59dacd42f24804619c4dc2eace92b82baf2d2c8cda5b6d8792d` |
| `ENVIRONMENT_MATERIALIZATION_BATCH_01_IDENTITY_COMPLETION.md` | `1ca7ca9767d83786edca494e88f54ad4eb62ad50bfcbb32e11ed9285fe0a69af` |
| `environment_materialization_batch_01_identity_completion.csv` | `bd17f23a0cf59167a96aab91b064f00bed8f0d2c3048fa2da493332128478f47` |

## C. Final case-level adjudication

| Order | Case | Final exclusion reason | First-pass evidence |
| ---: | --- | --- | --- |
| 5 | `scrapy::4` | `UNSUPPORTED_ENVIRONMENT` | Batch-01 ledger and report; identity references in companion CSV |
| 6 | `keras::9` | `DEPENDENCY_SETUP_FAILURE` | Batch-01 ledger and report; identity references in companion CSV |
| 8 | `keras::18` | `DEPENDENCY_SETUP_FAILURE` | Batch-01 ledger and report; identity references in companion CSV |
| 11 | `luigi::31` | `DEPENDENCY_SETUP_FAILURE` | Batch-02 ledger and report; identity references in companion CSV |
| 13 | `scrapy::19` | `UNSUPPORTED_ENVIRONMENT` | Batch-02 ledger and report; identity references in companion CSV |
| 14 | `scrapy::15` | `UNSUPPORTED_ENVIRONMENT` | Batch-02 ledger and report; identity references in companion CSV |
| 15 | `keras::15` | `DEPENDENCY_SETUP_FAILURE` | Batch-02 ledger and report; identity references in companion CSV |
| 17 | `scrapy::14` | `UNSUPPORTED_ENVIRONMENT` | Batch-02 ledger and report; identity references in companion CSV |
| 18 | `thefuck::9` | `DEPENDENCY_SETUP_FAILURE` | Batch-02 ledger and report; identity references in companion CSV |
| 20 | `ansible::15` | `DEPENDENCY_SETUP_FAILURE` | Batch-02 ledger and report; identity references in companion CSV |
| 21 | `tornado::6` | `DEPENDENCY_SETUP_FAILURE` | Batch-03 ledger and report; identity references in companion CSV |
| 22 | `luigi::4` | `UNSUPPORTED_ENVIRONMENT` | Batch-03 ledger and report; identity references in companion CSV |
| 26 | `spacy::4` | `DEPENDENCY_SETUP_FAILURE` | Batch-03 ledger and report; identity references in companion CSV |
| 27 | `ansible::2` | `DEPENDENCY_SETUP_FAILURE` | Batch-03 ledger and report; identity references in companion CSV |
| 28 | `sanic::1` | `UNSUPPORTED_ENVIRONMENT` | Batch-03 ledger and report; identity references in companion CSV |
| 29 | `thefuck::26` | `DEPENDENCY_SETUP_FAILURE` | Batch-03 ledger and report; identity references in companion CSV |
| 30 | `thefuck::28` | `DEPENDENCY_SETUP_FAILURE` | Batch-03 ledger and report; identity references in companion CSV |
| 32 | `ansible::4` | `DEPENDENCY_SETUP_FAILURE` | Batch-04 ledger and report; identity references in companion CSV |
| 34 | `spacy::1` | `DEPENDENCY_SETUP_FAILURE` | Batch-04 ledger and report; identity references in companion CSV |
| 37 | `tqdm::3` | `DEPENDENCY_SETUP_FAILURE` | Batch-04 ledger and report; identity references in companion CSV |
| 39 | `ansible::16` | `DEPENDENCY_SETUP_FAILURE` | Batch-04 ledger and report; identity references in companion CSV |

The six `UNSUPPORTED_ENVIRONMENT` cases are orders 5 `scrapy::4`, 13 `scrapy::19`, 14 `scrapy::15`, 17 `scrapy::14`, 22 `luigi::4`, and 28 `sanic::1`. Their first observed blocker is frozen `pywin32==227` on `linux/amd64`.

The 15 `DEPENDENCY_SETUP_FAILURE` cases are orders 6 `keras::9`, 8 `keras::18`, 11 `luigi::31`, 15 `keras::15`, 18 `thefuck::9`, 20 `ansible::15`, 21 `tornado::6`, 26 `spacy::4`, 27 `ansible::2`, 29 `thefuck::26`, 30 `thefuck::28`, 32 `ansible::4`, 34 `spacy::1`, 37 `tqdm::3`, and 39 `ansible::16`. The observed first blockers and proposal families are retained per row in the companion CSV. For `luigi::31`, the later pywin32 declaration remains a latent, unobserved blocker; the observed first blocker was the MySQL connector pin.

The Human PI explicitly adjudicates the four formerly unresolved proposal cases `thefuck::9`, `thefuck::26`, `thefuck::28`, and `spacy::4` as `DEPENDENCY_SETUP_FAILURE`, `NON_RETRY`, and `ACCEPTED_EXCLUSION`. This is a methodological decision under the frozen benchmark, not a claim that the cases are intrinsically impossible to reproduce in every conceivable environment.

## D. NON_RETRY semantics and preserved boundary

`NON_RETRY` means no build retry for any of these 21 under the initial-40 benchmark. No later toolchain rescue, artifact redirection, dependency substitution or omission, Python/platform change, source change, recipe change, or case-specific recovery is authorized. The preregistered construction policy, one governed first-pass attempt per identity, absence of a pre-frozen exact systemic recovery rule, and risk of outcome-informed intervention support deterministic attrition handling. This adjudication does not infer later build success or failure from the first blocker.

No Docker build, dependency installation, subject setup/import/test, oracle, 3/3 screening, eligibility execution, candidate expansion, repair, ErrPilot, or downstream model/API invocation is authorized or performed in this transaction. The first-pass evidence remains immutable historical evidence.

## E. Count, expansion, and downstream gates

The initial set has 40 candidates and 21 normative environment-materialization exclusions, leaving exactly 19 environment-ready cases. `MATERIALIZED != ELIGIBLE`: none of these 19 has passed 3/3 oracle screening, so `cases_manifest.csv` remains header-only. The benchmark needs at least 28 eligible slots: 24 final cases plus four permanently separate pilot cases. Even if every remaining environment-ready case later passes its oracle gate, the initial 40 can supply at most 19 slots; deterministic expansion is therefore unavoidable independent of future oracle outcomes. This transaction selects and admits no expansion candidate.

The oracle, eligibility, pilot, final allocation, repair, ErrPilot, and model/API gates remain closed. Any expansion construction, acquisition, materialization, or screening requires a separate authorized transaction under the frozen rules; this V1 alone supplies no such authority.
