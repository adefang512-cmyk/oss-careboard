import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from oss_careboard.cli import build_parser, main


class CLITests(unittest.TestCase):
    def _snapshot(self) -> dict[str, object]:
        return {
            "repository": "example/project",
            "description": "",
            "html_url": "https://github.com/example/project",
            "default_branch": "main",
            "stars": 1,
            "forks": 0,
            "subscribers": 0,
            "archived": False,
            "pushed_at": "2026-06-03T00:00:00Z",
            "issues": [],
            "pull_requests": [],
            "latest_release_name": None,
            "latest_release_url": None,
            "latest_release_published_at": None,
            "fetched_at": "2026-06-04T00:00:00Z",
        }

    def test_renders_saved_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(self._snapshot()), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main(["--snapshot", str(path)])

        self.assertEqual(result, 0)
        self.assertIn("OSS Careboard", output.getvalue())

    def test_prints_version_without_a_source(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as exit_info:
            build_parser().parse_args(["--version"])

        self.assertEqual(exit_info.exception.code, 0)
        self.assertIn("oss-careboard 0.6.0", output.getvalue())

    def test_accepts_repeatable_label_filters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(self._snapshot()), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main(
                    [
                        "--snapshot",
                        str(path),
                        "--include-label",
                        "bug",
                        "--exclude-label",
                        "wontfix",
                    ]
                )

        self.assertEqual(result, 0)
        self.assertIn("include any of `bug`", output.getvalue())
        self.assertIn("exclude any of `wontfix`", output.getvalue())

    def test_writes_summary_json(self) -> None:
        snapshot = self._snapshot()
        snapshot["issues"] = [
            {
                "number": 1,
                "title": "Old bug",
                "html_url": "https://github.com/example/project/issues/1",
                "created_at": "2026-04-01T00:00:00Z",
                "updated_at": "2026-04-01T00:00:00Z",
                "labels": ["bug"],
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            summary_path = Path(directory) / "summary.json"
            path.write_text(json.dumps(snapshot), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main(
                    [
                        "--snapshot",
                        str(path),
                        "--summary-json",
                        str(summary_path),
                    ]
                )

            summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(summary["schema_version"], "1.0")
        self.assertEqual(summary["attention"]["issues"], 1)
        self.assertEqual(summary["priority_items"]["issues"][0]["number"], 1)

    def test_rejects_invalid_max_pages(self) -> None:
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            result = main(["--snapshot", "unused.json", "--max-pages", "0"])

        self.assertEqual(result, 2)
        self.assertIn("max_pages must be at least one", error.getvalue())


if __name__ == "__main__":
    unittest.main()
