import unittest

from oss_careboard.github import parse_next_link, validate_repository


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


if __name__ == "__main__":
    unittest.main()

