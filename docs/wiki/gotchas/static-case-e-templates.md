# Gotcha: case de arquivos estáticos e cache de templates

Dois tropeços descobertos ao verificar visualmente a Fase 1.

## 1. Filesystem case-sensitive no Cloud Run
O dev roda em **Windows (case-insensitive)**, mas o Cloud Run é **Linux (case-sensitive)**. Um
`<img src="/static/images/product/foto.jpg">` apontando para um arquivo `foto.JPG` **funciona no
Windows e quebra em produção** (404).

- Alguns arquivos em `static/images/product/` têm extensão **maiúscula** (`alunos_formatura.JPG`,
  `medio_resultado.JPG`). Referencie com o case exato.
- `medio`/`integral` referenciavam `product/40|41|42.jpg`, que **não existem** — imagens quebradas
  pré-existentes, agora apontadas para arquivos reais.
- Guarda: `seo/tests/test_images.py` faz checagem **case-sensitive** (compara com `os.listdir`, não
  só `Path.exists()`, que no Windows ignora o case).

## 2. Templates são cacheados (precisa reiniciar o runserver)
O `runserver` estava servindo HTML de template **antigo** mesmo após editar os arquivos — há um
`cached.Loader` no `TEMPLATES['OPTIONS']['loaders']`. Ao validar mudança de template no dev server,
**reinicie o processo** (mesmo com `--noreload`), senão você vê conteúdo velho.

## 3. Grid de imagens dos serviços exige proporção certa
`.thumbnail-image-grid a img { width:100% }` — **sem `object-fit`/altura**, então a imagem renderiza na
proporção natural. O layout padrão do tema (infantil/fd1/fd2) é **2 quadradas empilhadas (col-lg-6) +
1 retrato ~1:2 (col-lg-6)**; a coluna única precisa ser retrato pra igualar a altura das duas. Pôr
quadrada/paisagem na posição única desalinha ("fora do grid"). `medio`/`integral` não têm imagens
retrato topicais → usam um **grid de 3 quadradas em linha (col-lg-4)**, que também fica alinhado.

## 4. `rel="stylesheet preload"` causa FOUC (shapes "grandes e à frente")
Os `<link>` de CSS usavam `rel="stylesheet preload" as="style"` (token combinado, não-padrão). Alguns
browsers tratam como **preload não-bloqueante** → a página pinta **antes** do CSS aplicar, mostrando por
um instante elementos decorativos (shapes) em tamanho natural e à frente do conteúdo. As shapes de
serviço são `display:none` no CSS, mas o FOUC as expõe. **Corrigido para `rel="stylesheet"`** (aplica
imediato, render-blocking). Ver [[seo-on-page]].

## Verificação de assets (sem browser)
Sem playwright/selenium no ambiente, valide integridade assim: suba o `runserver`, extraia todos os
`href`/`src` de `/static/` das páginas e faça `GET` em cada um esperando 200 (pega refs quebradas).
Para minificação: `node --check` nos `.min.js` e paridade de contagem de `{`/`}` no CSS
(rcssmin/rjsmin preservam a estrutura). Ver [[seo-on-page]].
