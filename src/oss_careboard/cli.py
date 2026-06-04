from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .github import GitHubAPIError, GitHubClient
from .models import snapshot_from_dict, snapshot_to_dict
from .report import render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-careboard",
        description="Generate an actionable maintenance dashboard for a GitHub repository.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--repo", help="GitHub repository in owner/name format.")
    source.add_argument("--snapshot", type=Path, help="Render a previously saved JSON snapshot.")
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub token. Defaults to the GITHUB_TOKEN environment variable.",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("GITHUB_API_URL", "https://api.github.com"),
        help="GitHub API base URL.",
    )
    parser.add_argument("--stale-days", type=int, default=30)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--language", choices=("en", "zh"), default="en")
    parser.add_argument(
        "--include-label",
        action="append",
        default=[],
        help="Only include attention items with this label. Repeat for multiple labels.",
    )
    parser.add_argument(
        "--exclude-label",
        action="append",
        default=[],
        help="Exclude attention items with this label. Repeat for multiple labels.",
    )
    parser.add_argument("--output", type=Path, help="Write Markdown to this path.")
    parser.add_argument("--json-output", type=Path, help="Write the raw snapshot to this path.")
    return parser


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.snapshot:
            data = json.loads(args.snapshot.read_text(encoding="utf-8"))
            snapshot = snapshot_from_dict(data)
        else:
            snapshot = GitHubClient(token=args.token, api_url=args.api_url).fetch_snapshot(
                args.repo
            )

        report = render_markdown(
            snapshot,
            stale_days=args.stale_days,
            limit=args.limit,
            language=args.language,
            include_labels=args.include_label,
            exclude_labels=args.exclude_label,
        )
        if args.output:
            _write(args.output, report)
        else:
            print(report, end="")

        if args.json_output:
            _write(
                args.json_output,
                json.dumps(snapshot_to_dict(snapshot), ensure_ascii=False, indent=2) + "\n",
            )
        return 0
    except (GitHubAPIError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"oss-careboard: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
