import unittest
from datetime import datetime, timezone
from io import BytesIO
from typing import Any
from unittest.mock import patch

from oss_careboard.github import GitHubClient, parse_next_link, validate_repository


class FakeHTTPResponse(BytesIO):
    def __init__(
        self,
        payload: bytes,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(payload)
        self.headers = headers or {}

    def __enter__(self) -> "FakeHTTPResponse":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class StubGitHubClient(GitHubClient):
    def __init__(self, responses: list[tuple[Any, str | None]], max_pages: int) -> None:
        super().__init__(max_pages=max_pages)
        self.responses = iter(responses)

    def _request(
        self, url_or_path: str, allow_not_found: bool = False
    ) -> tuple[Any, str | None]:
        return next(self.responses)


class ReleaseNotFoundGitHubClient(GitHubClient):
    def _request(
        self, url_or_path: str, allow_not_found: bool = False
    ) -> tuple[Any, str | None]:
        if url_or_path.endswith("/releases/latest"):
            self.assert_release_not_found_allowed = allow_not_found
            return None, None
        if url_or_path.endswith("/issues?state=open&sort=updated&direction=asc&per_page=100"):
            return [], None
        if url_or_path.endswith("/pulls?state=open&sort=updated&direction=asc&per_page=100"):
            return [], None
        return {
            "description": "Enterprise project",
            "html_url": "https://github.example.com/acme/project",
            "default_branch": "main",
            "stargazers_count": 1,
            "forks_count": 2,
            "subscribers_count": 3,
            "archived": False,
            "pushed_at": "2026-06-05T00:00:00Z",
        }, None


class GitHubHelpersTests(unittest.TestCase):
    def test_validate_repository(self) -> None:
        self.assertEqual(validate_repository("openai/openai-python"), ("openai", "openai-python"))

    def test_validate_repository_rejects_bad_slug(self) -> None:
        with self.assertRaises(ValueError):
            validate_repository("missing-owner")

    def test_parse_next_link(self) -> None:
        header = (
            '<https://api.github.com/repositories/1/issues?page=2>; rel="next", '
            '<https://api.github.com/repositories/1/issues?page=4>; rel="last"'
        )
        self.assertEqual(
            parse_next_link(header),
            "https://api.github.com/repositories/1/issues?page=2",
        )

    def test_page_limit_reports_incomplete_data(self) -> None:
        client = StubGitHubClient(
            responses=[
                (
                    [{"number": 1}],
                    '<https://api.github.com/repos/example/project/issues?page=2>; rel="next"',
                )
            ],
            max_pages=1,
        )

        items, complete = client._get_pages("/repos/example/project/issues")

        self.assertEqual(items, [{"number": 1}])
        self.assertFalse(complete)

    def test_last_page_reports_complete_data(self) -> None:
        client = StubGitHubClient(
            responses=[([{"number": 1}], None)],
            max_pages=1,
        )

        items, complete = client._get_pages("/repos/example/project/issues")

        self.assertEqual(items, [{"number": 1}])
        self.assertTrue(complete)

    def test_captures_rate_limit_headers(self) -> None:
        client = GitHubClient()
        reset = 1780588800

        client._capture_rate_limit(
            {
                "X-RateLimit-Remaining": "7",
                "X-RateLimit-Reset": str(reset),
            }
        )

        self.assertEqual(client.rate_limit_remaining, 7)
        self.assertEqual(
            client.rate_limit_reset_at,
            datetime.fromtimestamp(reset, timezone.utc),
        )

    def test_custom_enterprise_api_url_builds_expected_request(self) -> None:
        captured = {}

        def fake_urlopen(request: Any, timeout: int) -> FakeHTTPResponse:
            captured["url"] = request.full_url
            captured["authorization"] = request.get_header("Authorization")
            captured["user_agent"] = request.get_header("User-agent")
            captured["api_version"] = request.get_header("X-github-api-version")
            captured["timeout"] = timeout
            return FakeHTTPResponse(
                b'{"ok": true}',
                {
                    "Link": "",
                    "X-RateLimit-Remaining": "4999",
                    "X-RateLimit-Reset": "1780588800",
                },
            )

        client = GitHubClient(
            token="test-token",
            api_url="https://github.example.com/api/v3/",
        )
        with patch("oss_careboard.github.urlopen", fake_urlopen):
            payload, _ = client._request("/repos/acme/project")

        self.assertEqual(payload, {"ok": True})
        self.assertEqual(
            captured["url"],
            "https://github.example.com/api/v3/repos/acme/project",
        )
        self.assertEqual(captured["authorization"], "Bearer test-token")
        self.assertEqual(captured["user_agent"], "oss-careboard/0.6")
        self.assertEqual(captured["api_version"], "2022-11-28")
        self.assertEqual(captured["timeout"], 30)

    def test_enterprise_snapshot_allows_missing_latest_release(self) -> None:
        client = ReleaseNotFoundGitHubClient(
            api_url="https://github.example.com/api/v3"
        )

        snapshot = client.fetch_snapshot("acme/project")

        self.assertEqual(snapshot.repository, "acme/project")
        self.assertEqual(snapshot.html_url, "https://github.example.com/acme/project")
        self.assertIsNone(snapshot.latest_release_name)
        self.assertTrue(client.assert_release_not_found_allowed)


if __name__ == "__main__":
    unittest.main()
