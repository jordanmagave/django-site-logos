# Rule: padrões de SEO on-page

Convenções obrigatórias ao criar/editar páginas do site. Todas têm teste em `seo/tests/`.

## Title / description / canonical
- **Nunca** hardcodar título/descrição no template. O `{% block title %}` usa `{{ seo_title }}` e a
  meta description usa `{{ seo_description }}`, vindos de `seo/metadata.py` (indexado por `url_name`).
- Ao adicionar uma rota nova, registre o metadado em `SEO_METADATA` com title/description **únicos**.
- Canonical sempre no host canônico sem `www` (ver [[seo-canonical-host]]); vem de `canonical_url`.
- Testes: `test_metadata.py` (unicidade), `test_canonical.py`.

## Dados estruturados (JSON-LD)
- Um único bloco `<script type="application/ld+json">` renderiza `{{ seo_jsonld|safe }}`.
- O conteúdo vem de `seo/structured_data.py`: `EducationalOrganization` em todas as páginas +
  `BreadcrumbList` nas internas (rótulo em `BREADCRUMB_LABELS`). Consolidado num `@graph`.
- `json.dumps(..., ensure_ascii=False)` + `|safe` para preservar acentos e não escapar as aspas.
- Teste: `test_structured_data.py` (JSON válido, tipos presentes, host canônico).

## Imagens
- Imagem de **conteúdo** → `alt` descritivo em português com palavra-chave (ex.: série + "Logos").
- Imagem **decorativa** (sob `static/images/**/shape/`) → `alt=""` de propósito (leitor de tela ignora).
- Arquivos referenciados devem existir em `static/` **com case exato** (o `.webp` da pasta, não `.png`;
  `.JPG` maiúsculo quando é o caso) — o Cloud Run é case-sensitive. Ver [[static-case-e-templates]].
- Testes: `test_alt.py`, `test_images.py` (existência case-sensitive).

## Assets estáticos (CSS/JS)
- **Sempre** `{% static 'caminho' %}` — nunca `href="/static/..."`/`src="/static/..."` fixo (fura o
  hash/compressão do WhiteNoise). Lembre do `{% load static %}` no topo do partial.
- **Minificação**: CSS/JS hand-written (não-vendor) usam a variante `.min` gerada por
  `python manage.py seo_minify` (rcssmin/rjsmin conservadores). Ao editar `style.css`, `main.js`,
  `metismenu.js/css` ou `magnific-popup.css`, **rode o comando e recommite** o `.min`.
  Lista de fontes em `seo/management/commands/seo_minify.py::ASSETS`. Vendor já-`.min` fica de fora.
- Teste: `test_static_refs.py` (sem hardcoded), `test_minify.py` (`.min` existe/menor/referenciado).

## Conteúdo
- Evitar páginas com pouco texto ("low word count"). Páginas de serviço têm uma seção
  `short-case-studies-area` com parágrafo descritivo; `/contato/` tem seção de visita + NAP.
- NAP real: **Passagem Miranda, 300 — Coqueiro, CEP 67113-200, Ananindeua/PA**; tel/WhatsApp
  **+55 (91) 3013-0198**. Manter consistente entre página, footer e JSON-LD.
- Teste: `test_content.py`.
