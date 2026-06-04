import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from oss_careboard.models import RepoSnapshot, WorkItem
from oss_careboard.report import render_markdown


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
