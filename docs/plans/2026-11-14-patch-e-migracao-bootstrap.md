# Archives World Map — plano de patch e migração Bootstrap 3 → 5

**Repositório:** `~/websites/archives-worldmap` (origin `rsandrade/archives-worldmap`, branch `master`, HEAD `aa4ccb1`)
**Produção:** https://www.archivesmap.org (Cloudflare → app Flask em Docker)
**Data do levantamento:** 14/11/2026
**Escopo:** (1) patch dos 3 achados do Modern Web Guidance; (2) migração Bootstrap 3.3.7 → 5.3.9 sem jQuery.
**Fora de escopo:** redesenho visual, mudança de rotas, troca de Leaflet, i18n, banco.

---

## 1. Sumário

| Frente | Trabalho | Risco | Quando |
|---|---|---|---|
| Patch | 4 tarefas, ~10 linhas em 4 templates | baixo | primeiro, direto em produção |
| Migração | 313 classes em 18 templates + CSS global + ícones | médio | depois do patch, em branch própria |

A migração **não é grande**: 313 tokens de classe, zero `col-xs`, zero `pull-*`, zero modal/tooltip/tab/carousel. Só dois comportamentos JS do Bootstrap (collapse do menu e dismiss de alerta). O custo real está em QA visual, não em código.

Ganho medido (gzip, arquivos reais baixados hoje):

- hoje: Bootstrap 3 CSS+JS + jQuery = **81,6 KB**
- depois: Bootstrap 5 CSS+JS = **47,3 KB**
- **−34,3 KB** e uma origem externa a menos (jQuery sai, junto com o segundo CDN)

---

## 2. Estado medido

### 2.1 Inventário de classes Bootstrap 3

313 tokens em 18 templates (dos 23; e-mails não usam classes).

| Componente | Ocorrências | Observação |
|---|---|---|
| `form-control` | 44 | continua em BS5 |
| `form-group` | 41 | removido em BS5 → `mb-3` |
| `btn` + variantes | 40 + 61 | `btn-default` (18), `btn-xs` (11), `btn-block` (3) |
| `glyphicon*` | 20 (10 ícones) | removido em BS5 → SVG |
| grid `col-md/sm-*` | 44 | continua; só `col-md-offset-*` muda |
| `text-*` | 19 | `text-muted`, `text-center` |
| `table*` | 30 | `table-condensed` (3) → `table-sm` |
| `panel*` | 5 | 1 bloco em `admin/users.html` → `card` |
| `label-*` | 4 | badges de status → `badge` |
| `input-group-btn` | 4 | removido em BS5 |
| `input-sm` | 3 | → `form-control-sm` |
| `form-inline` | 1 | removido em BS5 |
| `navbar-*` | 9 | 1 navbar, 1 toggle |
| alertas | 2 | 1 bloco em `base.html` |

Não usados: `col-xs-*`, `pull-*`, `hidden-xs`, `visible-*`, modal, tooltip, popover, tabs, carousel, dropdown, scrollspy.

### 2.2 Dependências externas (8 tags, todas sem `integrity`)

| Arquivo | Tags | Versão |
|---|---|---|
| `bootstrap.min.css` | 1 | 3.3.7 (EOL 24/07/2019; final foi 3.4.1) |
| `bootstrap.min.js` | 1 | 3.3.7 |
| `jquery-1.12.4.min.js` | 1 | 2016, última da linha 1.x |
| `leaflet.css` / `leaflet.js` | 2 | 1.9.4 |
| `MarkerCluster.css` / `.Default.css` / `leaflet.markercluster.js` | 3 | 1.5.3 |

### 2.3 Restrições

- **Sem testes automatizados** (`CLAUDE.md:44`: "There are no automated tests").
- Deploy é `git pull && docker compose up --build -d` no servidor: **merge em `master` = deploy**.
- `style.css` (126 linhas) depende de detalhes do BS3: `#map-wrapper` com `margin -15px` (gutter BS3) e `.navbar-nav > li > a`.
- `base.html` é o único ponto de carga de CSS/JS.

---

## 3. Decisão de arquitetura

**Recomendado: Bootstrap 5.3.9 vendorizado em `app/static/vendor/`, sem jQuery, sem Popper.**

