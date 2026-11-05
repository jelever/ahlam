# CLAUDE.md — Ahlam Alqamar (ahlam)

Loaded automatically for sessions in this folder, on top of the portfolio
rules in `../../CLAUDE.md`.

---

## What this is

A bilingual product catalogue for شركة أحلام القمر للتجارة (Ahlam Alqamar
Trading Company), a wholesale supplier of household and commercial goods. It
shows collections and products to businesses and wholesale customers and
sends them to contact the company. **It is not a shop.** The client's brief
forbids prices, cart, payment, invented reviews, client logos, statistics,
branches and superlative claims, and forbids the crescent as a design
element. One exception, at the owner's request (2026-11-05): the brand slogan
"مصدرك الأول في جملة المفروشات" (Your first source for wholesale
furnishings). Add no other superlatives. Since the 2026-11-04 redesign, the design follows
`../../references/home-collections/ahlam` (a furniture-store layout): its
tokens, page structures and motion, with the store features removed. Before
it, the site was the company's previous site,
`../../references/home-collections/homely`; that version is kept on the
branch `homely-design`.

- Languages: Arabic default (RTL) at `/`, English at `/en/`
- Stack: static HTML from `build.py` (Jinja2, Pillow, PyYAML); vanilla CSS/JS
- Hosting: GitHub Pages (deployed by `.github/workflows/pages.yml` on every
  push to `main`), no Railway project
- Domain: **intended https://ahlamalqamar.com, but GitHub still serves
  https://ahlam.elgaily.com.** `base_url` has named ahlamalqamar.com since
  e094096 (2026-10-20), so canonical, sitemap and share images point there.
  But Settings → Pages still has the custom domain `ahlam.elgaily.com`
  (checked 2026-11-04 with `gh api repos/jelever/ahlam/pages`), so
  ahlamalqamar.com gets no site and no certificate. The owner `jelever` must
  set the custom domain to `ahlamalqamar.com`. DNS is at GoDaddy
  (`ns25/26.domaincontrol.com`): the apex has A records to GitHub Pages
  (correct through 8.8.8.8), and `www` is a CNAME. The MX and TXT records are
  the company's Google email: never touch them. The custom domain is set in
  Settings → Pages, which only the owner `jelever` can change.
- GitHub: `jelever/ahlam` (public; free Pages needs it). `MBajily` is a
  collaborator with push access but not admin: repository settings (Pages,
  Dependabot alerts, branch protection) need the owner, `jelever`

---

## Status — 2026-11-04

**Redesign: live since 2026-11-04** (branch `redesign` merged into `main`
as 5729915 and deployed; the previous design is on `homely-design`)

- New design after `references/home-collections/ahlam`, in Alexandria and
  Figtree (the owner kept the old fonts). All 127 pages, same URLs, same
  content and build checks. Verified: `build.py` passes; Chrome at 1366 px
  and at 390 px through iframes (the window would not resize), Arabic and
  English; no horizontal overflow; the products filter (`?c=`, the back
  button); quick view with the lightbox above it (Escape closes only the
  top layer); and a bilingual 404. Live smoke test on ahlam.elgaily.com:
  pages, favicons, manifest and share images return 200, and a missing path
  returns 404. **Not yet checked on the owner's iPhone.**
- Logo (owner, 2026-11-05): the company name as text, with no symbol, and
  the monogram "أق" for the favicon and app icons. It replaces the house
  emblem of 2026-11-04. The old crescent identity is in
  `archive/brand-2026-10/`. Tooling and the full set are in `brand/`
  (`brand/README.md`, brand sheet `brand/guide.html`).
- Owner's changes of 2026-11-05: the slogan "مصدرك الأول في جملة المفروشات"
  as the home hero title, a hero that states what the company supplies and
  that the site does not sell, "الشركات" for "الشركاء", "كتالوج" for "معرض
  رقمي", "رقم الجوال" for "الهاتف", and a shorter footer (name and slogan,
  pages, contact).
- Web assets: favicon (SVG, ICO), apple-touch and Android icons, a bilingual
  manifest, a default share image, product and collection share images on
  the brand band with a logo strip, `og:image` size and alt, Twitter tags,
  and Organization JSON-LD. The new checks were each shown to catch a
  planted fault.
- To confirm with the client: the feature-strip and "how it works" wording
  (`strip_*`, `step_*` in `strings.yml`), and the new logo.

**Done and verified (2026-10-01)**

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

1. **Custom domain (owner `jelever`):** Settings → Pages → custom domain
   `ahlamalqamar.com`, then enforce HTTPS once the certificate is issued.
   Until then the site answers only on ahlam.elgaily.com, and link previews
   point at an address that does not serve.
2. Client approval of the feature-strip and "how it works" wording
   (`strip_*`, `step_*` in `strings.yml`).
3. Check the redesign on the owner's iPhone.
4. Real contact details from the client (`content/site.yml`). The live site
   shows "سيُضاف قريبًا" until then; `build.py --release` blocks them.
5. Photos for the three coming-soon collections: event chairs, tablecloths,
   ready-packed bedding.
6. Client to confirm: the camp-bag dimension photos (filed in each other's
   folders again in the 2026-10-20 set, reassigned by material); the
   "صناعة وطنية" label, taken from the folder names; the meaning of "صفت"
   in the heavy-mesh bed's folder.
