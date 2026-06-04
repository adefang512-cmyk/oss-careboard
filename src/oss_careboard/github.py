from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .models import RepoSnapshot, work_item_from_dict


class GitHubAPIError(RuntimeError):
    """Raised when GitHub cannot return the requested repository data."""


def validate_repository(repository: str) -> tuple[str, str]:
    parts = repository.strip().split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("repository must use the owner/name format")
    return parts[0], parts[1]


def parse_next_link(link_header: str | None) -> str | None:
    if not link_header:
        return None
    for part in link_header.split(","):
        url_part, *attributes = part.split(";")
        if any('rel="next"' in attribute for attribute in attributes):
            return url_part.strip().strip("<>")
    return None


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        api_url: str = "https://api.github.com",
        max_pages: int = 10,
    ) -> None:
        self.token = token
        self.api_url = api_url.rstrip("/")
        self.max_pages = max_pages

    def _request(self, url_or_path: str, allow_not_found: bool = False) -> tuple[Any, str | None]:
        url = (
            url_or_path
            if url_or_path.startswith(("http://", "https://"))
            else f"{self.api_url}{url_or_path}"
        )
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "oss-careboard/0.3",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            with urlopen(Request(url, headers=headers), timeout=30) as response:
                return json.load(response), response.headers.get("Link")
        except HTTPError as error:
            if allow_not_found and error.code == 404:
                return None, None
            detail = error.read().decode("utf-8", errors="replace")
            raise GitHubAPIError(f"GitHub API returned {error.code}: {detail}") from error
        except URLError as error:
            raise GitHubAPIError(f"Could not reach GitHub API: {error.reason}") from error

    def _get_pages(self, path: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        next_url: str | None = path
        page = 0
        while next_url and page < self.max_pages:
            payload, link_header = self._request(next_url)
            if not isinstance(payload, list):
                raise GitHubAPIError("GitHub API returned an unexpected response")
            items.extend(payload)
            next_url = parse_next_link(link_header)
            page += 1
        return items

    def fetch_snapshot(self, repository: str) -> RepoSnapshot:
        owner, name = validate_repository(repository)
        slug = f"{quote(owner)}/{quote(name)}"
        repo, _ = self._request(f"/repos/{slug}")
        issues = self._get_pages(
            f"/repos/{slug}/issues?state=open&sort=updated&direction=asc&per_page=100"
        )
        pulls = self._get_pages(
            f"/repos/{slug}/pulls?state=open&sort=updated&direction=asc&per_page=100"
        )
        release, _ = self._request(f"/repos/{slug}/releases/latest", allow_not_found=True)

        if not isinstance(repo, dict):
            raise GitHubAPIError("GitHub API returned an unexpected repository response")

        return RepoSnapshot(
            repository=repository,
            description=str(repo.get("description") or ""),
            html_url=str(repo["html_url"]),
            default_branch=str(repo.get("default_branch") or "main"),
            stars=int(repo.get("stargazers_count", 0)),
            forks=int(repo.get("forks_count", 0)),
            subscribers=int(repo.get("subscribers_count", 0)),
            archived=bool(repo.get("archived", False)),
            pushed_at=work_time(repo.get("pushed_at")),
            issues=tuple(
                work_item_from_dict(item) for item in issues if "pull_request" not in item
            ),
            pull_requests=tuple(work_item_from_dict(item) for item in pulls),
            latest_release_name=release.get("name") or release.get("tag_name")
            if isinstance(release, dict)
            else None,
            latest_release_url=release.get("html_url")
            if isinstance(release, dict)
            else None,
            latest_release_published_at=work_time(release.get("published_at"))
            if isinstance(release, dict)
            else None,
            fetched_at=datetime.now(timezone.utc),
        )


def work_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