Alternativas consideradas:

| Opção | Prós | Contras |
|---|---|---|
| **A. BS 5.3.9 self-hosted** (recomendada) | remove jQuery (−97 KB raw), remove 2 CDNs, versão pinada no repo, sem SRI, funciona em rede filtrada | +110 KB raw de CSS (30,8 KB gz) |
| B. BS 5.3.9 via CDN + SRI | menos arquivos no repo | depende de jsdelivr/unpkg; SRI a manter a cada bump |
| C. Remover framework, CSS próprio | zero dívida, controle total | reimplementar grid/navbar/form/tabela/card; ~2 dias a mais e mais regressão |
| D. Só vendorizar BS3 | mínimo esforço | continua EOL, mantém jQuery |

**Por que A e não B:** o público é global e o site tem locale `zh`; `unpkg.com` e `cdn.jsdelivr.net` têm disponibilidade irregular em redes filtradas. Vendorizar também elimina o achado de SRI (recurso de mesma origem não precisa de `integrity`).

**Por que A e não C:** 313 tokens e nenhum componente JS complexo tornam a migração barata; reescrever o CSS agora é escopo novo, não migração. C fica registrado como possível fase futura, com a mesma rede de testes visuais.

**JS:** carregar `bootstrap.min.js` (sem Popper, 60,8 KB raw / 16,5 KB gz) — só `collapse` e `alert` são usados. Não usar o bundle.

---

## 4. Fase 0 — rede de segurança (1,5 h)

### Tarefa 0.1 — Tag e branch

```bash
cd ~/websites/archives-worldmap
git checkout master && git pull --ff-only
git tag -a pre-bs5-2026-11-14 -m "Estado antes do patch/migração Bootstrap"
git push origin pre-bs5-2026-11-14
git checkout -b fix/a11y-sri-ime
```

**Verificar:** `git tag -l 'pre-bs5*'` lista a tag; `git branch --show-current` mostra a branch.

### Tarefa 0.2 — Smoke tests (novo `tests/`)

Arquivo `tests/conftest.py`:

```python
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_PATH", os.path.join(_tmp, "test.db"))
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("BASE_URL", "http://localhost")

import pytest
from app import create_app

@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.test_client() as c:
        yield c
```

Arquivo `tests/test_smoke.py`:

```python
import pytest

PUBLIC = ["/", "/add", "/stats", "/q?q=brazil", "/api/pins", "/robots.txt",
          "/admin/login", "/admin/forgot-password"]

@pytest.mark.parametrize("url", PUBLIC)
def test_public_pages_render(client, url):
    r = client.get(url)
    assert r.status_code == 200, url
    if r.mimetype == "text/html":
        body = r.get_data(as_text=True)
        assert "bootstrap" in body          # CSS do framework presente
        assert "data-i18n" in body          # i18n não quebrou

def test_home_has_map(client):
    body = client.get("/").get_data(as_text=True)
    assert 'id="mapid"' in body
    assert "leaflet" in body
```

Adicionar `pytest==8.3.3` em `requirements-dev.txt` (novo arquivo, não misturar com produção).

**Pré-requisito:** venv com `pip install -r requirements.txt -r requirements-dev.txt` (o Python do sistema não tem Flask).
**Rodar:** `pytest -q`
**Esperado:** 9 passed (8 rotas parametrizadas + 1 teste do mapa).

### Tarefa 0.3 — Baseline visual (novo `scripts/visual_baseline.py`)

Playwright, 9 URLs × 2 viewports (390×844 e 1440×900), salva PNGs fora do repo:

```python
import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/awm-visual")
URLS = ["/", "/add", "/stats", "/q?q=archives", "/info/1",
        "/admin/login", "/admin/forgot-password", "/about", "/contact"]
VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, (w, h) in VIEWPORTS.items():
            ctx = await b.new_context(viewport={"width": w, "height": h})
            page = await ctx.new_page()
            for url in URLS:
                slug = (url.strip("/").replace("/", "-").replace("?", "-") or "home")
                await page.goto(BASE + url, wait_until="networkidle")
                await page.screenshot(path=str(OUT / f"{name}__{slug}.png"), full_page=True)
            await ctx.close()
        await b.close()

asyncio.run(main())
```

