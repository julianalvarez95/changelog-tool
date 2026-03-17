📄 PRD — Wave Changelog Intelligence V3 (AI Product Layer)
1. 📌 Overview

Nombre: Wave Changelog Intelligence V3
Tipo: AI Product Capability
Owner: Product (vos)
Stakeholders: Ops, Finance, Product, Tech Leadership

🎯 Visión

Construir una capa de inteligencia que:

Traduce cambios técnicos (git) en insights de producto accionables

🧠 Definición del producto

Wave Changelog Intelligence V3 es un sistema basado en IA (Claude) que:

Interpreta commits

Detecta iniciativas/product changes

Consolida y prioriza

Genera changelogs orientados a negocio

Clasifica por dominio funcional

2. 🚨 Problem Statement
Situación actual

El changelog:

está basado en commits

tiene ruido técnico

no escala para stakeholders

Problema real

No existe una capa que traduzca ingeniería → negocio

Impacto

Ops no entiende cambios → errores en delivery

Finance no detecta impacto → inconsistencias

Producto pierde visibilidad real de evolución

3. 🎯 Objetivos
Primary

Generar changelogs con:

< 60 segundos de lectura

orientados a impacto

sin duplicados

Identificar automáticamente:

features reales

fixes relevantes

mejoras internas

Secondary

Clasificar cambios por dominio Wave

Detectar importancia (high / medium / low)

Crear base para:

knowledge base automática

release notes

4. 👥 Usuarios
Usuario	Uso
Operaciones	Entender impacto en delivery
Finanzas	Detectar cambios en billing/contracts
Producto	Tracking de evolución
Tech	Validación técnica
5. 🧩 Scope
IN SCOPE (V3)

Prompt inteligente (Claude)

Clasificación por dominio

Deduplicación semántica

Priorización automática

Generación JSON estructurado

Output Slack-ready

OUT OF SCOPE

UI (por ahora)

Feedback loop manual (V4)

Integración con Jira (V4)

6. ⚙️ Arquitectura
High-Level
Git Logs → Preprocessing → Claude Prompt V3 → Post-processing → Output
Componentes
1. Ingesta

GitHub / Bitbucket API

Multi-repo

2. Preprocessing

Funciones:

limpiar commits

eliminar ruido

normalizar mensajes

3. 🧠 Claude Prompt V3 (CORE)

Responsabilidades:

deduplicación lógica

agrupación por feature

clasificación

scoring de importancia

reescritura product-oriented

4. Post-processing

validación de output

deduplicación adicional (embeddings)

enforcement de límites

5. Output Layer

Slack

(futuro: Notion / Confluence / Email)

7. 🧠 Diseño del Prompt (Feature Core)
Capacidades clave del prompt
1. Interpretación semántica

Detectar que múltiples commits pertenecen a:

una misma feature

un mismo bug

2. Product Thinking

Convertir:

"fix null branch id"
→ "Se corrigieron inconsistencias en filtros de personas relacionadas a branches"

3. Priorización

Clasificar:

high → features / capabilities

medium → fixes visibles

low → mejoras internas

4. Clasificación por dominio

Dominios definidos:

Deals

Talent

Contracts

Billing

UX/UI

Data

Infra

5. Síntesis ejecutiva

Generar:

"summary": "..."
8. 📊 Reglas de negocio
1. Deduplicación

Agrupar commits similares

threshold semántico

output = 1 item consolidado

2. Límites
Tipo	Max
Highlights	4
Fixes	5
Improvements	4
3. Filtro de ruido

Eliminar:

N/A

commits vacíos

mensajes genéricos

cambios irrelevantes

4. Lenguaje

Debe ser:

claro

orientado a negocio

sin jerga innecesaria

9. 🧾 Output esperado
JSON (core output)
{
  "summary": "Se mejoraron los flujos de búsqueda, gestión de contactos y consistencia de datos en Wave.",
  "highlights": [
    {
      "title": "Mejoras en búsqueda de personas",
      "description": "Se optimizó la búsqueda eliminando filtros por defecto y mejorando la relevancia de resultados.",
      "domain": "Talent",
      "importance": "high"
    }
  ]
}
Slack (renderizado)
🚀 Wave — Changelog semanal | {date}

{summary}

### Highlights
- ...

### Correcciones
- ...

### Mejoras internas
- ...
10. 📈 Métricas de éxito
Product Metrics

Reducción de bullets: -50%

Tiempo de lectura: < 60s

Adoption por stakeholders

Quality Metrics

duplicados → ~0

N/A → 0

clasificación correcta → >85%

AI Metrics

% commits agrupados correctamente

% highlights relevantes

11. ⚠️ Riesgos
Riesgo	Mitigación
Claude agrupa mal	post-processing
over-summarization	límites estrictos
pérdida de contexto	engineering output paralelo
clasificación incorrecta	dominios definidos
