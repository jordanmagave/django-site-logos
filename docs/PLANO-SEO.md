# Plano: Estruturação de SEO do site Centro Educacional Logos

> Cópia versionada no repo do plano aprovado em 2026-07-01 (o original vive fora do repo, em
> `~/.claude/plans/`). Estado de execução em [`docs/wiki/ESTADO-ATUAL.md`](wiki/ESTADO-ATUAL.md).

## Contexto
O site `celogos.com.br` (Django 5.2 no Cloud Run) precisa performar melhor em SEO. Insumos: um Site Audit
do Semrush (`celogos.com.br_mega_export_20260701.csv`, 24 URLs) e as APIs do Google Cloud (projeto
`site-logos-471718`). Objetivo: elevar o audit e montar uma base **em Python** para monitorar/melhorar SEO
continuamente, mantendo o **Segment como CDP** e adotando **memória de longo prazo** (wiki auto-aprendizado
estilo Karpathy/Hermes) com **TDD**.

### Diagnóstico do audit (causa-raiz)
Ver detalhes em [`docs/wiki/gotchas/audit-semrush-baseline.md`](wiki/gotchas/audit-semrush-baseline.md).
Resumo: duplicação www×não-www (sem 301/canonical); title/description iguais em todas as páginas;
robots/sitemap/llms = 404; sem GZip e assets não-minificados; 6 imagens quebradas em /about/; recurso
externo 403 por página; rota `contato` duplicada com underscore.

### Decisões
1. Host canônico: `celogos.com.br` (sem www) — 301 de www→raiz.
2. Sequência: correções técnicas primeiro (Fase 1), depois monitoramento (Fase 2) e memória (Fase 3).
3. Auth Google: service account read-only (padrão `blogops-reports@site-logos-471718`); PageSpeed via API key.
4. Memória: wiki versionada no repo (`docs/wiki/`) + memória nativa do Claude Code.

### Método
TDD em todas as fases: teste que falha primeiro, depois implementação (`manage.py test`).

## Fase 0 — Segurança + fundação  ✅
`.gitignore` p/ segredos; app Django `seo`; esqueleto de memória (`docs/wiki/` + `MEMORY.md` nativo).

## Fase 1 — Correções técnicas de SEO (TDD)  ✅
1. Canonical host + HTTPS/HSTS (301 www→raiz).
2. `<link rel=canonical>` + title/description únicos por página (`seo/metadata.py` + context processor).
3. `sitemap.xml` (django.contrib.sitemaps, host canônico forçado).
4. `robots.txt` + `llms.txt`.
5. Imagens quebradas /about/ (`.png`→`.webp`).
6. Rota `contato` duplicada → 301 de `/contato_logos/`.
7. Compressão (`GZipMiddleware`) + **minificação (follow-up aberto)**.
8. Recurso externo 403: removido polyfill; **Ketch a validar (follow-up)**.
9. `alt`/conteúdo/JSON-LD por página **(follow-up)**.
10. Baseline: model `AuditFinding` + comando `seo_import_semrush`.

## Fase 2 — Monitoramento via APIs do Google (Python, TDD)  ⬜
Service account read-only (GSC + GA4) + API key (PageSpeed). Serviços em `seo/services/google/`
(`gsc.py`, `pagespeed.py`, `ga4.py`); models `SearchAnalyticsSnapshot`/`PageSpeedSnapshot`; commands
`seo_pull_*`; testes com clientes mockados. Emitir KPIs de SEO ao Segment (CDP).

## Fase 3 — Memória de longo prazo + auto-aprendizado  ⬜
Consolidar `docs/wiki/` (decisions/gotchas/procedures/rules). Comando `seo_report` compara snapshots e
anexa aprendizados à wiki (loop Hermes: fazer × aprender separados). Espelhar essencial na memória nativa.

## Verificação
- `python manage.py test` verde (unitários por correção; Fase 2 com mocks).
- Local: `/sitemap.xml`, `/robots.txt`, `/llms.txt` → 200; title/description/canonical distintos por página;
  /about/ sem 404 de imagem; `Host: www...` → 301 não-www; `Content-Encoding: gzip`.
- Pós-deploy: re-rodar Site Audit do Semrush e comparar com baseline (`AuditFinding`); submeter sitemap
  no Search Console; medir Core Web Vitals (PageSpeed).
