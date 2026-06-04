# OSS Careboard

[![Tests](https://github.com/adefang512-cmyk/oss-careboard/actions/workflows/test.yml/badge.svg)](https://github.com/adefang512-cmyk/oss-careboard/actions/workflows/test.yml)

OSS Careboard turns GitHub repository activity into a short, actionable
maintenance dashboard. It highlights issues and pull requests that have gone
quiet, shows release freshness, and works as either a zero-dependency Python
CLI or a reusable GitHub Action.

中文简介：OSS Careboard 为开源维护者自动生成维护看板，集中展示长期未更新的
Issue、PR、最近发布与仓库活跃度。项目不依赖第三方 Python 包，可作为命令行工具
或 GitHub Action 使用。

## Why

Maintainers often have enough raw notifications but not enough time to decide
what needs attention first. OSS Careboard creates a calm weekly queue without
posting comments, changing labels, or modifying repository state.

## Quick start

Requires Python 3.10 or newer.

```bash
python -m pip install .
oss-careboard --repo owner/repository
```

Authenticated requests have a higher GitHub API rate limit:

```bash
export GITHUB_TOKEN=your_read_only_token
oss-careboard --repo owner/repository --output CAREBOARD.md --json-output snapshot.json
```

Render a saved snapshot again without making an API request:

```bash
oss-careboard --snapshot snapshot.json --language zh
```

## GitHub Action

Add a weekly workflow to the repository you maintain:

```yaml
name: Weekly Careboard

on:
  workflow_dispatch:
  schedule:
    - cron: "17 2 * * 1"

permissions:
  contents: read
  issues: read
  pull-requests: read

jobs:
  careboard:
    runs-on: ubuntu-latest
    steps:
      - uses: adefang512-cmyk/oss-careboard@main
        with:
          token: ${{ github.token }}
          stale-days: "30"
          language: en
```

The generated report is added to the workflow summary. The action does not
write to the target repository.

## CLI reference

```text
--repo owner/name        Fetch a public GitHub repository
--snapshot FILE          Render a previously saved JSON snapshot
--stale-days DAYS        Attention threshold, default 30
--limit COUNT            Items shown per queue, default 10
--language en|zh         Report language
--output FILE            Write the Markdown report
--json-output FILE       Save the fetched snapshot
```

Use either `--repo` or `--snapshot`, not both.

## Privacy and permissions

- Public repositories can be read without a token, subject to GitHub rate limits.
- For private repositories, use a read-only token with permission from the owner.
- The tool never posts comments, changes labels, merges pull requests, or scans code.
- Snapshot JSON can contain issue and pull request titles. Review it before sharing.

## Development

```bash
python -m pip install .
python -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance and the
small-project roadmap.

## License

MIT
