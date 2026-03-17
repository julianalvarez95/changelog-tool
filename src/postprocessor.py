"""
Post-processing safety layer for LLM intelligence output.
Cleans, deduplicates, and enforces caps without ever crashing.
"""

_DEFAULT_IMPORTANCE = {
    "highlights": "high",
    "fixes": "medium",
    "improvements": "low",
}

_VALID_IMPORTANCE = {"high", "medium", "low"}


def validate_and_clean(intelligence: dict, config: dict) -> dict:
    """Clean and enforce constraints on LLM intelligence output.

    - Preserves `summary` string as-is (empty string if missing)
    - For each item in each section:
      - Discards if not a dict
      - Requires `title` and `description` as non-empty strings > 10 chars
      - Normalizes `domain`: if not in config domains list → "Otro"
      - Normalizes `importance`: if not high/medium/low → section default
      - Deduplicates cross-section by title.lower().strip()
    - Enforces max caps from config["llm"] as a safety net

    Always returns a valid dict with summary/highlights/fixes/improvements.
    """
    try:
        llm_cfg = config.get("llm", {})
        max_highlights = llm_cfg.get("max_highlights", 4)
        max_fixes = llm_cfg.get("max_fixes", 5)
        max_improvements = llm_cfg.get("max_improvements", 4)
        valid_domains = set(llm_cfg.get("domains", []))

        caps = {
            "highlights": max_highlights,
            "fixes": max_fixes,
            "improvements": max_improvements,
        }

        summary = intelligence.get("summary") or ""
        if not isinstance(summary, str):
            summary = ""

        seen: set[str] = set()
        result = {"summary": summary}

        for section in ("highlights", "fixes", "improvements"):
            raw_items = intelligence.get(section) or []
            default_importance = _DEFAULT_IMPORTANCE[section]
            cleaned = []
            for item in raw_items:
                if not isinstance(item, dict):
                    continue
                title = item.get("title", "")
                description = item.get("description", "")
                if not isinstance(title, str) or not isinstance(description, str):
                    continue
                title = title.strip()
                description = description.strip()
                if len(title) < 10 or len(description) < 10:
                    continue
                title_key = title.lower()
                if title_key in seen:
                    continue
                seen.add(title_key)
                domain = item.get("domain", "")
                if not isinstance(domain, str) or domain not in valid_domains:
                    domain = "Otro"
                importance = item.get("importance", "")
                if importance not in _VALID_IMPORTANCE:
                    importance = default_importance
                cleaned.append({
                    "title": title,
                    "description": description,
                    "domain": domain,
                    "importance": importance,
                })
            result[section] = cleaned[:caps[section]]

        return result
    except Exception:
        return {"summary": "", "highlights": [], "fixes": [], "improvements": []}
