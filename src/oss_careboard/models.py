from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


def parse_github_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class WorkItem:
    number: int
    title: str
    html_url: str
    created_at: datetime
    updated_at: datetime
    labels: tuple[str, ...] = ()
    draft: bool = False

    def idle_days(self, now: datetime) -> int:
        return max(0, (now - self.updated_at).days)

    def age_days(self, now: datetime) -> int:
        return max(0, (now - self.created_at).days)


@dataclass(frozen=True)
class RepoSnapshot:
    repository: str
    description: str
    html_url: str
    default_branch: str
    stars: int
    forks: int
    subscribers: int
    archived: bool
    pushed_at: datetime | None
    issues: tuple[WorkItem, ...]
    pull_requests: tuple[WorkItem, ...]
    latest_release_name: str | None
    latest_release_url: str | None
    latest_release_published_at: datetime | None
    fetched_at: datetime


def work_item_from_dict(data: dict[str, Any]) -> WorkItem:
    labels = tuple(
        label["name"] if isinstance(label, dict) else str(label)
        for label in data.get("labels", [])
    )
    return WorkItem(
        number=int(data["number"]),
        title=str(data["title"]),
        html_url=str(data["html_url"]),
        created_at=parse_github_time(data["created_at"]) or datetime.now(timezone.utc),
        updated_at=parse_github_time(data["updated_at"]) or datetime.now(timezone.utc),
        labels=labels,
        draft=bool(data.get("draft", False)),
    )


def snapshot_to_dict(snapshot: RepoSnapshot) -> dict[str, Any]:
    data = asdict(snapshot)
    data["pushed_at"] = isoformat(snapshot.pushed_at)
    data["latest_release_published_at"] = isoformat(snapshot.latest_release_published_at)
    data["fetched_at"] = isoformat(snapshot.fetched_at)

    for key in ("issues", "pull_requests"):
        data[key] = [
            {
                **item,
                "created_at": isoformat(getattr(snapshot, key)[index].created_at),
                "updated_at": isoformat(getattr(snapshot, key)[index].updated_at),
                "labels": list(getattr(snapshot, key)[index].labels),
            }
            for index, item in enumerate(data[key])
        ]
    return data


def snapshot_from_dict(data: dict[str, Any]) -> RepoSnapshot:
    fetched_at = parse_github_time(data.get("fetched_at")) or datetime.now(timezone.utc)
    return RepoSnapshot(
        repository=str(data["repository"]),
        description=str(data.get("description") or ""),
        html_url=str(data["html_url"]),
        default_branch=str(data.get("default_branch") or "main"),
        stars=int(data.get("stars", 0)),
        forks=int(data.get("forks", 0)),
        subscribers=int(data.get("subscribers", 0)),
        archived=bool(data.get("archived", False)),
        pushed_at=parse_github_time(data.get("pushed_at")),
        issues=tuple(work_item_from_dict(item) for item in data.get("issues", [])),
        pull_requests=tuple(
            work_item_from_dict(item) for item in data.get("pull_requests", [])
        ),
        latest_release_name=data.get("latest_release_name"),
        latest_release_url=data.get("latest_release_url"),
        latest_release_published_at=parse_github_time(
            data.get("latest_release_published_at")
        ),
        fetched_at=fetched_at,
    )

