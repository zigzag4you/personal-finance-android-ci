# Private Android Source CI Runner

This repository is a **public CI control plane only**. It must never become a mirror or distribution location for the private application source.

## Source of truth

- Private application repository: `zigzag4you/personal-finance-android`
- Shared project memory for all projects: `zigzag4you/project-continuity`

## Room schema recovery workflow

The manual-only workflow at `.github/workflows/room-schema-recovery.yml` generates the three historical Room schema snapshots from exact, allowlisted private source commits:

| Schema | Source commit | Generated identity hash | Entities |
|---|---|---|---:|
| v1 | `61c2cf0ebbe99071c0cc16ad0dda6510a81b515f` | `b2862079fb29b46c2602a70c832883c1` | 6 |
| v2 | `1f814fda9f36fa1a3b2f60be25d5d8c33fa30db4` | `7c750a989b6ae29ac1ea05f3fa099784` | 7 |
| v3 | `016232db8bb587efd204a35ebb611c62e9eb65d9` | `702fba4d99cf12e95553a5414dcd0082` | 8 |

Generation succeeded across runs `45813789254` and `45814635637`. v2 required a temporary compile-only `LegacyImportDao` shim because the historical v2 commit references the DAO but omits its source file. The shim exists only in the ephemeral CI checkout, is never committed, and does not alter the Room database entity declaration or schema. All three artifacts were downloaded, parsed, SHA-256 checked against GitHub metadata and committed to the private app branch under `app/schemas/.../FinanceDatabase/`.

The workflow checks out only the fixed historical revisions, runs the configured Room KSP task, validates version, generated identity hash and exact entity set, removes the private checkout and Gradle state, then publishes only one allowlisted schema JSON per short-lived artifact (one-day retention).

## Room migration validation workflow

The manual-only workflow at `.github/workflows/room-migration-validation.yml` checks out the exact private app commit containing all three snapshots, runs the Quality Guardian Python unit suite and repository quality-profile/register validation, then runs the host-side Kotlin unit tests, lint, APK builds, and `FinanceDatabaseMigrationIntegrationTest` on an Android emulator. It covers v1→v2→v3 data preservation and the v2→v3 conversion-stage uniqueness constraint.

- Run `45815632959` failed before tests because the initial emulator profile identifier was invalid (`Pixel_2`).
- Run `45815670625` used the same initial profile and also failed during emulator setup.
- Run `45815906563` uses the corrected AVD identifier `pixel_2` and is the current migration-validation attempt.

Do not claim migration tests passed until the corrected run completes successfully.

## Security invariants

- No application source, source archives, source-bearing caches, or source-bearing artifacts are committed or uploaded here.
- No credentials, signing keys, personal financial data, production databases, or real backups are stored here.
- Cross-repository credentials must be read-only and restricted to the single private application repository.
- Never expose tokens in logs, URLs, shell tracing, caches, artifacts, or job summaries.
- Never execute untrusted pull-request code while a private-source credential is available.
- Third-party Actions are pinned to full commit SHAs.
- Gradle output is suppressed in the schema-generation workflow; only the allowlisted Room JSON is published.
- The migration workflow uses only synthetic integration-test data and publishes no artifacts.

## Current verification status

**Schema recovery: complete and committed to the private development branch. Migration validation: awaiting a user-dispatched run against private source SHA `80bc38d892f6eda48dba9595226ffbfe3edd82ee`.** The workflow runs on standard GitHub-hosted runners in this public repository, checks out the private source ephemerally with the read-only `PRIVATE_REPO_READ_TOKEN`, and removes the checkout/build state at the end. Quality Guardian tests are now included before Gradle. No run has been dispatched by the assistant.
