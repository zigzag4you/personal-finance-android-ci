# Private Android Source CI Runner

This repository is a **public CI control plane only**. It must never become a mirror or distribution location for the private application source.

## Source of truth

- Private application repository: `zigzag4you/personal-finance-android`
- Shared project memory for all projects: `zigzag4you/project-continuity`

## Room schema recovery workflow

The workflow at `.github/workflows/room-schema-recovery.yml` generates the three historical Room schema snapshots from exact, allowlisted private source commits:

| Schema | Source commit |
|---|---|
| v1 | `61c2cf0ebbe99071c0cc16ad0dda6510a81b515f` |
| v2 | `1f814fda9f36fa1a3b2f60be25d5d8c33fa30db4` |
| v3 | `016232db8bb587efd204a35ebb611c62e9eb65d9` |

It checks out only those fixed revisions, runs the configured Room KSP task, validates the generated version and identity hash, removes the private checkout and Gradle state, then publishes only one allowlisted schema JSON per short-lived artifact (one-day retention).

The workflow has no push, pull-request, schedule, or untrusted-code trigger. It can be started manually from the Actions tab; the initial recovery run is also triggered only by a change to this workflow file on the public runner's main branch. It uses the repository Actions secret `PRIVATE_REPO_READ_TOKEN`; the secret value is never printed or written to the repository.

## Security invariants

- No application source, source archives, source-bearing caches, or source-bearing artifacts are committed or uploaded here.
- No credentials, signing keys, personal financial data, production databases, or real backups are stored here.
- Cross-repository credentials must be read-only and restricted to the single private application repository.
- Never expose tokens in logs, URLs, shell tracing, caches, artifacts, or job summaries.
- Never execute untrusted pull-request code while a private-source credential is available.
- Third-party Actions are pinned to full commit SHAs.
- Build output is suppressed; only a non-sensitive success/failure summary is emitted.
- Only the explicitly allowlisted generated Room schema JSON is uploaded, with one-day retention.

## Current verification status

**Workflow committed; initial execution started.** The first run (ID `45813789254`) passed the secret-presence check and checked out the private v1 source. KSP generation and the remaining matrix jobs were still running at the last observation. GitHub does not expose secret values to repository readers; successful secret-presence validation is the evidence that the secret is available. No generated schema artifact is claimed until all jobs complete and artifacts are inspected.
