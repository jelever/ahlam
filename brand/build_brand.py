"""Generate the logo files, favicons, app icons and share image.

    .venv/Scripts/python -m pip install -r brand/requirements.txt
    .venv/Scripts/python brand/build_brand.py

The mark is defined once in marks.py ("home", and "home-icon" for small sizes);
everything here is drawn from it, and the words are outlined from the fonts in
brand/fonts, so no file depends on installed fonts. The outputs are committed:
the site build and CI never run this script.
"""
import io
import json
import re
import sys
from pathlib import Path

import resvg_py
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from lockup import NAME, SUB, horizontal, stacked  # noqa: E402
from marks import MARKS, mark_g  # noqa: E402
from textpath import Text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "brand"      # deployed: what the pages use
DIST = ROOT / "brand" / "dist"       # not deployed: the logo set for the client

# The palette (the same values are the tokens at the top of site.css).
OLIVE = "#3d4633"
INK = "#2a2a24"
BG = "#faf7f3"
BAND = "#f3eee8"
WHITE = "#fffdfb"
COLOURS = {"olive": (OLIVE, INK), "ink": (INK, INK), "white": (WHITE, WHITE)}

FULL, SMALL = "home", "home-icon"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def png(svg, width, height=None):
    data = resvg_py.svg_to_bytes(svg_string=svg, width=width, height=height)
    return Image.open(io.BytesIO(bytes(data))).convert("RGBA")


def size_of(svg):
    w, h = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups()
    return float(w), float(h)


def mark_file(key, colour, pad=0):
    s = 48 + 2 * pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" width="{s}" height="{s}">'
            f'<g transform="translate({pad} {pad})">{mark_g(key, colour=colour)}</g></svg>')


def tile(size, radius, key=SMALL, scale=.8, bg=OLIVE, fg=BAND, heavier=1.0):
    """The mark centred on a coloured square (favicons and app icons)."""
    sw = MARKS[key]["sw"] * heavier
    off = 24 - 24 * scale  # keep the mark centred
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="{size}" height="{size}">'
            f'<rect width="48" height="48" rx="{radius}" fill="{bg}"/>'
            f'<g transform="translate({off:.2f} {off + .4:.2f}) scale({scale})">{mark_g(key, sw, fg)}</g></svg>')


def logos():
    out = DIST / "logo"
    out.mkdir(parents=True, exist_ok=True)
    for name, (mark_colour, text_colour) in COLOURS.items():
        files = {
            f"mark-{name}": mark_file(FULL, mark_colour),
            f"icon-{name}": mark_file(SMALL, mark_colour),
            f"logo-ar-{name}": horizontal(FULL, "ar", mark_colour, text_colour),
            f"logo-en-{name}": horizontal(FULL, "en", mark_colour, text_colour),
            f"logo-stacked-{name}": stacked(FULL, mark_colour, text_colour),
        }
        for stem, svg in files.items():
            write(out / f"{stem}.svg", svg)
            w, h = size_of(svg)
            base = 512 if stem.startswith(("mark", "icon")) else 1200  # 1x width in px
            for k, suffix in ((1, ""), (2, "@2x")):
                png(svg, int(base * k)).save(out / f"{stem}{suffix}.png", optimize=True)
    print("logo files:", len(list(out.iterdir())))


