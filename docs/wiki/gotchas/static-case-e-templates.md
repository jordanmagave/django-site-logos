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

## Verificação de assets (sem browser)
Sem playwright/selenium no ambiente, valide integridade assim: suba o `runserver`, extraia todos os
`href`/`src` de `/static/` das páginas e faça `GET` em cada um esperando 200 (pega refs quebradas).
Para minificação: `node --check` nos `.min.js` e paridade de contagem de `{`/`}` no CSS
(rcssmin/rjsmin preservam a estrutura). Ver [[seo-on-page]].
