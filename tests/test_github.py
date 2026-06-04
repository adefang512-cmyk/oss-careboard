import unittest
from datetime import datetime, timezone
from typing import Any

from oss_careboard.github import GitHubClient, parse_next_link, validate_repository


class StubGitHubClient(GitHubClient):
    def __init__(self, responses: list[tuple[Any, str | None]], max_pages: int) -> None:
        super().__init__(max_pages=max_pages)
        self.responses = iter(responses)

    def _request(
        self, url_or_path: str, allow_not_found: bool = False
    ) -> tuple[Any, str | None]:
        return next(self.responses)


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


if __name__ == "__main__":
    unittest.main()
