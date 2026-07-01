# Estado atual do projeto (retomar aqui)

**Última atualização:** 2026-07-01
**Branch:** `feat/seo-foundation`
**Como rodar testes:** ver [[rodar-testes-venv-pipenv]] — usar o python do venv pipenv.

## Onde estamos
Projeto de SEO do site `celogos.com.br`. Plano completo em [`docs/PLANO-SEO.md`](../PLANO-SEO.md)
(3 fases). **Fase 0 e Fase 1 concluídas, incluindo os follow-ups on-page** (correções por TDD; suíte
inteira verde: **36 testes**).

### Feito (Fases 0–1)
- App `seo/` criado: middleware canônico, context processor de metadados, sitemaps, views robots/llms,
  model `AuditFinding` + comando `seo_import_semrush`, `structured_data.py` (JSON-LD).
- Correções técnicas: 301 www→raiz + HSTS; canonical tag + title/description por página; sitemap/robots/llms
  (antes 404); imagens `.png`→`.webp` em /about/; 301 de `/contato_logos/`→`/contato/`; `GZipMiddleware`;
  removido fallback de CDN 403 (polyfill) no RudderStack.
- Follow-ups on-page: JSON-LD `EducationalOrganization`+`BreadcrumbList` por página; `alt` nas imagens
  de conteúdo dos serviços; conteúdo em `/contato/` (visita + NAP real) e `/integral`; refs `/static/`
  de JS/CSS migradas para `{% static %}`. Padrões em [[seo-on-page]].
- Follow-ups menores: **minificação** dos 5 fontes hand-written (`.min` via comando `seo_minify`,
  `style.css` 473→381KB, `main.js` −48%); **`manifest.webmanifest`** criado (antes 404); **imagens
  quebradas** em `medio`/`integral` (`product/40|41|42.jpg`) apontadas para arquivos reais com case exato.
- Ketch: `boot.js` do slug `centro_educacional_logos` retorna 200 (não era a fonte do 403). Ver
  [[ketch-e-recursos-externos]].
- Verificação (sem browser): 120 assets em 8 páginas retornam 200; `node --check` + paridade de blocos
  confirmam que a minificação preservou a semântica. Ver [[static-case-e-templates]].
- Baseline do audit importado: 150 findings (`import_date=2026-07-01`) no model `AuditFinding`.
- Segurança: `.gitignore` bloqueia segredos e `*.csv`. Ver decisions/gotchas.

## Próximos passos (retomar por aqui)
1. **Verificação visual final**: sem playwright/selenium no ambiente. Rodar `runserver` e conferir a olho
   (home, contato, serviços) OU instalar playwright p/ screenshots. Integridade de assets + semântica da
   minificação já validadas automaticamente.
2. **Deploy + re-crawl**: promover para produção e re-rodar o Site Audit do Semrush; comparar com o
   baseline (`AuditFinding`, `import_date=2026-07-01`) via [[importar-semrush-e-medir]].
3. **Fase 2 — monitoramento Google** (ver [[google-api-auth]]): service account read-only p/ GSC+GA4,
   PageSpeed via API key; serviços em `seo/services/google/`, models de snapshot, commands de pull.
4. **Fase 3 — loop de memória/auto-aprendizado**: comando `seo_report` comparando snapshots e anexando
   aprendizados nesta wiki.

## Ação pendente do usuário
- **Rotacionar o `client_secret` do OAuth no console GCP** (ficou em claro na árvore antes do gitignore).

## Ponteiros
- Wiki (fonte de verdade): [`docs/wiki/INDEX.md`](INDEX.md) — sempre consultar antes de tarefa de SEO.
- Plano aprovado: [`docs/PLANO-SEO.md`](../PLANO-SEO.md).
- Guia do repo: [`CLAUDE.md`](../../CLAUDE.md).
