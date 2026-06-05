import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from oss_careboard.models import RepoSnapshot, WorkItem
from oss_careboard.report import build_summary, render_markdown


def make_snapshot() -> RepoSnapshot:
    now = datetime(2026, 6, 4, 2, 0, tzinfo=timezone.utc)
    old = now - timedelta(days=45)
    recent = now - timedelta(days=2)
    return RepoSnapshot(
        repository="example/project",
        description="A useful project",
        html_url="https://github.com/example/project",
        default_branch="main",
        stars=42,
        forks=3,
        subscribers=5,
        archived=False,
        pushed_at=recent,
        issues=(
            WorkItem(
                number=7,
                title="Improve docs",
                html_url="https://github.com/example/project/issues/7",
                created_at=old,
                updated_at=old,
                labels=("documentation",),
            ),
            WorkItem(
                number=8,
                title="Recent issue",
                html_url="https://github.com/example/project/issues/8",
                created_at=recent,
                updated_at=recent,
            ),
        ),
        pull_requests=(
            WorkItem(
                number=9,
                title="Old draft",
                html_url="https://github.com/example/project/pull/9",
                created_at=old,
                updated_at=old,
                draft=True,
            ),
        ),
        latest_release_name=None,
        latest_release_url=None,
        latest_release_published_at=None,
        fetched_at=now,
    )


class ReportTests(unittest.TestCase):
    def test_builds_machine_readable_summary(self) -> None:
        summary = build_summary(
            make_snapshot(),
            stale_days=30,
            limit=1,
            include_labels=("documentation",),
        )

        self.assertEqual(summary["schema_version"], "1.0")
        self.assertEqual(summary["repository"]["full_name"], "example/project")
        self.assertEqual(summary["parameters"]["include_labels"], ["documentation"])
        self.assertEqual(summary["coverage"]["complete"], True)
        self.assertEqual(summary["analyzed"]["issues"], 2)
        self.assertEqual(summary["attention"]["total"], 1)
        self.assertEqual(summary["attention"]["top_label"]["name"], "documentation")
        self.assertEqual(len(summary["priority_items"]["issues"]), 1)
        self.assertEqual(summary["priority_items"]["pull_requests"], [])
        self.assertEqual(summary["suggested_actions"][0]["type"], "triage_issue")

    def test_renders_comprehensive_maintainer_briefing(self) -> None:
        report = render_markdown(make_snapshot(), stale_days=30)

        self.assertIn("## Maintainer briefing", report)
        self.assertIn("2 items need attention. Pull requests: 1; issues: 1.", report)
        self.assertIn("Oldest unattended item:", report)
        self.assertIn("Review the oldest pull request first", report)
        self.assertIn("Check 1 stale draft pull request", report)
        self.assertIn("Consider preparing a release", report)
        self.assertIn("generated locally from repository metadata", report)

    def test_renders_only_stale_items_in_attention_queues(self) -> None:
        report = render_markdown(make_snapshot(), stale_days=30)

        self.assertIn("Issues needing attention (1)", report)
        self.assertIn("#7 Improve docs", report)
        self.assertNotIn("Recent issue", report)
        self.assertIn("Pull requests needing attention (1)", report)
        self.assertIn("draft", report)

    def test_briefing_reports_clear_attention_queue(self) -> None:
        snapshot = make_snapshot()
        snapshot = replace(
            snapshot,
            latest_release_name="v1.0.0",
            latest_release_url="https://github.com/example/project/releases/tag/v1.0.0",
            latest_release_published_at=snapshot.fetched_at,
        )

        report = render_markdown(snapshot, stale_days=100)

        self.assertIn("No items currently exceed the attention threshold.", report)
        self.assertIn("Keep the current review cadence", report)

    def test_filters_attention_queue_by_label(self) -> None:
        report = render_markdown(
            make_snapshot(),
            include_labels=("Documentation",),
            exclude_labels=("wontfix",),
        )

        self.assertIn("Attention filters", report)
        self.assertIn("include any of `documentation`", report)
        self.assertIn("#7 Improve docs", report)
        self.assertNotIn("#9 Old draft", report)

    def test_excludes_attention_queue_by_label(self) -> None:
        report = render_markdown(make_snapshot(), exclude_labels=("documentation",))

        self.assertNotIn("#7 Improve docs", report)
        self.assertIn("#9 Old draft", report)

    def test_warns_when_pagination_limit_truncates_data(self) -> None:
        snapshot = replace(
            make_snapshot(),
            issues_complete=False,
            pull_requests_complete=False,
        )

        report = render_markdown(snapshot)

        self.assertIn("| Open issues analyzed | 2+ |", report)
        self.assertIn("| Open pull requests analyzed | 1+ |", report)
        self.assertIn("Issue analysis reached the configured page limit", report)
        self.assertIn("Pull request analysis reached the configured page limit", report)
        self.assertIn("At least 2 analyzed items need attention", report)

        summary = build_summary(snapshot)
        self.assertEqual(summary["coverage"]["complete"], False)
        self.assertIn("issues_page_limit_reached", summary["coverage"]["warnings"])
        self.assertEqual(summary["attention"]["complete"], False)

    def test_warns_when_api_rate_limit_is_low(self) -> None:
        snapshot = make_snapshot()
        snapshot = replace(
            snapshot,
            rate_limit_remaining=3,
            rate_limit_reset_at=snapshot.fetched_at,
        )

        report = render_markdown(snapshot)

        self.assertIn("Only 3 GitHub API requests remained", report)

    def test_uses_singular_english_grammar(self) -> None:
        snapshot = make_snapshot()
        one_day_ago = snapshot.fetched_at - timedelta(days=1)
        snapshot = replace(
            snapshot,
            issues=(snapshot.issues[0],),
            pull_requests=(),
            pushed_at=one_day_ago,
            latest_release_name="v1.0.0",
            latest_release_url="https://github.com/example/project/releases/tag/v1.0.0",
            latest_release_published_at=one_day_ago,
        )

        report = render_markdown(snapshot)

        self.assertIn("1 item needs attention", report)
        self.assertIn("`documentation` (1 item)", report)
        self.assertIn("Latest release is 1 day old", report)
        self.assertIn("last pushed 1 day ago", report)
        self.assertNotIn("1 days", report)

    def test_renders_chinese_headings(self) -> None:
        report = render_markdown(make_snapshot(), language="zh")

        self.assertIn("# 开源维护看板", report)
        self.assertIn("## 维护者综合概括", report)
        self.assertIn("此概括完全根据仓库元数据在本地生成", report)
        self.assertIn("需要关注的 Issue", report)

    def test_rejects_invalid_limit(self) -> None:
        with self.assertRaises(ValueError):
            render_markdown(make_snapshot(), limit=0)


if __name__ == "__main__":
    unittest.main()
