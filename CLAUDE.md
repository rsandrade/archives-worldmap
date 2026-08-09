# Archives World Map — CLAUDE.md

## Stack e versões

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Linguagem | Python | 3.12+ (slim Docker) |
| Framework Web | Flask | 3.0.3 |
| ORM/DB | SQLite3 (stdlib) | — |
| Template Engine | Jinja2 (Flask bundled) | — |
| Frontend | Bootstrap | 3.3.7 |
| Mapa | Leaflet.js | 1.9.4 |
| Cluster de marcadores | Leaflet.markercluster | 1.5.3 |
| jQuery | jQuery | 1.12.4 |
| CSRF | Flask-WTF | 1.2.1 |
| Email | Flask-Mail | 0.10.0 |
| Rate Limit | Flask-Limiter | 3.8.0 |
| WSGI Server | Gunicorn | 22.0.0 |
| Container | Docker + docker-compose | — |
| HTTP Client | Requests | 2.32.3 |

## Como rodar localmente

```bash
# Opção 1: Docker (recomendado)
cp .env.example .env
# Edite .env com suas credenciais
docker compose up --build
# App em http://localhost:5000

# Opção 2: Local
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Crie .env (veja .env.example)
flask run
```

Gerar hash de senha do admin:
```bash
docker compose exec web flask hash-password suasenha
# ou local: flask hash-password suasenha
```

Após pull no servidor:
```bash
git pull && docker compose up --build -d
```

## Como rodar testes

Não existem testes automatizados no projeto.

## Estrutura de diretórios

```
.
├── run.py                    # Entry point WSGI + CLI commands
├── config.py                 # Config from environment variables
├── schema.sql                # SQLite schema (4 tabelas)
├── migrate.py                # Script de migração MySQL → SQLite
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE                   # AGPL-3.0
├── README.md
├── CLAUDE.md                 # ← Este arquivo
└── app/
    ├── __init__.py           # App factory, DB init, CSRF, security headers
    ├── db.py                 # get_db() / close_db()
    ├── extensions.py         # Flask-Mail instance (mail = Mail())
    ├── email_utils.py        # Todas as funções de envio de email (assíncrono)
    ├── countries.py          # ISO 3166-1 alpha-2 → nome/flag
    ├── routes/
    │   ├── __init__.py       # Vazio
    │   ├── public.py         # Rotas públicas (mapa, add, info, stats, etc.)
    │   ├── moderation.py     # /approve/<token>, /reject/<token>
    │   └── admin.py          # /admin/* painel, CRUD, gerenciamento de usuários
    ├── templates/
    │   ├── base.html         # Layout base (Bootstrap 3 + Leaflet + i18n.js)
    │   ├── public/           # 10 templates públicos
    │   ├── admin/            # 7 templates do admin
    │   ├── emails/           # 5 templates de email HTML
    │   └── moderation/       # 1 template (confirm.html)
    └── static/
        ├── css/style.css     # CSS customizado (~80 linhas)
        ├── js/i18n.js        # Engine client-side de internacionalização
        ├── img/LogoArchivesMap.png
        └── lang/             # 6 arquivos JSON (en, pt-br, es, zh, ro, pl)
```

## Convenções do projeto

### Nomenclatura
- **Arquivos Python**: snake_case (ex: `email_utils.py`, `config.py`)
- **Templates Jinja2**: snake_case com contexto (`public/home.html`, `admin/dashboard.html`)
- **Blueprints**: `public_bp`, `moderation_bp`, `admin_bp`
- **Rotas**: snake_case, verbos HTTP explícitos (`home()`, `add_submit()`, `login_submit()`)
- **Funções helpers**: prefixo `_` para privadas (ex: `_verify_recaptcha()`, `_sanitize_text()`)
- **Variáveis no template**: snake_case (`inst_id`, `qty_institutions`, `status_filter`)
- **Chaves i18n**: snake_case com prefixo de contexto (`flash_add_success`, `admin_col_name`)

