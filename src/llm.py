"""
LLM intelligence — generates a consolidated, cross-repo changelog using a single
API call. Replaces the old per-repo enrich_descriptions() approach.
"""
import json
import logging
import sys

logger = logging.getLogger(__name__)

_INTELLIGENCE_SYSTEM_PROMPT = """\
You are a Senior Product Manager for a B2B SaaS ATS/CRM platform called Wave.
Analyze git commits from multiple repos and produce a structured product changelog.

Rules:
- Group related commits into 1 item (deduplicate semantically)
- Focus on user/business impact, not technical details
- Ignore noise: merges, version bumps, config-only, empty messages
- Use clear product language — no jargon
- Classify each item by functional domain: {domains}
- Assign importance: high (new feature/capability), medium (visible fix), low (internal/minor)
- Max {max_highlights} highlights, {max_fixes} fixes, {max_improvements} improvements
- Respond entirely in English

Output ONLY valid JSON — no markdown, no explanation:
{{"summary": "1-sentence executive summary in English", \
"highlights": [{{"title": "...", "description": "...", "domain": "...", "importance": "high"}}], \
"fixes": [{{"title": "...", "description": "...", "domain": "...", "importance": "medium"}}], \
"improvements": [{{"title": "...", "description": "...", "domain": "...", "importance": "low"}}]}}\
"""


def generate_intelligence(
    all_categorized: dict,
    config: dict,
    since,
    until,
) -> dict | None:
    """Generate consolidated changelog intelligence from all repos in one LLM call.

    Args:
        all_categorized: {repo_name: {category_key: [ParsedCommit]}}
        config: full config dict
        since: datetime start of period
        until: datetime end of period

    Returns:
        dict with keys summary/highlights/fixes/improvements, or None on any failure.
    """
    api_key = config.get("_env", {}).get("openai_api_key")
    if not api_key:
        print("[WARN] OPENAI_API_KEY not set — skipping LLM intelligence.", file=sys.stderr)
        return None

    llm_cfg = config.get("llm", {})
    model = llm_cfg.get("model", "gpt-4o-mini")
    max_highlights = llm_cfg.get("max_highlights", 4)
    max_fixes = llm_cfg.get("max_fixes", 5)
    max_improvements = llm_cfg.get("max_improvements", 4)
    domains = llm_cfg.get("domains", ["Deals", "Talent", "Contracts", "Billing", "UX/UI", "Data", "Infra"])

    # Collect all commits across all repos as flat list
    commits_payload = []
    for repo_name, repo_cats in all_categorized.items():
        for commits in repo_cats.values():
            for commit in commits:
                commits_payload.append({
                    "repo": repo_name,
                    "message": commit.raw_message,
                })

    if not commits_payload:
        return None

    since_str = since.strftime("%Y-%m-%d") if since else "?"
    until_str = until.strftime("%Y-%m-%d") if until else "?"
    week_range = f"{since_str} to {until_str}"

    system_prompt = _INTELLIGENCE_SYSTEM_PROMPT.format(
        domains=", ".join(domains),
        max_highlights=max_highlights,
        max_fixes=max_fixes,
        max_improvements=max_improvements,
    )
    user_prompt = json.dumps({
        "week_range": week_range,
        "commits": commits_payload,
    }, ensure_ascii=False)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        raw = response.choices[0].message.content or ""
    except Exception as exc:
        print(f"[WARN] LLM intelligence failed: {exc} — using categorized fallback.", file=sys.stderr)
        return None

    return _parse_intelligence_response(raw)


def _parse_intelligence_response(raw: str) -> dict | None:
    """Parse and normalize LLM JSON response. Returns None on any error."""
    try:
        data = json.loads(raw)
    except Exception as exc:
        print(f"[WARN] Failed to parse LLM response as JSON: {exc}", file=sys.stderr)
        return None

    return {
        "summary": data.get("summary") or "",
        "highlights": list(data.get("highlights") or []),
        "fixes": list(data.get("fixes") or []),
        "improvements": list(data.get("improvements") or []),
    }
