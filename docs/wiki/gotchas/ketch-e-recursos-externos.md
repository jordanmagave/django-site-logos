# Gotcha: Ketch boot.js e o "external 403" do audit

O Site Audit do Semrush (2026-07-01) reportava **um recurso externo 403 em toda página**. Havia dois
candidatos: o `boot.js` do Ketch e um fallback de CDN legado (polyfill) dentro do snippet do RudderStack.

## Verificação
```
curl -sS -o /dev/null -w "%{http_code}\n" -A "Mozilla/5.0" \
  "https://global.ketchcdn.com/web/v3/config/centro_educacional_logos/website_smart_tag/boot.js"
# -> 200
```

## Conclusão
- O **slug `centro_educacional_logos`** do Ketch é válido: o `boot.js` responde **200**. **Não** era a
  fonte do 403. Não mexer nesse `<script>` do Ketch em `head.html`.
- O 403 vinha do **fallback de CDN depreciado (polyfill)** no snippet do RudderStack, que já foi
  **removido** (ver comentário em `head.html`, seção RudderStack). O re-crawl deve confirmar que o 403 sumiu.

## Relacionado
- `/static/manifest.webmanifest` retorna 404 (arquivo não existe em `static/`). É um link quebrado
  pré-existente; a ref foi mantida hardcoded de propósito (migrar p/ `{% static %}` quebraria o
  `CompressedManifestStaticFilesStorage`). Follow-up: criar o webmanifest ou remover a `<link rel=manifest>`.
- Padrões on-page em [[seo-on-page]].
