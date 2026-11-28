"""Aurean Axis render kit — "GOLD 101" educational reels + IB/join promo reels.

Usage:
  python3 aa.py lesson spec.json out_dir      -> out_dir/<slug>.mp4, <slug>_cover_light.jpg, <slug>.json (cover info)
  python3 aa.py promo  spec.json out_dir      -> promo reel (IB recruitment / join)

Lesson spec (JSON):
{
 "n": 19, "slug": "e19_fvg", "theme": "dark"|"light"   (light = ivory cover tile for the checkered grid),
 "hook": "What is a fair value gap?",
 "chart_title": "Fair value gap (FVG)",
 "candles": [[o,h,l,c], ...]          (any price units, 8-16 candles),
 "marks": [ {"type":"hline","y":price,"label":"Support"},
            {"type":"ring","i":idx},                         (oval round candle i)
            {"type":"tag","i":idx,"text":"Long lower wick","pos":"below"|"above"},
            {"type":"zone","i0":a,"i1":b,"y0":p,"y1":q,"label":"FVG"} ],
 "explain": "One or two sentences under the chart.",
 "how_title": "How to use it",
 "bullets": ["...", "...", "..."],
 "cover_sub": "Short subtitle for the light cover"
}
Add --tiktok as the last argument to render a TikTok-safe copy (<slug>_tt.mp4) whose end card says
"Follow @aureanaxis" instead of a DM ask. Optional "cta" key overrides the end-card pill text.
Promo spec: {"slug","theme","kicker","head":["line","*gold line"],"points":["..",".."],"cta":"DM \\"PARTNER\\""}
"""
import json, os, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from animate import frames, encode, FPS

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
GOLD = (214, 178, 96)
GOLD_HI = (246, 222, 150)
GOLD_LO = (150, 112, 44)
BLACK = (8, 8, 8)
PANEL = (20, 19, 16)
EDGE = (60, 52, 34)
WHITE = (240, 238, 232)
MUTED = (150, 146, 136)
GREEN = (38, 196, 120)
RED = (224, 66, 66)
IVORY = (241, 235, 224)
INK = (18, 16, 12)
RISK = "RISK WARNING: Trading forex and CFDs is high risk. Only risk what you can afford to lose. Past results are not a guarantee of future results. Not financial advice."

STAGES = []


def snap(img):
    STAGES.append(img.copy())


def font(size, w="Bold"):
    return ImageFont.truetype(os.path.join(ROOT, "fonts", f"Inter-{w}.otf"), size)


def gold_fill(size, seed=0):
    w, h = size
    ys = np.linspace(0, 1, h)[:, None, None]
    xs = np.linspace(0, 1, w)[None, :, None]
    t = np.clip(0.8 * ys + 0.2 * xs, 0, 1)
    a, b, c = np.array(GOLD_HI), np.array(GOLD), np.array(GOLD_LO)
    col = np.where(t < 0.5, a + (b - a) * (t / 0.5), b + (c - b) * ((t - 0.5) / 0.5))
    return Image.fromarray(col.astype("uint8"))


def text_w(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, maxw):
    out, cur = [], ""
    for w_ in s.split():
        t = (cur + " " + w_).strip()
        if text_w(d, t, f) <= maxw:
            cur = t
        else:
            out.append(cur); cur = w_
    if cur:
        out.append(cur)
    return out


def draw_lines(img, lines, f, cx, y, fill=WHITE, gold=False, gap=1.12, align="center", x=None):
    d = ImageDraw.Draw(img)
    for ln in lines:
        tw = text_w(d, ln, f)
        px = cx - tw / 2 if align == "center" else x
        if gold:
            m = Image.new("L", img.size, 0)
            ImageDraw.Draw(m).text((px, y), ln, font=f, fill=255)
            img.paste(gold_fill(img.size), (0, 0), m)
        else:
            d.text((px, y), ln, font=f, fill=fill)
        y += int(f.size * gap)
    return y


