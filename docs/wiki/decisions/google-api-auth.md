# Decisão: autenticação nas APIs do Google para SEO

**Data:** 2026-07-01
**Status:** aprovado (a implementar na Fase 2)

## Decisão
Usar uma **service account read-only** para GSC e GA4 (padrão já usado no projeto irmão `ghost-blog`:
`blogops-reports@site-logos-471718.iam.gserviceaccount.com`), adicionada como **usuário no Search Console**
e **Viewer no GA4**. **PageSpeed Insights** usa apenas **API key**. O JSON da SA fica **fora do repo**
(path em `GOOGLE_SEO_SA_JSON`).

## Contexto / porquê
- O OAuth client "web" (`client_secret_*.json`) exige login interativo no browser — inadequado para jobs
  headless/cron.
- User-ADC (`gcloud auth application-default login`) é **bloqueado** pelo Google nos escopos restritos
  `webmasters.readonly` e `analytics.readonly` — lição já registrada no `ghost-blog`.

## APIs
- **Search Console API** (`google-api-python-client`): Search Analytics, URL Inspection, submit sitemap.
- **PageSpeed Insights API** (`requests` + API key): Core Web Vitals / Lighthouse.
- **Analytics Data API GA4** (`google-analytics-data`): comportamento/conversões.
- **Indexing API**: NÃO usar (oficialmente só JobPosting/BroadcastEvent). Usar sitemap + URL Inspection.

## Segurança
`client_secret_*.json` esteve em claro na árvore de trabalho — **rotacionar o secret** no console GCP.
`.gitignore` já bloqueia `client_secret_*.json`, `*-sa.json`, `credentials/`, `*.csv`.
