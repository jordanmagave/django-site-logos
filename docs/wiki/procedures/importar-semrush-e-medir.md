# Procedure: importar o Site Audit do Semrush e medir evolução

## Importar um export
1. Exportar o "mega export" do Site Audit no Semrush (CSV) para a raiz do repo (fica gitignored).
2. Rodar:
   ```
   python manage.py seo_import_semrush "celogos.com.br_mega_export_YYYYMMDD.csv"
   ```
   A data é extraída do nome do arquivo (`YYYYMMDD`) ou passada com `--date YYYY-MM-DD`.
3. O comando popula o model `AuditFinding` (uma linha por URL × issue com contagem > 0). É idempotente
   (`update_or_create`), então reimportar a mesma data não duplica.

## Medir evolução
- Comparar totais por issue entre duas `import_date` (baseline 2026-07-01 vs. re-crawl posterior).
- Ver no Django admin: `AuditFinding` tem filtro por data/issue e `date_hierarchy`.

## O que já foi corrigido (Fase 1) — esperar cair no próximo crawl
- Duplicate title/content/meta → canonical host (301 www→raiz) + canonical tag + title/description por página.
- sitemap.xml / robots.txt / llms.txt → agora retornam 200 (antes 4xx).
- Broken internal images (/about/) → `.png`→`.webp`.
- Underscores in URL → `/contato_logos/` faz 301 para `/contato/`.
- Uncompressed pages (HTML) → `GZipMiddleware`.
- External 403 → removido o fallback de CDN depreciado no RudderStack.
- **Missing ALT** → `alt` descritivo nas imagens de conteúdo dos serviços (as decorativas em
  `/shape/` mantêm `alt=""` de propósito). Guardado por `seo/tests/test_alt.py`.
- **JSON-LD por página** → `EducationalOrganization` + `BreadcrumbList` num único `@graph`
  (`seo/structured_data.py`, injetado pelo context processor). Ver [[seo-on-page]].
- **Low word count** → `/contato/` ganhou seção de visita + NAP real; `/integral` ganhou parágrafo
  descritivo. Guardado por `seo/tests/test_content.py`.
- **Unminified/Uncompressed JS/CSS** → refs `/static/...` (JS/CSS) migradas para `{% static %}` em
  `head.html`/`script.html` (WhiteNoise `CompressedManifestStaticFilesStorage` serve hasheado+comprimido).
  Guardado por `seo/tests/test_static_refs.py`.
- **External 403 / Ketch** → o `boot.js` do slug `centro_educacional_logos` retorna **200**; o slug é
  válido e não era a fonte do 403 (era o polyfill legado, já removido). Ver [[ketch-e-recursos-externos]].

## Follow-ups ainda abertos (menores)
- **Minificação de fonte**: os arquivos `.js`/`.css` não-`.min` (ex.: `main.js`, `style.css`) ainda não
  são minificados no build; o `{% static %}` já resolve compressão/hash, mas minificar reduz mais o peso.
- **`/static/manifest.webmanifest` = 404**: o arquivo não existe em `static/` (ref mantida hardcoded de
  propósito — migrar p/ `{% static %}` quebraria o ManifestStorage). Criar o webmanifest ou remover a tag.
