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

## Follow-ups ainda abertos (não movem 100% do audit ainda)
- **Unminified/Uncompressed JS/CSS (256/32)**: falta step de minificação no build e migrar refs
  `/static/...` para `{% static %}` (WhiteNoise serve as variantes comprimidas/hasheadas).
- **Ketch boot.js 403**: validar o slug `centro_educacional_logos` (segundo candidato ao 403 por página).
- **Low word count / text-to-HTML**: ampliar conteúdo de `/contato/` e `/integral`.
- **Missing ALT**: preencher `alt` das imagens de grid dos serviços.
- **JSON-LD por página**: adicionar `EducationalOrganization` + `BreadcrumbList`.