def favicons():
    out = OUT / "favicon"
    out.mkdir(parents=True, exist_ok=True)
    # The tab icon: a solid olive tile reads on light and dark tab strips alike.
    write(out / "favicon.svg", tile(48, 11, heavier=1.2))
    # Small rasters get a heavier stroke so the armchair survives at 16 px.
    ico = [png(tile(s, 11 if s > 16 else 9, heavier=1.35 if s <= 32 else 1.2), s) for s in (16, 32, 48)]
    ico[2].save(out / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:2])
    # iOS rounds the corners itself and shows transparency as black: square, solid.
    png(tile(180, 0, scale=.72), 180).convert("RGB").save(out / "apple-touch-icon.png", optimize=True)
    for s in (192, 512):
        png(tile(s, 11), s).save(out / f"icon-{s}.png", optimize=True)
    # Maskable: full bleed, artwork inside the central 80% safe zone.
    png(tile(512, 0, scale=.62), 512).save(out / "icon-maskable-512.png", optimize=True)
    manifest = {
        "id": "/",
        "name": "أحلام القمر للتجارة",
        "short_name": "أحلام القمر",
        "description": "معرض منتجات شركة أحلام القمر للتجارة",
        "lang": "ar",
        "dir": "rtl",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "theme_color": OLIVE,
        "background_color": BG,
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    write(out / "site.webmanifest", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print("favicon files:", len(list(out.iterdir())))


def social():
    """The default share image, 1200x630: the bilingual lockup on the brand band."""
    W, H = 1200, 630
    ar = Text("ar", NAME["ar"], 92, wght=600)
    en = Text("en", NAME["en"], 30, wght=600, tracking=.2)
    sub_ar = Text("ar", "شركة أحلام القمر للتجارة", 30, wght=400)
    sub_en = Text("en", "Ahlam Alqamar Trading Company", 24, wght=400, tracking=.02)
    mark_px = 190
    body = [
        f'<rect width="{W}" height="{H}" fill="{BAND}"/>',
        f'<rect y="{H - 18}" width="{W}" height="18" fill="{OLIVE}"/>',
        f'<g transform="translate({(W - mark_px) / 2:.1f} 70) scale({mark_px / 48:.4f})">{mark_g(FULL, colour=OLIVE)}</g>',
        ar.at((W - ar.width) / 2, 375, INK),
        en.at((W - en.width) / 2, 428, INK),
        f'<rect x="{W / 2 - 30}" y="462" width="60" height="2" fill="{OLIVE}" opacity=".5"/>',
        sub_ar.at((W - sub_ar.width) / 2, 520, "#4b4a43"),
        sub_en.at((W - sub_en.width) / 2, 560, "#7d776d"),
    ]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
           + "".join(body) + "</svg>")
    out = OUT / "social"
    out.mkdir(parents=True, exist_ok=True)
    write(DIST / "og-default.svg", svg)
    png(svg, W).convert("RGB").save(out / "og-default.jpg", quality=88, optimize=True, progressive=True)
    print("social: og-default.jpg")

    # The logo strip under every product and collection share image
    # (build.py pastes it below the photo): olive, Arabic lockup at the
    # reading start, English name at the other end.
    SH = 76
    lock = horizontal(FULL, "ar", BAND, WHITE)
    lw, lh = size_of(lock)
    k = 44 / lh
    en_name = Text("en", NAME["en"], 15, wght=600, tracking=.2)
    strip = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {SH}" width="{W}" height="{SH}">'
             f'<rect width="{W}" height="{SH}" fill="{OLIVE}"/>'
             f'<g transform="translate({W - 40 - lw * k:.1f} {(SH - 44) / 2:.1f}) scale({k:.4f})">'
             f'{lock[lock.index(">") + 1:lock.rindex("</svg>")]}</g>'
             + en_name.at(40, SH / 2 + 5, BAND) + "</svg>")
    png(strip, W).convert("RGB").save(DIST / "og-strip.png", optimize=True)
    print("social: og-strip.png")


def template_mark():
    """The site's inline logo symbol (templates/partials/mark.svg), in currentColor."""
    write(ROOT / "templates" / "partials" / "mark.svg",
          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
          f'{mark_g(FULL)}</svg>\n')


