"""Opal Marketing render kit — dark backgrounds, logo-matched opal gradient, type, logo, stage capture."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, "fonts")

# Palette sampled from the official logo
NAVY = (10, 13, 36)
NAVY2 = (13, 16, 44)
INK = (12, 16, 42)
MINT = (150, 225, 205)
GREEN = (24, 72, 84)
TEAL = (30, 90, 100)
BLUE = (30, 44, 104)
VIOLET = (58, 42, 122)
PURPLE = (60, 45, 125)
CREAM = (246, 242, 234)
MUTED = (176, 180, 200)
LINE = (70, 78, 120)

LIGHT = os.environ.get("OPAL_THEME") == "light"
if LIGHT:  # ivory tiles for the checkered grid
    NAVY, NAVY2 = (247, 243, 236), (238, 234, 242)
    INK = (14, 18, 48)
    MINT = (38, 128, 112)
    GREEN, TEAL, BLUE = (205, 236, 226), (190, 225, 225), (212, 220, 244)
    VIOLET, PURPLE = (222, 208, 244), (215, 205, 240)
    CREAM = (18, 22, 56)
    MUTED = (88, 94, 124)
    LINE = (205, 205, 220)
    OPAL_STOPS_LIGHT = [(0.0, (40, 150, 128)), (0.3, (45, 118, 176)), (0.62, (96, 78, 190)), (1.0, (150, 88, 180))]

ON_OPAL = (250, 248, 244) if LIGHT else INK

# ---------- stage capture (for animation) ----------
STAGES = []


def snap(img):
    STAGES.append(img.copy())


def reset_stages():
    STAGES.clear()


def serif(size):
    f = ImageFont.truetype(os.path.join(F, "PlayfairDisplay.ttf"), size)
    f.set_variation_by_name("Regular")
    return f


def sans(size, weight="Bold"):
    f = ImageFont.truetype(os.path.join(F, "Jost.ttf"), size)
    f.set_variation_by_name(weight)
    return f


# ---------- textures ----------
def _smooth_noise(w, h, scale, seed):
    rng = np.random.default_rng(seed)
    sw, sh = max(2, w // scale), max(2, h // scale)
    n = Image.fromarray((rng.random((sh, sw)) * 255).astype("uint8"))
    n = n.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(max(1, scale / 3)))
    return np.asarray(n).astype(float) / 255.0


OPAL_STOPS = [(0.0, (170, 238, 218)), (0.3, (150, 205, 236)), (0.62, (186, 168, 242)), (1.0, (236, 220, 240))]


def opal_texture(w, h, seed=7):
    stops_ = OPAL_STOPS_LIGHT if LIGHT else OPAL_STOPS
    """Logo-style gradient: mint/green at top-left flowing to purple at bottom-right."""
    w, h = max(int(w), 2), max(int(h), 2)
    a = _smooth_noise(w, h, max(40, min(w, h) // 2), seed)
    xs = np.linspace(0, 1, w)[None, :]
    ys = np.linspace(0, 1, h)[:, None]
    t = np.clip(0.75 * ys + 0.35 * xs - 0.08 + 0.25 * (a - 0.5), 0, 1)
    out = np.zeros((h, w, 3))
    for (p0, c0), (p1, c1) in zip(stops_[:-1], stops_[1:]):
        m = (t >= p0) & (t <= p1)
        k = ((t - p0) / (p1 - p0))[..., None]
        out = np.where(m[..., None], np.array(c0) * (1 - k) + np.array(c1) * k, out)
    return Image.fromarray(np.clip(out, 0, 255).astype("uint8"))


def grain(img, amount=5, seed=3):
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(float)
    a += rng.normal(0, amount * (0.5 if LIGHT else 1), a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


GLOW_POS = {"tl": (0.08, 0.06), "tr": (0.92, 0.08), "bl": (0.08, 0.94), "br": (0.92, 0.92),
            "c": (0.5, 0.5), "ml": (0.0, 0.5), "mr": (1.0, 0.45), "tc": (0.5, 0.0), "bc": (0.5, 1.0)}


def bg_dark(w, h, glows=(("tl", VIOLET, 0.32), ("br", GREEN, 0.24)), seed=1):
    ys = np.linspace(0, 1, h)[:, None, None]
    base = np.array(NAVY) * (1 - ys) + np.array(NAVY2) * ys
    img = Image.fromarray(np.broadcast_to(base, (h, w, 3)).astype("uint8"))
    for where, col, strength in glows:
        px, py = GLOW_POS[where]
        layer = Image.new("L", (w, h), 0)
        r = int(w * 0.55)
        cx, cy = int(px * w), int(py * h)
        ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r], fill=int(255 * strength))
        layer = layer.filter(ImageFilter.GaussianBlur(w * 0.22))
        img = Image.composite(Image.new("RGB", (w, h), col), img, layer)
    return grain(img, 4, seed)


# ---------- logo ----------
def logo(width, kind="lockup"):
    fn = ({"lockup": "logo_final_light.png", "mark": "logo_final_light_mark.png"} if LIGHT else {"lockup": "logo_final.png", "mark": "logo_final_mark.png"}).get(kind, f"{kind}.png")
    L = Image.open(os.path.join(ROOT, "src", fn)).convert("RGBA")
    return L.resize((int(width), int(L.height * width / L.width)), Image.LANCZOS)


def paste_logo(img, width, cx, top, kind="lockup"):
    L = logo(width, kind)
    img.paste(L, (int(cx - L.width / 2), int(top)), L)
    return top + L.height


# ---------- type ----------
def tracked_width(text, font, tracking):
    if not text:
        return 0
    return sum(font.getlength(c) for c in text) + tracking * (len(text) - 1)


def draw_tracked(d, xy, text, font, fill, tracking=0):
    if tracking == 0:
        d.text(xy, text, font=font, fill=fill)
        return
    x, y = xy
    for c in text:
        d.text((x, y), c, font=font, fill=fill)
        x += font.getlength(c) + tracking


def _seg_width(segs, font, tracking):
    return sum(tracked_width(t, font, tracking) for t, _ in segs)


def rich_lines(img, lines, font, x, y, align="left", fill=CREAM, line_gap=1.12, tracking=0,
               opal_seed=7, stage_each=False):
    """lines: list of str or list of (text, colour|'opal'). stage_each snaps after each line."""
    W, H = img.size
    d = ImageDraw.Draw(img)
    asc, desc = font.getmetrics()
    lh = int((asc + desc) * line_gap)
    for line in lines:
        segs = [(line, fill)] if isinstance(line, str) else line
        lw = _seg_width(segs, font, tracking)
        cx = x - lw / 2 if align == "center" else (x - lw if align == "right" else x)
        for text, col in segs:
            tw = tracked_width(text, font, tracking)
            if col == "opal":
                bw, bh = int(tw + 40), int((asc + desc) * 1.15)
                bx, by = int(cx - 10), int(y)
                t = opal_texture(bw, bh, opal_seed + int(cx) % 13)
                mask = Image.new("L", (bw, bh), 0)
                draw_tracked(ImageDraw.Draw(mask), (cx - bx, 0), text, font, 255, tracking)
                img.paste(t, (bx, by), mask)
            else:
                draw_tracked(d, (cx, y), text, font, col, tracking)
            cx += tw + (tracking if text else 0)
        y += lh
        if stage_each:
            snap(img)
    return y


def wrap(text, font, maxw, tracking=0):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tracked_width(t, font, tracking) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(img, text, font, x, y, maxw, fill, align="left", line_gap=1.4, tracking=0):
    return rich_lines(img, wrap(text, font, maxw, tracking), font, x, y, align, fill=fill,
                      line_gap=line_gap, tracking=tracking)


def opal_rule(img, x, y, w, h=6, seed=11):
    img.paste(opal_texture(w, h, seed), (int(x), int(y)))


def pill(img, cx, y, text, font, fg, outline, pad=(34, 16), tracking=4):
    d = ImageDraw.Draw(img)
    tw = tracked_width(text, font, tracking)
    asc, desc = font.getmetrics()
    w, h = tw + pad[0] * 2, asc + pad[1] * 2 - 4
    x0 = cx - w / 2
    d.rounded_rectangle([x0, y, x0 + w, y + h], radius=h / 2, outline=outline, width=3)
    draw_tracked(d, (x0 + pad[0], y + pad[1] - 3), text, font, fg, tracking)
    return y + h


def footer(img, sub="SOCIAL MEDIA FOR TRADING BRANDS", y=None):
    W, H = img.size
    d = ImageDraw.Draw(img)
    y = y if y is not None else H - 110
    line = f"OPAL MARKETING  ·  {sub}"
    size, tr = 24, 5
    while True:
        f = sans(size, "SemiBold")
        tw = tracked_width(line, f, tr)
        if tw <= W * 0.78 or size <= 16:
            break
        size -= 1
        tr = max(3, tr - 0.3)
    draw_tracked(d, ((W - tw) / 2, y), line, f, MUTED, tr)


def glass_card(img, box, radius=32):
    x0, y0, x1, y1 = [int(v) for v in box]
    W, H = img.size
    region = img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(18))
    region = Image.blend(region, Image.new("RGB", region.size, (255, 255, 255)), 0.55 if LIGHT else 0.06)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=radius, fill=255)
    full = img.copy()
    full.paste(region, (x0, y0))
    img.paste(full, (0, 0), mask)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(box, radius=radius, outline=(170, 180, 225, 85), width=2)
    img.paste(ov, (0, 0), ov)


def opal_dot(img, cx, cy, r, seed=5):
    tex = opal_texture(2 * r, 2 * r, seed)
    m = Image.new("L", (2 * r, 2 * r), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    img.paste(tex, (int(cx - r), int(cy - r)), m)


def opal_button(img, cx, y, text, w=640, h=170, size=70):
    tex = opal_texture(w, h, 93).filter(ImageFilter.GaussianBlur(6))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=255)
    img.paste(tex, (int(cx - w / 2), int(y)), m)
    f = sans(size, "ExtraBold")
    asc, desc = f.getmetrics()
    rich_lines(img, [text], f, cx, y + (h - asc) / 2 + 2, align="center", fill=ON_OPAL, tracking=3)
    return y + h


def kicker(img, text, x, y, align="left", size=30):
    rich_lines(img, [text], sans(size, "Regular"), x, y, align=align, fill=MINT, tracking=10)


def save(img, path):
    img.convert("RGB").save(path, "PNG", optimize=True)