**Pré-requisito:** `pip install playwright && playwright install chromium`. `/info/1` exige uma instituição id=1 no banco local; se não houver, trocar o id ou remover a URL.
**Rodar:** `docker compose up -d` e depois `python scripts/visual_baseline.py http://localhost:5000 /tmp/awm-visual/antes`
**Esperado:** 18 PNGs.

**Verificar:** `ls /tmp/awm-visual/antes | wc -l` → 18.

---

## 5. Fase 1 — patch (branch `fix/a11y-sri-ime`, 1 h)

Independente da migração. Pode ir para produção antes.

### Tarefa 1.1 — `autocomplete` no login

`app/templates/admin/login.html:11-15`:

```html
<div class="form-group">
    <label for="username" data-i18n="admin_username">Username</label>
    <input type="text" id="username" name="username" class="form-control"
           autocomplete="username" required>
</div>
<div class="form-group">
    <label for="password" data-i18n="admin_password">Password</label>
    <input type="password" id="password" name="password" class="form-control"
           autocomplete="current-password" required>
</div>
```

### Tarefa 1.2 — `autocomplete` na troca de senha

`app/templates/admin/change_password.html`:

- `:12` `name="current_password"` → `autocomplete="current-password"`
- `:17` `name="new_password"` → `autocomplete="new-password"`
- `:21` `name="confirm_password"` → `autocomplete="new-password"`

### Tarefa 1.3 — guarda de IME no geocode

`app/templates/public/add.html:279-281` e `app/templates/admin/edit.html:273-275`:

```js
document.getElementById('geocode-input').addEventListener('keydown', function(e) {
    // IME (zh/ja/ko): Enter confirma o candidato, não envia.
    if (e.isComposing || e.keyCode === 229) return;
    if (e.key === 'Enter') { e.preventDefault(); geocodeAddress(); }
});
```

O `keyCode === 229` cobre o Safari, onde `isComposing` chega `false` no keydown de confirmação (bug WebKit 165004). `readonly`? não — o campo é editável.

**Verificar:** com locale ZH, digitar no campo de endereço e confirmar candidato do IME não deve disparar o geocode; com teclado latino, Enter continua disparando.

### Tarefa 1.4 — SRI nas 8 tags externas

Hashes calculados hoje a partir dos bytes servidos (revalidar antes do commit com `curl … | openssl dgst -sha384 -binary | openssl base64 -A`):

| Asset | `integrity` |
|---|---|
| bootstrap 3.3.7 CSS | `sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u` |
| bootstrap 3.3.7 JS | `sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa` |
| jquery 1.12.4 | `sha384-nvAa0+6Qg9clwYCGGPpDQLVpLNn0fRaROjHqs13t4Ggj3Ez50XnGQqc/r8MhnRDZ` |
| leaflet 1.9.4 CSS | `sha384-sHL9NAb7lN7rfvG5lfHpm643Xkcjzp4jFvuavGOndn6pjVqS6ny56CAt3nsEVT4H` |
| leaflet 1.9.4 JS | `sha384-cxOPjt7s7Iz04uaHJceBmS+qpjv2JkIHNVcuOrM+YHwZOmJGBXI00mdUXEq65HTH` |
| MarkerCluster.css | `sha384-pmjIAcz2bAn0xukfxADbZIb3t8oRT9Sv0rvO+BR5Csr6Dhqq+nZs59P0pPKQJkEV` |
| MarkerCluster.Default.css | `sha384-wgw+aLYNQ7dlhK47ZPK7FRACiq7ROZwgFNg0m04avm4CaXS+Z9Y7nMu8yNjBKYC+` |
| leaflet.markercluster.js | `sha384-eXVCORTRlv4FUUgS/xmOyr66XBVraen8ATNLMESp92FKXLAMiKkerixTiBvXriZr` |

Formato de cada tag:

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css"
      integrity="sha384-BVYii…"
      crossorigin="anonymous"
      referrerpolicy="no-referrer">
