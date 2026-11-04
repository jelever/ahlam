"""Logo lockups: the mark beside the company name, drawn as outlines.

All measurements are in the mark's units (the mark is 48 tall).
"""
from marks import mark_g
from textpath import Text

NAME = {"ar": "أحلام القمر", "en": "AHLAM ALQAMAR"}
SUB = {"ar": "للتجارة", "en": "TRADING"}


def _texts(lang):
    if lang == "ar":
        return Text("ar", NAME["ar"], 25, wght=600), Text("ar", SUB["ar"], 12.5, wght=400)
    return (Text("en", NAME["en"], 17.5, wght=600, tracking=0.12),
            Text("en", SUB["en"], 8.6, wght=500, tracking=0.42))


def horizontal(key, lang, mark_colour, text_colour, pad=0):
    """Mark and name side by side. Arabic puts the mark on the right."""
    name, sub = _texts(lang)
    gap = 12
    text_w = max(name.width, sub.width)
    w = 48 + gap + text_w
    if lang == "ar":
        # baselines tuned by eye for Alexandria's tall ascenders and descenders
        name_y, sub_y = 25, 41
        tx = w - 48 - gap  # right edge of the text block
        body = (mark_g(key, colour=mark_colour).replace("<g ", f'<g transform="translate({w - 48:.2f} 0)" ', 1)
                + name.at(tx - name.width, name_y, text_colour)
                + sub.at(tx - sub.width, sub_y, text_colour))
    else:
        name_y, sub_y = 25.5, 39.5
        tx = 48 + gap
        body = (mark_g(key, colour=mark_colour)
                + name.at(tx, name_y, text_colour)
                + sub.at(tx, sub_y, text_colour))
    return _svg(body, w, 48, pad)


def stacked(key, mark_colour, text_colour, pad=0):
    """Mark on top, Arabic name, then English name: the bilingual lockup."""
    ar = Text("ar", NAME["ar"], 25, wght=600)
    en = Text("en", NAME["en"] + "  " + SUB["en"], 8.4, wght=600, tracking=0.3)
    w = max(ar.width, en.width, 48)
    mx = (w - 48) / 2
    body = (mark_g(key, colour=mark_colour).replace("<g ", f'<g transform="translate({mx:.2f} 0)" ', 1)
            + ar.at((w - ar.width) / 2, 82, text_colour)
            + en.at((w - en.width) / 2, 103, text_colour))
    return _svg(body, w, 106, pad)


def _svg(body, w, h, pad):
    W, H = w + 2 * pad, h + 2 * pad
    if pad:
        body = f'<g transform="translate({pad} {pad})">{body}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}" '
            f'width="{W:.2f}" height="{H:.2f}">{body}</svg>')
