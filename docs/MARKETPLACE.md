# GitHub Marketplace Readiness

OSS Careboard includes a reusable composite action, but publishing an action to
GitHub Marketplace has repository-structure and account-agreement requirements.

## Current Status

Ready:

- Public repository.
- Root `action.yml` metadata file.
- Unique action name, description, author, inputs, outputs, and branding.
- Versioned releases through `v0.6.0`.
- Passing GitHub Actions CI.
- Zero-cost and read-only operating model.

Not ready:

- This repository contains workflow files in `.github/workflows`.
- GitHub Marketplace publishing requires the repository owner to accept the
  GitHub Marketplace Developer Agreement in the GitHub web UI.

GitHub's publishing documentation says Marketplace action repositories must not
contain workflow files. Because this repository keeps its tests and weekly demo
workflow in `.github/workflows`, the compliant path is to publish from a
separate action-only wrapper repository or to restructure the project.

## Recommended Path

1. Keep `adefang512-cmyk/oss-careboard` as the main source, test, and release
   repository.
2. Create a public action-only wrapper repository, for example
   `adefang512-cmyk/oss-careboard-action`.
3. Include only the files necessary for the action listing:
   - `action.yml`
   - `README.md`
   - `LICENSE`
4. Make the wrapper action install a pinned OSS Careboard release, such as
   `v0.6.0`.
5. Publish the wrapper repository through GitHub's Marketplace release flow.
6. The repository owner must personally accept any Marketplace terms in GitHub's
   web UI before publishing.

## Suggested Categories

- Primary: Utilities
- Secondary: Code quality or Project management

## Listing Message

OSS Careboard is a zero-cost, read-only GitHub Action and Python CLI that turns
repository metadata into an actionable maintainer briefing. It highlights stale
issues and pull requests, release freshness, data coverage, and structured next
steps without posting comments, changing labels, or calling paid model APIs.

## Source

GitHub documentation for publishing actions in Marketplace:

<https://docs.github.com/en/actions/sharing-automations/creating-actions/publishing-actions-in-github-marketplace>
