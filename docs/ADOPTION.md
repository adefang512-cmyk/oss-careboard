# Adoption Guide

OSS Careboard is designed for incremental, read-only adoption. Start with a
workflow summary, review whether the queue is useful, and then tune the
thresholds and labels.

## Weekly general triage

```yaml
- uses: adefang512-cmyk/oss-careboard@v0.6.0
  with:
    token: ${{ github.token }}
    stale-days: "30"
    limit: "10"
```

## Security-focused queue

```yaml
- uses: adefang512-cmyk/oss-careboard@v0.6.0
  with:
    token: ${{ github.token }}
    stale-days: "7"
    include-labels: "security,vulnerability"
    exclude-labels: "duplicate,wontfix"
```

## Large repository

```yaml
- uses: adefang512-cmyk/oss-careboard@v0.6.0
  with:
    token: ${{ github.token }}
    max-pages: "25"
    limit: "20"
```

Increasing `max-pages` uses more GitHub API requests. The generated report
marks incomplete coverage and warns when the remaining API allowance is low.

## Rollout checklist

- Keep the workflow permissions read-only.
- Review the first report before sharing it broadly.
- Tune `stale-days` to match the repository's normal review cadence.
- Use label filters for queues with a clear owner or response policy.
- Invite contributors to report false priorities or missing signals.

OSS Careboard never posts comments, changes labels, closes work, or calls a
paid model API.

## Automation consumers

```yaml
- uses: adefang512-cmyk/oss-careboard@v0.6.0
  with:
    token: ${{ github.token }}
    summary-output: careboard-summary.json
```

The summary JSON includes a `schema_version`, analyzed counts, coverage
completeness, priority items, and structured suggested actions. Treat incomplete
coverage warnings as "at least this much work needs attention," not as complete
repository totals.

## GitHub Enterprise Server

Use the enterprise API base URL with the CLI:

```bash
oss-careboard --repo owner/repository --api-url https://github.example.com/api/v3
```

The project tests custom API base URLs, pagination links, rate-limit headers,
and repositories without a latest release using offline fixtures. Do not share
private enterprise server URLs, tokens, or repository snapshots in public issues.
