# Brand: logo, icons and share images

The logo is the company name, set as text, with no symbol (the owner's
decision, 2026-11-05): "أحلام القمر للتجارة" in Alexandria and "AHLAM ALQAMAR
TRADING" in tracked Figtree capitals, the name heavier and "للتجارة / TRADING"
lighter. Where the name cannot fit (favicons, app icons), the monogram "أق",
the initials of أحلام القمر, stands in. The slogan is "مصدرك الأول في جملة
المفروشات" (Your first source for wholesale furnishings).

History: the client's official logo (a house with a crescent) is kept in
`archive/brand-2026-10/`. The house emblem drawn on 2026-11-04 (`marks.py`,
the candidates sheet `concepts.py`) was dropped on 2026-11-05. Nothing in
the build reads `marks.py` any more.

Open `guide.html` (the brand sheet) for the logo variants, colours, type,
clear space and the rules.

## Files

| Path | What it is | Deployed |
|---|---|---|
| `marks.py` | the dropped house emblems (history; used only by `concepts.py`) | no |
| `lockup.py`, `textpath.py` | the wordmarks and the monogram; the words outlined from the fonts with HarfBuzz | no |
| `build_brand.py` | writes everything below | no |
| `fonts/` | Alexandria and Figtree (SIL Open Font License, from google/fonts) | no |
| `dist/logo/` | the logo set for the client: Arabic, English and stacked wordmarks and the monogram, in olive, ink and white, as SVG and PNG (1x, 2x) | no |
| `dist/og-strip.png` | the olive logo strip `build.py` puts under every product and collection share image | no |
| `guide.html` | the brand sheet | no |
| `../static/brand/favicon/` | favicon (.svg, .ico 16/32/48), apple-touch icon, Android icons (192, 512, maskable), `site.webmanifest` | yes |
| `../static/brand/social/og-default.jpg` | the share image for pages without a photo of their own | yes |

## Rebuild

```bash
.venv/Scripts/python -m pip install -r brand/requirements.txt
.venv/Scripts/python brand/build_brand.py
.venv/Scripts/python build.py
```

The site build and CI never run `build_brand.py`; its outputs are committed.
Change the wordmark in `lockup.py` and run both commands. `build.py` caches share
images by photo, so delete `.cache/img` after changing `dist/og-strip.png`.

`concepts.py` writes `concepts.html`, a comparison sheet of marks from
`marks.py` (for example `concepts.py home home-icon`). The sheet is not
committed.

## Colours

| Name | Hex | Use |
|---|---|---|
| Olive | `#3d4633` | the logo, buttons, dark panels |
| Olive 2 | `#4b5641` | the slider and call-to-action bands |
| Ink | `#2a2a24` | text |
| Sand | `#f3eee8` | bands, share image background |
| Ivory | `#faf7f3` | page background |
| Stone | `#e4ddd3` | hairlines |

These are the tokens at the top of `static/css/site.css`, taken from the
reference design.
