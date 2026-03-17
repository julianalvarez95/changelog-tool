"""
Renders changelog using Jinja2 templates.
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("[ERROR] Jinja2 not installed. Run: pip install jinja2", file=sys.stderr)
    raise

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"


def _build_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _build_intel_summary(intelligence: dict) -> str:
    """Return executive summary from intelligence, with count-based fallback."""
    if intelligence.get("summary"):
        return intelligence["summary"]

    h = len(intelligence.get("highlights") or [])
    f = len(intelligence.get("fixes") or [])
    i = len(intelligence.get("improvements") or [])

    parts = []
    if h:
        parts.append(f"{h} novedad{'es' if h != 1 else ''} relevante{'s' if h != 1 else ''}")
    if f:
        parts.append(f"{f} corrección{'es' if f != 1 else ''}")
    if i:
        parts.append(f"{i} mejora{'s' if i != 1 else ''} interna{'s' if i != 1 else ''}")

    if not parts:
        return "sin cambios"
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " y " + parts[-1]


def render(
    categorized: dict,          # {repo_name: {category_key: [ParsedCommit]}}
    config: dict,
    since: Optional[datetime],
    until: Optional[datetime],
    template_name: str,         # "email.html.j2" | "slack.j2" | "markdown.md.j2"
    intelligence: Optional[dict] = None,
) -> str:
    """Render the changelog for the given template."""
    env = _build_env()
    template = env.get_template(template_name)

    changelog_cfg = config.get("changelog", {})
    categories_cfg = config.get("categories", {})

    # Build ordered category list with label + commits across all repos
    category_data = []
    for cat_key, cat_cfg in categories_cfg.items():
        commits = []
        for repo_name, repo_cats in categorized.items():
            commits.extend(repo_cats.get(cat_key, []))
        if commits:
            category_data.append({
                "key": cat_key,
                "label": cat_cfg.get("label", cat_key.title()),
                "emoji": cat_cfg.get("emoji", ""),
                "commits": commits,
            })

    # Period string
    since_str = since.strftime("%-d %b") if since else "?"
    until_str = until.strftime("%-d %b %Y") if until else datetime.utcnow().strftime("%-d %b %Y")
    period = f"{since_str} — {until_str}"

    total_commits = sum(len(c) for cats in categorized.values() for c in cats.values())
    total_repos = len(categorized)

    summary = [
        f"{cat['emoji']} {len(cat['commits'])} {cat['label'].lower()}"
        for cat in category_data
        if cat["commits"]
    ]

    use_intelligence = intelligence is not None and any(
        intelligence.get(k) for k in ("highlights", "fixes", "improvements")
    )

    context = {
        "title": changelog_cfg.get("title", "Novedades"),
        "period": period,
        "since": since,
        "until": until,
        "categories": category_data,
        "summary": summary,
        "total_commits": total_commits,
        "total_repos": total_repos,
        "has_changes": total_commits > 0,
        "mention": config.get("distribution", {}).get("slack", {}).get("mention", ""),
        "tone": changelog_cfg.get("tone", "business"),
        "use_intelligence": use_intelligence,
        "intelligence": intelligence or {},
        "intel_summary": _build_intel_summary(intelligence) if use_intelligence else None,
    }

    return template.render(**context)
