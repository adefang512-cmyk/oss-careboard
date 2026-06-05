# Changelog

All notable changes to OSS Careboard will be documented here.

## [Unreleased]

### Added

- Marketplace readiness document with the compliant action-only publishing path.

## [0.6.0] - 2026-06-05

### Added

- Offline GitHub Enterprise compatibility tests for custom API base URLs,
  pagination links, rate-limit headers, and missing latest releases.
- README guidance for `--api-url` with GitHub Enterprise Server.

### Changed

- Adoption recipes now reference `v0.6.0`.

## [0.5.0] - 2026-06-05

### Added

- Adoption recipes for general triage, security-focused queues, and large
  repositories.
- Community Code of Conduct and support policy.
- Fictional offline snapshot and generated example report for installation-free
  evaluation.
- `python -m oss_careboard` module entry point and `--version` CLI flag.
- Public adoption-report issue template for permissioned, verifiable usage
  evidence.
- Machine-readable `--summary-json` output for automation consumers.
- Optional `summary-output` GitHub Action input and `summary` Action output.
- Example summary JSON artifact.

### Changed

- Adoption recipes now reference `v0.5.0`.

## [0.4.0] - 2026-06-04

### Added

- Explicit data coverage warnings when the GitHub API page limit truncates
  issue or pull request analysis.
- `+` count suffixes and "at least" language for incomplete datasets.
- Low GitHub API rate-limit warnings with reset timestamps.
- Configurable `--max-pages` CLI option and `max-pages` GitHub Action input.

### Changed

- Snapshot JSON now records pagination completeness and GitHub API rate-limit
  metadata for transparent offline rendering.

## [0.3.0] - 2026-06-04

### Added

- Repeatable `--include-label` and `--exclude-label` CLI filters.
- Comma-separated `include-labels` and `exclude-labels` GitHub Action inputs.
- Transparent filter descriptions in generated reports.
- Tests against include, exclude, case-insensitive, and CLI filter behavior.

## [0.2.0] - 2026-06-04

### Added

- Comprehensive maintainer briefing with key signals and prioritized next steps.
- Local analysis of stale work, label concentration, draft pull requests, release
  freshness, and repository activity.
- Explicit zero-cost documentation and human-review notice.

### Changed

- GitHub Action description now highlights the zero-cost maintenance briefing.

## [0.1.0] - 2026-06-04

### Added

- Zero-dependency Python CLI for GitHub repository maintenance reports.
- English and Chinese Markdown output.
- Stale issue and pull request attention queues.
- Release freshness and repository activity signals.
- Offline rendering from saved JSON snapshots.
- Reusable composite GitHub Action.
- Unit tests and community contribution files.
