"""Write concepts.html: the three mark candidates side by side, for choosing.

    .venv/Scripts/python brand/concepts.py
"""
import re
import sys
from pathlib import Path

from lockup import horizontal, stacked
from marks import MARKS, mark_svg

OLIVE, INK, BG, BAND, WHITE = "#3d4633", "#2a2a24", "#faf7f3", "#f3eee8", "#fffdfb"
OUT = Path(__file__).parent / "concepts.html"


def sized(svg, height):
    """Scale an SVG to a display height, keeping its aspect ratio."""
    w, h = (float(v) for v in re.search(r'width="([\d.]+)" height="([\d.]+)"', svg).groups())
    return re.sub(r'width="[\d.]+" height="[\d.]+"',
                  f'width="{w * height / h:.1f}" height="{height}"', svg, count=1)


def favicon(key):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="{{s}}" height="{{s}}">'
            f'<rect width="48" height="48" rx="11" fill="{OLIVE}"/>'
            f'<g transform="translate(5 4) scale(.79)">{mark_svg(key, 48, BAND, sw=MARKS[key]["sw"] * 1.25)}</g></svg>')


cards = []
KEYS = sys.argv[1:] or list(MARKS)
for key in KEYS:
    m = MARKS[key]
    fav = favicon("home-icon" if key.startswith("home") else key)
    cards.append(f"""
<section class="card">
  <header><h2>{m['title']}</h2><p>{m['idea']}</p></header>
  <div class="row big">
    <div class="tile light">{mark_svg(key, 180, OLIVE)}</div>
    <div class="tile dark">{mark_svg(key, 180, BAND)}</div>
  </div>
  <div class="row sizes">
    <span>Favicon</span>
    {fav.replace('{s}', '16')}{fav.replace('{s}', '32')}{fav.replace('{s}', '64')}
    <span>Mark</span>
    {mark_svg(key, 16, INK)}{mark_svg(key, 24, INK)}{mark_svg(key, 32, INK)}
  </div>
  <div class="lock light" dir="rtl">{sized(horizontal(key, 'ar', OLIVE, INK), 56)}</div>
  <div class="lock light">{sized(horizontal(key, 'en', OLIVE, INK), 56)}</div>
  <div class="lock dark">{sized(horizontal(key, 'ar', BAND, WHITE), 44)}&nbsp;&nbsp;&nbsp;{sized(horizontal(key, 'en', BAND, WHITE), 44)}</div>
  <div class="lock light">{sized(stacked(key, OLIVE, INK), 150)}</div>
  <div class="lock light header">
    <span class="fake-nav">header, 40 px</span>{sized(horizontal(key, 'ar', OLIVE, INK), 40)}
  </div>
</section>""")

OUT.write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Logo concepts</title>
<style>
  body {{ margin:0; background:{BG}; color:{INK}; font:15px/1.6 system-ui, sans-serif; }}
  h1 {{ font-weight:500; margin:32px 24px 4px; }}  .lead {{ margin:0 24px 24px; color:#7d776d; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(420px, 1fr)); gap:24px; padding:0 24px 48px; }}
  .card {{ background:#fff; border:1px solid #e4ddd3; border-radius:18px; padding:20px; display:grid; gap:14px; }}
  .card h2 {{ margin:0; font-size:20px; font-weight:600; }}  .card p {{ margin:4px 0 0; color:#7d776d; }}
  .row {{ display:flex; gap:12px; align-items:center; flex-wrap:wrap; }}
  .tile {{ flex:1; display:grid; place-items:center; padding:22px; border-radius:14px; }}
  .light {{ background:{BAND}; }}  .dark {{ background:{OLIVE}; }}
  .sizes span {{ font-size:12px; color:#7d776d; margin-inline-start:8px; }}
  .lock {{ padding:22px; border-radius:14px; display:flex; justify-content:center; align-items:center; }}
  .header {{ justify-content:space-between; background:{BG}; border:1px solid #e4ddd3; }}
  .fake-nav {{ font-size:12px; color:#7d776d; }}
</style></head><body>
<h1>Ahlam Alqamar: logo concepts</h1>
<p class="lead">Three marks, no crescent. Each shown large, as a favicon (16, 32, 64 px), as a small mark, and in the Arabic, English and bilingual lockups. Text is outlined from Alexandria and Figtree.</p>
<div class="grid">{''.join(cards)}</div>
</body></html>
""", encoding="utf-8")
print("wrote", OUT)
