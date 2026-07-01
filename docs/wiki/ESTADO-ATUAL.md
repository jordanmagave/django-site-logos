# Estado atual do projeto (retomar aqui)

**Última atualização:** 2026-07-01
**Branch:** `feat/seo-foundation`
**Como rodar testes:** ver [[rodar-testes-venv-pipenv]] — usar o python do venv pipenv.

## Onde estamos
Projeto de SEO do site `celogos.com.br`. Plano completo em [`docs/PLANO-SEO.md`](../PLANO-SEO.md)
(3 fases). **Fase 0 e Fase 1 concluídas** (correções técnicas por TDD, 18 testes novos, suíte
inteira verde: 26 testes).

### Feito (Fases 0–1)
- App `seo/` criado: middleware canônico, context processor de metadados, sitemaps, views robots/llms,
  model `AuditFinding` + comando `seo_import_semrush`.
- Correções: 301 www→raiz + HSTS; canonical tag + title/description por página; sitemap/robots/llms
  (antes 404); imagens `.png`→`.webp` em /about/; 301 de `/contato_logos/`→`/contato/`; `GZipMiddleware`;
  removido fallback de CDN 403 (polyfill) no RudderStack.
- Baseline do audit importado: 150 findings (`import_date=2026-07-01`) no model `AuditFinding`.
- Segurança: `.gitignore` bloqueia segredos e `*.csv`. Ver decisions/gotchas.

## Próximos passos (retomar por aqui)
1. **Follow-ups da Fase 1** (não movem 100% do audit ainda): minificação JS/CSS + migrar `/static/`
   para `{% static %}`; validar 403 do Ketch `boot.js`; `alt`/conteúdo; JSON-LD por página.
   Detalhe em [[importar-semrush-e-medir]] (seção "Follow-ups").
2. **Fase 2 — monitoramento Google** (ver [[google-api-auth]]): service account read-only p/ GSC+GA4,
   PageSpeed via API key; serviços em `seo/services/google/`, models de snapshot, commands de pull.
3. **Fase 3 — loop de memória/auto-aprendizado**: comando `seo_report` comparando snapshots e anexando
   aprendizados nesta wiki.

## Ação pendente do usuário
- **Rotacionar o `client_secret` do OAuth no console GCP** (ficou em claro na árvore antes do gitignore).

## Ponteiros
- Wiki (fonte de verdade): [`docs/wiki/INDEX.md`](INDEX.md) — sempre consultar antes de tarefa de SEO.
- Plano aprovado: [`docs/PLANO-SEO.md`](../PLANO-SEO.md).
- Guia do repo: [`CLAUDE.md`](../../CLAUDE.md).