```

**Já validado:** os 8 endpoints respondem `Access-Control-Allow-Origin: *`, então `crossorigin` não bloqueia. Se algum hash divergir, a página perde CSS/JS — testar local antes do merge.

**Nota:** este patch é transitório. A Fase 2 (vendorização) remove as tags externas e, com elas, a necessidade de SRI.

### Tarefa 1.5 — Verificação e commit

```bash
pytest -q
python scripts/visual_baseline.py http://localhost:5000 /tmp/awm-visual/pos-patch
git add app/templates tests requirements-dev.txt scripts/visual_baseline.py
git commit -m "fix(a11y,security): autocomplete em senhas, Enter seguro para IME e SRI nos CDNs"
git push -u origin fix/a11y-sri-ime
```

**Checklist antes do merge:** login funciona; campo de endereço geocodifica; console sem erro de integridade; layout idêntico ao baseline.

---

## 6. Fase 2 — vendorização (branch `chore/bootstrap-5`, 45 min)

### Tarefa 2.1 — Baixar e fixar versões

```bash
mkdir -p app/static/vendor/{bootstrap,leaflet,leaflet-markercluster}
cd app/static/vendor
curl -fsSLO https://cdn.jsdelivr.net/npm/bootstrap@5.3.9/dist/css/bootstrap.min.css
curl -fsSLO https://cdn.jsdelivr.net/npm/bootstrap@5.3.9/dist/js/bootstrap.min.js
curl -fsSL https://unpkg.com/leaflet@1.9.4/dist/{leaflet.js,leaflet.css} -O
mkdir -p leaflet/images && for i in marker-icon.png marker-icon-2x.png marker-shadow.png layers.png layers-2x.png; do
  curl -fsSL "https://unpkg.com/leaflet@1.9.4/dist/images/$i" -o "leaflet/images/$i"; done
```

`leaflet.css` referencia `images/marker-icon.png` e `images/layers*.png` — as imagens são obrigatórias, senão os pinos somem.

### Tarefa 2.2 — Manifesto e script de atualização

`app/static/vendor/VERSIONS.md` com versão, URL de origem, SHA256 de cada arquivo e data.
`scripts/update_vendor.sh` baixa de novo, compara SHA256 e falha se mudou sem bump de versão.

**Verificar:** `find app/static/vendor -type f | wc -l` → 12 arquivos: 2 Bootstrap, 2 Leaflet (js/css), 3 MarkerCluster, 5 imagens do Leaflet. Conferir cada SHA256 contra o manifesto.

### Tarefa 2.3 — Trocar as tags em `base.html`

```html
<link rel="stylesheet" href="{{ url_for('static', filename='vendor/bootstrap/bootstrap.min.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='vendor/leaflet/leaflet.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
…
<script src="{{ url_for('static', filename='vendor/bootstrap/bootstrap.min.js') }}"></script>
<script src="{{ url_for('static', filename='vendor/leaflet/leaflet.js') }}"></script>
```

`home.html` e demais templates que carregam MarkerCluster passam a apontar para `vendor/leaflet-markercluster/`.

**Atenção:** trocar BS3 por BS5 no `base.html` quebra todas as páginas de uma vez. Fazer essa troca **junto** com o commit da Fase 3, nunca isolada.

---

## 7. Fase 3 — `base.html` e CSS global (1,5 h)

### Tarefa 3.1 — Navbar

```html
<nav class="navbar navbar-expand-md bg-body-tertiary border-bottom">
  <div class="container">
    <a class="navbar-brand fw-bold" href="{{ url_for('public.home') }}" data-i18n="site_name">Archives World Map</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
            data-bs-target="#navbar" aria-controls="navbar" aria-expanded="false"
            aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div id="navbar" class="collapse navbar-collapse">
      <ul class="navbar-nav">
        <li class="nav-item"><a class="nav-link" href="…" data-i18n="nav_map">Map</a></li>
        …
      </ul>
      <ul class="navbar-nav ms-auto lang-selector">
        <li class="nav-item"><a class="nav-link" href="#" data-lang="en">EN</a></li>
        …
      </ul>
    </div>
  </div>
</nav>
```

`navbar-expand-md` mantém o ponto de colapso atual (<768 px). `navbar-right` → `ms-auto`; `navbar-static-top` não existe em BS5.

### Tarefa 3.2 — Alerta

```html
<div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
  <span data-i18n="{{ message }}">{{ message }}</span>
  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>
