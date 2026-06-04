import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from oss_careboard.cli import main


class CLITests(unittest.TestCase):
    def test_renders_saved_snapshot(self) -> None:
        snapshot = {
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
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(snapshot), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main(["--snapshot", str(path)])

        self.assertEqual(result, 0)
        self.assertIn("OSS Careboard", output.getvalue())


if __name__ == "__main__":
    unittest.main()

