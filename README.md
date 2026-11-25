# Private Android Source CI Runner

This repository is a **public CI control plane only**. It must never become a mirror or distribution location for the private application source.

## Source of truth

- Private application repository: `zigzag4you/personal-finance-android`
- Shared project memory for all projects: `zigzag4you/project-continuity`

## Intended operation

A workflow in this repository will, after explicit security setup, fetch a specific commit from the private source repository at runtime, build and test it, and publish only allowlisted, non-sensitive summaries.

## Security invariants

- No application source, source archives, source-bearing caches, or source-bearing artifacts are committed or uploaded here.
- No credentials, signing keys, personal financial data, production databases, or real backups are stored here.
- Cross-repository credentials must be read-only and restricted to the single private application repository.
- Never expose tokens in logs, URLs, shell tracing, caches, artifacts, or job summaries.
- Never execute untrusted pull-request code while a private-source credential is available.
- Pin third-party Actions to full commit SHAs.
- Build outputs and test reports must be reviewed for sensitive content before publication.

## Status

**Not configured.** This repository was confirmed empty before this README was added. No workflow, secret, cross-repository permission, or successful CI run has been configured or verified yet.

Do not add a workflow until the access mechanism and account Actions settings are verified. See the private repository's `docs/CI_SECURITY_BOUNDARY.md` for the full threat model.