7. Brand logos in photos: since 2026-10-20 the site uses the client's new
   set as supplied, with CROWN on the three iron beds and ROSHINA, ROSHAN
   and CROWN on comforters and pillows (owner's choice). The logo-free
   versions are in `archive/product-images-2026-10-20/`.
8. Real company photos for the about and contact pages (warehouse, stock in
   quantity, loading or delivery, office or showroom front). They replace
   the brand panels. Never stock photos: they would present someone else's
   premises as the company's.
9. Owner's repository settings: protect `main`, and turn on Dependabot
   alerts and security updates. An uptime monitor.

---

## Run it

```bash
.venv/Scripts/python build.py --serve 8741
```

Serve on your own port, not 8080 (other sessions use it). The server maps
`base_path` (now `""`) to `_site/` the way GitHub Pages does.

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
- Share images are cached by photo (`.cache/img/…-share.jpg`). After changing
  `brand/dist/og-strip.png`, delete `.cache/img` so they are redrawn.
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

- **Design = the reference `references/home-collections/ahlam`, by the
  owner's instruction (2026-11-04, branch `redesign`).** `static/css/site.css`
  was derived once from its `css/styles.css` (store-only rules dropped, its
  serifs replaced by the brand's Alexandria and Figtree at weight 500) and is
  edited directly since. `static/js/site.js` combines its `main.js` and
  `search.js` (no cart, wizard, newsletter or reviews code) with this site's
  quick view, lightbox and gallery. Templates follow its structures. When in
  doubt about a style or motion, match the reference. The Homely design
  before it is in git history (`main` up to e094096).
- **Departures from the reference, on purpose:** the home hero photo starts
  below the header (the nav cannot be read over a darker photo); all ten
  collections show in a 5×2 grid on desktop (the reference shows four rooms);
  the slider fades its photo with a gradient overlay, not `mask-image` (iOS);
  the eyebrow bullet is a dot, not the reference's four-point sparkle (it
  reads as a star).
- **Store structures, repurposed:** "trusted by" avatars → the range as
  collection chips; rooms → collection cards; crafted card price and swatches
  → the product's details list and view and enquire buttons; reviews → the
  featured products grid; "why" → "how it works" (four steps); newsletter →
  partners panel (enquire button in place of the e-mail form); add to cart →
  quick view and enquire. Quick view: `build.py` writes
  `static/js/data.<lang>.js` (`window.AHLAM`), which `site.js` renders the
  modal and the header search from. The build checks every path in those
  files. No invented reviews, stats, journal or partner logos.
- **Products page filters by collection in place** (chips; the choice is kept
  in `?c=`, and the back button works). Without JavaScript the chips are
  links and every product shows. Collection pages link to `/products/?c=…`.
- **Gallery preview (lightbox):** the product page viewer and quick view open
  the product's photos full size and whole (expand button or a click on the
  photo), with arrows (reading-direction aware), swipe and a counter. It
  stacks above quick view; Escape closes the top modal only. Page frames
  keep the old site's crop on purpose; the preview is where the whole photo
  is seen. An edge-to-edge treatment for photos cut by the photographer was
  tried and rejected by the owner (2026-10-01).
- **The about header and the contact card use a brand panel**, not a
  product photo: the company name and slogan on olive (`macros.html`
  `brand_panel`). It is a stopgap until the client sends real company photos.
- **Product cut-outs** (photos with a mostly light border: designed cards and
  studio shots) are shown whole, and the rest of their frame takes the
  photo's own background tone, sampled by `build.py` as `--edge`. Home picks
  the hero card and slider collections from covers that are real photos (the
  `is_cutout` test).
- **One image per product in every listing.** Other colours and real-life
  photos appear only as thumbnails on the product page. This is the client's
  core requirement.
- **Home hero is the nano 4×3 rug's room scene** (`home.hero` in
  `catalog.yml`). The products hero is `ambience/flint-room.jpg`.
- **Product photos are the client's set of 2026-10-20, used as supplied**
  (`products images - new (2)`). That includes the CROWN, ROSHINA and ROSHAN
  logos printed on beds, comforters and pillows: the owner's choice. Names,
  details and URLs stay brand-free, and the build's BRANDS check enforces
  that. Most products have a single real-background photo. The previous
  set is kept in `archive/product-images-2026-10-20/`, with a README on how
  to restore it: the white cut-outs, the logo-free bed shots, the RT-M101
  colour cut-outs. Nothing reads that folder.
- **The logo is the company name, with no symbol (owner, 2026-11-05).** The
  header, footer and 404 show the name as text: "أحلام القمر للتجارة" /
  "AHLAM ALQAMAR TRADING", the name heavier and "للتجارة" lighter. The house
  emblem drawn on 2026-11-04 is dropped. Where the name cannot fit (favicon,
  app icons) the monogram "أق" stands in. The logo files, icons and share
  images are generated by `brand/build_brand.py` (see `brand/README.md`).
  The client's official crescent set is in `archive/brand-2026-10/`.
- **Audience wording (owner, 2026-11-05):** "الشركات وعملاء الجملة" (businesses
  and wholesale customers), not "الشركاء"; "كتالوج", not "معرض رقمي"; "رقم
  الجوال" (mobile number), not "الهاتف". The home hero states what the
  company supplies and that the site displays products and does not sell
  (`hero_lead`, `hero_note`).
- **Merged or renamed products keep their old address working.** List the old
  slug under `redirects:` at the end of `catalog.yml`. The build writes a
  noindex page there that forwards to the new product, keeping the query and
  hash, and leaves it out of the sitemap. GitHub Pages cannot redirect on the
  server. The build fails if an old slug is still a product. First use
  (2026-11-04): `pillow-hotel-50x70` was merged into `pillow-hotel` (the
  lifestyle photo and its box were the same ROSHAN hotel pillow).
- **No contact form.** A static host cannot send mail; WhatsApp, phone and
  email links instead.

## Where things are explained

| | |
|---|---|
| `README.md` | setup, editing content, deploy |
| `content/catalog.yml` | catalogue rules in its header comment |
| `brand/README.md` | the logo, icons and share images, and how to rebuild them |
| `archive/brand-2026-10/README.md` | the previous official logo, and how to restore it |
