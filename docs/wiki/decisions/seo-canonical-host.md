# Decisão: host canônico do site

**Data:** 2026-07-01
**Status:** aprovado

## Decisão
O host canônico é **`celogos.com.br` (sem www)**. `www.celogos.com.br` deve retornar **301** para a raiz,
preservando path e query string. Toda tag `<link rel="canonical">` e todas as URLs do `sitemap.xml`
usam o host sem www e esquema `https`.

## Contexto / porquê
O Site Audit do Semrush (2026-07-01) apontou 16× "Duplicate title/content/meta" porque `www` e não-www
serviam conteúdo idêntico sem redirect nem canonical. É o problema nº1 do audit. O site já é referenciado
majoritariamente como `celogos.com.br` sem www. Ver [[audit-semrush-baseline]].

## Implementação
- `seo/middleware.py::CanonicalHostMiddleware` faz o 301 www→raiz.
- `fluxi/settings.py`: `SECURE_PROXY_SSL_HEADER`, `SECURE_SSL_REDIRECT` (prod), `USE_X_FORWARDED_HOST`,
  HSTS. Cloud Run fica atrás de proxy, por isso o `SECURE_PROXY_SSL_HEADER` é obrigatório.
- `django.contrib.sites` (SITE_ID=1) com domínio `celogos.com.br` alimenta URLs absolutas do sitemap.
