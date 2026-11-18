"""Reusable Opal reel templates (1080x1920). Theme comes from OPAL_THEME (navy default / light)."""
from opal import *

W, H = 1080, 1920
M = 96


def start(seed, glows=None):
    reset_stages()
    g = glows or [(("tl", VIOLET, 0.32), ("br", GREEN, 0.24)),
                  (("tr", BLUE, 0.30), ("bl", VIOLET, 0.30)),
                  (("tc", BLUE, 0.34), ("bl", VIOLET, 0.26), ("br", GREEN, 0.20)),
                  (("tl", GREEN, 0.22), ("br", VIOLET, 0.36))][seed % 4]
    img = bg_dark(W, H, g, seed)
    snap(img)
    return img


def _lines(spec):
    """spec: list of str; a str starting with '*' renders in opal."""
    out = []
    for s in spec:
        out.append([(s[1:], "opal")] if s.startswith("*") else s)
    return out


def statement(seed, kicker_txt, head, body=None, sub=None, size=104):
    img = start(seed)
    y = 420
    kicker(img, kicker_txt, M, y); snap(img)
    y = rich_lines(img, _lines(head), serif(size), M - 6, y + 70, line_gap=1.1, stage_each=True)
    opal_rule(img, M, y + 50, 120, 6); snap(img)
    y += 120
    if body:
        y = text_block(img, body, sans(42, "Regular"), M, y, W - 2 * M, CREAM, line_gap=1.45); snap(img)
    if sub:
        text_block(img, sub, sans(38, "Regular"), M, y + 40, W - 2 * M, MUTED, line_gap=1.45); snap(img)
    paste_logo(img, 380, W / 2, 1500); snap(img)
    return img


def listing(seed, kicker_txt, head, items, numbered=True):
    """items: list of (title, desc)."""
    img = start(seed)
    kicker(img, kicker_txt, M, 300); snap(img)
    y = rich_lines(img, _lines(head), serif(100), M - 4, 360, line_gap=1.08, stage_each=True)
    y += 70
    step = min(190, int((1560 - y) / max(len(items), 1)))
    for i, (a, b) in enumerate(items):
        if numbered:
            rich_lines(img, [[(f"0{i + 1}", "opal")]], serif(64), M, y - 6)
        else:
            opal_dot(img, M + 26, y + 30, 16, seed=40 + i)
        rich_lines(img, [a], sans(44, "SemiBold"), M + 130, y)
        if b:
            text_block(img, b, sans(32, "Regular"), M + 130, y + 62, W - 2 * M - 130, MUTED, line_gap=1.35)
        if i < len(items) - 1:
            ImageDraw.Draw(img).line([M + 130, y + step - 26, W - M, y + step - 26], fill=LINE, width=2)
        snap(img)
        y += step
    paste_logo(img, 300, W / 2, 1620); snap(img)
    return img


def stat(seed, kicker_txt, number, label, body=None, source=None):
    img = start(seed)
    kicker(img, kicker_txt, W / 2, 420, align="center"); snap(img)
    y = rich_lines(img, [[(number, "opal")]], serif(250), W / 2, 500, align="center"); snap(img)
    y = rich_lines(img, [label], serif(64), W / 2, y + 10, align="center"); snap(img)
    opal_rule(img, W / 2 - 70, y + 50, 140, 5); snap(img)
    if body:
        y = text_block(img, body, sans(40, "Regular"), W / 2, y + 110, W - 2 * M - 40, MUTED, align="center", line_gap=1.45)
        snap(img)
    if source:
        rich_lines(img, [source], sans(26, "Regular"), W / 2, 1460, align="center", fill=MUTED)
    paste_logo(img, 340, W / 2, 1560); snap(img)
    return img


def myth(seed, myth_txt, fact_head, fact_body):
    img = start(seed)
    kicker(img, "MYTH", M, 380); snap(img)
    f = serif(76)
    y = 450
    for line in wrap(myth_txt, f, W - 2 * M):
        rich_lines(img, [line], f, M - 4, y, fill=MUTED)
        tw = tracked_width(line, f, 0)
        ImageDraw.Draw(img).line([M - 4, y + 52, M + tw, y + 52], fill=(150, 100, 220), width=6)
        y += 92
    snap(img)
    kicker(img, "FACT", M, y + 80); snap(img)
    y = rich_lines(img, _lines(fact_head), serif(92), M - 4, y + 150, line_gap=1.1, stage_each=True)
    text_block(img, fact_body, sans(40, "Regular"), M, y + 60, W - 2 * M, CREAM, line_gap=1.45); snap(img)
    paste_logo(img, 340, W / 2, 1580); snap(img)
    return img


def offer(seed):
    img = start(seed)
    kicker(img, "MAIN PAGE PACKAGE", W / 2, 300, align="center"); snap(img)
    y = rich_lines(img, [[("£1,500", "opal")]], serif(200), W / 2, 360, align="center"); snap(img)
    y = rich_lines(img, ["per month"], sans(40, "Regular"), W / 2, y, align="center", fill=MUTED); snap(img)
    items = [("20 reels a day", "Instagram, Facebook & X"), ("14 a day on TikTok", "paced to keep you safe from bans"),
             ("5 YouTube Shorts a day", None), ("2 story sequences a week", "saved to your highlights")]
    y += 70
    for i, (a, b) in enumerate(items):
        glass_card(img, (M, y, W - M, y + 150))
        opal_dot(img, M + 64, y + 75, 16, seed=50 + i)
        rich_lines(img, [a], sans(42, "SemiBold"), M + 110, y + (30 if b else 50))
        if b:
            rich_lines(img, [b], sans(30, "Regular"), M + 110, y + 88, fill=MUTED)
        snap(img)
        y += 175
    rich_lines(img, ["Extra clipping pages £1,000 each · bigger packages on request"], sans(28, "Regular"),
               W / 2, y + 20, align="center", fill=MUTED); snap(img)
    opal_button(img, W / 2, 1600, "DM “OPAL”", w=600, h=160, size=64); snap(img)
    return img


def cta(seed, head, sub):
    img = start(seed)
    rich_lines(img, _lines(head), serif(100), W / 2, 420, align="center", line_gap=1.1, stage_each=True)
    y = opal_button(img, W / 2, 800, "DM “OPAL”", w=700, h=190, size=78); snap(img)
    text_block(img, sub, sans(40, "Regular"), W / 2, y + 60, W - 2 * M - 80, CREAM, align="center"); snap(img)
    paste_logo(img, 600, W / 2, 1260); snap(img)
    return img
