"""Shape text with HarfBuzz and return it as SVG outlines.

The logo files must not depend on installed fonts, so every word in them is
drawn as a path. Arabic needs real shaping (joining forms, lam-alef), which is
why this goes through HarfBuzz rather than reading glyphs one by one.
"""
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = Path(__file__).parent / "fonts"
FILES = {
    "ar": FONTS / "Alexandria-VF.ttf",
    "en": FONTS / "Figtree-VF.ttf",
}


class Text:
    """A run of text set in one font, weight and size, as one SVG path."""

    def __init__(self, lang, text, size, wght=500, tracking=0.0):
        path = FILES[lang]
        face = hb.Face(hb.Blob.from_file_path(str(path)))
        font = hb.Font(face)
        font.set_variations({"wght": wght})
        upem = face.upem
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, {"kern": True, "liga": True})

        scale = size / upem
        track = tracking * upem  # tracking is in em
        pen = SVGPathPen(None, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        x = 0.0
        infos, positions = buf.glyph_infos, buf.glyph_positions
        # Arabic must never be tracked: it breaks the joins.
        if lang == "ar":
            track = 0.0
        for i, (info, pos) in enumerate(zip(infos, positions)):
            gx = x + pos.x_offset
            gy = pos.y_offset
            # font units, y up  ->  px, y down
            t = TransformPen(pen, (scale, 0, 0, -scale, gx * scale, -gy * scale))
            font.draw_glyph_with_pen(info.codepoint, t)
            x += pos.x_advance + (track if i < len(infos) - 1 else 0)
        self.d = pen.getCommands()
        self.width = x * scale

        tt = TTFont(str(path), lazy=True)
        os2 = tt["OS/2"]
        self.cap = (getattr(os2, "sCapHeight", 0) or 700) * scale
        self.ascent = os2.sTypoAscender * scale
        self.descent = -os2.sTypoDescender * scale
        self.size = size

    def at(self, x, y, fill="currentColor"):
        """SVG <path> with the baseline at (x, y)."""
        return f'<path transform="translate({x:.2f} {y:.2f})" fill="{fill}" d="{self.d}"/>'
