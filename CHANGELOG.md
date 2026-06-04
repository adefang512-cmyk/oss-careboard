# Changelog

All notable changes to OSS Careboard will be documented here.

## [Unreleased]

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