def bg(seed, bokeh=False):
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (W, H), BLACK)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-300, 1200, 900, 2300], fill=(46, 36, 12))
    gd.ellipse([400, -400, 1500, 600], fill=(34, 27, 10))
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    img = Image.fromarray(np.clip(np.asarray(img, float) + np.asarray(glow, float), 0, 255).astype("uint8"))
    if bokeh:
        lay = Image.new("RGB", (W, H), (0, 0, 0))
        ld = ImageDraw.Draw(lay)
        for _ in range(90):
            x, y, r = rng.integers(0, W), rng.integers(0, H), rng.integers(10, 46)
            a = rng.uniform(0.25, 1)
            ld.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(c * a) for c in GOLD))
        lay = lay.filter(ImageFilter.GaussianBlur(7))
        img = Image.fromarray(np.clip(np.asarray(img, float) + np.asarray(lay, float) * 0.55, 0, 255).astype("uint8"))
    # thin gold frame
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([28, 28, W - 28, H - 28], 26, outline=(54, 44, 22), width=2)
    return img


def footer(img, dark=True):
    d = ImageDraw.Draw(img)
    f1, f2 = font(26, "SemiBold"), font(19, "Medium")
    d.text((W / 2, 1745), "@aureanaxis", font=f1, fill=GOLD if dark else GOLD_LO, anchor="mm")
    lines = wrap(d, RISK, f2, W - 220)
    y = 1780
    for ln in lines:
        d.text((W / 2, y), ln, font=f2, fill=(120, 116, 104) if dark else (110, 100, 86), anchor="mt")
        y += 26


def pill(img, cx, y, text, f, fg=GOLD, solid=False):
    d = ImageDraw.Draw(img)
    tw = text_w(d, text, f)
    box = [cx - tw / 2 - 30, y, cx + tw / 2 + 30, y + f.size + 30]
    if solid:
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).rounded_rectangle(box, (box[3] - box[1]) / 2, fill=255)
        img.paste(gold_fill(img.size), (0, 0), m)
        d.text((cx, y + 15 + f.size / 2), text, font=f, fill=BLACK, anchor="mm")
    else:
        d.rounded_rectangle(box, (box[3] - box[1]) / 2, outline=fg, width=3, fill=(24, 20, 10))
        d.text((cx, y + 15 + f.size / 2), text, font=f, fill=fg, anchor="mm")
    return box[3]


def logo(width, dark_ink=False):
    lg = Image.open(os.path.join(ROOT, "logo_gold.png")).convert("RGBA")
    lg = lg.resize((width, int(lg.height * width / lg.width)), Image.LANCZOS)
    if dark_ink:
        a = lg.getchannel("A")
        lg = Image.new("RGBA", lg.size, INK + (255,))
        lg.putalpha(a)
    return lg


