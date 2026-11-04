"""The logo mark candidates, as SVG geometry on a 48-unit grid.

Every mark is a set of strokes (round caps and joins) drawn in currentColor,
so one definition serves every colour and size. No crescent, moon or star:
the client's brief forbids them.

  paths  strokes at the mark's weight
  fine   strokes at 72% weight (a pen detail, such as the hamza)
  fill   small solid shapes
"""

MARKS = {
    # A: an arch (the doorway of a home) holding a smaller arch, on a ground line.
    "arch": {
        "title": "A. Arch",
        "idea": "A doorway inside a doorway: home and welcome. Simple enough to stay clear at 16 px.",
        "sw": 3.2,
        "paths": [
            "M11 41V22a13 13 0 0 1 26 0v19",
            "M19.5 41v-9a4.5 4.5 0 0 1 9 0v9",
            "M6 41h36",
        ],
    },
    # B: a house holding the letter alef with its hamza: the first letter of أحلام.
    "alef": {
        "title": "B. House and alef",
        "idea": "The first letter of أحلام standing inside a house: the company's name and the home in one sign.",
        "sw": 3.2,
        "paths": [
            "M6.5 22.5 24 8.5l17.5 14",
            "M11.5 21v20h25V21",
            "M24 26.5V41",
        ],
        "fine": ["M27.2 17.4c-1.5-1.3-4.6-1-4.5 1 .1 1.6 2.3 1.8 4.3 1L21.4 22.3"],
    },
    # C: a pointed arch with the triangular vent of Najdi houses above the door.
    "najdi": {
        "title": "C. Najdi arch",
        "idea": "A pointed arch with the triangular vent of Najdi houses over the door: a local home, in one line.",
        "sw": 3.2,
        "paths": [
            "M10.5 41V25.5C10.5 17 16.5 11.5 24 7c7.5 4.5 13.5 10 13.5 18.5V41",
            "M19.5 41v-7a4.5 4.5 0 0 1 9 0v7",
            "M6 41h36",
        ],
        "fill": ["M24 18.2l3 4.6h-6z"],
    },
    # D: the owner's choice (2026-11-04): a redraw of the supplied "Warm Home
    # Collections" emblem: a house with a chimney holding a floor lamp, an
    # armchair and a potted plant.
    "home": {
        "title": "D. Home (full)",
        "idea": "Redraw of the supplied 'Warm Home Collections' emblem, for the logo and lockups (32 px and up).",
        "sw": 2.8,
        "fine_k": .56,
        "paths": [
            # roof with the chimney on the right slope, then the walls
            "M3.5 22.5 24 5.6l7.8 6.4V7h4.6v8.8l8.1 6.7",
            "M7 20v19.5a2.5 2.5 0 0 0 2.5 2.5h29a2.5 2.5 0 0 0 2.5-2.5V20",
        ],
        "fine": [
            # floor lamp
            "M12.6 26h3.8l1.2 4.2h-6.2z",
            "M14.5 30.2V40",
            # armchair: back, arms and seat, legs
            "M21.6 32v-2.2a2.4 2.4 0 0 1 2.4-2.4h2.8a2.4 2.4 0 0 1 2.4 2.4V32",
            "M19.6 37v-3.4a1.6 1.6 0 0 1 3.2 0v1.6h5.2v-1.6a1.6 1.6 0 0 1 3.2 0V37z",
            "M21 37l-.4 2.6M29.8 37l.4 2.6",
            # potted plant
            "M33 35.6h4.2l-.6 4h-3z",
            "M35.1 35.6v-6.8",
            "M35.1 32.8c-2 0-3.1-1.3-3.1-3.1 1.9 0 3.1 1.2 3.1 3.1zM35.1 29.8c0-2.1 1.2-3.5 3-3.5 0 2-1.2 3.5-3 3.5z",
        ],
    },
    # D, small: the same house, with only the armchair, drawn large and heavy,
    # for favicons and app icons where the lamp and plant become noise.
    "home-icon": {
        "title": "D. Home (small sizes)",
        "idea": "Favicon and app-icon version: the house and a large armchair only.",
        "sw": 3.4,
        "paths": [
            "M3.5 22.5 24 5.6l7.8 6.4V7h4.6v8.8l8.1 6.7",
            "M7 20v19.5a2.5 2.5 0 0 0 2.5 2.5h29a2.5 2.5 0 0 0 2.5-2.5V20",
            "M18.2 30.6v-1.8a3.2 3.2 0 0 1 3.2-3.2h5.2a3.2 3.2 0 0 1 3.2 3.2v1.8",
            "M15.6 37.4v-4.6a2.2 2.2 0 0 1 4.4 0v1.6h8v-1.6a2.2 2.2 0 0 1 4.4 0v4.6z",
        ],
    },
}


def mark_g(key, sw=None, colour="currentColor"):
    """The mark as an SVG <g>, for a 0 0 48 48 viewBox."""
    m = MARKS[key]
    sw = sw or m["sw"]
    paths = "".join(f'<path d="{d}"/>' for d in m["paths"])
    paths += "".join(f'<path stroke-width="{sw * m.get("fine_k", .72):.2f}" d="{d}"/>' for d in m.get("fine", []))
    paths += "".join(f'<path fill="{colour}" stroke-width="{sw * .5:.2f}" d="{d}"/>'
                     for d in m.get("fill", []))
    return (f'<g fill="none" stroke="{colour}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{paths}</g>')


def mark_svg(key, size=48, colour="currentColor", sw=None):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
            f'width="{size}" height="{size}">{mark_g(key, sw, colour)}</svg>')
