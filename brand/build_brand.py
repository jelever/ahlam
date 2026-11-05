"""Generate the logo files, favicons, app icons and share images.

    .venv/Scripts/python -m pip install -r brand/requirements.txt
    .venv/Scripts/python brand/build_brand.py

The logo is the company name, with no symbol (owner's decision, 2026-11-05).
Where the name cannot fit (favicons, app icons) the monogram "أق" stands in.
Everything is drawn from lockup.py, with the words outlined from the fonts in
brand/fonts, so no file depends on installed fonts. The outputs are
committed: the site build and CI never run this script.
"""
import io
import json
import re
import shutil
import sys
from pathlib import Path

import resvg_py
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from lockup import SLOGAN, monogram_path, stacked, wordmark, wordmark_body  # noqa: E402
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
COLOURS = {"olive": OLIVE, "ink": INK, "white": WHITE}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def png(svg, width, height=None):
    data = resvg_py.svg_to_bytes(svg_string=svg, width=width, height=height)
    return Image.open(io.BytesIO(bytes(data))).convert("RGBA")


def tile(size, radius, scale=1.0, bg=OLIVE, fg=BAND):
    """The monogram centred on a coloured square (favicons and app icons)."""
    off = 24 - 24 * scale
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="{size}" height="{size}">'
            f'<rect width="48" height="48" rx="{radius}" fill="{bg}"/>'
            f'<g transform="translate({off:.2f} {off:.2f}) scale({scale})">{monogram_path(fg)}</g></svg>')


def monogram_file(colour):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">'
            f'{monogram_path(colour)}</svg>')


def logos():
    out = DIST / "logo"
    if out.exists():
        shutil.rmtree(out)   # the files of the earlier symbol logo go too
    out.mkdir(parents=True)
    for name, colour in COLOURS.items():
        files = {
            f"logo-ar-{name}": wordmark("ar", colour),
            f"logo-en-{name}": wordmark("en", colour),
            f"logo-stacked-{name}": stacked(colour),
            f"monogram-{name}": monogram_file(colour),
        }
        for stem, svg in files.items():
            write(out / f"{stem}.svg", svg)
            base = 512 if stem.startswith("monogram") else 1200   # 1x width in px
            for k, suffix in ((1, ""), (2, "@2x")):
                png(svg, int(base * k)).save(out / f"{stem}{suffix}.png", optimize=True)
    print("logo files:", len(list(out.iterdir())))


def favicons():
    out = OUT / "favicon"
    out.mkdir(parents=True, exist_ok=True)
    write(out / "favicon.svg", tile(48, 11))
    ico = [png(tile(s, 11 if s > 16 else 9, scale=1.08 if s <= 32 else 1.0), s) for s in (16, 32, 48)]
    ico[2].save(out / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:2])
    # iOS rounds the corners itself and shows transparency as black: square, solid.
    png(tile(180, 0, scale=.92), 180).convert("RGB").save(out / "apple-touch-icon.png", optimize=True)
    for s in (192, 512):
        png(tile(s, 11), s).save(out / f"icon-{s}.png", optimize=True)
    # Maskable: full bleed, artwork inside the central 80% safe zone.
    png(tile(512, 0, scale=.8), 512).save(out / "icon-maskable-512.png", optimize=True)
    manifest = {
        "id": "/",
        "name": "أحلام القمر للتجارة",
        "short_name": "أحلام القمر",
        "description": "مصدرك الأول في جملة المفروشات",
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


def centred(lang, colour, size, baseline, W):
    body, w, _ = wordmark_body(lang, colour, size, baseline=baseline)
    return f'<g transform="translate({(W - w) / 2:.1f} 0)">{body}</g>'


def social():
    """The default share image, 1200x630: the name and the slogan on the band."""
    W, H = 1200, 630
    slogan_ar = Text("ar", SLOGAN["ar"], 40, wght=400)
    slogan_en = Text("en", SLOGAN["en"], 17, wght=500, tracking=.2)
    body = [
        f'<rect width="{W}" height="{H}" fill="{BAND}"/>',
        f'<rect y="{H - 18}" width="{W}" height="18" fill="{OLIVE}"/>',
        centred("ar", INK, 104, 250, W),
        centred("en", INK, 50, 330, W),
        f'<rect x="{W / 2 - 30}" y="380" width="60" height="2" fill="{OLIVE}" opacity=".5"/>',
        slogan_ar.at((W - slogan_ar.width) / 2, 465, OLIVE),
        slogan_en.at((W - slogan_en.width) / 2, 515, "#7d776d"),
    ]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
           + "".join(body) + "</svg>")
    (OUT / "social").mkdir(parents=True, exist_ok=True)
    write(DIST / "og-default.svg", svg)
    png(svg, W).convert("RGB").save(OUT / "social" / "og-default.jpg", quality=88, optimize=True, progressive=True)
    print("social: og-default.jpg")

    # The strip under every product and collection share image (build.py
    # pastes it below the photo): the Arabic name at the reading start, the
    # English at the other end.
    SH = 76
    ar, aw, _ = wordmark_body("ar", WHITE, 30, baseline=SH / 2 + 11)
    en, ew, _ = wordmark_body("en", BAND, 24, baseline=SH / 2 + 5)
    strip = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {SH}" width="{W}" height="{SH}">'
             f'<rect width="{W}" height="{SH}" fill="{OLIVE}"/>'
             f'<g transform="translate({W - 40 - aw:.1f} 0)">{ar}</g>'
             f'<g transform="translate(40 0)">{en}</g></svg>')
    png(strip, W).convert("RGB").save(DIST / "og-strip.png", optimize=True)
    print("social: og-strip.png")


