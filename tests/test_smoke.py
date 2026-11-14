"""Smoke tests: as páginas públicas precisam continuar renderizando depois
do patch de acessibilidade e da migração Bootstrap 3 -> 5."""

import pytest

PUBLIC_PAGES = [
    "/",
    "/add",
    "/stats",
    "/q?q=archives",
    "/about",
    "/contact",
    "/admin/",
    "/admin/forgot-password",
    "/api/pins",
    "/robots.txt",
]


@pytest.mark.parametrize("url", PUBLIC_PAGES)
def test_public_pages_render(client, url):
    response = client.get(url)
    assert response.status_code == 200, url

    if response.mimetype == "text/html":
        body = response.get_data(as_text=True)
        assert "bootstrap" in body.lower(), f"CSS do framework ausente em {url}"
        assert "data-i18n" in body, f"i18n ausente em {url}"


def test_home_has_map(client):
    body = client.get("/").get_data(as_text=True)
    assert 'id="mapid"' in body
    assert "leaflet" in body.lower()


def test_home_has_navigation(client):
    body = client.get("/").get_data(as_text=True)
    assert "navbar" in body
    assert 'data-lang="pt-br"' in body
