# CLAUDE.md — Ahlam Alqamar (ahlam)

Loaded automatically for sessions in this folder, on top of the portfolio
rules in `../../CLAUDE.md`.

---

## What this is

A bilingual product catalogue for شركة أحلام القمر للتجارة (Ahlam Alqamar
Trading Company), a wholesale supplier of household and commercial goods. It
shows collections and products to wholesale customers and partners and sends
them to contact the company. **It is not a shop.** The client's brief
forbids prices, cart, payment, invented reviews, client logos, statistics,
branches and superlative claims, and forbids the crescent as a design
element. The design **is** the company's previous site,
`../../references/home-collections/homely` (a furniture store), carried over
unchanged: same stylesheet, scripts, page structures and animations, with
the store features removed and the new identity, products and content in.

- Languages: Arabic default (RTL) at `/`, English at `/en/`
- Stack: static HTML from `build.py` (Jinja2, Pillow, PyYAML); vanilla CSS/JS
- Hosting: GitHub Pages (deployed by `.github/workflows/pages.yml` on every
  push to `main`), no Railway project
- Live at https://jelever.github.io/ahlam/; no custom domain yet
- GitHub: `jelever/ahlam` (public; free Pages needs it). `MBajily` is a
  collaborator with push access but not admin: repository settings (Pages,
  Dependabot alerts, branch protection) need the owner, `jelever`

---

## Status — 2026-10-01

**Done and verified**

- Site built: home, collections, collection ×5, products, product ×9,
  about, contact, 404, in both languages (39 pages). `build.py` checks pass;
  each check was shown to catch a planted fault.
- Checked in Chrome at desktop, 768px and 390px, Arabic and English: no
  horizontal overflow, drawer menu with focus and Escape, gallery
  thumbnails, quick view (thumbnails, Escape, phone layout), language
  switch keeps the page, no console errors.
- **Live since 2026-10-01** at https://jelever.github.io/ahlam/. The CI run
  for 45c0323 built, checked and deployed. Smoke-tested live:
  - `/`, `/en/`, a product page, `data.ar.js` and a product photo return 200
  - `/products/` has all 9 quick-view buttons
  - a missing path returns 404 with the bilingual page

**Open work, in priority order**

1. Real contact details from the client (`content/site.yml`). The live site
   shows "سيُضاف قريبًا" until then; `build.py --release` blocks them.
2. Photos for the six coming-soon collections: chairs, event chairs,
   blankets, pillows, tablecloths, ready-packed bedding.
3. Client to confirm: the camp-bag dimension photos (filed in each other's
   folders, reassigned by material); the "صناعة وطنية" label, taken from
   the folder names; the meaning of "صفت" in the heavy-mesh bed's folder.
4. Clean photos without the CROWN logo (2 photos left: the heavy-mesh bed,
   folded and unfolded). The user chose to use them as they are for now.
   Replaced on 2026-10-01 with the client's logo-free shots: the bunk bed
   (`دورين 2.png`, 1536×1024) and the single bed
   (`crown_bed_product_1200x1200.png`, 1200×1200, a little soft at full
   size).
5. Real company photos for the about and contact pages (warehouse, stock in
   quantity, loading or delivery, office or showroom front). They replace
   the brand panels. Never stock photos: they would present someone else's
   premises as the company's.
6. Owner's repository settings: protect `main`, and turn on Dependabot
   alerts and security updates. An uptime monitor, and a custom domain if
   the client wants one (see README).

---

## Run it

```bash
.venv/Scripts/python build.py --serve 8741
```

Serve on your own port, not 8080 (other sessions use it). The server maps
`/ahlam/` to `_site/` the way GitHub Pages does.

## Commands

```bash
.venv/Scripts/python build.py            # build + checks (what CI runs)
.venv/Scripts/python build.py --release  # also fails on contact placeholders
```

**Before saying something is finished**, run `python build.py`; it must end
with "checks passed".

---

## Conventions that will bite

- Every link and asset goes through `url()` / `asset()` so it carries
  `base_path`. A hard-coded `/…` path breaks on GitHub Pages, and the build
  check reports it.
- Templates use `StrictUndefined`: optional data (such as an image `label`)
  must be normalised in `load_content()`.
