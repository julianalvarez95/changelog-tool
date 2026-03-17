# 📄 PRD — Wave Changelog Intelligence (v2)

## 1. 📌 Overview

**Nombre:** Wave Changelog Intelligence
**Tipo:** Internal Product Tool
**Owner:** Product (vos)
**Objetivo:** Transformar git logs en **changelogs de producto claros, deduplicados y orientados a impacto**

---

## 2. 🎯 Problem Statement

Actualmente:

* Los changelogs son **derivados directamente de commits**
* Contienen:

  * ruido técnico
  * duplicados
  * mala clasificación
  * bajo valor para stakeholders

👉 Resultado:
**Ops, Finance y Leadership no consumen el changelog**

---

## 3. 🎯 Objetivos

### Primary Goals

* Generar changelogs **legibles en < 1 minuto**
* Reducir ruido en un **60%+**
* Mejorar comprensión cross-team (Ops, Finance, Product)

### Secondary Goals

* Trazabilidad a repos / PRs
* Base para futura **knowledge base automática**

---

## 4. 👥 Usuarios

| Usuario     | Necesidad                             |
| ----------- | ------------------------------------- |
| Operaciones | Entender qué cambió en delivery       |
| Finanzas    | Detectar impacto en billing/contracts |
| Producto    | Seguimiento de releases               |
| Tech        | Debug + tracking                      |

---

## 5. 🧩 Scope

## IN SCOPE (v1)

* Ingesta de commits (multi-repo)
* Clasificación automática
* Deduplicación semántica
* Agrupación por feature/capability
* Reescritura orientada a producto
* Generación de output Slack-ready

## OUT OF SCOPE (v1)

* UI frontend
* Integración con Jira
* Feedback loop humano (v2)

---

# 6. ⚙️ Arquitectura

## High Level Flow

```
Git Logs → Normalization → AI Processing → Post-processing → Output
```

---

## Componentes

### 1. **Ingestor**

* Input: git log / GitHub API / Bitbucket
* Output:

```json
{
  "repo": "wave-angular",
  "message": "...",
  "author": "...",
  "date": "...",
  "hash": "..."
}
```

---

### 2. **Normalizer**

* Limpia:

  * merges
  * commits vacíos
  * mensajes basura

Reglas:

* eliminar:

  * "merge branch"
  * "fix typo"
  * "minor"
  * "N/A"

---

### 3. **Claude Processing Engine (CORE)**

👉 Este es el corazón del PRD

#### Input:

Lista de commits limpios

#### Output:

```json
{
  "highlights": [],
  "fixes": [],
  "improvements": []
}
```

---

## 7. 🧠 Prompt Design (Claude Code)

### System Prompt

```text
You are a Senior Product Manager for a B2B SaaS (ATS/CRM platform).

Your task is to transform raw git commits into a structured product changelog.

Rules:
- Focus on user impact, not technical implementation
- Merge related commits into a single item
- Remove duplicates
- Ignore low-value or unclear commits
- Rewrite everything in clear product language
- Group into:
  - highlights (major changes)
  - fixes (bugs)
  - improvements (minor / internal)

Constraints:
- Max 5 highlights
- Max 7 fixes
- Max 5 improvements
- Each item must be 1 sentence
- Avoid technical jargon unless necessary

Output format must be JSON.
```

---

### User Prompt (dinámico)

```json
{
  "week_range": "2026-03-10 to 2026-03-17",
  "commits": [
    {
      "repo": "wave-angular",
      "message": "Improve company selection process and reset owner branch when necessary"
    },
    ...
  ]
}
```

---

## 8. 🧪 Post-processing Layer

Después de Claude:

### 1. Deduplication (extra safety)

* cosine similarity (embeddings)
* threshold: 0.85

### 2. Validation rules

* eliminar items con:

  * "N/A"
  * longitud < 10 chars
  * duplicados exactos

### 3. Enrichment

Agregar:

* repo tags
* conteo commits

---

## 9. 🧾 Output

## Slack Format

```text
🚀 Wave — Changelog semanal | {date_range}

Esta semana se liberaron {X} mejoras relevantes, {Y} correcciones y mejoras internas.

### Highlights
- ...

### Correcciones
- ...

### Mejoras
- ...

{repos} repos · {commits} commits
```

---

## 10. 📊 Reglas de negocio clave

### 1. Deduplicación semántica

Ejemplo:

INPUT:

* "Add current branch info to persona"
* "Include current branch in profile"
* "Add branch to responses"

OUTPUT:
→ 1 solo bullet consolidado

---

### 2. Clasificación

| Tipo        | Regla                         |
| ----------- | ----------------------------- |
| Highlight   | nuevas capacidades o features |
| Fix         | bug / error                   |
| Improvement | UX, refactor, interno         |

---

### 3. Filtro de ruido

Eliminar commits con:

* bajo contexto
* mensajes genéricos
* cambios internos irrelevantes

---

## 11. 📈 Métricas de éxito

### Product Metrics

* % reducción de bullets (target: -50%)
* Tiempo de lectura (< 60s)
* Adoption por stakeholders

### Quality Metrics

* Duplicados detectados (↓)
* Items “N/A” (0)
* Clasificación correcta (>80%)

---

## 12. ⚠️ Riesgos

| Riesgo                  | Mitigación                   |
| ----------------------- | ---------------------------- |
| Claude agrupa mal       | post-processing + thresholds |
| Over-summarization      | límite de consolidación      |
| pérdida de info técnica | generar “engineering mode”   |
| mala clasificación      | feedback loop (v2)           |

---

## 13. 🚀 Roadmap

### v1 (este PRD)

* pipeline básico
* Claude summarization
* Slack output

### v2

* feedback humano
* UI simple
* edición manual

### v3

* integración con:

  * Jira
  * HubSpot
  * Wave analytics

---

## 14. 💡 Extensiones futuras (muy alineado a tu visión)

* Knowledge Base auto-generada desde changelogs
* Release notes por cliente
* Tracking de impacto por feature
* AI tagging por dominio:

  * Deals
  * Contracts
  * Billing
  * Talent

---

# 15. 🔥 Recomendación estratégica (clave)

No lo pienses como:

> “un bot que resume commits”

Pensalo como:

> **“la capa de traducción entre ingeniería y negocio en Wave”**

Esto puede escalar a:

* documentación automática
* onboarding
* auditoría
* reporting ejecutivo

