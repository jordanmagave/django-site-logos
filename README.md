# Site Institucional - Centro Educacional Logos

Este é o repositório do site institucional do Centro Educacional Logos, uma aplicação web construída com Django e hospedada na nuvem do Google Cloud.

## Descrição do Projeto

O objetivo principal do site é servir como um portal informativo para pais e alunos, apresentando a instituição, seus serviços e valores. A principal funcionalidade de conversão é um formulário de contato para agendamento de visitas, cujos dados são armazenados de forma segura e integrados com ferramentas de análise.

## Principais Funcionalidades

* **Páginas Institucionais:** Home, Sobre, Serviços (Educação Infantil, Fundamental, etc.).
* **Formulário de Contato:** Captura de leads com validação e armazenamento em banco de dados.
* **Rastreamento de Marketing (Client-Side):** Captura automática de parâmetros de URL (`utm_*`, `gclid`, `fbclid`) para análise de campanhas.
* **Gestão de Consentimento (LGPD):** Integração com a plataforma Ketch para gerenciar o consentimento de cookies e rastreamento.
* **Painel de Administração:** Interface do Django Admin para visualização dos contatos recebidos.
* **Testes Automatizados:** Suíte de testes para garantir a qualidade e estabilidade do código.

## Tecnologias Utilizadas

* **Backend:** Django
* **Frontend:** HTML, CSS, JavaScript
* **Banco de Dados:** PostgreSQL (gerenciado pelo Google Cloud SQL)
* **Infraestrutura:**
    * **Hospedagem:** Google Cloud Run
    * **CI/CD:** Google Cloud Build com gatilhos do GitHub
    * **Armazenamento de Imagens Docker:** Google Artifact Registry
    * **Gerenciamento de Segredos:** Google Secret Manager
* **Serviços Adicionais:**
    * **Servidor de Arquivos Estáticos:** Whitenoise
    * **Análise (Client-Side):** RudderStack
    * **Privacidade (LGPD):** Ketch

## Configuração do Ambiente Local

Siga os passos abaixo para rodar o projeto em um ambiente de desenvolvimento local.

**1. Instale as dependencias:**
```bash
pip install -r requirements.txt
```

**2. Configure as Variáveis de Ambiente:**
```bash
# .env  Example

# Chave secreta do Django (gere uma nova para desenvolvimento)
SECRET_KEY="sua-secret-key-de-desenvolvimento"

# Ative o modo DEBUG para desenvolvimento
DEBUG=True
```

```python
# URL do banco de dados local (exemplo para PostgreSQL)
# Se estiver usando SQLite para desenvolvimento, a configuração no settings.py já funcionará.
# DATABASE_URL="postgres://usuario:senha@localhost:5432/nome_do_banco"

# Domínios permitidos em desenvolvimento
ALLOWED_HOSTS=[127.0.0.1, localhost]
```

**3. Aplique as Migrações do Banco de Dados:**

```bash
python manage.py migrate
```

**4. Rode o Servidor de Desenvolvimento:**
```bash
python manage.py runserver
```
Acesse http://127.0.0.1:8000/ no seu navegador.

## Retomar o Projeto em Outra Sessão

Este projeto usa uma estratégia de **memória de longo prazo versionada no próprio repositório**, para que
qualquer nova sessão (outra máquina ou um novo agente de IA) consiga continuar de onde paramos, sem
depender de estado local fora do repo.

**Ao retomar, leia nesta ordem:**
1. **[`CLAUDE.md`](CLAUDE.md)** — guia do repositório (arquitetura, comandos, branches/ambientes) e a
   seção "▶ Retomar o projeto".
2. **[`docs/wiki/ESTADO-ATUAL.md`](docs/wiki/ESTADO-ATUAL.md)** — onde estamos agora e os próximos passos.
3. **[`docs/wiki/INDEX.md`](docs/wiki/INDEX.md)** — a wiki do projeto (fonte de verdade): decisões,
   *gotchas* e procedimentos. **Consulte antes de qualquer tarefa de SEO.**
4. **[`docs/PLANO-SEO.md`](docs/PLANO-SEO.md)** — o plano completo das 3 fases (fundação/correções →
   monitoramento via APIs do Google → loop de memória/auto-aprendizado).

**Passos para restaurar o ambiente:**
```bash
git clone git@github.com:jordanmagave/django-site-logos.git
cd django-site-logos
git switch feat/seo-foundation        # branch de trabalho atual
pipenv install                        # ou: pip install -r requirements.txt
cp .env.example .env                  # crie/preencha o .env (não versionado)
python manage.py migrate
python manage.py test                 # método do projeto é TDD; a suíte deve ficar verde
```

**O que NÃO está versionado** (reprovisionar por fora): `.env` (segredos), a *service account* das APIs
do Google (Fase 2) e o `db.sqlite3` local. O `client_secret` do OAuth **deve ser rotacionado** no GCP.

> Convenção: ao concluir uma sessão, registre aprendizados duráveis como novas páginas em `docs/wiki/`
> (categorias `decisions/`, `gotchas/`, `procedures/`, `rules/`) e atualize `docs/wiki/ESTADO-ATUAL.md`.