```

### Tarefa 3.3 — `style.css`

```css
/* gutter BS5 = 1.5rem (24px), não 15px */
#map-wrapper { margin-inline: calc(var(--bs-gutter-x, 1.5rem) * -0.5); }
@media (min-width: 768px) { #map-wrapper { margin-inline: 0; } }

.lang-selector .nav-link { padding: .5rem; font-size: 12px; opacity: .6; }
.lang-selector .nav-link.active-lang { opacity: 1; font-weight: 600; }

@media (max-width: 767.98px) {
  .lang-selector { flex-direction: row; flex-wrap: wrap; padding: .5rem 0;
                   border-top: 1px solid var(--bs-border-color); }
}
```

Remover `.navbar-nav > li > a` e `float: none` (a nav BS5 já é flex).

### Tarefa 3.4 — Ajuste de tom visual

BS5 difere do BS3 em três pontos que aparecem em todas as páginas:

- links vêm **sublinhados** → `a { text-decoration: none } a:hover { text-decoration: underline }` no `style.css`, se quisermos manter o look atual;
- fonte padrão é a system stack (BS3 usava Helvetica Neue) → fixar `--bs-body-font-family` se a diferença incomodar;
- `.btn` tem raio e padding maiores; `.form-control` é mais alto (BS5: 38px vs 34px).

**Verificar:** `python scripts/visual_baseline.py … /tmp/awm-visual/pos-bs5` e comparar com `/antes` (ver Fase 7).

---

## 8. Fase 4 — templates (3 h, 5 commits)

Ordem por risco crescente. Renomeações mecânicas:

| BS3 | BS5 |
|---|---|
| `form-group` | `mb-3` |
| `control-label` | `form-label` |
| `help-block` | `form-text` |
| `input-sm` | `form-control-sm` |
| `form-inline` | `d-flex gap-2 align-items-center` |
| `btn-default` | `btn-outline-secondary` (mantém o cinza claro) |
| `btn-xs` | `btn-sm` |
| `btn-block` | `w-100` |
| `col-md-offset-N` | `offset-md-N` |
| `col-sm-offset-N` | `offset-sm-N` |
| `table-condensed` | `table-sm` |
| `label label-warning` | `badge text-bg-warning` |
| `label label-success` | `badge text-bg-success` |
| `label label-danger` | `badge text-bg-danger` |
| `label label-default` | `badge text-bg-secondary` |
| `panel / panel-heading / panel-body` | `card / card-header / card-body` |
| `input-group-btn` (span) | remover wrapper; botão vira filho direto do `.input-group` |
| `text-muted` | `text-body-secondary` |
| `text-left` | `text-start` |
| `close` + `&times;` | `btn-close` |
| `img-responsive` | `img-fluid` |
| `hidden-xs` | `d-none d-sm-block` |

### Tarefa 4.1 — Formulários públicos (commit 1)

`admin/login.html`, `admin/forgot_password.html`, `admin/change_password.html`, `admin/user_edit.html`, `public/contact.html`, `public/info.html`.

Exemplo (`login.html`):

```html
<div class="row">
  <div class="col-md-4 offset-md-4">
    <h2 data-i18n="admin_login_title">Admin Login</h2>
    <form method="post" action="…">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
      <div class="mb-3">
        <label class="form-label" for="username" data-i18n="admin_username">Username</label>
        <input type="text" id="username" name="username" class="form-control"
               autocomplete="username" required>
      </div>
      …
      <button type="submit" class="btn btn-primary w-100" data-i18n="btn_login">Login</button>
    </form>
    <p class="text-center mt-3">
      <a href="…" class="text-body-secondary small">Forgot password?</a>
    </p>
  </div>
</div>
```

**Verificar:** `pytest -q` (10 passed) + screenshots de `/admin/login`, `/admin/forgot-password`.

### Tarefa 4.2 — Dashboard admin (commit 2)

`admin/dashboard.html` (56 tokens): botões de filtro, `form-inline` → `d-flex`, `input-group` sem `input-group-btn`, badges de status, `table-condensed` → `table-sm`.

```html
<form method="get" class="d-flex gap-2">
  <input type="hidden" name="status" value="{{ status_filter }}">
  <div class="input-group input-group-sm">
    <input type="text" name="q" class="form-control" placeholder="Name, city, collaborator..." value="{{ q }}">
    <button type="submit" class="btn btn-outline-secondary">Search</button>
    {% if q %}<a href="…" class="btn btn-outline-secondary" aria-label="Clear">&times;</a>{% endif %}
  </div>
</form>
```

### Tarefa 4.3 — Admin users (commit 3)

`admin/users.html` (46 tokens): `panel` → `card`, `data-toggle="collapse"` → `data-bs-toggle="collapse"`, `glyphicon` → SVG.

Alternativa nativa (recomendada se quiser cortar JS): trocar card+collapse por `<details class="card"><summary class="card-header">…</summary><div class="card-body">…</div></details>`. Zero JS, teclado e leitor de tela nativos. Decidir na execução.

### Tarefa 4.4 — Formulário público de submissão e edição (commit 4)

`public/add.html` (38), `admin/edit.html` (40), `public/home.html` (6), `public/search.html` (7), `public/about.html`, `public/stats.html`.

Foco: `input-group-btn` (4 ocorrências), `input-group-lg` (home), grids `col-md-*`.

### Tarefa 4.5 — Moderação e páginas finais (commit 5)

`moderation/confirm.html` (25): `btn-lg`, `table-bordered`, ícones.
`public/add_done.html`, `public/thankyou_donation.html`, `emails/*` (2 tokens cada; e-mails podem ficar como estão — clientes de e-mail não carregam BS5).

**Verificar cada commit:** `grep -Rn "btn-default\|form-group\|panel\|glyphicon\|data-toggle\|data-target\|data-dismiss\|col-md-offset\|btn-block\|input-group-btn\|input-sm\|form-inline\|text-muted" app/templates` deve encolher até zero no commit 5.

---

## 9. Fase 5 — ícones (1 h)

10 ícones em 3 arquivos: `ok` (5), `remove` (2), `user` (1), `plus` (1), `pencil` (1).

Criar `app/templates/_icons.html` com sprite de 5 símbolos, paths de Bootstrap Icons 1.13.2 (MIT), baixados de `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.2/icons/<nome>.svg`:

| Glyphicon | Bootstrap Icon |
|---|---|
| `glyphicon-ok` | `check-lg` |
| `glyphicon-remove` | `x-lg` |
| `glyphicon-user` | `person-fill` |
| `glyphicon-plus` | `plus-lg` |
| `glyphicon-pencil` | `pencil-fill` |

Macro:

```jinja
{% macro icon(name, cls="") -%}
<svg class="bi {{ cls }}" width="1em" height="1em" fill="currentColor" aria-hidden="true" focusable="false">
  <use href="#i-{{ name }}"></use>
</svg>
{%- endmacro %}
```

Uso: `{% from "_icons.html" import icon %}` … `{{ icon('check-lg') }}`.

**Verificar:** contagem `grep -ro 'glyphicon' app/templates | wc -l` → 0; cada botão de ação do dashboard e da moderação mostra o ícone alinhado ao texto.

---

## 10. Fase 6 — remoção do legado (30 min)

1. Remover `jquery-1.12.4.min.js` do `base.html` e de qualquer template que ainda carregue.
2. Remover link/script do Bootstrap 3.
3. `grep -Rn "jquery\|\$(" app/templates app/static/js` → só deve sobrar `i18n.js` sem jQuery.
4. Rodar o gate de classes da Fase 4 (deve sair vazio).
5. `pytest -q` → 9 passed.

---

## 11. Fase 7 — QA (2 h)

| Verificação | Como | Critério |
|---|---|---|
| Funcional | `pytest -q` | 9 passed |
| Visual | 18 screenshots antes/depois + `compare` do ImageMagick | diferenças explicadas, nenhuma quebra de layout |
| Mobile | viewport 390 px em `/`, `/add`, `/admin/login` | menu abre/fecha, mapa ocupa a largura |
| Teclado | Tab por `/add` e `/admin/dashboard` | foco visível, ordem coerente |
| Acessibilidade | `npx pa11y http://localhost:5000/` e `/add` | sem erros novos vs baseline |
| i18n | trocar para ZH e conferir textos + Enter no geocode | sem string em inglês vazando |
| Gerenciador de senhas | Chrome/Safari em `/admin/login` | oferece preencher |
| Performance | DevTools Network (gzip) | ≤ 48 KB de BS5, jQuery ausente |

Salvar o relatório em `docs/qa-bootstrap5-2026-11.md` (no repo, commit final).

---

## 12. Deploy e rollback

**Patch (Fase 1):** merge após checklist → servidor `git pull && docker compose up --build -d` → Cloudflare purge `/` e `/static/*`.

**Migração (Fases 2–6):** só depois de QA local; merge em `master` = deploy imediato.

```bash
# deploy
cd /caminho/no/servidor && git pull && docker compose up --build -d
# rollback
git checkout pre-bs5-2026-11-14 && git pull --ff-only && docker compose up --build -d
```

Purge do Cloudflare nas duas direções (CSS/JS ficam em cache por path). Verificar `curl -sI https://www.archivesmap.org/static/vendor/bootstrap/bootstrap.min.css` → 200 e `content-type: text/css`.

---

## 13. Riscos

| Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|
| Regressão visual em página não testada | média | médio | 18 screenshots + revisão página a página antes do merge |
| Cache do Cloudflare servir CSS antigo com HTML novo | média | alto | purge de `/static/*` após deploy; versionar `style.css?v=2` se persistir |
| Hash SRI divergente quebra CSS/JS em produção | baixa | alto | testar local; validar hash com `openssl` imediatamente antes do commit |
| Ajuste fino de espaçamento/formulários consumir mais tempo | alta | baixo | tratar como esperado; reservar 1 dia extra |
| Sem testes automatizados → bug silencioso em rota admin | média | médio | smoke tests + login manual no dashboard antes do merge |
| Ícones SVG com alinhamento diferente dos glyphicons | baixa | baixo | `width/height: 1em` + `vertical-align: -0.125em` |
| Mapa perder pinos por falta das imagens do Leaflet | baixa | alto | vendorizar `images/` (Tarefa 2.1) e checar `/` na QA |

---

## 14. Decisões pendentes (precisam do Ricardo)

1. **Vendorizar ou CDN+SRI?** Recomendo vendorizar (Fase 2). Se preferir CDN, o SRI do patch fica permanente e cada bump exige novo hash.
2. **`<details>` no card de criação de usuário** (sem JS) ou manter collapse do BS5?
3. **Manter a aparência idêntica** (links sem sublinhado, fonte Helvetica) ou aceitar o look padrão BS5?
4. **Janela de deploy**: patch pode ir hoje; migração em fim de semana/horário de baixa?
5. **PR separado por fase** (recomendado) ou um único PR grande?

---

## 15. Sequência de commits

```
pre-bs5-2026-11-14                     (tag)

fix/a11y-sri-ime
 1. test: smoke tests das rotas públicas
 2. fix(a11y): autocomplete em login e troca de senha
 3. fix(a11y): Enter seguro para IME no geocode
 4. fix(security): SRI + crossorigin nos 8 assets de CDN

chore/bootstrap-5
 5. chore(vendor): bootstrap 5.3.9 e leaflet 1.9.4 self-hosted + manifesto
 6. feat(ui): base.html e CSS global em Bootstrap 5
 7. feat(ui): formulários e dashboard em Bootstrap 5
 8. feat(ui): admin users, submissão e moderação em Bootstrap 5
 9. feat(ui): ícones SVG no lugar dos glyphicons
10. chore: remove jQuery e Bootstrap 3
11. docs: relatório de QA da migração
```

---

## 16. Estimativa

| Fase | Horas |
|---|---|
| 0 — rede de segurança | 1,5 |
| 1 — patch | 1,0 |
| 2 — vendorização | 0,75 |
| 3 — base + CSS | 1,5 |
| 4 — templates | 3,0 |
| 5 — ícones | 1,0 |
| 6 — remoção | 0,5 |
| 7 — QA | 2,0 |
| **Total** | **11,25 h** (~2 dias úteis com folga) |

O patch sozinho entrega valor em ~1 h e não depende da migração.
