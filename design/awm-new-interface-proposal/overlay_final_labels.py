from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "gpt-image-2" / "awm-interface-concept-gpt-image-2-clean-base.png"
OUT = ROOT / "gpt-image-2" / "awm-interface-concept-gpt-image-2-final.png"

img = Image.open(BASE).convert("RGBA")
W, H = img.size

def font(path_candidates, size):
    for p in path_candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size=size)

serif = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
], 54)
serif_sm = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
], 26)
sans = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
], 24)
sans_bold = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
], 22)
mono = font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
], 18)

over = Image.new("RGBA", img.size, (0,0,0,0))
d = ImageDraw.Draw(over)

navy = (32, 48, 96, 255)
blue = (48, 96, 192, 255)
muted = (92, 104, 130, 255)
paper = (255, 253, 247, 230)
line = (32, 48, 96, 42)
white = (255, 255, 255, 235)
rust = (182, 90, 54, 255)
green = (76, 122, 105, 255)

# Title overlay card
x, y = 58, 52
card_w, card_h = 585, 158
d.rounded_rectangle([x, y, x+card_w, y+card_h], radius=28, fill=paper, outline=line, width=2)
d.text((x+28, y+22), "Archives World Map", fill=navy, font=serif)
d.text((x+31, y+92), "institutional map · ISDIAH layer", fill=muted, font=sans)
# small blue marker
cx, cy = x+card_w-54, y+52
d.ellipse([cx-14, cy-14, cx+14, cy+14], fill=blue, outline=(255,255,255,255), width=3)
d.ellipse([cx-5, cy-5, cx+5, cy+5], fill=(255,255,255,255))

# ArchivAI bridge tag
bx, by = W-446, 58
bw, bh = 376, 78
d.rounded_rectangle([bx, by, bx+bw, by+bh], radius=22, fill=white, outline=line, width=2)
d.text((bx+22, by+15), "AWM → ArchivAI", fill=blue, font=sans_bold)
d.text((bx+22, by+45), "map first, collections next", fill=muted, font=mono)

# Legend with exact text
lx, ly = W-410, H-160
lw, lh = 338, 98
d.rounded_rectangle([lx, ly, lx+lw, ly+lh], radius=22, fill=paper, outline=line, width=2)
legend = [(blue, "verified institution"), (green, "ArchivAI available"), (rust, "review needed")]
for i, (col, label) in enumerate(legend):
    yy = ly + 18 + i*25
    d.ellipse([lx+20, yy+3, lx+32, yy+15], fill=col)
    d.text((lx+44, yy), label, fill=muted, font=mono)

# Subtle footer note
fx, fy = 58, H-78
d.rounded_rectangle([fx, fy, fx+520, fy+40], radius=18, fill=(255,253,247,205), outline=(32,48,96,30), width=1)
d.text((fx+20, fy+10), "Concept render from Huashu HTML prototype · gpt-image-2", fill=(92,104,130,230), font=mono)

final = Image.alpha_composite(img, over).convert("RGB")
final.save(OUT, quality=95)
print(OUT)
