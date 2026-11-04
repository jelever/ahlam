# Archived identity (live until the 2026-11 redesign)

The official logo set the site used until the redesign on the `redesign`
branch (2026-11-04): the client's identity kit, a house with a crescent cut
out of it, in black and white. The redesign proposes a new mark (see
`brand/README.md`). These files are kept in case the client keeps the
official logo.

Nothing reads this folder. The build reads `static/` and `templates/`, and
GitHub Pages deploys only `_site/`, so these files are never published.

## What is here

- `static-brand/favicon/`: the favicon set and web manifest that were in
  `static/brand/favicon/`
- `static-brand/logo/`: four logo SVGs that were in `static/brand/logo/`.
  The site never linked them.
- `templates/mark.svg`: the mark the site drew inline (`viewBox 48 48 189.2 193.5`)

All of them are byte-for-byte copies of the client's kit in
`assets/ahlam/ahlam-alqamar-web-assets/` (moved with `git mv`).

## Restoring the official logo

1. Move `templates/mark.svg` back to `templates/partials/mark.svg`.
2. In `templates/partials/sprite.html`, `macros.html` (`brand_panel`) and
   `404.html`, set the mark's `viewBox` back to `48 48 189.2 193.5`.
3. Move `static-brand/favicon/` back to `static/brand/favicon/`.
4. Run `build.py`. The checks report any missing icon.
