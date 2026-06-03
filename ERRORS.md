# ERRORS.md

Registro de erros relevantes encontrados durante o desenvolvimento e suas soluções.
Convenção: cada entrada tem **título**, **contexto**, **causa raiz**, **solução** e **lição**.

---

## Histórico

### 2026-06-02 — `git status`/`git commit` travando indefinidamente

**Contexto:** ao tentar fazer o primeiro commit da Fase 0, todas as operações git porcelain (status, commit, add) pendiam por minutos sem terminar.

**Causa raiz:** 416 arquivos em `static/` foram comitados em versões antigas do repositório, antes de `static/` ser adicionado ao `.gitignore`. O `.gitignore` impede tracking de arquivos novos, mas não desfaz tracking. Como muitos desses arquivos são imagens grandes (até 28MB), cada `lstat` do refresh-index demorava demais. O `.git/objects/pack/` ficou com 465MB.

**Solução:** marcar todos os arquivos tracked em `static/` com `git update-index --assume-unchanged`:

```bash
git ls-files static/ | while read f; do
    git update-index --assume-unchanged "$f" 2>/dev/null || true
done
```

**Solução definitiva (futuro):** rodar `git rm --cached -r static/` para removê-los do tracking, e/ou usar `git filter-repo` para limpar o histórico. Será feito quando otimizarmos as imagens na Fase 6 (substituição completa).

**Lição:** sempre adicionar diretórios pesados ao `.gitignore` ANTES de comitar conteúdo. Verificar `git ls-files | wc -l` e o tamanho de `.git/objects/` periodicamente.

