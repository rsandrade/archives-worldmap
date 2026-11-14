# QA — migração Bootstrap 3.3.7 → 5.3.9

Data: 2026-11-14
Branch: `chore/bootstrap-5`
Ambiente: app local (Flask, SQLite de teste com 3 instituições), Python 3.14.7, Chromium headless 159.

## Resultado

| Verificação | Resultado |
|---|---|
| `pytest -q` | 12 passed |
| Screenshots (2 viewports × 12 páginas) | 24 gerados |
| Erros de console | 0 |
| Requisições com erro (≥400) | 0 |
| Diferença visual média vs. BS3 | 6,34% dos pixels |
| Bootstrap JS carregado | sim (`window.bootstrap` = object) |
| Menu mobile abre/fecha | sim (clique no `.navbar-toggler`) |
| Card "New user" expande | sim (collapse do BS5) |

Páginas cobertas: `/`, `/add`, `/stats`, `/q`, `/info/1`, `/about`, `/contact`, `/admin/` (login), `/admin/forgot-password`, `/admin/` (dashboard autenticado), `/admin/users`, `/admin/edit/1`.

## Diferenças visuais

Nenhuma quebra de layout. As diferenças são tipográficas e de acabamento do BS5:

- Controles de formulário e botões têm altura/raio levemente diferentes (BS5 usa padding em `rem`).
- Badges de status passaram de `.label` para `.badge text-bg-*` (mesmas cores semânticas).
- O menu mobile usa o toggler do BS5 (ícone hambúrguer desenhado em CSS) em vez do `.icon-bar` do BS3.
- Links do rodapé mantêm o tom atual; a regra global impede o sublinhado padrão do BS5.

Maior diferença medida: `mobile__about.png` (23,3%), por quebra de linha do rodapé em viewport de 390 px — comportamento responsivo esperado, não regressão.

## Peso transferido

| | Antes | Depois |
|---|---|---|
| Bootstrap CSS + JS | 19,5 + 9,8 KB gz | 30,8 + 16,5 KB gz |
| jQuery | 33,6 KB gz | removido |
| **Total do framework** | **62,9 KB gz** | **47,3 KB gz** |
| Tags de CDN | 8 | 0 (vendorizado) |

## Pendências conhecidas

- Sem verificação em Safari/Firefox real; QA feita em Chromium. `keyCode === 229` cobre o caso do Safari por especificação, mas não foi exercitado em dispositivo.
- Teste de IME com teclado chinês real não executado — validado por código e documentação, não por digitação.
- Login do painel admin usa senha temporária no teste local; fluxo de e-mail não exercitado.
