# Brand: logo, icons and share images

The identity proposed on 2026-11-04 with the redesign. It replaces the
official crescent-and-house logo, which is kept in `archive/brand-2026-10/`.
**It is a proposal until the client approves it.**

The mark is a line-drawn house with a chimney, holding a floor lamp, an
armchair and a potted plant. It is a clean vector redraw of the "Warm Home
Collections" emblem the owner chose. For 16 to 32 px (favicons and app icons)
there is a small version with only the house and the armchair, because the
lamp and plant cannot be read at that size. No crescent, moon or star
appears anywhere, as the client's brief asks.

Open `guide.html` (the brand sheet) for the logo variants, colours, type,
clear space and the rules.

## Files

| Path | What it is | Deployed |
|---|---|---|
| `marks.py` | the mark as SVG geometry on a 48-unit grid (`home`, `home-icon`); A to C are the candidates set aside | no |
| `lockup.py`, `textpath.py` | the mark beside the name; the words outlined from the fonts with HarfBuzz | no |
| `build_brand.py` | writes everything below | no |
| `fonts/` | Alexandria and Figtree (SIL Open Font License, from google/fonts) | no |
| `dist/logo/` | the logo set for the client: mark, small mark, Arabic, English and stacked lockups, in olive, ink and white, as SVG and PNG (1x, 2x) | no |
| `dist/og-strip.png` | the olive logo strip `build.py` puts under every product and collection share image | no |
| `guide.html` | the brand sheet | no |
| `../static/brand/favicon/` | favicon (.svg, .ico 16/32/48), apple-touch icon, Android icons (192, 512, maskable), `site.webmanifest` | yes |
| `../static/brand/social/og-default.jpg` | the share image for pages without a photo of their own | yes |
| `../templates/partials/mark.svg` | the mark the site draws inline (header, footer, brand panels, 404) | yes, inlined |

## Rebuild

```bash
.venv/Scripts/python -m pip install -r brand/requirements.txt
.venv/Scripts/python brand/build_brand.py
.venv/Scripts/python build.py
```

The site build and CI never run `build_brand.py`; its outputs are committed.
Change the mark in `marks.py` and run both commands. `build.py` caches share
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
