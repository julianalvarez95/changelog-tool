"""
Fetch commits from GitHub API using PyGithub.
"""
import sys
from datetime import datetime, timezone
from typing import Optional

try:
    from github import Github, GithubException
except ImportError:
    print("[ERROR] PyGithub not installed. Run: pip install PyGithub", file=sys.stderr)
    raise


def fetch_commits(
    token: str,
    owner: str,
    repo: str,
    branch: str = "main",
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> list[dict]:
    """
    Fetch commits from a GitHub repo between since and until.
    Returns list of dicts: {sha, message, url, author, date}
    """
    if not token:
        print(f"[ERROR] GITHUB_TOKEN is required to fetch from {owner}/{repo}", file=sys.stderr)
        return []

    try:
        g = Github(token)
        repository = g.get_repo(f"{owner}/{repo}")
        kwargs = {"sha": branch}
        if since:
            kwargs["since"] = since
        if until:
            kwargs["until"] = until

        commits = repository.get_commits(**kwargs)
        result = []
        for c in commits:
            result.append({
                "sha": c.sha[:8],
                "message": c.commit.message,
                "url": c.html_url,
                "author": c.commit.author.name if c.commit.author else "Unknown",
                "date": c.commit.author.date.isoformat() if c.commit.author else None,
            })
        print(f"[github] Fetched {len(result)} commits from {owner}/{repo}@{branch}")
        return result

    except GithubException as e:
        print(f"[ERROR] GitHub API error for {owner}/{repo}: {e.status} {e.data}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error fetching from GitHub ({owner}/{repo}): {e}", file=sys.stderr)
        return []
