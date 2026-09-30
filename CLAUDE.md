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
- Hosting: GitHub Pages, no Railway project
- Domain: none yet; https://jelever.github.io/ahlam/
- GitHub: `jelever/ahlam` (public; free Pages needs it). The account
  `MBajily` has only pull access; pushing needs a collaborator invite

---

## Status — 2026-10-01

**Done and verified**

- Site built: home, collections, collection ×5, products, product ×9,
  about, contact, 404, in both languages (39 pages). `build.py` checks pass;
  each check was shown to catch a planted fault.
- Checked in Chrome at desktop, 768px and 390px, Arabic and English: no
  horizontal overflow, drawer menu with focus and Escape, gallery
  thumbnails, language switch keeps the page, no console errors.

**Open work, in priority order**

1. Push access to `jelever/ahlam`, set Pages source to GitHub Actions, first
   deploy, then smoke-test the live URL.
2. Real contact details from the client (`content/site.yml`).
3. Photos for the six coming-soon collections: chairs, event chairs,
   blankets, pillows, tablecloths, ready-packed bedding.
4. Client to confirm: the camp-bag dimension photos (filed in each other's
   folders, reassigned by material); the "صناعة وطنية" label, taken from
   the folder names; the meaning of "صفت" in the heavy-mesh bed's folder.
5. Clean photos without the CROWN logo (4 bed photos). The user chose to use
   them as they are for now.

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
- Image fit is automatic: photos whose border is at least 70% near-white are
  shown whole on white (`is-cutout`); others fill the frame (`is-photo`).
- The source photo folders in `assets/ahlam/products images` contain an
  invisible U+200F in one folder name. The repo copies use ASCII names;
  never read from the Arabic paths in code.
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
