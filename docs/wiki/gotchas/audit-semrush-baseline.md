# Gotcha: causas-raiz do Site Audit Semrush (baseline 2026-07-01)

Export: `celogos.com.br_mega_export_20260701.csv` (24 URLs). Totais por issue e a causa no código:

| Issue (total) | Causa-raiz | Correção |
|---|---|---|
| Duplicate title/content/meta (16 cada) | www × não-www servem idêntico, sem 301/canonical | [[seo-canonical-host]] + canonical tag |
| Uncompressed JS/CSS (256), Unminified (32), Uncompressed pages (16) | sem GZipMiddleware; refs `/static/...` absolutas furam WhiteNoise; arquivos não-`.min` | GZip + `{% static %}` + minify |
| Broken internal images (24; 6 em /about/) | `about.html` referencia `.png` numa pasta só com `.webp` | trocar para `.webp` |
| Low text/HTML ratio (16), Low word count (4) | páginas com pouco conteúdo | ampliar conteúdo |
| External 403 (16, 1 por página) | recurso externo em toda página — suspeita Ketch `boot.js`/`polyfill-fastly.io` | remover polyfill; validar slug Ketch |
| sitemap.xml/robots.txt/llms.txt (4xx) | `contrib.sitemaps` instalado mas nunca ligado; sem robots/llms | criar rotas |
| Underscores in URL (2) | rota `contato_logos/` com `name` duplicado de `contato/` | name distinto + 301 |
| Neither canonical nor 301 from HTTP homepage (1), No HSTS (2) | falta redirect HTTP→HTTPS e HSTS | SECURE_SSL_REDIRECT + HSTS |

Detalhes de arquivo/linha: `templates/partials/head.html:5-8,77` (title/description compartilhados),
`about.html:759-761,886-889` (imagens .png), `fluxi/urls.py:13,34` (rota contato duplicada),
`templates/partials/script.html` (polyfill/segment/leadster), `fluxi/settings.py:71-81` (MIDDLEWARE).

Baseline importável via `python manage.py seo_import_semrush` → model `AuditFinding` (medir evolução).
