import unittest
from datetime import datetime, timezone

from oss_careboard.models import RepoSnapshot, WorkItem, snapshot_from_dict, snapshot_to_dict


class SnapshotRoundTripTests(unittest.TestCase):
    def test_snapshot_round_trip(self) -> None:
        now = datetime(2026, 6, 4, 2, 0, tzinfo=timezone.utc)
        snapshot = RepoSnapshot(
            repository="example/project",
            description="A useful project",
            html_url="https://github.com/example/project",
            default_branch="main",
            stars=42,
            forks=3,
            subscribers=5,
            archived=False,
            pushed_at=now,
            issues=(
                WorkItem(
                    number=7,
                    title="Improve docs",
                    html_url="https://github.com/example/project/issues/7",
                    created_at=now,
                    updated_at=now,
                    labels=("documentation",),
                ),
            ),
            pull_requests=(),
            latest_release_name="v1.0.0",
            latest_release_url="https://github.com/example/project/releases/tag/v1.0.0",
            latest_release_published_at=now,
            fetched_at=now,
            rate_limit_remaining=42,
            rate_limit_reset_at=now,
        )

        restored = snapshot_from_dict(snapshot_to_dict(snapshot))

        self.assertEqual(restored, snapshot)


if __name__ == "__main__":
    unittest.main()
