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
OUT = OUTDIR / "awm-interface-concept-gpt-image-2-clean-base.png"
RESP = OUTDIR / "openai-response-clean-base.json"


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
Use the attached screenshot only as a composition reference. Recreate it as a premium, polished high-fidelity concept render for a modern archival world map interface.

IMPORTANT TEXT RULE:
- Do not generate any readable text, letters, words, numbers, icons with letters, or fake UI copy anywhere in the image.
- Replace all text areas with clean abstract grey/navy horizontal lines and small neutral blocks, like a text skeleton/wireframe.
- The final image must be free of pseudo-text and misspelled labels.
- Leave tasteful blank/low-detail space in the top-left header for a real title overlay later.

Preserve the visual structure:
- warm cartographic paper background;
- top app navigation/header area;
- left panel with search/filter skeleton controls;
- central world map with institutional pins, subtle grid and soft continent shapes;
- right panel with institutional detail card skeleton;
- small conceptual bridge area suggesting AWM to ArchivAI, but without text;
- mobile preview / bottom sheet hint may appear subtly.

Visual style:
- contemporary cartographic archive interface;
- elegant, calm, institutional, credible;
- warm ivory paper, deep navy blue, archival blue, muted rust, green, and gold accents;
- high-end UX mockup for a grant proposal/product strategy presentation;
- crisp panels, subtle shadows, no neon, no purple gradients, no emojis, no flags, no decorative fake statistics.

Landscape 3:2 composition. Make it beautiful and coherent, but with absolutely no readable text.
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
    if b64:
        img = base64.b64decode(b64)
    else:
        url = payload["data"][0].get("url")
        if not url:
            raise RuntimeError(f"No b64_json or url in response: {payload}")
        img = requests.get(url, timeout=120).content
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
