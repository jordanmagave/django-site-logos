# Gotcha: rodar os testes (ambiente pipenv)

O `python` global da máquina **não** tem as dependências (`environ`, etc.) — `manage.py` quebra com
`ModuleNotFoundError: No module named 'environ'`.

As deps estão no virtualenv do pipenv:
`C:\Users\jorda\.virtualenvs\django-site-logos-asuSwHNi\Scripts\python.exe`

Rodar testes/manage com esse interpretador (ou `pipenv run`):
```
"C:/Users/jorda/.virtualenvs/django-site-logos-asuSwHNi/Scripts/python.exe" manage.py test
```

O warning `No directory at: .../staticfiles/` nos testes é inofensivo (WhiteNoise sem collectstatic).
Método do projeto: **TDD** — escrever o teste em `seo/tests/` antes da implementação. Ver [[audit-semrush-baseline]].
