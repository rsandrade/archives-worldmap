import base64
import json
import os
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "screenshots" / "awm-interface-proposal.png"
OUTDIR = ROOT / "gpt-image-2"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / "awm-interface-concept-gpt-image-2.png"
RESP = OUTDIR / "openai-response.json"


def get_key():
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key.strip().strip('"')
    for p in [Path.home() / ".hermes/.env", Path.home() / ".hermes/config.yaml"]:
        if not p.exists():
            continue
        txt = p.read_text(errors="ignore")
        m = re.search(r"sk-proj-[A-Za-z0-9_-]{20,}", txt) or re.search(r"sk-[A-Za-z0-9_-]{20,}", txt)
        if m:
            return m.group(0)
    raise RuntimeError("OPENAI_API_KEY not found")

PROMPT = """
Use the attached screenshot as the primary composition reference. Recreate it as a polished high-fidelity product design concept image for the Archives World Map (AWM) interface, not as a literal browser screenshot.

Goal: a refined editorial UI presentation showing a modern archival world map dashboard.

Preserve these structural ideas from the reference:
- warm cartographic paper background;
- top navigation bar with AWM identity;
- left panel with search and filters;
- central world map with institutional pins and subtle grid/continent shapes;
- right institutional detail panel with a selected archive record;
- a visible conceptual bridge from AWM to ArchivAI;
- professional public-sector / archival heritage tone.

Visual style:
- contemporary cartographic archive interface;
- elegant, calm, institutional, credible;
- warm ivory paper, deep navy blue, archival blue, muted rust, green, gold accents;
- high-end UX mockup, not SaaS marketing slop;
- crisp panels, tasteful shadows, glass only very subtle;
- no neon, no purple gradients, no emojis, no fake flags.

Text handling:
- Avoid generating long readable paragraphs. Use mostly abstract UI text lines.
- The only exact readable title allowed is: “Archives World Map”.
- If adding a short label, use: “AWM → ArchivAI” and “Institutional map”.
- Do not invent statistics or country flags.

Output should feel like a premium design-board render suitable for a grant proposal or product strategy presentation. Landscape composition, 3:2, very clean, detailed, realistic UI mockup.
""".strip()


def call(model):
    key = get_key()
    url = "https://api.openai.com/v1/images/edits"
    headers = {"Authorization": f"Bearer {key}"}
    with INPUT.open("rb") as f:
        files = {"image": (INPUT.name, f, "image/png")}
        data = {
            "model": model,
            "prompt": PROMPT,
            "n": "1",
            "size": "1536x1024",
            "quality": "medium",
        }
        r = requests.post(url, headers=headers, files=files, data=data, timeout=300)
    try:
        payload = r.json()
    except Exception:
        payload = {"status_code": r.status_code, "text": r.text[:2000]}
    RESP.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    if r.status_code >= 400:
        raise RuntimeError(f"{model} failed: {r.status_code} {payload}")
    b64 = payload["data"][0].get("b64_json")
    if not b64:
        # Some APIs return a URL; download if present.
        url = payload["data"][0].get("url")
        if not url:
            raise RuntimeError(f"No b64_json or url in response: {payload}")
        img = requests.get(url, timeout=120).content
    else:
        img = base64.b64decode(b64)
    OUT.write_bytes(img)
    return model

if __name__ == "__main__":
    for model in ["gpt-image-2", "gpt-image-1"]:
        try:
            used = call(model)
            print(json.dumps({"ok": True, "model": used, "output": str(OUT), "response": str(RESP)}, ensure_ascii=False))
            break
        except Exception as e:
            print(json.dumps({"ok": False, "model": model, "error": str(e)[:1000]}, ensure_ascii=False))
    else:
        raise SystemExit(1)
