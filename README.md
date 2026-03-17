# Changelog Generator

Herramienta que monitorea repositorios de GitHub y Bitbucket, parsea el historial de commits y distribuye changelogs en lenguaje de negocio a stakeholders no técnicos via Slack y email.

## Qué hace

1. Obtiene commits desde GitHub y Bitbucket en un rango de fechas
2. Filtra commits de merge y ruido técnico
3. Clasifica por categorías: Nuevas Funcionalidades, Correcciones, Mejoras, Otros Cambios
4. Opcionalmente, envía todos los commits a GPT-4o-mini para generar un changelog inteligente con resumen ejecutivo en inglés, títulos descriptivos y clasificación por dominio funcional
5. Renderiza el resultado con templates Jinja2 (Slack, email HTML, Markdown)
6. Distribuye por Slack y/o email, y guarda un `.md` local

## Instalación

```bash
pip install -r requirements.txt
cp .env.example .env
# Completar .env con tokens reales
```

## Configuración

### `.env`

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
BITBUCKET_USERNAME=mi-usuario
BITBUCKET_APP_PASSWORD=xxxxxxxxxxxx
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx
GMAIL_ADDRESS=bot@empresa.com
GMAIL_APP_PASSWORD=xxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxx   # opcional — habilita LLM intelligence
```

### `config.yaml`

```yaml
changelog:
  title: "Novedades del Producto"
  tone: "business"
  since_last_run: true   # usa last_run.json; alternativa: since: "2025-03-10"

repositories:
  - name: "CRM Backend"
    provider: github
    owner: "mi-org"
    repo: "crm-backend"
    branch: main

  - name: "CRM Frontend"
    provider: bitbucket
    workspace: "mi-workspace"
    repo: "crm-frontend"
    branch: main

categories:
  features:
    label: "Nuevas Funcionalidades"
    emoji: "🚀"
    commit_types: ["feat", "feature"]
  fixes:
    label: "Correcciones"
    emoji: "🐛"
    commit_types: ["fix", "hotfix", "bugfix"]
  improvements:
    label: "Mejoras"
    emoji: "⚡"
    commit_types: ["perf", "refactor", "chore", "docs", "style"]
  other:
    label: "Otros Cambios"
    emoji: "📋"

distribution:
  slack:
    channel: "#actualizaciones-producto"
  email:
    subject: "Novedades {title} - {period}"
    recipients:
      - maria@empresa.com
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

## Uso

```bash
# Run normal (desde last_run.json hasta hoy)
python3 changelog.py

# Dry-run: genera y muestra en consola sin enviar
python3 changelog.py --dry-run

# Rango de fechas manual
python3 changelog.py --since 2025-03-10 --until 2025-03-17

# Sin LLM (modo fallback, solo categorías)
python3 changelog.py --dry-run --no-llm

# Forzar llamada a OpenAI aunque exista cache para ese período
python3 changelog.py --since 2026-03-10 --no-cache

# Solo Slack
python3 changelog.py --only slack

# Solo email
python3 changelog.py --only email
```

## Modos de output

### Con LLM (`OPENAI_API_KEY` configurada)

Todos los commits de todos los repos se envían en una sola llamada a GPT-4o-mini (fetch en paralelo). El modelo produce:

- **Resumen ejecutivo** de una línea en inglés
- **Highlights** — nuevas funcionalidades o capacidades (máx. 4)
- **Correcciones** — bugs visibles al usuario (máx. 5)
- **Mejoras** — cambios internos o menores (máx. 4)

Cada ítem incluye `title`, `description`, `domain` (dominio funcional) e `importance`.

El resultado se guarda en `changelogs/.intel_cache/<since>_<until>.json`. Las re-ejecuciones del mismo período reutilizan el cache sin llamar a OpenAI. Usar `--no-cache` para forzar una llamada nueva.

```
🚀 Wave — Changelog semanal | 10 Mar — 17 Mar 2026
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

### Sin LLM (fallback)

Muestra los commits agrupados por categoría, con repo de origen y link al commit.

```
🚀 Wave — Changelog semanal | 10 Mar — 17 Mar 2026
_Esta semana: 🚀 4 nuevas funcionalidades · 🐛 9 correcciones · 📋 21 otros cambios_

🚀 *Nuevas Funcionalidades*
• Agregar endpoint para KPIs de oportunidades _Wave SVC Entity_
• Implementar soporte multi-branch _Wave Backend PHP_

🐛 *Correcciones*
• Corregir campo de industria opcional en formularios de solución _Wave Angular_

_4 repos · 34 commits · 10 Mar — 17 Mar 2026_
```

Si `OPENAI_API_KEY` no está configurada, la clave `llm.enabled` está en `false`, o se pasa `--no-llm`, el fallback se activa automáticamente sin errores.

## Estructura

```
changelog-tool/
├── changelog.py              # Entry point + CLI
├── config.yaml               # Repos, destinatarios, formato, LLM
├── .env                      # Tokens (no versionar)
├── .env.example
├── requirements.txt
├── last_run.json             # Persiste el último run exitoso
├── changelogs/
│   └── .intel_cache/         # Cache de output LLM por período (no versionado)
├── templates/
│   ├── slack.j2              # Formato Slack
│   ├── email.html.j2         # HTML para email
│   └── markdown.md.j2        # Archivo .md local
└── src/
    ├── config.py             # Carga config.yaml + .env
    ├── parser.py             # Parser de Conventional Commits
    ├── generator.py          # Renderiza Jinja2
    ├── llm.py                # LLM intelligence (OpenAI)
    ├── postprocessor.py      # Validación y limpieza del output LLM
    ├── fetchers/
    │   ├── github.py         # GitHub API via PyGithub
    │   └── bitbucket.py      # Bitbucket REST API v2
    └── distributors/
        ├── slack.py          # Envío via slack_sdk
        └── email.py          # Envío SMTP G Suite
```

## Persistencia

`last_run.json` guarda el timestamp del último run exitoso. Se actualiza automáticamente al final de cada ejecución.

```json
{
  "last_run": "2026-03-17T09:00:00+00:00",
  "changelogs_generated": 5
}
```

## Cron

```cron
# Todos los lunes a las 9am
0 9 * * 1 cd /path/to/changelog-tool && python3 changelog.py >> logs/changelog.log 2>&1
```

## Dependencias

| Paquete | Uso |
|---|---|
| `PyGithub` | GitHub API |
| `requests` | Bitbucket REST API |
| `slack_sdk` | Envío a Slack |
| `jinja2` | Renderizado de templates |
| `pyyaml` | Lectura de config.yaml |
| `python-dotenv` | Carga de .env |
| `openai` | LLM intelligence (opcional) |
