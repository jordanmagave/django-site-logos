# Wiki do Projeto — Centro Educacional Logos (SEO)

Fonte de verdade de longo prazo do projeto (padrão Karpathy-wiki / auto-aprendizado Hermes).
**Sempre consulte este índice antes de qualquer tarefa de SEO.** Páginas são pequenas, com nome
estável, agrupadas por tipo de conhecimento. O índice de busca é derivável e descartável; o markdown
versionado é a fonte de verdade.

## Como usar
1. Antes de agir, leia as páginas relevantes abaixo (decisions/gotchas/procedures/rules).
2. Ao terminar uma sessão de trabalho, registre aprendizados duráveis como novas páginas (com evidência).
3. Cross-linke páginas com `[[nome-da-pagina]]`.

## ▶ Retomar o projeto
- **[ESTADO-ATUAL](ESTADO-ATUAL.md)** — onde estamos e próximos passos (leia primeiro ao retomar).
- [Plano completo](../PLANO-SEO.md) — as 3 fases.

## Decisions
- [seo-canonical-host](decisions/seo-canonical-host.md) — host canônico é `celogos.com.br` (sem www).
- [google-api-auth](decisions/google-api-auth.md) — auth das APIs Google via service account read-only.

## Gotchas
- [audit-semrush-baseline](gotchas/audit-semrush-baseline.md) — causas-raiz do audit Semrush 2026-07-01.
- [rodar-testes-venv-pipenv](gotchas/rodar-testes-venv-pipenv.md) — usar o python do venv pipenv p/ rodar testes.
- [ketch-e-recursos-externos](gotchas/ketch-e-recursos-externos.md) — Ketch boot.js = 200; 403 era o polyfill legado.
- [static-case-e-templates](gotchas/static-case-e-templates.md) — case-sensitive no Cloud Run + cache de templates no runserver.

## Procedures
- [importar-semrush-e-medir](procedures/importar-semrush-e-medir.md) — importar o CSV do Semrush e medir evolução.
- _(a preencher)_ submeter sitemap no Search Console, puxar GSC/PageSpeed (Fase 2).

## Rules
- [seo-on-page](rules/seo-on-page.md) — padrões on-page (title/description/canonical/JSON-LD/alt/{% static %}/conteúdo).