def guide():
    """brand/guide.html: a one-page brand sheet for the client, drawn from the
    same files (open it from the brand folder; it is not deployed)."""
    swatches = [("Olive", "زيتوني", OLIVE, "#fff"), ("Ink", "حبر", INK, "#fff"), ("Sand", "رملي", BAND, INK),
                ("Ivory", "عاجي", BG, INK), ("Olive 2", "زيتوني فاتح", "#4b5641", "#fff"), ("Stone", "حجري", "#e4ddd3", INK)]
    sw_html = "".join(
        f'<div class="sw"><span style="background:{c};color:{fg}">{c}</span><b>{en}</b><small lang="ar">{ar}</small></div>'
        for en, ar, c, fg in swatches)

    def img(path, h, bg="transparent"):
        return f'<div class="tile" style="background:{bg}"><img src="{path}" style="height:{h}px" alt=""></div>'

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ahlam Alqamar brand sheet</title>
<link href="https://fonts.googleapis.com/css2?family=Alexandria:wght@300;400;500;600&family=Figtree:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{ --olive:{OLIVE}; --ink:{INK}; --band:{BAND}; --bg:{BG}; --line:#e4ddd3; --muted:#7d776d; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.6 Figtree, system-ui, sans-serif; }}
  main {{ max-width:1080px; margin:0 auto; padding:48px 24px 80px; }}
  h1 {{ font-weight:500; font-size:40px; letter-spacing:-.02em; margin:0 0 6px; }}
  h2 {{ font-weight:600; font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin:56px 0 16px; }}
  p {{ margin:0 0 10px; max-width:70ch; }}  [lang="ar"] {{ font-family:Alexandria, sans-serif; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:16px; }}
  .tile {{ border-radius:18px; padding:36px; display:grid; place-items:center; border:1px solid var(--line); min-height:160px; }}
  .tile img {{ max-width:100%; }}
  .sws {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:14px; }}
  .sw span {{ display:flex; align-items:flex-end; height:110px; border-radius:14px; padding:12px; font:600 13px Figtree; border:1px solid var(--line); }}
  .sw b {{ display:block; margin-top:8px; font-weight:600; }}  .sw small {{ color:var(--muted); }}
  .type {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  .type div {{ background:#fff; border:1px solid var(--line); border-radius:18px; padding:28px; }}
  .type .big {{ font-size:40px; font-weight:500; line-height:1.4; }}
  .slogan {{ background:var(--olive); color:#fff; border-radius:18px; padding:32px; text-align:center; }}
  .slogan p {{ max-width:none; margin:0; }}  .slogan .ar {{ font:400 30px/1.6 Alexandria, sans-serif; }}
  .slogan .en {{ font-size:13px; letter-spacing:.2em; opacity:.8; }}
  .rules {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; }}
  .rule {{ background:#fff; border:1px solid var(--line); border-radius:18px; padding:20px; }}
  .rule .demo {{ height:110px; display:grid; place-items:center; background:var(--band); border-radius:12px; margin-bottom:12px; overflow:hidden; }}
  .rule b {{ color:#a4553f; }}
  .space {{ display:inline-block; padding:24px 32px; outline:1px dashed var(--olive); background:#fff; }}
  .icons {{ display:flex; gap:24px; align-items:flex-end; flex-wrap:wrap; }}
  .icons figure {{ margin:0; text-align:center; font-size:12px; color:var(--muted); }}
  .icons img {{ display:block; margin:0 auto 8px; }}
  @media (max-width:700px) {{ .type {{ grid-template-columns:1fr; }} }}
</style></head><body><main>
<h1>Ahlam Alqamar: brand sheet</h1>
<p>Logo, slogan, colours, type and web icons for شركة أحلام القمر للتجارة. All logo files are in <code>dist/logo/</code>, as SVG (for print and the web) and PNG at 1x and 2x.</p>
<p><b>The logo is the company name</b>, set in Alexandria and Figtree, with no symbol (owner's decision, 2026-11-05). Where the name cannot fit, in browser tabs and app icons, the monogram <span lang="ar">أق</span> (the initials of أحلام القمر) stands in.</p>

<h2>Logo</h2>
<div class="grid">
  {img("dist/logo/logo-ar-olive.svg", 52, BG)}
  {img("dist/logo/logo-en-olive.svg", 30, BG)}
  {img("dist/logo/logo-stacked-olive.svg", 110, "#fff")}
  {img("dist/logo/logo-ar-white.svg", 52, OLIVE)}
  {img("dist/logo/logo-en-white.svg", 30, INK)}
  {img("dist/logo/logo-stacked-ink.svg", 110, BAND)}
</div>

<h2>Slogan</h2>
<div class="slogan"><p class="ar" lang="ar">{SLOGAN["ar"]}</p><p class="en">{SLOGAN["en"]}</p></div>

<h2>Clear space and minimum size</h2>
<p>Keep a margin of at least the height of the name's letters on every side. Minimum widths: the Arabic wordmark 110 px (28 mm in print), the English 140 px (36 mm). Below that, use the monogram.</p>
<div class="space"><img src="dist/logo/logo-ar-olive.svg" style="height:44px;display:block" alt=""></div>

<h2>Colours</h2>
<div class="sws">{sw_html}</div>
<p style="margin-top:14px">Olive is the brand colour: buttons, dark panels and the icons. Ink is for text and the logo on light backgrounds. Sand and Ivory are the page and card backgrounds.</p>

<h2>Type</h2>
<div class="type">
  <div lang="ar"><p class="big">أحلام القمر</p><p>Alexandria: Arabic headings (500 to 600) and text (300 to 400).</p></div>
  <div><p class="big">Ahlam Alqamar</p><p>Figtree: English headings (500), text (400), and the logo's tracked capitals (700 and 400).</p></div>
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
  <div class="rule"><div class="demo"><img src="dist/logo/logo-ar-olive.svg" style="height:40px;transform:scaleX(1.5)" alt=""></div><b>Stretch or squash</b> the name.</div>
  <div class="rule"><div class="demo"><span lang="ar" style="font:italic 700 34px Georgia, serif">أحلام القمر</span></div><b>Retype it in another font;</b> use the logo files.</div>
  <div class="rule"><div class="demo" style="background:#8a7f6e"><img src="dist/logo/logo-ar-ink.svg" style="height:40px" alt=""></div><b>Place it on a busy or low-contrast background;</b> use the white version on dark or photo backgrounds.</div>
  <div class="rule"><div class="demo"><span style="font-size:56px">☾</span></div><b>Add a crescent, moon or stars:</b> the client's brief forbids them.</div>
</div>
</main></body></html>
"""
    write(Path(__file__).parent / "guide.html", html)
    print("guide: brand/guide.html")


if __name__ == "__main__":
    logos()
    favicons()
    social()
    guide()