def guide():
    """brand/guide.html: a one-page brand sheet for the client, drawn from
    the same files (open it from the brand folder; it is not deployed)."""
    swatches = [("Olive", "زيتوني", OLIVE, "#fff"), ("Ink", "حبر", INK, "#fff"), ("Sand", "رملي", BAND, INK),
                ("Ivory", "عاجي", BG, INK), ("Olive 2", "زيتوني فاتح", "#4b5641", "#fff"), ("Stone", "حجري", "#e4ddd3", INK)]
    sw_html = "".join(
        f'<div class="sw"><span style="background:{c};color:{fg}">{c}</span><b>{en}</b><small lang="ar">{ar}</small></div>'
        for en, ar, c, fg in swatches)

    def img(path, h, bg="transparent", cls=""):
        return f'<div class="tile {cls}" style="background:{bg}"><img src="{path}" style="height:{h}px" alt=""></div>'

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ahlam Alqamar brand sheet</title>
<link href="https://fonts.googleapis.com/css2?family=Alexandria:wght@300;400;500;600&family=Figtree:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{ --olive:{OLIVE}; --ink:{INK}; --band:{BAND}; --bg:{BG}; --line:#e4ddd3; --muted:#7d776d; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.6 Figtree, system-ui, sans-serif; }}
  main {{ max-width:1080px; margin:0 auto; padding:48px 24px 80px; }}
  h1 {{ font-weight:500; font-size:40px; letter-spacing:-.02em; margin:0 0 6px; }}
  h2 {{ font-weight:600; font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin:56px 0 16px; }}
  p {{ margin:0 0 10px; max-width:70ch; }}  [lang="ar"] {{ font-family:Alexandria, sans-serif; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:16px; }}
  .tile {{ border-radius:18px; padding:36px; display:grid; place-items:center; border:1px solid var(--line); min-height:180px; }}
  .tile img {{ max-width:100%; }}
  .sws {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:14px; }}
  .sw span {{ display:flex; align-items:flex-end; height:110px; border-radius:14px; padding:12px; font:600 13px Figtree; border:1px solid var(--line); }}
  .sw b {{ display:block; margin-top:8px; font-weight:600; }}  .sw small {{ color:var(--muted); }}
  .type {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  .type div {{ background:#fff; border:1px solid var(--line); border-radius:18px; padding:28px; }}
  .type .big {{ font-size:44px; font-weight:500; line-height:1.3; }}
  .rules {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; }}
  .rule {{ background:#fff; border:1px solid var(--line); border-radius:18px; padding:20px; }}
  .rule .demo {{ height:120px; display:grid; place-items:center; background:var(--band); border-radius:12px; margin-bottom:12px; overflow:hidden; }}
  .rule b {{ color:#a4553f; }}
  .space {{ position:relative; display:inline-block; padding:28px; outline:1px dashed var(--olive); outline-offset:0; background:#fff; }}
  .icons {{ display:flex; gap:24px; align-items:flex-end; flex-wrap:wrap; }}
  .icons figure {{ margin:0; text-align:center; font-size:12px; color:var(--muted); }}
  .icons img {{ display:block; margin:0 auto 8px; }}
  @media (max-width:700px) {{ .type {{ grid-template-columns:1fr; }} }}
</style></head><body><main>
<h1>Ahlam Alqamar: brand sheet</h1>
<p class="muted">Logo, colours, type and web icons for شركة أحلام القمر للتجارة. All logo files are in <code>dist/logo/</code>, as SVG (for print and the web) and PNG at 1x and 2x.</p>
<p><b>Status:</b> a proposal for the client's approval. The mark is a clean redraw of the "Warm Home Collections" emblem the owner chose on 2026-11-04: a house with a chimney holding a floor lamp, an armchair and a potted plant. It has no crescent or moon, as the client's brief asks.</p>

<h2>Logo</h2>
<div class="grid">
  {img("dist/logo/logo-ar-olive.svg", 72, BG)}
  {img("dist/logo/logo-en-olive.svg", 72, BG)}
  {img("dist/logo/logo-stacked-olive.svg", 150, "#fff")}
  {img("dist/logo/logo-ar-white.svg", 72, OLIVE)}
  {img("dist/logo/logo-en-white.svg", 72, INK)}
  {img("dist/logo/logo-stacked-ink.svg", 150, BAND)}
</div>

<h2>Mark: full and small</h2>
<p>Use the full mark from 32 px up. Below that, and for app and browser icons, use the small mark (the house and the armchair only): the lamp and plant cannot be read at 16 px.</p>
<div class="grid">
  {img("dist/logo/mark-olive.svg", 140, "#fff")}
  {img("dist/logo/icon-olive.svg", 140, "#fff")}
  {img("dist/logo/mark-white.svg", 140, OLIVE)}
</div>

<h2>Clear space and minimum size</h2>
<p>Keep a margin of at least a quarter of the mark's height on every side. Minimum sizes: the mark 24 px (6 mm in print), a horizontal lockup 120 px wide (30 mm).</p>
<div class="space"><img src="dist/logo/logo-ar-olive.svg" style="height:64px;display:block" alt=""></div>

<h2>Colours</h2>
<div class="sws">{sw_html}</div>
<p style="margin-top:14px">Olive is the brand colour: the logo, buttons and dark panels. Ink is for text. Sand and Ivory are the page and card backgrounds.</p>

<h2>Type</h2>
<div class="type">
  <div lang="ar"><p class="big">أحلام القمر</p><p>Alexandria: Arabic headings (500) and text (300 to 400).</p></div>
  <div><p class="big">Ahlam Alqamar</p><p>Figtree: English headings (500), text (400) and the logo's capitals (600 to 700, tracked).</p></div>
</div>
<p style="margin-top:14px">Both are free (SIL Open Font License) from Google Fonts; the files are in <code>fonts/</code>.</p>

<h2>Web and app icons</h2>
<div class="icons">
  <figure><img src="../static/brand/favicon/favicon.svg" width="16" height="16" alt="">16 px</figure>
  <figure><img src="../static/brand/favicon/favicon.svg" width="32" height="32" alt="">32 px</figure>
  <figure><img src="../static/brand/favicon/apple-touch-icon.png" width="90" height="90" alt="" style="border-radius:20px">iPhone home screen</figure>
  <figure><img src="../static/brand/favicon/icon-maskable-512.png" width="90" height="90" alt="" style="border-radius:50%">Android (maskable)</figure>
  <figure><img src="../static/brand/social/og-default.jpg" width="300" alt="" style="border-radius:8px">Share preview (1200 × 630)</figure>
</div>

<h2>Do not</h2>
<div class="rules">
  <div class="rule"><div class="demo"><img src="dist/logo/mark-olive.svg" style="height:80px;transform:scaleX(1.5)" alt=""></div><b>Stretch or squash</b> the logo.</div>
  <div class="rule"><div class="demo"><img src="dist/logo/mark-olive.svg" style="height:80px;filter:drop-shadow(0 0 12px #c08a3e) hue-rotate(160deg)" alt=""></div><b>Add glows, shadows or other colours.</b></div>
  <div class="rule"><div class="demo" style="background:#8a7f6e"><img src="dist/logo/mark-olive.svg" style="height:80px" alt=""></div><b>Place it on a busy or low-contrast background;</b> use the white version on dark or photo backgrounds.</div>
  <div class="rule"><div class="demo"><span style="font-size:60px">☾</span></div><b>Add a crescent, moon or stars:</b> the client's brief forbids them.</div>
</div>
</main></body></html>
"""
    write(Path(__file__).parent / "guide.html", html)
    print("guide: brand/guide.html")


if __name__ == "__main__":
    guide()
    logos()
    favicons()
    social()
    template_mark()
