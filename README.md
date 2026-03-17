# Changelog Generator

A tool that monitors GitHub and Bitbucket repositories, parses the commit history, and distributes business-language changelogs to non-technical stakeholders via Slack and email.

## What It Does

1. Fetches commits from GitHub and Bitbucket within a date range
2. Filters out merge commits and technical noise
3. Classifies commits into categories: New Features, Fixes, Improvements, Other Changes
4. Optionally sends all commits to GPT-4o-mini to generate an intelligent changelog with an executive summary in English, descriptive titles, and classification by functional domain
5. Renders the result using Jinja2 templates (Slack, HTML email, Markdown)
6. Distributes via Slack and/or email, and saves a local `.md` file

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in .env with real tokens
```

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
  since_last_run: true   # uses last_run.json; alternative: since: "2025-03-10"

repositories:
  - name: "CRM Backend"
    provider: github
    owner: "my-org"
    repo: "crm-backend"
    branch: main

  - name: "CRM Frontend"
    provider: bitbucket
    workspace: "my-workspace"
    repo: "crm-frontend"
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
    subject: "Product Updates {title} - {period}"
    recipients:
      - maria@company.com
    from_name: "Changelog Bot"

llm:
  enabled: true
  model: "gpt-4o-mini"
  max_highlights: 4
  max_fixes: 5
  max_improvements: 4
  domains:
    - Deals
    - Talent
    - Contracts
    - Billing
    - UX/UI
    - Data
    - Infra

output:
  save_markdown: true
  output_dir: "./changelogs"
```

## Usage

```bash
# Normal run (from last_run.json to today)
python3 changelog.py

# Dry-run: generates and prints to console without sending
python3 changelog.py --dry-run

# Manual date range
python3 changelog.py --since 2025-03-10 --until 2025-03-17

# Without LLM (fallback mode, categories only)
python3 changelog.py --dry-run --no-llm

# Force OpenAI call even if cache exists for that period
python3 changelog.py --since 2026-03-10 --no-cache

# Slack only
python3 changelog.py --only slack

# Email only
python3 changelog.py --only email
```

## Output Modes

### With LLM (`OPENAI_API_KEY` configured)

All commits from all repos are sent in a single call to GPT-4o-mini (fetched in parallel). The model produces:

- **Executive summary** — one-line summary in English
- **Highlights** — new features or capabilities (max 4)
- **Fixes** — user-visible bugs (max 5)
- **Improvements** — internal or minor changes (max 4)

Each item includes `title`, `description`, `domain` (functional domain), and `importance`.

The result is cached at `changelogs/.intel_cache/<since>_<until>.json`. Re-runs for the same period reuse the cache without calling OpenAI. Use `--no-cache` to force a fresh call.

```
🚀 Wave — Weekly Changelog | Mar 10 — Mar 17 2026
Multi-branch support, payment fixes, and KPI improvements shipped this week.

*Highlights*
• *Multi-Branch Functionality Added* — Users can now select and manage multiple branches from the user dropdown. [Deals]
• *KPI Data Integration* — New model integrating KPI data into the OpportunityCount component. [Data]

*Fixes*
• *Contract Payment Fixes* — Checks and early returns added to prevent processing errors. [Contracts]
• *Deleted Entries Filter* — Filters applied to billing and business deal APIs for data accuracy. [Data]

*Improvements*
• Resume Builder Adjustments — Adjusted textarea rows for better usability. [UX/UI]

_4 repos · 34 commits_
```

### Without LLM (fallback)

Displays commits grouped by category, with source repo and commit link.

```
🚀 Wave — Weekly Changelog | Mar 10 — Mar 17 2026
_This week: 🚀 4 new features · 🐛 9 fixes · 📋 21 other changes_

🚀 *New Features*
• Add endpoint for opportunity KPIs _Wave SVC Entity_
• Implement multi-branch support _Wave Backend PHP_

🐛 *Fixes*
• Fix optional industry field in solution forms _Wave Angular_

_4 repos · 34 commits · Mar 10 — Mar 17 2026_
```

If `OPENAI_API_KEY` is not set, `llm.enabled` is `false`, or `--no-llm` is passed, fallback activates automatically without errors.

## Structure

```
changelog-tool/
├── changelog.py              # Entry point + CLI
├── config.yaml               # Repos, recipients, format, LLM
├── .env                      # Tokens (do not version)
├── .env.example
├── requirements.txt
├── last_run.json             # Persists the last successful run
├── changelogs/
│   └── .intel_cache/         # LLM output cache by period (not versioned)
├── templates/
│   ├── slack.j2              # Slack format
│   ├── email.html.j2         # HTML for email
│   └── markdown.md.j2        # Local .md file
└── src/
    ├── config.py             # Loads config.yaml + .env
    ├── parser.py             # Conventional Commits parser
    ├── generator.py          # Renders Jinja2
    ├── llm.py                # LLM intelligence (OpenAI)
    ├── postprocessor.py      # LLM output validation and cleanup
    ├── fetchers/
    │   ├── github.py         # GitHub API via PyGithub
    │   └── bitbucket.py      # Bitbucket REST API v2
    └── distributors/
        ├── slack.py          # Sending via slack_sdk
        └── email.py          # SMTP G Suite sending
```

## Persistence

`last_run.json` stores the timestamp of the last successful run. It is updated automatically at the end of each execution.

```json
{
  "last_run": "2026-03-17T09:00:00+00:00",
  "changelogs_generated": 5
}
```

## Cron

```cron
# Every Monday at 9am
0 9 * * 1 cd /path/to/changelog-tool && python3 changelog.py >> logs/changelog.log 2>&1
```

## Dependencies

| Package | Usage |
|---|---|
| `PyGithub` | GitHub API |
| `requests` | Bitbucket REST API |
| `slack_sdk` | Send to Slack |
| `jinja2` | Template rendering |
| `pyyaml` | Read config.yaml |
| `python-dotenv` | Load .env |
| `openai` | LLM intelligence (optional) |
