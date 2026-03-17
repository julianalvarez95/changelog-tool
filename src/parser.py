"""
Conventional Commits parser and commit categorizer.
"""
import re
from dataclasses import dataclass, field
from typing import Optional

# Regex for Conventional Commits: type(scope)!: description
CC_PATTERN = re.compile(
    r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<description>.+)",
    re.DOTALL,
)

BREAKING_FOOTER = re.compile(r"BREAKING[\s-]CHANGE\s*:", re.IGNORECASE)

# Patterns for merge/noise commits that should be discarded
_NOISE_PATTERNS = re.compile(
    r"^(Merged?\s+(in|branch|pull request|remote-tracking)\b"
    r"|Merge pull request #"
    r"|Merge branch\b"
    r"|Merged\s+\w.*\s+into\b)",
    re.IGNORECASE,
)


def _is_noise_commit(message: str) -> bool:
    """Return True if the commit is a merge/noise commit that should be discarded."""
    first_line = message.strip().splitlines()[0].strip()
    return bool(_NOISE_PATTERNS.match(first_line))


def _clean_description(description: str) -> str:
    """Capitalize first letter and strip trailing period."""
    if not description:
        return description
    desc = description.strip()
    # Strip trailing period
    if desc.endswith("."):
        desc = desc[:-1]
    # Capitalize first letter
    desc = desc[0].upper() + desc[1:] if len(desc) > 1 else desc.upper()
    return desc


@dataclass
class ParsedCommit:
    sha: str
    raw_message: str
    commit_type: Optional[str]        # feat, fix, chore, etc.
    scope: Optional[str]
    description: str                   # clean, human-readable description
    is_breaking: bool
    category: str                      # features | fixes | improvements | other
    repo_name: str
    url: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None


def _default_categories() -> dict:
    return {
        "features": {
            "label": "Nuevas Funcionalidades",
            "commit_types": ["feat", "feature"],
        },
        "fixes": {
            "label": "Correcciones",
            "commit_types": ["fix", "hotfix", "bugfix"],
        },
        "improvements": {
            "label": "Mejoras",
            "commit_types": ["perf", "refactor", "chore", "docs", "style"],
        },
        "other": {
            "label": "Otros Cambios",
        },
    }


def _build_type_map(categories: dict) -> dict[str, str]:
    """Return {commit_type: category_key} mapping."""
    mapping = {}
    for key, cfg in categories.items():
        for t in cfg.get("commit_types", []):
            mapping[t.lower()] = key
    return mapping


def parse_commit(
    sha: str,
    message: str,
    repo_name: str,
    categories: dict = None,
    url: str = None,
    author: str = None,
    date: str = None,
) -> ParsedCommit:
    """Parse a single commit message and return a ParsedCommit."""
    if categories is None:
        categories = _default_categories()

    type_map = _build_type_map(categories)

    # Only use the first line for type/scope parsing
    first_line = message.strip().splitlines()[0].strip()
    match = CC_PATTERN.match(first_line)

    is_breaking = bool(BREAKING_FOOTER.search(message))

    if match:
        commit_type = match.group("type").lower()
        scope = match.group("scope")
        description = _clean_description(match.group("description").strip())
        if match.group("breaking"):
            is_breaking = True
        category = type_map.get(commit_type, "other")
    else:
        commit_type = None
        scope = None
        description = _clean_description(first_line)
        category = "other"

    return ParsedCommit(
        sha=sha,
        raw_message=message,
        commit_type=commit_type,
        scope=scope,
        description=description,
        is_breaking=is_breaking,
        category=category,
        repo_name=repo_name,
        url=url,
        author=author,
        date=date,
    )


def categorize_commits(
    raw_commits: list[dict],
    repo_name: str,
    categories: dict = None,
) -> dict[str, list[ParsedCommit]]:
    """
    raw_commits: list of dicts with keys: sha, message, url, author, date
    Returns: {category_key: [ParsedCommit, ...]}
    """
    if categories is None:
        categories = _default_categories()

    result: dict[str, list] = {key: [] for key in categories}

    for rc in raw_commits:
        message = rc.get("message", "")
        if _is_noise_commit(message):
            continue
        parsed = parse_commit(
            sha=rc.get("sha", ""),
            message=message,
            repo_name=repo_name,
            categories=categories,
            url=rc.get("url"),
            author=rc.get("author"),
            date=rc.get("date"),
        )
        result[parsed.category].append(parsed)

    return result
