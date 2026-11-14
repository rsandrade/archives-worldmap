"""Captura screenshots e diagnóstico de console/rede das páginas do site.

Uso:
    python scripts/visual_baseline.py [base_url] [pasta_saida]

Compara estados antes/depois de mudanças de CSS. Requer o app rodando e
playwright instalado (`pip install -r requirements-dev.txt && playwright install chromium`).
"""

import asyncio
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5055"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/awm-visual/atual")
ADMIN_USER = os.environ.get("AWM_USER", "admin")
ADMIN_PASS = os.environ.get("AWM_PASS", "senha-teste-123")

PUBLIC = [
    ("/", "home"),
    ("/add", "add"),
    ("/stats", "stats"),
    ("/q?q=archives", "search"),
    ("/info/1", "info"),
    ("/about", "about"),
    ("/contact", "contact"),
    ("/admin/", "login"),
    ("/admin/forgot-password", "forgot"),
]
ADMIN = [
    ("/admin/", "dashboard"),
    ("/admin/users", "users"),
    ("/admin/edit/1", "edit"),
]
VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}


async def capture(page, url, path, problems):
    page.on("console", lambda m: problems.append(f"console[{m.type}] {url}: {m.text}")
            if m.type == "error" else None)
    page.on("pageerror", lambda e: problems.append(f"pageerror {url}: {e}"))
    page.on("requestfailed", lambda r: problems.append(f"requestfailed {url}: {r.url} {r.failure}"))
    page.on("response", lambda r: problems.append(f"http {r.status} {url}: {r.url}")
            if r.status >= 400 else None)
    await page.goto(BASE + url, wait_until="load")
    await page.wait_for_timeout(700)
    await page.screenshot(path=str(path), full_page=True)


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    problems = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, (width, height) in VIEWPORTS.items():
            ctx = await browser.new_context(viewport={"width": width, "height": height})
            page = await ctx.new_page()
            for url, slug in PUBLIC:
                await capture(page, url, OUT / f"{name}__{slug}.png", problems)

            if ADMIN_USER:
                await page.goto(BASE + "/admin/", wait_until="load")
                await page.fill('input[name="username"]', ADMIN_USER)
                await page.fill('input[name="password"]', ADMIN_PASS)
                await page.click('button[type="submit"]')
                await page.wait_for_load_state("load")
                for url, slug in ADMIN:
                    await capture(page, url, OUT / f"{name}__{slug}.png", problems)
            await ctx.close()
        await browser.close()

    (OUT / "problems.txt").write_text("\n".join(problems) + ("\n" if problems else ""))
    print(f"{len(list(OUT.glob('*.png')))} screenshots em {OUT}")
    print(f"{len(problems)} problemas de console/rede")
    for line in problems[:15]:
        print("  " + line)


asyncio.run(main())