# ---------------- charts ----------------
def chart(img, box, candles, marks, upto=None, show_marks=True, stage=False):
    """Draw candles in box=(x0,y0,x1,y1). If stage, snap after each group of candles and each mark."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 22, fill=PANEL, outline=EDGE, width=2)
    lo = min(c[2] for c in candles); hi = max(c[1] for c in candles)
    for m in marks:
        for k in ("y", "y0", "y1"):
            if k in m:
                lo, hi = min(lo, m[k]), max(hi, m[k])
    pad = (hi - lo) * 0.18
    lo, hi = lo - pad, hi + pad
    iw, ih = x1 - x0 - 90, y1 - y0 - 110
    n = len(candles)
    step = iw / n
    X = lambda i: x0 + 45 + step * (i + 0.5)
    Y = lambda p: y0 + 55 + ih * (1 - (p - lo) / (hi - lo))
    bw = max(10, step * 0.52)
    groups = [list(range(i, min(i + 3, n))) for i in range(0, n, 3)]
    for g in groups:
        for i in g:
            o, h_, l, c = candles[i]
            col = GREEN if c >= o else RED
            d.line([X(i), Y(h_), X(i), Y(l)], fill=col, width=4)
            top, bot = Y(max(o, c)), Y(min(o, c))
            d.rectangle([X(i) - bw / 2, top, X(i) + bw / 2, max(bot, top + 4)], fill=col)
        if stage:
            snap(img)
    if not show_marks:
        return
    ft = font(26, "SemiBold")
    for m in marks:
        t = m["type"]
        if t == "hline":
            yy = Y(m["y"])
            for xx in range(int(x0 + 30), int(x1 - 30), 26):
                d.line([xx, yy, xx + 14, yy], fill=GOLD, width=3)
            d.text((x1 - 40, yy + 10), m.get("label", ""), font=ft, fill=GOLD, anchor="ra")
        elif t == "ring":
            i = m["i"]; o, h_, l, c = candles[i]
            d.ellipse([X(i) - bw * 1.1, Y(h_) - 24, X(i) + bw * 1.1, Y(l) + 24], outline=GOLD, width=4)
        elif t == "zone":
            xa, xb = X(m["i0"]) - bw, X(m["i1"]) + bw
            ya, yb = Y(max(m["y0"], m["y1"])), Y(min(m["y0"], m["y1"]))
            ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(ov).rectangle([xa, ya, x1 - 30, yb], fill=GOLD + (60,), outline=GOLD + (200,), width=3)
            img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"))
            d = ImageDraw.Draw(img)
            if m.get("label"):
                d.text((x1 - 44, (ya + yb) / 2), m["label"], font=ft, fill=GOLD_HI, anchor="rm")
        elif t == "tag":
            i = m["i"]; o, h_, l, c = candles[i]
            below = m.get("pos", "below") == "below"
            yy = Y(l) + 40 if below else Y(h_) - 40
            tw = text_w(d, m["text"], ft)
            bx = [X(i) - tw / 2 - 16, yy - 22, X(i) + tw / 2 + 16, yy + 22]
            if bx[0] < x0 + 10:
                bx[2] += x0 + 10 - bx[0]; bx[0] = x0 + 10
            if bx[2] > x1 - 10:
                bx[0] -= bx[2] - (x1 - 10); bx[2] = x1 - 10
            d.rounded_rectangle(bx, 22, fill=(30, 26, 14), outline=GOLD, width=2)
            d.text(((bx[0] + bx[2]) / 2, yy), m["text"], font=ft, fill=WHITE, anchor="mm")
        if stage:
            snap(img)


# ---------------- scenes ----------------
def scene_hook(spec):
    STAGES.clear()
    img = bg(spec["n"], bokeh=True)
    footer(img); snap(img)
    f = font(40, "Bold")
    pill(img, W / 2, 640, f"GOLD 101 · LESSON {spec['n']}", font(30, "Bold")); snap(img)
    d = ImageDraw.Draw(img)
    fh = font(118, "ExtraBold")
    lines = wrap(d, spec["hook"], fh, W - 200)
    draw_lines(img, lines, fh, W / 2, 760, gold=True, gap=1.08); snap(img)
    return list(STAGES)


def scene_chart(spec):
    STAGES.clear()
    img = bg(spec["n"] + 1)
    footer(img)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 230), spec["chart_title"], font=font(66, "ExtraBold"), fill=WHITE, anchor="mm"); snap(img)
    chart(img, (80, 320, W - 80, 1240), spec["candles"], spec.get("marks", []), stage=True)
    f = font(44, "Medium")
    lines = wrap(ImageDraw.Draw(img), spec["explain"], f, W - 200)
    draw_lines(img, lines, f, W / 2, 1300, fill=WHITE, gap=1.3); snap(img)
    return list(STAGES)


def scene_how(spec):
    STAGES.clear()
    img = bg(spec["n"] + 2)
    footer(img)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 560), spec.get("how_title", "How to use it"), font=font(70, "ExtraBold"), fill=WHITE, anchor="mm"); snap(img)
    f = font(46, "SemiBold")
    y = 680
    for b in spec["bullets"]:
        d.ellipse([110, y + 4, 156, y + 50], outline=GOLD, width=4)
        d.line([122, y + 28, 131, y + 38], fill=GOLD, width=5); d.line([131, y + 38, 146, y + 16], fill=GOLD, width=5)
        lines = wrap(d, b, f, W - 300)
        y = draw_lines(img, lines, f, 0, y, fill=WHITE, gap=1.25, align="left", x=190) + 40
        snap(img)
    return list(STAGES)


def scene_cta(seed, head=("Learn this live,", "every day."), cta='DM "GOLD"'):
    STAGES.clear()
    img = bg(seed, bokeh=False)
    footer(img); snap(img)
    lg = logo(330)
    img.paste(lg, (int(W / 2 - lg.width / 2), 520), lg); snap(img)
    y = draw_lines(img, list(head), font(84, "ExtraBold"), W / 2, 900, gold=True, gap=1.12); snap(img)
    pill(img, W / 2, y + 60, cta, font(46, "ExtraBold"), solid=True); snap(img)
    return list(STAGES)


def light_cover(spec, out):
    img = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(img)
    d.rectangle([40, 280, W - 40, 1640], outline=(192, 160, 96), width=3)
    lg = logo(240, dark_ink=True)
    img.paste(lg, (int(W / 2 - lg.width / 2), 350), lg)
    d.text((W / 2, 640), f"GOLD 101 · LESSON {spec['n']}", font=font(40, "SemiBold"), fill=(160, 120, 40), anchor="mm")
    fh = font(112, "Black")
    lines = wrap(d, spec.get("cover_title", spec["hook"]), fh, W - 180)
    y = draw_lines(img, lines, fh, W / 2, 700, fill=INK, gap=1.08)
    if spec.get("cover_sub"):
        draw_lines(img, wrap(d, spec["cover_sub"], font(46, "Medium"), W - 240), font(46, "Medium"), W / 2, y + 20, fill=(70, 62, 50))
    f2 = font(24, "Medium")
    yy = 1560
    for ln in wrap(d, "Trading forex and CFDs is high risk. Only risk what you can afford to lose. Not financial advice.", f2, W - 220):
        d.text((W / 2, yy), ln, font=f2, fill=(120, 110, 96), anchor="mm"); yy += 32
    img.save(out, quality=92)


def light_scene(spec):
    """Light-theme opener (ivory tile) — used as the first 2.5 s of light reels so the grid tile matches."""
    STAGES.clear()
    p = f"/tmp/_lc_{spec['slug']}.jpg"; light_cover(spec, p)
    STAGES.append(Image.open(p).convert("RGB"))
    return list(STAGES)


def render_lesson(spec, out_dir, music=None, offset=0.0):
    os.makedirs(out_dir, exist_ok=True)
    slug = spec["slug"]
    parts = []
    if spec.get("theme") == "light":
        parts.append(frames(light_scene(spec), 2.5, intro=0.1, anim=0.4, zoom=0.02))
    parts += [frames(scene_hook(spec), 3.0, intro=0.15, span=0.6, anim=0.5),
              frames(scene_chart(spec), 8.0, intro=0.1, span=4.6, anim=0.45),
              frames(scene_how(spec), 5.0, intro=0.1, span=2.4, anim=0.5),
              frames(scene_cta(spec["n"] + 3, cta=spec.get("cta", 'DM "GOLD"')), 4.2, intro=0.1, span=1.2, anim=0.5)]
    dur = sum([2.5 if spec.get("theme") == "light" else 0, 3.0, 8.0, 5.0, 4.2])

    def it():
        for p in parts:
            yield from p
    music = music or os.path.join(ROOT, "music", random.choice(sorted(os.listdir(os.path.join(ROOT, "music")))))
    out = os.path.join(out_dir, slug + ".mp4")
    encode(it(), (W, H), out, dur, music_offset=offset, music=music, afade=1.2, vfade_out=0.4)
    light_cover(spec, os.path.join(out_dir, slug + "_cover_light.jpg"))
    # dark tiles: cover frame = hook scene fully revealed (~2.2 s in, +2.5 s if light opener)
    info = {"cover_ms": 1300 if spec.get("theme") == "light" else 2200, "duration": dur}  # light: ivory opener tile
    json.dump(info, open(os.path.join(out_dir, slug + ".json"), "w"))
    return out


def render_promo(spec, out_dir, music=None, offset=0.0):
    """IB-recruitment / join promo reel: kicker + headline, 3–5 points revealed one by one, CTA."""
    os.makedirs(out_dir, exist_ok=True)
    seed = abs(hash(spec["slug"])) % 1000
    STAGES.clear()
    img = bg(seed, bokeh=True); footer(img); snap(img)
    pill(img, W / 2, 620, spec.get("kicker", "AUREAN AXIS"), font(30, "Bold")); snap(img)
    y = 740
    for ln in spec["head"]:
        g = ln.startswith("*")
        y = draw_lines(img, wrap(ImageDraw.Draw(img), ln.lstrip("*"), font(100, "ExtraBold"), W - 180), font(100, "ExtraBold"),
                       W / 2, y, gold=g, fill=WHITE, gap=1.08); snap(img)
    s1 = list(STAGES)
    STAGES.clear()
    img = bg(seed + 1); footer(img); snap(img)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 300 + max(0, 4 - len(spec["points"])) * 90 + 200), spec.get("points_title", "What you get"), font=font(66, "ExtraBold"), fill=WHITE, anchor="mm"); snap(img)
    y = 620 + max(0, 4 - len(spec["points"])) * 90
    f = font(44, "SemiBold")
    for p in spec["points"]:
        d.rounded_rectangle([90, y, W - 90, y + 150], 28, fill=PANEL, outline=EDGE, width=2)
        d.ellipse([130, y + 55, 170, y + 95], fill=GOLD)
        lines = wrap(d, p, f, W - 330)
        yy = y + 75 - (len(lines) * 54) / 2
        for ln in lines:
            d.text((200, yy), ln, font=f, fill=WHITE); yy += 54
        snap(img); y += 180
    s2 = list(STAGES)
    s3 = scene_cta(seed + 2, head=tuple(spec.get("cta_head", ["Partners first.", "Always."])), cta=spec.get("cta", 'DM "PARTNER"'))
    parts = []
    if spec.get("theme") == "light":
        cov = dict(n=0, hook=spec.get("cover_title", " ".join(h.lstrip("*") for h in spec["head"])), cover_sub=spec.get("cover_sub"))
        STAGES.clear(); p = f"/tmp/_lcp_{spec['slug']}.jpg"; promo_cover(spec, p)
        parts.append(frames([Image.open(p).convert("RGB")], 2.5, intro=0.1, anim=0.4, zoom=0.02))
    parts += [frames(s1, 3.5, intro=0.15, span=1.0, anim=0.5), frames(s2, 7.5, intro=0.1, span=4.5, anim=0.45),
              frames(s3, 4.5, intro=0.1, span=1.2, anim=0.5)]
    dur = (2.5 if spec.get("theme") == "light" else 0) + 3.5 + 7.5 + 4.5

    def it():
        for p in parts:
            yield from p
    music = music or os.path.join(ROOT, "music", random.choice(sorted(os.listdir(os.path.join(ROOT, "music")))))
    out = os.path.join(out_dir, spec["slug"] + ".mp4")
    encode(it(), (W, H), out, dur, music_offset=offset, music=music, afade=1.2, vfade_out=0.4)
    promo_cover(spec, os.path.join(out_dir, spec["slug"] + "_cover_light.jpg"))
    json.dump({"cover_ms": 1300 if spec.get("theme") == "light" else 2800, "duration": dur},
              open(os.path.join(out_dir, spec["slug"] + ".json"), "w"))
    return out


def promo_cover(spec, out):
    img = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(img)
    d.rectangle([40, 280, W - 40, 1640], outline=(192, 160, 96), width=3)
    lg = logo(240, dark_ink=True)
    img.paste(lg, (int(W / 2 - lg.width / 2), 350), lg)
    d.text((W / 2, 640), spec.get("kicker", "AUREAN AXIS"), font=font(40, "SemiBold"), fill=(160, 120, 40), anchor="mm")
    fh = font(104, "Black")
    y = 700
    for ln in spec["head"]:
        y = draw_lines(img, wrap(d, ln.lstrip("*"), fh, W - 180), fh, W / 2, y, fill=INK, gap=1.08)
    d.text((W / 2, 1590), "Trading forex and CFDs is high risk. Not financial advice.", font=font(24, "Medium"), fill=(120, 110, 96), anchor="mm")
    img.save(out, quality=92)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--tiktok"]
    kind, spec_path, out_dir = args[:3]
    spec = json.load(open(spec_path))
    music = args[3] if len(args) > 3 else None
    if "--tiktok" in sys.argv:  # TikTok-safe copy: no DM ask on screen
        spec["slug"] += "_tt"; spec["cta"] = "Follow @aureanaxis"
        if kind != "lesson":
            spec["cta_head"] = ["Learn more,", "follow along."]
    print((render_lesson if kind == "lesson" else render_promo)(spec, out_dir, music))