### i18n
- 6 idiomas: `en`, `pt-br`, `es`, `zh`, `ro`, `pl`
- Arquivos JSON em `app/static/lang/{lang}.json`
- Atributos HTML: `data-i18n` (texto), `data-i18n-html` (HTML com links), `data-i18n-placeholder`, `data-i18n-confirm`
- Detecção de idioma: `?lang=xx` > localStorage > browser > `en`
- Evento custom DOM: `awm:langchange` disparado após troca de idioma
- JS expõe `window.awmLang` (código) e `window.i18nDict` (dict de traduções)
- Flash messages usam chaves i18n (ex: `flash('flash_add_success', 'success')`)
- Para NÃO traduzir (admin, emails, change_password): sem `data-i18n`

### Templates
- `base.html` é o layout raiz com navbar, footer, flashes, scripts CDN
- Todos os templates estendem `base.html` via `{% extends "base.html" %}`
- `{% block scripts %}` para JS específico da página (após jQuery/Bootstrap/Leaflet)
- `{% block head %}` para CSS extra no `<head>`
- `{% block container_class %}` para override da classe container (não usado atualmente)
- Emails HTML são templates separados em `emails/` (sem `base.html`, HTML puro inline)

### Banco de dados
- SQLite puro (sem ORM), acesso via `app.db.get_db()` que retorna `sqlite3.Row`
- Conexão por requisição, fechada em `teardown_appcontext`
- `schema.sql` executado no `create_app()` com `CREATE TABLE IF NOT EXISTS`
- Migrações schema: ALTER TABLE com `try/except` em `_init_db()` (colunas adicionais)
- 4 tabelas: `institutions`, `settings`, `password_resets`, `users`

## O que NÃO fazer (armadilhas conhecidas)

1. **NÃO use `SELECT *` em rotas públicas** — as colunas internas (token, admin_notes, collaborator_email) vazariam para o frontend. Sempre liste colunas explicitamente.
2. **NÃO bloqueie a thread com envio de email** — `email_utils.py` usa `threading.Thread` (daemon) para envio assíncrono. O `_send_async()` pega o `current_app._get_current_object()` para evitar contextos perdidos.
3. **NÃO remova o `ProxyFix`** em `app/__init__.py` — necessário para login funcionar atrás de proxy HTTPS.
4. **NÃO use porta 465 para SMTP** — o servidor bloqueia. Use 587 + STARTTLS.
5. **NÃO hardcode `debug=True`** no `run.py` — use variável de ambiente `FLASK_DEBUG=1`.
6. **NÃO esqueça o `csrf_token()`** em formulários POST — Flask-WTF exige.
7. **NÃO confie no `REMOTE_ADDR`** para rate limiting atrás de proxy — o `ProxyFix` já trata `x_for=1`.
8. **NÃO use `|safe` em dados de instituições** nos templates públicos — sempre use `|e` (escaping), exceto `data-i18n-html` que tem HTML seguro controlado.
9. **NÃO armazene `token` no session** — tokens vão na URL para email, são one-time use.
10. **NÃO adicione novas chaves i18n só no `en.json`** — repita para todos os 6 idiomas, mesmo que seja só o placeholder em inglês.

## Links úteis

- **Site ao vivo**: https://www.archivesmap.org
- **Repositório**: https://github.com/rsandrade/archives-worldmap
- **Maintainer**: https://feudo.org
- **LABHDUFBA**: https://labhd.ufba.br
- **Leaflet.js**: https://leafletjs.com
- **Nominatim (geocoding)**: https://nominatim.openstreetmap.org
- **Bootstrap 3.3.7**: https://getbootstrap.com/docs/3.3/
- **Flask-Mail**: https://pythonhosted.org/flask-mail/
- **Flask-Limiter**: https://flask-limiter.readthedocs.io
