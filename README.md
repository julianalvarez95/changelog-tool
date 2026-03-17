# Changelog Generator

> Turns git history into business-friendly changelogs and delivers them to the right people — automatically.

Built for teams where developers ship fast but non-technical stakeholders (executives, sales, ops) struggle to understand what changed and why. This tool bridges that gap by monitoring GitHub and Bitbucket repositories, summarizing commits using an LLM, and distributing polished changelogs via Slack and email.

**Stack:** Python · OpenAI API · GitHub API · Bitbucket API · Slack SDK · Jinja2 · SMTP

---

## Features

- **Multi-repo support** — monitors any combination of GitHub and Bitbucket repositories simultaneously
- **LLM-powered summaries** — sends all commits to GPT-4o-mini in a single call; produces an executive summary, highlights, fixes, and improvements in plain English
- **Parallel fetching** — all repos are fetched concurrently via `ThreadPoolExecutor`
- **Output cache** — LLM results are cached by date range; re-runs don't call OpenAI unless commits changed or `--no-cache` is passed
- **Fallback mode** — works without an OpenAI key; outputs categorized commits using Conventional Commits parsing
- **Flexible distribution** — Slack (bot), email (Gmail SMTP), and local Markdown file
- **Configurable templates** — Jinja2 templates for Slack, HTML email, and Markdown; fully customizable tone and categories
- **Scheduled runs** — designed for cron; persists last run timestamp to avoid duplicate changelogs

---

## How It Works

```
Fetch commits (parallel) → Parse & categorize → LLM intelligence → Render templates → Distribute
```

1. Fetches commits from all configured repos in the given date range
2. Filters noise (merges, version bumps, empty messages) and classifies by Conventional Commits type
3. Sends all commits to GPT-4o-mini → structured JSON with summary, highlights, fixes, improvements
4. Caches the LLM output for the period
5. Renders Slack message, HTML email, and Markdown via Jinja2
6. Distributes via Slack bot and/or SMTP, saves `.md` locally

---

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
cp config.example.yaml config.yaml
# Fill in tokens and repo config
python3 changelog.py --dry-run
```

---

## Configuration

### `.env`

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
BITBUCKET_USERNAME=my-username
BITBUCKET_APP_PASSWORD=xxxxxxxxxxxx
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx
GMAIL_ADDRESS=bot@company.com
GMAIL_APP_PASSWORD=xxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxx   # optional — enables LLM intelligence
```

### `config.yaml`

```yaml
changelog:
  title: "Product Updates"
  tone: "business"
  since_last_run: true

repositories:
  - name: "Backend"
    provider: github
    owner: "my-org"
    repo: "my-backend"
    branch: main

  - name: "Frontend"
    provider: bitbucket
    workspace: "my-workspace"
    repo: "my-frontend"
    branch: main

categories:
  features:
    label: "New Features"
    emoji: "🚀"
    commit_types: ["feat", "feature"]
  fixes:
    label: "Fixes"
    emoji: "🐛"
    commit_types: ["fix", "hotfix", "bugfix"]
  improvements:
    label: "Improvements"
    emoji: "⚡"
    commit_types: ["perf", "refactor", "chore", "docs", "style"]
  other:
    label: "Other Changes"
    emoji: "📋"

distribution:
  slack:
    channel: "#product-updates"
  email:
    subject: "Product Updates - {period}"
    recipients:
      - stakeholder@company.com
    from_name: "Changelog Bot"

llm:
  enabled: true
  model: "gpt-4o-mini"
  max_highlights: 4
  max_fixes: 5
  max_improvements: 4
  domains:
    - Core Product
    - Billing
    - UX/UI
    - Data
    - Infra

output:
  save_markdown: true
  output_dir: "./changelogs"
```

---

## CLI

```bash
# Run from last successful run to today
python3 changelog.py

# Dry-run: generate and print without sending
python3 changelog.py --dry-run

# Custom date range
python3 changelog.py --since 2025-03-10 --until 2025-03-17

# Skip LLM — categorized output only
python3 changelog.py --no-llm

# Force fresh LLM call (ignore cache)
python3 changelog.py --since 2025-03-10 --no-cache

# Send to one channel only
python3 changelog.py --only slack
python3 changelog.py --only email

# Save Markdown output
python3 changelog.py --dry-run --save-markdown
```

---

## Sample Output

### With LLM

```
🚀 Weekly Changelog | Mar 10 — Mar 17 2025
Multi-branch support, payment fixes, and KPI improvements shipped this week.

*Highlights*
• *Multi-Branch Support* — Users can now select and manage multiple branches from the profile dropdown. [Core Product]
• *KPI Dashboard Integration* — New data model surfacing opportunity KPIs directly in the main dashboard. [Data]

*Fixes*
• *Payment Processing Fix* — Added guards to prevent errors on contracts with missing payment data. [Billing]
• *Deleted Records Filter* — API responses now correctly exclude soft-deleted entries. [Data]

*Improvements*
• Form layout adjustments for better usability on smaller screens. [UX/UI]

_3 repos · 34 commits_
```

### Without LLM (fallback)

```
🚀 Weekly Changelog | Mar 10 — Mar 17 2025
_This week: 🚀 4 new features · 🐛 9 fixes · 📋 21 other changes_

🚀 *New Features*
• Add endpoint for opportunity KPIs [backend]
• Implement multi-branch support [backend]

🐛 *Fixes*
• Fix optional industry field in solution forms [frontend]

_3 repos · 34 commits · Mar 10 — Mar 17 2025_
```

---

## Project Structure

```
changelog-tool/
├── changelog.py              # Entry point + CLI
├── config.example.yaml       # Config template
├── .env.example
├── requirements.txt
├── templates/
│   ├── slack.j2              # Slack message template
│   ├── email.html.j2         # HTML email template
│   └── markdown.md.j2        # Markdown file template
└── src/
    ├── config.py             # Config + env loader
    ├── parser.py             # Conventional Commits parser
    ├── generator.py          # Jinja2 renderer
    ├── llm.py                # OpenAI intelligence call
    ├── postprocessor.py      # LLM output validation
    ├── fetchers/
    │   ├── github.py         # GitHub API (PyGithub)
    │   └── bitbucket.py      # Bitbucket REST API v2
    └── distributors/
        ├── slack.py          # Slack SDK
        └── email.py          # SMTP / Gmail
```

---

## Scheduling

```cron
# Every Monday at 9am
0 9 * * 1 cd /path/to/changelog-tool && python3 changelog.py >> logs/changelog.log 2>&1
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `PyGithub` | GitHub API |
| `requests` | Bitbucket REST API |
| `slack_sdk` | Slack bot |
| `jinja2` | Template rendering |
| `pyyaml` | Config parsing |
| `python-dotenv` | `.env` loading |
| `openai` | LLM intelligence (optional) |
