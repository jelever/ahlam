"""Build the Ahlam Alqamar catalogue into _site/.

    python build.py                 build
    python build.py --release       build, and fail if a contact placeholder remains
    python build.py --serve 8741    build, then serve _site under the base path

Every build also runs the checks at the bottom of this file (broken links,
image attributes, words that would make the site look like a shop). A
failed check exits non-zero, so CI never deploys a broken site.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import http.server
import json
import re
import shutil
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
IMAGES = CONTENT / "images"
OUT = ROOT / "_site"
CACHE = ROOT / ".cache" / "img"
LANGS = ("ar", "en")
WIDTHS = (640, 1200, 2000)
FIELD_ORDER = ("brand", "model", "code", "type", "material", "pattern", "size",
               "contents", "filling", "weight", "origin")


class BuildError(Exception):
    pass


def load(name: str):
    with open(CONTENT / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_placeholder(value) -> bool:
    if isinstance(value, dict):
        return any(is_placeholder(v) for v in value.values())
    return isinstance(value, str) and value.startswith("[") and value.endswith("]")


# --------------------------------------------------------------------------
# Content loading and validation
# --------------------------------------------------------------------------

def bilingual(value, where: str):
    """A field is either one string for both languages or {ar, en}."""
    if isinstance(value, dict):
        missing = [lang for lang in LANGS if not value.get(lang)]
        if missing:
            raise BuildError(f"{where}: missing {', '.join(missing)}")
        # In YAML flow style {ar: ..., en: a, b} a comma ends the value and
        # "b" becomes a stray key: quote any text that contains a comma.
        extra = set(value) - set(LANGS)
        if extra:
            raise BuildError(f"{where}: unexpected keys {sorted(map(str, extra))}; "
                             "a comma in an unquoted value? quote the text")
        return value
    if isinstance(value, (str, int, float)):
        return {lang: str(value) for lang in LANGS}
    raise BuildError(f"{where}: expected text or {{ar, en}}")


def load_content():
    site = load("site.yml")
    strings = load("strings.yml")
    catalog = load("catalog.yml")

    for key, value in strings.items():
        bilingual(value, f"strings.yml: {key}")
    for key in ("name", "legal_name"):
        bilingual(site[key], f"site.yml: {key}")
    site["base_path"] = (site.get("base_path") or "").rstrip("/")

    collections = {}
    for c in catalog["collections"]:
        slug = c["slug"]
        if slug in collections:
            raise BuildError(f"duplicate collection {slug}")
        c["name"] = bilingual(c["name"], f"collection {slug}: name")
        c["soon"] = bool(c.get("soon"))
        if not c["soon"]:
            c["summary"] = bilingual(c["summary"], f"collection {slug}: summary")
            if not (IMAGES / c["cover"]).is_file():
                raise BuildError(f"collection {slug}: cover {c['cover']} not found")
        c["products"] = []
        collections[slug] = c

    products = {}
    for p in catalog["products"]:
        slug = p["slug"]
        if slug in products:
            raise BuildError(f"duplicate product {slug}")
        coll = collections.get(p["collection"])
        if coll is None or coll["soon"]:
            raise BuildError(f"product {slug}: unknown or unpublished collection {p['collection']}")
        p["name"] = bilingual(p["name"], f"product {slug}: name")
        fields = p.get("fields") or {}
        unknown = set(fields) - set(FIELD_ORDER)
        if unknown:
            raise BuildError(f"product {slug}: unknown fields {sorted(unknown)}")
        p["fields"] = [(k, bilingual(fields[k], f"product {slug}: {k}")) for k in FIELD_ORDER if k in fields]
        if not p.get("images"):
            raise BuildError(f"product {slug}: no images")
        for im in p["images"]:
            if not (IMAGES / im["src"]).is_file():
                raise BuildError(f"product {slug}: image {im['src']} not found")
            im["label"] = bilingual(im["label"], f"product {slug}: image label") if im.get("label") else None
        p["coll"] = coll
        coll["products"].append(p)
        products[slug] = p

    for c in collections.values():
        if not c["soon"] and not c["products"]:
            raise BuildError(f"collection {c['slug']} has no products; mark it soon: true")
        # The two products the products menu previews on hover: `preview` in
        # catalog.yml, else the collection's first two.
        own = [p["slug"] for p in c["products"]]
        chosen = c.get("preview") or own[:2]
        stray = [s for s in chosen if s not in own]
        if stray:
            raise BuildError(f"collection {c['slug']}: preview {stray} not in this collection")
        c["preview_slugs"] = chosen[:2]

    home = catalog["home"]
    for slug in home["featured"]:
        if slug not in products:
            raise BuildError(f"home.featured: unknown product {slug}")
    if home["hero"] not in products:
        raise BuildError(f"home.hero: unknown product {home['hero']}")

    return site, strings, collections, products, home


# --------------------------------------------------------------------------
# Images: responsive WebP sizes, cached between local builds
# --------------------------------------------------------------------------

class Images:
    def __init__(self):
        self.info: dict[str, dict] = {}

    def get(self, src: str) -> dict:
        if src not in self.info:
            self.info[src] = self._process(src)
        return self.info[src]

    def _process(self, src: str) -> dict:
        path = IMAGES / src
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            w, h = im.size
            cutout = self._is_cutout(im)
            stem = src.rsplit(".", 1)[0]
            widths = sorted({min(x, w) for x in WIDTHS})
            variants = []
            for width in widths:
                rel = f"img/{stem}-{width}.webp"
                cached = CACHE / rel
                if not cached.exists() or cached.stat().st_mtime < path.stat().st_mtime:
                    cached.parent.mkdir(parents=True, exist_ok=True)
                    height = round(h * width / w)
                    im.resize((width, height), Image.LANCZOS).save(cached, "WEBP", quality=84, method=6)
                variants.append((width, rel))
            og_rel = f"img/{stem}-og.jpg"
            og_cached = CACHE / og_rel
            if not og_cached.exists() or og_cached.stat().st_mtime < path.stat().st_mtime:
                og_cached.parent.mkdir(parents=True, exist_ok=True)
                self._og(im).save(og_cached, "JPEG", quality=86)
        for _, rel in variants + [(0, og_rel)]:
            target = OUT / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(CACHE / rel, target)
        return {"w": w, "h": h, "cutout": cutout, "variants": variants, "og": og_rel}

    @staticmethod
    def _is_cutout(im: Image.Image) -> bool:
        """True for product shots on a white background, which are shown
        whole ("contain") on white; photos are cropped to fill instead."""
        # Share of near-white pixels along the border. The client's white
        # cut-outs measure 0.85-1.0 (some are cropped at an edge); real
        # photos measure under 0.5.
        small = im.convert("L")
        small.thumbnail((400, 400))
        w, h = small.size
        border = [small.getpixel((x, y)) for x in range(w) for y in (1, h - 2)]
        border += [small.getpixel((x, y)) for y in range(h) for x in (1, w - 2)]
        return sum(v >= 235 for v in border) / len(border) >= 0.7

    @staticmethod
    def _og(im: Image.Image) -> Image.Image:
        canvas = Image.new("RGB", (1200, 630), "white")
        copy = im.copy()
        copy.thumbnail((1100, 590), Image.LANCZOS)
        canvas.paste(copy, ((1200 - copy.width) // 2, (630 - copy.height) // 2))
        return canvas


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def page_path(lang: str, path: str) -> str:
    """Site-relative path of a page, e.g. ('en', '/products/') -> '/en/products/'."""
    return ("/en" if lang == "en" else "") + path


def build_version() -> str:
    """Short hash of everything that shapes the CSS, JS and quick-view data:
    the static files, the content files and the list of product photos."""
    h = hashlib.sha1()
    for p in sorted((ROOT / "static").rglob("*")) + sorted(CONTENT.glob("*.yml")):
        if p.is_file():
            h.update(p.relative_to(ROOT).as_posix().encode())
            h.update(p.read_bytes())
    for p in sorted(IMAGES.rglob("*")):
        if p.is_file():
            h.update(f"{p.relative_to(IMAGES).as_posix()}:{p.stat().st_size}".encode())
    return h.hexdigest()[:10]


def make_env(site, strings, images: Images):
    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    base = site["base_path"]
    version = build_version()

    def asset(path: str) -> str:
        # Stylesheets and scripts carry a content version: browsers (iOS
        # Safari above all) otherwise keep an old copy for up to GitHub
        # Pages' 10-minute cache and pair it with new pages.
        url = f"{base}/{path.lstrip('/')}"
        if path.endswith((".css", ".js")):
            url += f"?v={version}"
        return url

    def img(src, alt, sizes="100vw", cls="", eager=False):
        info = images.get(src)
        srcset = ", ".join(f"{asset(rel)} {w}w" for w, rel in info["variants"])
        largest_w, largest = info["variants"][-1]
        height = round(info["h"] * largest_w / info["w"])
        classes = " ".join(x for x in (cls, "is-cutout" if info["cutout"] else "is-photo") if x)
        loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
        return Markup(
            f'<img src="{asset(largest)}" srcset="{srcset}" sizes="{html.escape(sizes)}" '
            f'width="{largest_w}" height="{height}" alt="{html.escape(alt)}" class="{classes}" '
            f'{loading} decoding="async">'
        )

    # The logo mark's shapes, used as the <symbol id="i-logo"> of the sprite.
    mark = (ROOT / "templates" / "partials" / "mark.svg").read_text(encoding="utf-8")
    mark_g = Markup(mark[mark.index("<g"):mark.rindex("</g>") + 4])

    whatsapp = site["contact"]["whatsapp"]
    env.globals.update(asset=asset, img=img, site=site, year=dt.date.today().year,
                       is_placeholder=is_placeholder, mark_g=mark_g,
                       whatsapp_number=None if is_placeholder(whatsapp) else whatsapp)
    return env


def contact_items(site, t, lang):
    """(key, label, value, href, icon) for each contact channel."""
    c = site["contact"]
    city = c["city"][lang] if isinstance(c["city"], dict) else c["city"]
    return [
        ("whatsapp", t["contact_whatsapp"], c["whatsapp"],
         f"https://wa.me/{c['whatsapp']}?text={urllib.parse.quote(t['whatsapp_general'])}", "i-whatsapp"),
        ("phone", t["contact_phone"], c["phone"], "tel:" + str(c["phone"]).replace(" ", ""), "i-phone"),
        ("email", t["contact_email"], c["email"], f"mailto:{c['email']}", "i-mail"),
        ("city", t["contact_city"], city, None, "i-pinmap"),
    ]


def quick_view_data(site, strings, products, images: Images, lang: str) -> dict:
    """Everything the quick-view modal shows, keyed by product slug."""
    base = site["base_path"]
    t = {k: v[lang] for k, v in strings.items()}
    number = site["contact"]["whatsapp"]

    def L(value):
        return value[lang] if isinstance(value, dict) else value

    def enquire(p):
        if is_placeholder(number):
            return base + page_path(lang, "/contact/")
        text = t["whatsapp_message"] + L(p["name"]) + " (" + p["slug"] + ")"
        return f"https://wa.me/{number}?text={urllib.parse.quote(text)}"

    data = {}
    for p in products.values():
        pics = []
        for im in p["images"]:
            info = images.get(im["src"])
            pics.append({
                "src": f"{base}/{info['variants'][-1][1]}",
                "srcset": ", ".join(f"{base}/{rel} {w}w" for w, rel in info["variants"]),
                "w": info["variants"][-1][0],
                "h": round(info["h"] * info["variants"][-1][0] / info["w"]),
                "cutout": info["cutout"],
                "label": L(im["label"]) if im["label"] else "",
            })
        data[p["slug"]] = {
            "name": L(p["name"]),
            "collection": L(p["coll"]["name"]),
            "summary": L(p["coll"]["summary"]),
            "fields": [[t["field_" + k], L(v)] for k, v in p["fields"]],
            "images": pics,
            "url": base + page_path(lang, f"/products/{p['slug']}/"),
            "enquire": enquire(p),
            "external": not is_placeholder(number),
        }
    return {
        "lang": lang,
        "products": data,
        "strings": {k: t[k] for k in ("enquire", "view_details", "images_shown", "close", "gallery_open")},
    }


def build(release: bool = False):
    site, strings, collections, products, home = load_content()
    if release:
        pending = [k for k, v in site["contact"].items() if is_placeholder(v)]
        if pending:
            raise BuildError(f"--release: contact placeholders still in site.yml: {', '.join(pending)}")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "static", OUT / "static")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    images = Images()
    env = make_env(site, strings, images)
    published = [c for c in collections.values() if not c["soon"]]
    soon = [c for c in collections.values() if c["soon"]]

    featured = [products[s] for s in home["featured"]]
    mega_featured = [products[s] for s in home.get("mega", home["featured"][:2])]
    pages: list[tuple[str, str, dict]] = [
        ("/", "home.html", {"page": "home", "hero": products[home["hero"]],
                            "hero_image": home.get("hero_image")}),
        ("/collections/", "collections.html", {"page": "collections"}),
        ("/products/", "products.html", {"page": "products"}),
        ("/about/", "about.html", {"page": "about"}),
        ("/contact/", "contact.html", {"page": "contact"}),
    ]
    for c in published:
        pages.append((f"/collections/{c['slug']}/", "collection.html", {"page": "collections", "c": c}))
    for p in products.values():
        pages.append((f"/products/{p['slug']}/", "product.html", {"page": "products", "p": p}))

    sitemap = []
    for lang in LANGS:
        t = {k: v[lang] for k, v in strings.items()}

        def L(value, lang=lang):
            return value[lang] if isinstance(value, dict) else value

        def url(path, lang=lang):
            return site["base_path"] + page_path(lang, path)

        for path, template, ctx in pages:
            context = dict(
                ctx, lang=lang, dir="rtl" if lang == "ar" else "ltr", t=t, L=L, url=url,
                path=path, collections=published, soon=soon, products=products,
                featured=featured, mega_featured=mega_featured,
                contact_items=contact_items(site, t, lang),
                other_lang="en" if lang == "ar" else "ar",
                other_url=site["base_path"] + page_path("en" if lang == "ar" else "ar", path),
                alternates={x: site["base_url"] + site["base_path"] + page_path(x, path) for x in LANGS},
                canonical=site["base_url"] + site["base_path"] + page_path(lang, path),
                og_image=None,
            )
            og_src = (ctx["p"]["images"][0]["src"] if "p" in ctx
                      else ctx["c"]["cover"] if "c" in ctx
                      else products[home["hero"]]["images"][0]["src"])
            context["og_image"] = site["base_url"] + env.globals["asset"](images.get(og_src)["og"])
            out = OUT / page_path(lang, path).lstrip("/") / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(env.get_template(template).render(context), encoding="utf-8")
            sitemap.append(context["canonical"])

    # Quick-view data, one file per language (as the old site's js/data.*.js).
    for lang in LANGS:
        (OUT / "static" / "js" / f"data.{lang}.js").write_text(
            "/* Generated by build.py — do not edit. */\nwindow.AHLAM = "
            + json.dumps(quick_view_data(site, strings, products, images, lang), ensure_ascii=False)
            + ";\n", encoding="utf-8")

    # 404 page, served by GitHub Pages for any missing path. Arabic first.
    t_ar = {k: v["ar"] for k, v in strings.items()}
    t_en = {k: v["en"] for k, v in strings.items()}
    (OUT / "404.html").write_text(
        env.get_template("404.html").render(t_ar=t_ar, t_en=t_en, home_ar=site["base_path"] + "/",
                                            home_en=site["base_path"] + "/en/"),
        encoding="utf-8")

    stamp = dt.date.today().isoformat()
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{html.escape(u)}</loc><lastmod>{stamp}</lastmod></url>\n" for u in sitemap)
        + "</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {site['base_url']}{site['base_path']}/sitemap.xml\n",
        encoding="utf-8")
    return site


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

class PageScan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs: list[str] = []
        self.imgs: list[dict] = []
        self.text: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self._skip += 1
        for key in ("href", "src"):
            if a.get(key):
                self.refs.append(a[key])
        if a.get("srcset"):
            self.refs += [part.strip().split(" ")[0] for part in a["srcset"].split(",")]
        if tag == "img":
            self.imgs.append(a)
        for key in ("alt", "title", "aria-label", "content"):
            if a.get(key):
                self.text.append(a[key])

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)


# The site is a catalogue, not a shop: none of these may appear in any page.
AR = r"ء-ي"
BANNED = [
    re.compile(rf"(?<![{AR}])(ال|و|ب)?(سعر|أسعار|ريال|سلة|السلة|شراء|اشتر|الدفع)(?![{AR}])"),
    re.compile(r"أضف إلى"),
    re.compile(r"\b(price|prices|pricing|cart|basket|checkout|buy|SAR|add to)\b", re.I),
]


# The site speaks mainly to Arabic readers: no em or en dash anywhere a
# visitor reads or hears (use parentheses, a colon or "|" instead).
DASH = re.compile("[–—]")

# Product brands are not shown, at the owner's request (2026-10-08): the site
# presents the company's range, not other companies' names.
BRANDS = re.compile(rf"\b(ROSHINA|ROSHAN|CROWN)\b|(?<![{AR}])(روشينا|روشن|كراون)(?![{AR}])", re.I)


def check(site) -> list[str]:
    base = site["base_path"]
    errors = []
    pages = sorted(OUT.rglob("*.html"))
    for page in pages:
        rel = page.relative_to(OUT).as_posix()
        scan = PageScan()
        scan.feed(page.read_text(encoding="utf-8"))
        for ref in scan.refs:
            if ref.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                continue
            if not ref.startswith(base + "/"):
                errors.append(f"{rel}: link not under base path: {ref}")
                continue
            target = urllib.parse.unquote(ref[len(base):].split("#")[0].split("?")[0])
            path = OUT / target.lstrip("/")
            if target.endswith("/"):
                path = path / "index.html"
            if not path.is_file():
                errors.append(f"{rel}: broken link {ref}")
        for im in scan.imgs:
            if im.get("alt") is None:
                errors.append(f"{rel}: <img> without alt: {im.get('src')}")
            if not (im.get("width") and im.get("height")) and not im.get("src", "").endswith(".svg"):
                errors.append(f"{rel}: <img> without width/height: {im.get('src')}")
        text = " ".join(scan.text)
        for pattern in BANNED:
            for m in pattern.finditer(text):
                errors.append(f"{rel}: shop wording '{m.group(0)}'")
        for m in BRANDS.finditer(text):
            errors.append(f"{rel}: brand name '{m.group(0)}'")
        for m in DASH.finditer(text):
            errors.append(f"{rel}: dash in visible text: '{text[max(0, m.start() - 25):m.end() + 25].strip()}'")
    # Quick-view data: every image and page it points at must exist too.
    for data_file in sorted((OUT / "static" / "js").glob("data.*.js")):
        text = data_file.read_text(encoding="utf-8")
        data = json.loads(text[text.index("{"):text.rindex("}") + 1])
        if DASH.search(json.dumps(data, ensure_ascii=False)):
            errors.append(f"{data_file.name}: dash in quick-view text")
        if BRANDS.search(json.dumps(data, ensure_ascii=False)):
            errors.append(f"{data_file.name}: brand name in quick-view text")
        for slug, p in data["products"].items():
            refs = [p["url"]] + [im["src"] for im in p["images"]]
            refs += [part.strip().split(" ")[0] for im in p["images"] for part in im["srcset"].split(",")]
            if not p["external"]:
                refs.append(p["enquire"])
            for ref in refs:
                target = ref[len(base):]
                path = OUT / target.lstrip("/")
                if target.endswith("/"):
                    path = path / "index.html"
                if not ref.startswith(base + "/") or not path.is_file():
                    errors.append(f"{data_file.name}: {slug}: broken link {ref}")
    for lang_root in ("", "en/"):
        if not (OUT / lang_root / "index.html").is_file():
            errors.append(f"missing home page {lang_root or '(ar)'}")
    ar = {p.relative_to(OUT).as_posix() for p in pages if not p.relative_to(OUT).as_posix().startswith("en/")}
    en = {p.relative_to(OUT).as_posix()[3:] for p in pages if p.relative_to(OUT).as_posix().startswith("en/")}
    for missing in sorted((ar - {"404.html"}) ^ en):
        errors.append(f"page exists in one language only: {missing}")
    return errors


def serve(port: int, base: str):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(OUT), **kw)

        def translate_path(self, path):
            clean = path.split("?")[0].split("#")[0]
            if base and clean.startswith(base + "/"):
                clean = clean[len(base):]
            elif base:
                clean = "/__outside_base_path__"
            return super().translate_path(clean)

        def send_error(self, code, message=None, explain=None):
            if code == 404:
                body = (OUT / "404.html").read_bytes()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            super().send_error(code, message, explain)

    print(f"Serving http://localhost:{port}{base}/  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", action="store_true", help="fail if contact placeholders remain")
    ap.add_argument("--serve", type=int, metavar="PORT", help="serve _site after building")
    args = ap.parse_args()
    try:
        site = build(release=args.release)
    except BuildError as e:
        sys.exit(f"build failed: {e}")
    errors = check(site)
    count = len(list(OUT.rglob("*.html")))
    if errors:
        print("\n".join(errors))
        sys.exit(f"checks failed: {len(errors)} problem(s)")
    print(f"built {count} pages into {OUT.name}/, checks passed")
    if args.serve:
        serve(args.serve, site["base_path"])


if __name__ == "__main__":
    main()
