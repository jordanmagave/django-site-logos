# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ▶ Retomar o projeto (long-term memory)
A memória de longo prazo deste projeto vive **versionada no repo**, em `docs/wiki/`. Ao iniciar uma
sessão, **leia primeiro** `docs/wiki/ESTADO-ATUAL.md` (onde estamos + próximos passos) e consulte
`docs/wiki/INDEX.md` antes de qualquer tarefa de SEO. Plano completo em `docs/PLANO-SEO.md`.
Rodar testes: usar o python do venv pipenv (ver `docs/wiki/gotchas/rodar-testes-venv-pipenv.md`).
O app `seo/` concentra o trabalho de SEO (middleware canônico, metadados, sitemaps, robots/llms,
`AuditFinding` + comando `seo_import_semrush`).

## Project

Institutional website for **Centro Educacional Logos** (celogos.com.br), a Django 5.2 app deployed to Google Cloud Run. Repo: https://github.com/jordanmagave/django-site-logos. Codebase language and comments are in Brazilian Portuguese (`pt-br`, `America/Belem`). The primary conversion path is a contact/lead-capture form; a second app (`boleto`) is being built to let parents look up school payment slips (boletos) by CPF.

### Branches & environments
- **`main`** → production deploy: **celogos.com.br**.
- **`dev`** → staging deploy: a separate Cloud Run `*.run.app` dev domain (not the custom domain).

Both are separate Cloud Run environments driven by their own Google Cloud Build triggers. Note: the committed `cloudbuild.yaml` is currently **identical on `main` and `dev`** (both name service `django-site-logos`), so the actual service/domain split lives in the **Cloud Build trigger configuration in GCP**, not in this file. Do all feature work off `dev` (or a feature branch merged into `dev`) and promote to `main` for production.

## Commands

```bash
# Install deps (project uses pip + requirements.txt; a Pipfile also exists)
pip install -r requirements.txt

# Run dev server (defaults to SQLite, DEBUG from .env)
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Tests (Django test runner)
python manage.py test                       # all apps
python manage.py test fluxi                 # single app
python manage.py test boleto.tests.SomeTest.test_method   # single test

# Collect static (Whitenoise; required before deploy, run in Docker build)
python manage.py collectstatic --noinput --clear

# Management command: bulk-upload local boleto PDFs to Cloud Storage
python manage.py migrar_boletos_cloud --pasta-boletos /path/to/pdfs
```

CI (`.github/workflows/django.yml`) runs on push/PR to `main`/`dev`: makemigrations → migrate → `manage.py test` on Python 3.12.

## Environment & configuration

Settings read from a `.env` file (via `django-environ`) at repo root. Relevant vars:
- `SECRET_KEY`, `DEBUG` (when `DEBUG=True`, `ALLOWED_HOSTS` becomes `["*"]`)
- `SEGMENT_WRITE_KEY` — Segment/analytics ingestion (server-side lead tracking)
- `GCP_SERVICE_URL` — appended to `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` in prod
- Database selection is **implicit**: if `DB_NAME` is present in the environment, settings use Cloud SQL PostgreSQL (`/cloudsql/<CLOUD_SQL_CONNECTION_NAME>`); otherwise it falls back to local `db.sqlite3`. There is no `DATABASE_URL` wiring despite the README example.
- `GCS_BUCKET_NAME` is referenced by `boleto/services/cloud_storage.py` but is **not** defined in `settings.py` — must be added before the boleto cloud features work.

## Deployment

Pushing to `main` (production) or `dev` (staging) triggers **Google Cloud Build** (`cloudbuild.yaml`): it builds the `Dockerfile`, pushes to Artifact Registry (`southamerica-east1`), and deploys to Cloud Run with Cloud SQL attached — `main` serving celogos.com.br and `dev` serving the dev `*.run.app` domain (see Branches & environments above). Secrets (`SECRET_KEY`, `DB_*`) come from Google Secret Manager. The container runs Gunicorn (`fluxi.wsgi:application`) on `$PORT`. Note: Dockerfile pins Python 3.12 while `Pipfile` declares 3.13.

## Architecture

Two Django apps under one project (`fluxi`):

### `fluxi` — the public website + lead capture
- **Views are split by page group**, not in a single `views.py`: `homeViews.py` (home), `pagesViews.py` (about, contato, Leadster webhook), `servicesViews.py` (the five "serviços educacionais" pages). URLs in `fluxi/urls.py`.
- **Lead-tracking flow**: `middleware.TrackingParamsMiddleware` captures marketing URL params (`utm_*`, `gclid`, `fbclid`) into the session on any request. When the contact form (`ContatoForm`) is submitted, `pagesViews.contato` copies those session values onto the `Contato` model before saving.
- **Leadster webhook** (`pagesViews.leadster_webhook`, csrf-exempt POST at a UUID-obscured path): ingests external chatbot leads, derives Facebook `fbc` from `fbclid`, resolves IP → location via the bundled MaxMind DB (`geoip/GeoLite2-City.mmdb`), saves a `Contato`, and fires Segment `identify` + `track("Lead")` calls server-side.
- **Models** (`fluxi/models.py`): `Contato` (lead record with all attribution fields), plus `TrackingEvents` / `TrackSession` (session/interaction tracking).
- The `geoip/` directory holds the GeoLite2 database file, not Python code.

### `boleto` — CPF-based boleto lookup (WORK IN PROGRESS, on branch `feat/web-boleto`)
Intended flow: parent enters CPF → sees their students' available boletos → downloads via a time-limited signed URL from Cloud Storage. Access is gated by storing `cpf_validado` in the session; every consulta/download writes a `LogAcesso` audit row.
- **Models**: `ResponsavelFinanceiro` (guardian, keyed by CPF) → `Aluno` (student) → `BoletoArquivo` (PDF metadata + Cloud Storage URL); `LogAcesso` (access audit log).
- **Services layer** (`boleto/services/`): `cloud_storage.py` (GCS upload + v4 signed URLs), `pdf_manager.py` (locate/parse boleto PDFs), `sql_sync.py` (pull guardians from an external SQL Server backup via `pyodbc`/`pandas`), `access_log.py`.

**Incomplete / inconsistent state to be aware of before extending `boleto`:**
- `boleto/urls.py` (namespace `boletos`) is **not included** in `fluxi/urls.py`, so its views aren't routed yet.
- `pdf_manager.PDFManager` is a stub whose constructor signature (`pdf_folder`) does not match how `views.ConsultaBoletoView` calls it (`PDFManager()` + `get_boletos_por_responsavel`); `sql_sync.py` and `access_log.py` are largely stubbed.
- There are **two management dirs**: `boleto/management/commands/` (the real Django location — `migrar_boletos_cloud.py`, `sicronizar_boletos.py`) and a stale `boleto/management/cmd/` copy that Django ignores. Add/edit commands only under `commands/`.
- `DownloadBoletoView` returns `Http404(...)` (constructed, not raised) on a missing file — a bug to fix, not a pattern to copy.

## Conventions

- Static assets live in `static/` (served by Whitenoise with compressed-manifest storage); templates in `templates/` organized by area (`home/`, `pages/`, `services/`, `landing/`, `partials/`, `layout/`).
- Keep user-facing strings and new comments in Portuguese to match the codebase.
