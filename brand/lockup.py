"""The logo: the company name as a wordmark, with no symbol (owner's
decision, 2026-11-05), and the monogram used where the name cannot fit
(favicons, app icons).

Words are outlined from the fonts, so the files need no fonts installed.
"""
from textpath import Text

NAME = {"ar": "أحلام القمر", "en": "AHLAM ALQAMAR"}
SUB = {"ar": "للتجارة", "en": "TRADING"}
SLOGAN = {"ar": "مصدرك الأول في جملة المفروشات", "en": "YOUR FIRST SOURCE FOR WHOLESALE FURNISHINGS"}
MONOGRAM = "أق"   # the initials of أحلام القمر


def _parts(lang, size):
    """The name and its suffix, set on one line."""
    if lang == "ar":
        return Text("ar", NAME["ar"], size, wght=600), Text("ar", SUB["ar"], size, wght=300)
    return (Text("en", NAME["en"], size * .62, wght=700, tracking=.14),
            Text("en", SUB["en"], size * .62, wght=400, tracking=.14))


def wordmark_body(lang, colour, size=40, x0=0, baseline=None):
    """The one-line wordmark as SVG paths; returns (body, width, height)."""
    name, sub = _parts(lang, size)
    gap = size * (.24 if lang == "ar" else .42)
    w = name.width + gap + sub.width
    h = size * (1.25 if lang == "ar" else .75)
    y = baseline if baseline is not None else (size * .82 if lang == "ar" else size * .6)
    if lang == "ar":   # right to left: the name first, at the right
        body = name.at(x0 + w - name.width, y, colour) + sub.at(x0, y, colour)
    else:
        body = name.at(x0, y, colour) + sub.at(x0 + name.width + gap, y, colour)
    return body, w, h


def wordmark(lang, colour, pad=0):
    body, w, h = wordmark_body(lang, colour)
    return _svg(body, w, h, pad)


def stacked(colour, pad=0):
    """Bilingual: the Arabic name over the English, centred."""
    ar, aw, _ = wordmark_body("ar", colour, 40)
    en_name, en_sub = _parts("en", 26)
    gap = 26 * .42
    ew = en_name.width + gap + en_sub.width
    w = max(aw, ew)
    ar, aw, _ = wordmark_body("ar", colour, 40, x0=(w - aw) / 2)
    ex = (w - ew) / 2
    en = en_name.at(ex, 82, colour) + en_sub.at(ex + en_name.width + gap, 82, colour)
    return _svg(ar + en, w, 90, pad)


def monogram_path(colour, size=26):
    """The monogram's paths centred in a 48x48 box."""
    t = Text("ar", MONOGRAM, size, wght=600)
    return t.at((48 - t.width) / 2, 33, colour)


def _svg(body, w, h, pad):
    W, H = w + 2 * pad, h + 2 * pad
    if pad:
        body = f'<g transform="translate({pad} {pad})">{body}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}" '
            f'width="{W:.2f}" height="{H:.2f}">{body}</svg>')