- **iOS Safari is the owner's test phone.** Safari does not stretch a grid row
  to a height that comes from `aspect-ratio`, so grid-centred content sits at
  the top edge (this broke the brand panels). Centre with absolute positioning
  and give SVGs a `viewBox` and explicit width and height. Avoid CSS masks and
  `z-index: -1` pseudo-elements inside clipped, animated boxes. Chrome will
  not show these bugs.
- CSS and JS URLs carry `?v=<hash>` (`build_version()` in `build.py`) so
  phones never pair new pages with a cached old stylesheet. Keep loading them
  through `asset()`.
- Image fit is automatic: photos whose border is at least 70% near-white are
  shown whole on white (`is-cutout`); others fill the frame (`is-photo`).
- The source photo folders in `assets/ahlam/products images` contain an
  invisible U+200F in one folder name. The repo copies use ASCII names;
  never read from the Arabic paths in code.
- **No em or en dash (— –) in anything a visitor reads or hears**, at the
  owner's request: the audience is mainly Arabic. Use parentheses for a
  variant ("شنطة عزبة (صيني)"), " | " in page titles, and a colon or full
  stop in sentences. The build fails on a dash in page text, titles, alt
  text, labels or the quick-view data. Code comments are exempt.
- Shop wording is a build failure. Words such as الشراكة and المراسلة are
  fine; the check matches whole words.

## Site-specific decisions

- **Design = the old Homely site, by the user's instruction (2026-10-01).**
  An earlier beige redesign was rejected. `static/css/site.css` was generated
  once from Homely's `css/styles.css` (store-only rules dropped, Manrope
  replaced by the brand's Figtree) and is edited directly since. Ahlam
  additions sit at the end of the file. `static/js/site.js` is Homely's
  `main.js` without cart, modal and form code. Templates mirror Homely's
  (`base`, `macros`, pages). When in doubt about a style or motion, match the
  reference.
- **Store structures, repurposed:** rating card → company card; "trusted by"
  logos → collection chips (marquee on phones); set-row price card →
  "details available" card; features card → enquiry card; newsletter panel →
  partners panel; add to cart → enquire. Quick view is kept (Homely's
  modal): `build.py` writes `static/js/data.<lang>.js` (`window.AHLAM`) and
  `site.js` renders the modal from it, with photo thumbnails, details list,
  enquire button and a link to the full page. The build checks every path in
  those files. No invented reviews, stats, journal or partner logos.
- **Gallery preview (lightbox):** the product page viewer and quick view open
  the product's photos full size and whole (expand button or a click on the
  photo), with arrows (reading-direction aware), swipe and a counter. It
  stacks above quick view; Escape closes the top modal only. Page frames
  keep the old site's crop on purpose; the preview is where the whole photo
  is seen. An edge-to-edge treatment for photos cut by the photographer was
  tried and rejected by the owner (2026-10-01).
- **About and contact headers use brand panels, not product photos**
  (`page_hero(..., brand='dark'|'light')`). The about header repeated the home
  hero, and the contact header's table was unrelated. The panel is the logo
  mark and the kit's `corner-arcs` (copied to `static/brand/decor/`, drawn
  through a CSS mask as the kit's own CSS does) over a soft radial light.
  The kit's dot texture was tried and dropped at the owner's choice: the old
  site uses no textures.
  The kit's `pattern-houses` and `ornament-roof` contain the crescent and
  `rings` reads as a moon halo, so they are not used. This is a stopgap until
  the client sends real company photos.
- **Product cut-outs** use `mix-blend-mode: multiply` so their white
  background melts into the grey panels.
- **One image per product in every listing.** Other colours and real-life
  photos appear only as thumbnails on the product page. This is the client's
  core requirement.
- **Hero is the bunk bed, not RT-M101.** The RT-M101 photos are cropped at
  the right and bottom edges.
- **The official logo mark is kept although it contains a crescent.** It is
  the identity. None of the kit's crescent or moon decorations are used.
- **No contact form.** A static host cannot send mail; WhatsApp, phone and
  email links instead.

## Where things are explained

| | |
|---|---|
| `README.md` | setup, editing content, deploy |
| `content/catalog.yml` | catalogue rules in its header comment |
