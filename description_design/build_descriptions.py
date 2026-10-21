# -*- coding: utf-8 -*-
"""Build Odoo Apps Store description pages for CPA Books modules.

Odoo 14 runs index.html through html_sanitize, which removes <style> tags.
Every visual rule is therefore inline. Layout uses inline-block plus min-width
so columns stack on a narrow screen without media queries.

Run from anywhere:
    python3 build_descriptions.py
"""
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"

# Alternating feature-card backgrounds. Neighbours are never the same.
BACKGROUNDS = [
    "linear-gradient(180deg,#FFFFFF 0%,#F7FBFF 100%)",
    "linear-gradient(160deg,#F4F0FF 0%,#EEF5FF 100%)",
    "linear-gradient(180deg,#F3F8FF 0%,#FFFFFF 100%)",
    "linear-gradient(160deg,#FFF8F3 0%,#F4F0FF 100%)",
    "linear-gradient(180deg,#F7FBFF 0%,#EEF4FF 100%)",
]


def e(value):
    return html.escape(value, quote=True)


def brand(light=False):
    name = "#FFFFFF" if light else "#102A52"
    sub = "#D6E6FF" if light else "#5C6B86"
    bars = (
        ("#34D399", "10px"),
        ("#22C55E", "16px"),
        ("#3B82F6", "22px"),
        ("#1D4ED8", "28px"),
    )
    bar_html = "".join(
        '<span style="display:inline-block;width:6px;height:%s;background:%s;'
        'border-radius:3px;margin:0 1px;vertical-align:bottom;"></span>' % (height, color)
        for color, height in bars
    )
    return (
        '<span style="display:inline-block;vertical-align:middle;">'
        '<span style="display:inline-block;background:#FFFFFF;border-radius:12px;'
        'padding:8px 8px 6px;margin-right:10px;line-height:0;vertical-align:middle;'
        'box-shadow:0 6px 16px rgba(16,42,82,0.12);">%s</span>'
        '<span style="display:inline-block;vertical-align:middle;text-align:left;">'
        '<span style="display:block;font-weight:800;font-size:16px;color:%s;'
        'letter-spacing:-0.02em;line-height:1.1;">CPA Books</span>'
        '<span style="display:block;font-size:11px;color:%s;margin-top:2px;">'
        'Smart Accounting for a Smarter Business</span>'
        '</span></span>'
    ) % (bar_html, name, sub)


def version_pill():
    return (
        '<span style="display:inline-block;background:#0C2E62;color:#FFFFFF;'
        'border-radius:999px;padding:7px 8px 7px 14px;font-size:12px;font-weight:700;'
        'vertical-align:middle;">Built for odoo '
        '<span style="display:inline-block;background:#714B67;color:#FFFFFF;'
        'border-radius:7px;padding:2px 8px;margin-left:4px;">14</span></span>'
    )


def shot(src, alt):
    return (
        '<div style="background:#FFFFFF;border:1px solid #E3ECF8;border-radius:18px;'
        'padding:8px;box-shadow:0 18px 42px rgba(16,42,82,0.16);">'
        '<img src="%s" alt="%s" style="width:100%%;max-width:100%%;height:auto;'
        'border-radius:12px;display:block;border:0;"/>'
        '</div>'
    ) % (e(src), e(alt))


def dots():
    colors = ("#2166C1", "#60A5FA", "#DBEAFE")
    bits = "".join(
        '<span style="display:inline-block;width:7px;height:7px;border-radius:7px;'
        'background:%s;margin-right:5px;"></span>' % color
        for color in colors
    )
    return '<div style="margin:0 0 12px;line-height:1;">%s</div>' % bits


def glyph(icon, fg):
    """Flat icons drawn with CSS so they do not depend on an emoji font."""
    bar = (
        '<span style="display:block;height:2px;background:%s;border-radius:2px;margin:3px 0;"></span>'
        % fg
    )
    icons = {
        "list": '<span style="display:inline-block;width:16px;vertical-align:middle;">%s</span>' % (bar * 3),
        "plus": '<span style="color:%s;font-size:20px;font-weight:800;line-height:1;">+</span>' % fg,
        "pct": '<span style="color:%s;font-size:16px;font-weight:800;">%%</span>' % fg,
        "check": '<span style="color:%s;font-size:16px;font-weight:800;">&#10003;</span>' % fg,
        "dot": '<span style="display:inline-block;width:10px;height:10px;border-radius:10px;background:%s;"></span>' % fg,
        "box": (
            '<span style="display:inline-block;width:14px;height:12px;border:2px solid %s;'
            'border-radius:2px;vertical-align:middle;"></span>' % fg
        ),
        "cal": (
            '<span style="display:inline-block;width:14px;height:12px;border:2px solid %s;'
            'border-top-width:4px;border-radius:2px;vertical-align:middle;"></span>' % fg
        ),
        "link": (
            '<span style="display:inline-block;width:8px;height:8px;border:2px solid %s;'
            'border-radius:8px;vertical-align:middle;"></span>'
            '<span style="display:inline-block;width:8px;height:2px;background:%s;vertical-align:middle;"></span>'
            '<span style="display:inline-block;width:8px;height:8px;border:2px solid %s;'
            'border-radius:8px;vertical-align:middle;"></span>'
        ) % (fg, fg, fg),
    }
    kind = {
        "📋": "list", "📄": "list", "📑": "list", "📒": "list", "📚": "book", "📝": "list",
        "🍽️": "list", "🥣": "list", "📞": "dot", "🎫": "list",
        "⚙️": "gear", "🔧": "gear", "🛠️": "gear", "🧩": "box",
        "🔗": "link", "✏️": "edit", "🔎": "search", "🔍": "search", "👁️": "search",
        "💶": "coin", "📈": "chart", "📊": "chart", "📉": "chart", "%": "pct", "#️⃣": "pct",
        "➕": "plus", "🧮": "calc", "🎯": "target", "📦": "box", "⚖️": "scale",
        "📅": "cal", "✅": "check", "🚩": "dot", "⚠️": "dot", "📌": "dot",
        "🏢": "box", "🏗️": "box", "🏦": "box", "🚪": "box", "👤": "dot", "👷": "dot",
        "📍": "dot", "🔥": "dot", "🧪": "dot", "🧾": "list", "🤝": "dot", "📁": "box",
        "▶️": "dot", "⏱️": "cal", "📥": "box", "🛒": "box", "🏭": "box", "🏷️": "dot",
        "🔁": "link", "🔒": "box", "⚡": "dot", "💱": "coin", "🖨️": "list",
        "📤": "list", "🇦🇪": "dot", "💧": "dot", "📘": "list",
    }.get(icon, "dot")
    if kind == "gear":
        return (
            '<span style="display:inline-block;width:14px;height:14px;border:2px solid %s;'
            'border-radius:14px;vertical-align:middle;box-sizing:border-box;"></span>' % fg
        )
    if kind == "book":
        return icons["list"]
    if kind in ("edit", "search", "coin", "chart", "calc", "target", "scale"):
        marks = {
            "edit": "&#9998;",
            "search": "&#9906;",
            "coin": "&#9679;",
            "chart": "&#9650;",
            "calc": "=",
            "target": "&#9678;",
            "scale": "&#9671;",
        }
        return '<span style="color:%s;font-size:15px;font-weight:800;line-height:1;">%s</span>' % (fg, marks[kind])
    return icons.get(kind, icons["dot"])


def point(icon, bg, title, text):
    fg = {
        "#DCFCE7": "#15803D",
        "#DBEAFE": "#1D4ED8",
        "#EDE9FE": "#6D28D9",
        "#FFEDD5": "#C2410C",
        "#CCFBF1": "#0F766E",
        "#FCE7F3": "#BE185D",
    }.get(bg, "#1D4ED8")
    return (
        '<div style="margin:0 0 14px;text-align:left;">'
        '<span style="display:inline-block;width:40px;height:40px;line-height:40px;'
        'text-align:center;border-radius:12px;background:%s;font-size:16px;'
        'margin-right:10px;vertical-align:middle;">%s</span>'
        '<span style="display:inline-block;vertical-align:middle;max-width:250px;">'
        '<span style="display:block;font-weight:800;color:#14213D;font-size:14px;'
        'line-height:1.3;">%s</span>'
        '<span style="display:block;color:#52627A;font-size:12px;line-height:1.45;'
        'margin-top:2px;">%s</span></span></div>'
    ) % (bg, glyph(icon, fg), e(title), e(text))


def hero_bullet(color, text):
    return (
        '<div style="margin:0 0 8px;">'
        '<span style="display:inline-block;width:22px;height:22px;line-height:22px;'
        'text-align:center;border-radius:7px;background:%s;color:#FFFFFF;'
        'font-size:12px;font-weight:800;margin-right:8px;vertical-align:middle;">&#10003;</span>'
        '<span style="color:#F4F8FF;font-size:14px;font-weight:600;vertical-align:middle;">%s</span>'
        '</div>'
    ) % (color, e(text))


def feature_block(index, block):
    bg = BACKGROUNDS[index % len(BACKGROUNDS)]
    text = (
        '<div style="padding:8px 6px;">'
        '<div style="font-size:11px;font-weight:800;letter-spacing:0.12em;'
        'text-transform:uppercase;color:#2166C1;margin-bottom:8px;">%s</div>'
        '%s'
        '<h2 style="font-size:30px;line-height:1.15;font-weight:800;margin:0 0 12px;'
        'color:#102A52;letter-spacing:-0.02em;">%s<br/>'
        '<span style="color:#2166C1;">%s</span></h2>'
        '<p style="font-size:15px;line-height:1.65;color:#3E4E68;margin:0 0 16px;">%s</p>'
        '%s'
        '%s'
        '</div>'
    ) % (
        e(block["kicker"]),
        dots(),
        e(block["title"]),
        e(block["emphasis"]),
        e(block["body"]),
        "".join(point(p["icon"], p["bg"], p["title"], p["text"]) for p in block["points"]),
        (
            '<p style="font-size:12px;color:#6B7C93;margin:6px 0 0;">%s</p>' % e(block["note"])
            if block["note"] and not block["note"].lower().startswith("screenshot:")
            else ""
        ),
    )
    image = shot(block["image"], block["alt"])
    left, right = (image, text) if block["image_first"] else (text, image)
    bgcolor = "#FFFFFF" if index % 2 == 0 else "#F4F0FF"
    shell = (
        '<div bgcolor="%s" style="background:%s;border-radius:28px;padding:28px 16px;'
        'margin:18px 0;box-shadow:0 12px 32px rgba(16,42,82,0.06);">'
        '<div style="font-size:0;text-align:center;">'
        '<div style="display:inline-block;width:52%%;min-width:290px;max-width:560px;'
        'vertical-align:middle;font-size:16px;text-align:left;padding:8px;'
        'box-sizing:border-box;">@@LEFT@@</div>'
        '<div style="display:inline-block;width:46%%;min-width:270px;max-width:480px;'
        'vertical-align:middle;font-size:16px;text-align:left;padding:8px;'
        'box-sizing:border-box;">@@RIGHT@@</div>'
        '</div></div>'
    ) % (bgcolor, bg)
    return shell.replace("@@LEFT@@", left).replace("@@RIGHT@@", right)


def card(icon, bg, title, text):
    fg = {
        "#DCFCE7": "#15803D",
        "#DBEAFE": "#1D4ED8",
        "#EDE9FE": "#6D28D9",
        "#FFEDD5": "#C2410C",
        "#CCFBF1": "#0F766E",
        "#FCE7F3": "#BE185D",
    }.get(bg, "#1D4ED8")
    return (
        '<div style="display:inline-block;width:31%%;min-width:220px;vertical-align:top;'
        'box-sizing:border-box;padding:8px;font-size:15px;text-align:left;">'
        '<div style="background:#FFFFFF;border:1px solid #E3ECF8;border-radius:16px;'
        'padding:18px 16px;box-shadow:0 8px 22px rgba(16,42,82,0.05);min-height:148px;">'
        '<span style="display:inline-block;width:40px;height:40px;line-height:40px;'
        'text-align:center;border-radius:12px;background:%s;font-size:16px;'
        'margin-bottom:10px;">%s</span>'
        '<div style="font-weight:800;color:#102A52;font-size:15px;margin:0 0 6px;">%s</div>'
        '<div style="color:#52627A;font-size:13px;line-height:1.55;">%s</div>'
        '</div></div>'
    ) % (bg, glyph(icon, fg), e(title), e(text))


def step(number, title, text, last=False):
    arrow = "" if last else (
        '<span style="display:inline-block;color:#93C5FD;font-size:20px;font-weight:800;'
        'padding:28px 2px 0;vertical-align:top;">&#8594;</span>'
    )
    return (
        '<div style="display:inline-block;width:21%%;min-width:160px;vertical-align:top;'
        'box-sizing:border-box;padding:8px;font-size:14px;text-align:left;">'
        '<div style="background:#FFFFFF;border:1px solid #E3ECF8;border-radius:16px;'
        'padding:16px;min-height:150px;box-shadow:0 8px 20px rgba(16,42,82,0.04);">'
        '<span style="display:inline-block;width:34px;height:34px;line-height:34px;'
        'text-align:center;border-radius:17px;background:#2166C1;color:#FFFFFF;'
        'font-weight:800;font-size:13px;margin-bottom:8px;">%s</span>'
        '<div style="font-weight:800;color:#102A52;margin:0 0 6px;">%s</div>'
        '<div style="color:#52627A;font-size:13px;line-height:1.5;">%s</div>'
        '</div></div>%s'
    ) % (number, e(title), e(text), arrow)


def pills(items):
    return "".join(
        '<span style="display:inline-block;background:#FFFFFF;border:1px solid #D6E4F7;'
        'color:#1E40AF;border-radius:999px;padding:7px 12px;font-size:13px;'
        'font-weight:700;margin:4px;">%s</span>' % e(item)
        for item in items
    )


def section_shell(bg, inner, bgcolor="#FFFFFF"):
    return (
        '<div bgcolor="%s" style="background:%s;border-radius:28px;padding:32px 18px;'
        'margin:18px 0;box-shadow:0 12px 32px rgba(16,42,82,0.06);">%s</div>'
    ) % (bgcolor, bg, inner)


def heading(kicker, title, emphasis, intro):
    return (
        '<div style="text-align:center;margin:0 0 8px;">'
        '<div style="font-size:11px;font-weight:800;letter-spacing:0.12em;'
        'text-transform:uppercase;color:#2166C1;">%s</div>'
        '<h2 style="font-size:30px;line-height:1.2;font-weight:800;margin:8px 0 8px;'
        'color:#102A52;letter-spacing:-0.02em;">%s '
        '<span style="color:#2166C1;">%s</span></h2>'
        '<p style="font-size:15px;color:#52627A;max-width:640px;margin:0 auto 8px;'
        'line-height:1.6;">%s</p></div>'
    ) % (e(kicker), e(title), e(emphasis), e(intro))


def render(mod):
    hero_points = "".join(hero_bullet(color, text) for color, text in mod["hero_points"])
    card_points = "".join(
        '<div style="display:inline-block;width:48%%;min-width:180px;vertical-align:top;'
        'box-sizing:border-box;padding:4px 6px;font-size:14px;">%s</div>'
        % point(p["icon"], p["bg"], p["title"], p["text"])
        for p in mod["hero_card"]["points"]
    )
    features = "".join(feature_block(i, block) for i, block in enumerate(mod["sections"]))
    cards = "".join(card(c["icon"], c["bg"], c["title"], c["text"]) for c in mod["cards"])
    steps = "".join(
        step(str(i + 1).zfill(2), s["title"], s["text"], last=(i == len(mod["steps"]) - 1))
        for i, s in enumerate(mod["steps"])
    )
    extra = mod.get("extra", "")
    req_note = (
        '<p style="font-size:13px;color:#3E4E68;margin:12px 0 0;line-height:1.55;">%s</p>'
        % e(mod["requirement_note"])
        if mod.get("requirement_note")
        else ""
    )
    page = '''<div style="font-family:%(font)s;color:#14213D;background:#F3F7FC;padding:16px 10px 28px;line-height:1.5;">
<div style="max-width:1080px;margin:0 auto;">

<div bgcolor="#12356F" style="background:linear-gradient(135deg,#0E3A86 0%%,#1B5FBF 48%%,#3B82F6 100%%);border-radius:28px;padding:28px 22px 22px;box-shadow:0 22px 48px rgba(16,42,82,0.22);">
  <div style="margin:0 0 18px;font-size:0;">
    <div style="display:inline-block;width:58%%;min-width:260px;vertical-align:middle;font-size:16px;text-align:left;">%(brand)s</div>
    <div style="display:inline-block;width:40%%;min-width:220px;vertical-align:middle;font-size:16px;text-align:right;">%(pill)s</div>
  </div>
  <div style="font-size:0;">
    <div style="display:inline-block;width:48%%;min-width:280px;vertical-align:top;font-size:16px;text-align:left;padding:6px 12px 6px 0;box-sizing:border-box;">
      <div style="font-size:12px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;color:#D6E6FF;margin-bottom:8px;">%(category)s</div>
      <h1 style="font-size:40px;line-height:1.08;font-weight:800;margin:0 0 10px;color:#FFFFFF;letter-spacing:-0.03em;">%(title)s</h1>
      <p style="font-size:16px;line-height:1.6;color:#E7F0FF;margin:0 0 16px;max-width:460px;">%(summary)s</p>
      %(hero_points)s
    </div>
    <div style="display:inline-block;width:50%%;min-width:280px;vertical-align:top;font-size:16px;text-align:left;box-sizing:border-box;">
      <div style="background:#FFFFFF;border-radius:22px;padding:22px 18px 12px;box-shadow:0 16px 36px rgba(8,28,68,0.18);">
        <div style="font-size:11px;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;color:#2166C1;">%(card_kicker)s</div>
        <h2 style="font-size:28px;line-height:1.15;font-weight:800;margin:8px 0 8px;color:#102A52;">%(card_title)s <span style="color:#2166C1;">%(card_emphasis)s</span></h2>
        <p style="font-size:14px;line-height:1.6;color:#52627A;margin:0 0 14px;">%(card_body)s</p>
        <div style="font-size:0;">%(card_points)s</div>
        <div style="margin-top:8px;">
          <a href="https://www.cpabooks.org/contactus" style="display:inline-block;background:#2166C1;color:#FFFFFF;text-decoration:none;font-weight:800;font-size:14px;border-radius:999px;padding:11px 18px;">Contact CPA Books &#8594;</a>
        </div>
      </div>
    </div>
  </div>
  <div style="margin:18px auto 8px;max-width:920px;">%(hero_shot)s</div>
  <div style="text-align:center;color:#D6E6FF;font-size:12px;font-weight:800;letter-spacing:0.16em;margin-top:14px;">%(words)s</div>
</div>

%(features)s

%(cards_block)s
%(steps_block)s
%(extra)s
%(compat)s
%(why)s
%(footer)s

</div>
</div>'''
    cards_block = section_shell(
        "linear-gradient(180deg,#FFFFFF 0%,#F7FBFF 100%)",
        heading("Key features", "What this", "module covers", mod["cards_intro"])
        + '<div style="font-size:0;text-align:center;">%s</div>' % cards,
    )
    steps_block = section_shell(
        "linear-gradient(160deg,#F4F0FF 0%,#F7FBFF 100%)",
        heading("How it works", "A clear", "working sequence", mod["steps_intro"])
        + '<div style="font-size:0;text-align:center;">%s</div>' % steps,
        "#F4F0FF",
    )
    compat = section_shell(
        "linear-gradient(180deg,#EAF3FF 0%,#FFFFFF 100%)",
        heading("Compatibility", "Verified for", "Odoo 14", mod["compat_intro"])
        + '<div style="text-align:center;">'
        + '<div style="margin:8px 0 4px;font-size:12px;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:#2166C1;">Required apps</div>'
        + pills(mod["depends"])
        + req_note
        + '</div>',
        "#EAF3FF",
    )
    why = section_shell(
        "#FFFFFF",
        heading("Why CPA Books", "Odoo applications", "for operations",
                "CPA Books publishes Odoo applications for accounting and day-to-day operations. This page describes only what this module does.")
        + '<div style="text-align:center;font-size:14px;color:#3E4E68;line-height:1.7;">'
        + 'Publisher: CPA Books<br/>License: LGPL-3<br/>'
        + 'Website: <a href="https://www.cpabooks.org" style="color:#2166C1;font-weight:700;text-decoration:none;">www.cpabooks.org</a>'
        + ' &nbsp;·&nbsp; <a href="https://www.cpabooks.co" style="color:#2166C1;font-weight:700;text-decoration:none;">www.cpabooks.co</a>'
        + '</div>',
    )
    footer = (
        '<div bgcolor="#102A52" style="background:#102A52;border-radius:28px;padding:28px 18px;'
        'margin:18px 0 0;text-align:center;box-shadow:0 12px 32px rgba(16,42,82,0.16);">'
        '<div style="margin-bottom:12px;">%s</div>'
        '<div style="color:#FFFFFF;font-weight:800;font-size:18px;margin-bottom:6px;">Technical support</div>'
        '<p style="color:#D6E6FF;font-size:14px;margin:0 0 8px;line-height:1.6;">'
        'Questions about installation or how this module is meant to be used.</p>'
        '<p style="margin:0;font-size:14px;line-height:1.8;">'
        '<a href="mailto:info@cpabooks.org" style="color:#FFFFFF;font-weight:700;text-decoration:none;">info@cpabooks.org</a>'
        '<span style="color:#93C5FD;"> &nbsp;·&nbsp; </span>'
        '<a href="tel:+971562568128" style="color:#FFFFFF;font-weight:700;text-decoration:none;">+971 56 256 8128</a>'
        '<span style="color:#93C5FD;"> &nbsp;·&nbsp; </span>'
        '<a href="https://www.cpabooks.org" style="color:#FFFFFF;font-weight:700;text-decoration:none;">www.cpabooks.org</a>'
        '</p></div>'
    ) % brand(True)
    return page % {
        "font": FONT,
        "brand": brand(True),
        "pill": version_pill(),
        "category": e(mod["category"]),
        "title": e(mod["title"]),
        "summary": e(mod["summary"]),
        "hero_points": hero_points,
        "card_kicker": e(mod["hero_card"]["kicker"]),
        "card_title": e(mod["hero_card"]["title"]),
        "card_emphasis": e(mod["hero_card"]["emphasis"]),
        "card_body": e(mod["hero_card"]["body"]),
        "card_points": card_points,
        "hero_shot": shot(mod["hero_image"], mod["hero_alt"]),
        "words": e(mod["words"]),
        "features": features,
        "cards_block": cards_block,
        "steps_block": steps_block,
        "extra": extra,
        "compat": compat,
        "why": why,
        "footer": footer,
    }


def P(icon, bg, title, text):
    return {"icon": icon, "bg": bg, "title": title, "text": text}


def S(image_first, image, alt, kicker, title, emphasis, body, points, note):
    return {
        "image_first": image_first,
        "image": image,
        "alt": alt,
        "kicker": kicker,
        "title": title,
        "emphasis": emphasis,
        "body": body,
        "points": points,
        "note": note,
    }


MODULES = []


def add(technical, **kwargs):
    kwargs["technical"] = technical
    MODULES.append(kwargs)


add(
    "recipe_book_cpa",
    category="Restaurant management",
    title="Recipe Book",
    summary="Menu items, food cost and chef stock in one place. Each dish is linked to a sales product, with ingredients stored per portion.",
    hero_points=[
        ("#22C55E", "All recipes in one list"),
        ("#3B82F6", "Ingredients and margin on the recipe"),
        ("#8B5CF6", "Theoretical use from sales"),
        ("#F59E0B", "Chef closing stock and variance"),
        ("#14B8A6", "Food cost on the dashboard"),
    ],
    hero_card={
        "kicker": "Menu book",
        "title": "All recipes in",
        "emphasis": "one list",
        "body": "Menu Book shows each dish, its sales product, portions, food cost, selling price and margin.",
        "points": [
            P("📋", "#DCFCE7", "Complete recipe list", "See menu items with the costing columns."),
            P("⚙️", "#DBEAFE", "Food cost and margin", "Budget cost, current cost, price and margin."),
            P("🔗", "#EDE9FE", "Link with sales product", "Each recipe is tied to the item you sell."),
            P("✏️", "#FFEDD5", "Easy to manage", "Create, edit and organise recipes."),
        ],
    },
    hero_image="banner_store.jpg",
    hero_alt="Recipe Book store banner",
    words="SIMPLE  ·  FLEXIBLE  ·  ACCURATE",
    sections=[
        S(True, "recipe_ui_1.jpg", "Menu Book list", "Menu book", "Every dish", "on one list",
          "The list keeps the sales product, portions, budget food cost, current recipe cost, selling price and margin percent.",
          [P("🍽️", "#DCFCE7", "One row per dish", "Grills, soups, salads and the rest of the menu."),
           P("💶", "#DBEAFE", "Cost next to price", "Budget and current food cost sit beside the selling price."),
           P("📈", "#EDE9FE", "Margin percent", "The list shows the margin for each menu item."),
           P("🔎", "#FFEDD5", "Search and filter", "Find a dish without leaving Menu Book.")],
          "Screenshot: Menu Book."),
        S(False, "recipe_ui_2.jpg", "Recipe ingredients and margin", "Ingredients and margin", "Ingredients and margin", "on the recipe",
          "Open a dish to see ingredients per portion, food cost, selling price and margin.",
          [P("➕", "#DCFCE7", "Add ingredients", "Quantity per portion, unit and unit cost."),
           P("🧮", "#DBEAFE", "Automatic food cost", "Cost is calculated from the ingredient lines."),
           P("%", "#EDE9FE", "Selling price and margin", "Margin uses the current selling price and food cost."),
           P("🎯", "#FFEDD5", "Budget comparison", "Budget food cost and target margin stay on the recipe.")],
          "Screenshot: recipe form, ingredients and costing."),
        S(True, "recipe_ui_3.jpg", "Consumption analysis", "Consumption", "Theoretical use", "from sales",
          "Consumption Analysis turns confirmed sales into the ingredients the kitchen should have used.",
          [P("📦", "#DCFCE7", "Quantity from sales", "Theoretical quantity is built from recipes and sales."),
           P("⚖️", "#DBEAFE", "Unit on each line", "Kilogram, piece, litre and the other recipe units."),
           P("💶", "#EDE9FE", "Cost of that use", "Each ingredient line carries a cost."),
           P("📅", "#FFEDD5", "Date range", "Review one service period at a time.")],
          "Screenshot: Consumption Analysis."),
        S(False, "recipe_ui_4.jpg", "Closing stock and variance", "Closing stock", "Chef closing stock", "and variance",
          "Compare theoretical use with the chef's closing stock and see the quantity and value gap.",
          [P("📝", "#DCFCE7", "Enter closing stock", "Start the daily closing from this screen."),
           P("📉", "#DBEAFE", "Quantity variance", "Short and over quantities are shown on the line."),
           P("💶", "#EDE9FE", "Value variance", "The value gap is shown next to the quantity."),
           P("📅", "#FFEDD5", "Same date range", "Closing uses the period already reviewed in consumption.")],
          "Screenshot: Closing Stock and Variance."),
        S(True, "recipe_ui_5.jpg", "Recipe Book dashboard", "Dashboard", "Food cost", "on the dashboard",
          "The dashboard shows recipe count, average food cost, today's theoretical consumption and closing variance.",
          [P("📚", "#DCFCE7", "Total recipes", "How many recipes are on the book."),
           P("%", "#DBEAFE", "Average food cost", "A single food-cost percentage for the period."),
           P("📊", "#EDE9FE", "Cost against budget", "Actual cost and budgeted cost on one chart."),
           P("⚖️", "#FFEDD5", "Closing variance", "The period variance is on the same screen.")],
          "Screenshot: Recipe Book dashboard."),
    ],
    cards_intro="Daily controls for a restaurant that already sells in Odoo.",
    cards=[
        P("🍽️", "#DCFCE7", "Menu recipes", "One recipe per menu item, with ingredients stored per portion."),
        P("💶", "#DBEAFE", "Food cost and margin", "Compare budget food cost with the current recipe cost, selling price and margin."),
        P("🥣", "#EDE9FE", "Prep and sub-recipes", "Batch yield and unit cost for items prepared before they go on a plate."),
        P("📦", "#FFEDD5", "Theoretical consumption", "Ingredient use is calculated from confirmed sales orders."),
        P("⚖️", "#CCFBF1", "Closing stock variance", "Enter the chef's closing stock and see the gap against theoretical use."),
        P("📋", "#FCE7F3", "Sample recipes", "Load sample recipes, then clone them into live recipes."),
    ],
    steps_intro="From the recipe card to the end-of-day variance.",
    steps=[
        {"title": "Write the recipe", "text": "Attach ingredients to the menu product, per portion."},
        {"title": "Link the sales item", "text": "The dish stays tied to the product sold on the order."},
        {"title": "Sell as usual", "text": "Confirmed sales build theoretical ingredient consumption."},
        {"title": "Close the day", "text": "Compare chef stock with theoretical use and review the dashboard."},
    ],
    compat_intro="This release is built for Odoo 14. Later Odoo versions are not part of this module.",
    depends=["Sales", "Inventory", "Purchase", "Products"],
    requirement_note="Installs on Odoo 14 together with Sales, Inventory and Purchase.",
)

add(
    "sequences_cpa",
    category="Document numbering",
    title="Invoice Sequence Numbering",
    summary="Reset and align document numbers for accounting, sales, inventory, project and CRM from one screen.",
    hero_points=[
        ("#22C55E", "Invoice, sale and stock numbers"),
        ("#8B5CF6", "Bulk prefix and padding"),
        ("#F59E0B", "Yearly or monthly format"),
        ("#3B82F6", "Many journals in one update"),
        ("#EF4444", "Lock a sequence when it is done"),
    ],
    hero_card={
        "kicker": "Numbering",
        "title": "One screen for",
        "emphasis": "document numbers",
        "body": "Create, lock and reset company prefixes without opening every journal.",
        "points": [
            P("📄", "#DCFCE7", "Many documents", "Invoices, bills, orders and transfers."),
            P("⚙️", "#DBEAFE", "Prefix and digits", "Set the prefix, padding and format together."),
            P("🏢", "#EDE9FE", "One or many companies", "Apply the setup to the companies you select."),
            P("🔒", "#FFEDD5", "Sequence lock", "Lock a sequence so it is not edited by accident."),
        ],
    },
    hero_image="banner_screenshot.jpg",
    hero_alt="Invoice sequence numbering banner",
    words="CONSISTENT  ·  BULK  ·  LOCKED",
    sections=[
        S(False, "banner_alt.jpg", "Re-Sequences bulk update", "Bulk update", "Reset prefixes", "in one pass",
          "The Re-Sequences screen lists each sequence, whether it is locked, what it is for, and the company it belongs to.",
          [P("✅", "#DCFCE7", "Select the rows", "Choose the sequences that should change."),
           P("🔒", "#DBEAFE", "Lock", "Lock the sequences that should stay as they are."),
           P("🔁", "#EDE9FE", "Reset company prefix", "Push a company prefix across the selection."),
           P("📅", "#FFEDD5", "Yearly or monthly", "The list shows which format each sequence uses.")],
          "The same screen is used to create, lock and reset company prefixes."),
    ],
    cards_intro="Controls already described for everyday sequence work.",
    cards=[
        P("🔁", "#DCFCE7", "Bulk prefix reset", "Reset sequence prefixes for many journals and documents in one go."),
        P("🏢", "#DBEAFE", "Multi-company", "Apply the same sequence setup to one company or several at once."),
        P("📅", "#EDE9FE", "Yearly or monthly", "Switch between yearly or monthly sequence formats."),
        P("#️⃣", "#FFEDD5", "Digits and padding", "Change the number of digits so numbers stay aligned."),
        P("⚡", "#CCFBF1", "Journal updates", "Update many journals together instead of opening each one."),
        P("🔒", "#FCE7F3", "Sequence lock", "Lock sequences so an accidental edit does not change the series."),
    ],
    steps_intro="Set the pattern once, apply it, then lock what should not move.",
    steps=[
        {"title": "Set the pattern", "text": "Define prefixes, digits and yearly or monthly format."},
        {"title": "Apply in bulk", "text": "Push the update across the journals and documents you selected."},
        {"title": "Lock the series", "text": "Lock what should not change."},
        {"title": "Keep numbering aligned", "text": "New documents follow the same prefix and padding."},
    ],
    compat_intro="This release is built for Odoo 14. Later Odoo versions are not part of this module.",
    depends=["Accounting", "Sales", "Inventory", "Project", "CRM"],
    requirement_note="Purchase order numbering is included in the module screens. Purchase is not listed in the module dependencies.",
)

add(
    "audited_financial_cpa",
    category="Financial statements",
    title="Audited Financial Statements",
    summary="Build the statement pack from the Odoo trial balance: profit or loss, financial position, equity, cash flow, PPE and notes.",
    hero_points=[
        ("#22C55E", "Profit or loss and financial position"),
        ("#3B82F6", "Equity, cash flow and PPE"),
        ("#8B5CF6", "Notes beside the statements"),
        ("#F59E0B", "UAE corporate tax layout"),
        ("#14B8A6", "PDF, Excel, Word and CSV"),
    ],
    hero_card={
        "kicker": "From the ledger",
        "title": "Statements from",
        "emphasis": "posted books",
        "body": "Figures come from the accounting already kept in Odoo. Balances are not re-keyed into a spreadsheet.",
        "points": [
            P("📒", "#DCFCE7", "Trial balance", "The pack starts from Odoo accounting data."),
            P("🏢", "#DBEAFE", "Company and period", "Choose the company and the reporting period."),
            P("📊", "#EDE9FE", "Comparative columns", "Current period beside the prior period."),
            P("🖨️", "#FFEDD5", "Review, then export", "Preview the pack before sending it out."),
        ],
    },
    hero_image="banner_screenshot.jpg",
    hero_alt="Audited financial statements banner",
    words="LEDGER  ·  STATEMENTS  ·  EXPORT",
    sections=[
        S(True, "feature_01_setup.jpg", "Company and period setup", "Setup", "Company and", "period setup",
          "Configure the company, reporting periods, comparative periods and statement data from one place.",
          [P("🏢", "#DCFCE7", "Company selection", "Single company or the companies you report together."),
           P("📅", "#DBEAFE", "Period selection", "Yearly, monthly or a custom period."),
           P("💱", "#EDE9FE", "Currency", "Uses the currencies already set in Odoo, including AED."),
           P("📒", "#FFEDD5", "Posted journals", "Statement data is taken from posted Odoo journals.")],
          "Screenshot: company and period setup."),
        S(False, "feature_02_reporting.jpg", "Financial reporting", "Reporting", "Generate the", "financial pack",
          "Create the statements with flexible periods, comparative columns and more than one report level.",
          [P("📅", "#DCFCE7", "Comparative reporting", "Current year beside the prior year."),
           P("📑", "#DBEAFE", "Report levels", "A presentation layout and a more detailed working layout."),
           P("👁️", "#EDE9FE", "Print preview", "Review the pack before it is final."),
           P("📤", "#FFEDD5", "Export", "PDF, Excel, Word and CSV.")],
          "Screenshot: financial reporting."),
        S(True, "feature_03_structure.jpg", "Financial statement structure", "Structure", "Map the", "chart of accounts",
          "Map Odoo accounts into the statement groups used by the pack.",
          [P("🧩", "#DCFCE7", "Statement sections", "Profit or loss, financial position, cash flow, equity and PPE."),
           P("⚠️", "#DBEAFE", "Unmapped accounts", "See accounts that still need a group."),
           P("🔁", "#EDE9FE", "Reuse the map", "Keep the structure and run it again next period."),
           P("📝", "#FFEDD5", "Notes", "Supporting notes stay with the statements.")],
          "Screenshot: financial structure."),
    ],
    cards_intro="The statement pack prepared from Odoo accounting.",
    cards=[
        P("📈", "#DCFCE7", "Profit or loss", "Income statement for management review."),
        P("🏦", "#DBEAFE", "Financial position", "Assets, liabilities and equity, with comparative columns."),
        P("📘", "#EDE9FE", "Changes in equity", "Equity movements across the reporting periods."),
        P("💧", "#FFEDD5", "Cash flows", "Operating, investing and financing movements."),
        P("🏗️", "#CCFBF1", "PPE schedule", "Property, plant and equipment in the same pack."),
        P("🇦🇪", "#FCE7F3", "UAE corporate tax layout", "A financial layout used in UAE corporate tax work."),
    ],
    steps_intro="From the books already in Odoo to a pack you can export.",
    steps=[
        {"title": "Map the accounts", "text": "Place chart-of-accounts lines into statement groups."},
        {"title": "Choose company and period", "text": "Set the reporting period and the comparative period."},
        {"title": "Review the pack", "text": "Check unmapped accounts and the statement preview."},
        {"title": "Export", "text": "Send the pack to PDF, Excel, Word or CSV."},
    ],
    extra=section_shell(
        "#FFF8F1",
        '<h2 style="font-size:22px;font-weight:800;color:#102A52;margin:0 0 8px;text-align:center;">Management-prepared statements</h2>'
        '<p style="font-size:14px;color:#3E4E68;line-height:1.7;max-width:760px;margin:0 auto;text-align:center;">'
        'These statements are prepared from the accounting records in Odoo. They are management-prepared financial statements. '
        'They are not an independent external audit and they are not an auditor\'s opinion. '
        'Where a statutory audit is required, the audit report is issued by the appointed external auditor. '
        'The module does not replace the accounting system, and balances do not have to be typed in again.'
        '</p>',
        "#FFF8F1",
    ),
    compat_intro="This release is built for Odoo 14. Later Odoo versions are not part of this module.",
    depends=["Accounting", "Project Dashboard"],
    requirement_note="Depends on Accounting and the Project Dashboard app (project_dashboard_odoo). Exports: PDF, Excel, Word and CSV.",
)

add(
    "cafm_cpa",
    category="Facility management",
    title="Facility Management",
    summary="Service calls, AMC contracts, planned maintenance, project units and monthly billing in one Odoo app.",
    hero_points=[
        ("#22C55E", "Service calls in one list"),
        ("#3B82F6", "AMC register"),
        ("#8B5CF6", "PPM on the calendar"),
        ("#F59E0B", "Project units and tenants"),
        ("#14B8A6", "Monthly billing"),
    ],
    hero_card={
        "kicker": "Service desk",
        "title": "Calls, contracts",
        "emphasis": "and PPM",
        "body": "A facility team keeps the open call, the contract and the planned visit in the same app.",
        "points": [
            P("📞", "#DCFCE7", "Service calls", "Site, unit, category, priority and status."),
            P("📄", "#DBEAFE", "AMC register", "Client, site, dates and invoice status."),
            P("📅", "#EDE9FE", "Planned visits", "PPM on the calendar by day."),
            P("💶", "#FFEDD5", "Monthly billing", "Contract period, amount and invoice."),
        ],
    },
    hero_image="banner_store.jpg",
    hero_alt="Facility management store banner",
    words="CALLS  ·  CONTRACTS  ·  PPM",
    sections=[
        S(True, "cafm_ui_1.jpg", "Service calls", "Service calls", "Every ticket", "in one list",
          "Each ticket shows the site, unit, category, priority and whether it is open, in progress or done.",
          [P("🎫", "#DCFCE7", "Ticket number", "A number for every service call."),
           P("🏢", "#DBEAFE", "Site and unit", "The building and the unit are on the row."),
           P("🚩", "#EDE9FE", "Priority", "Urgent, high, medium and low."),
           P("✅", "#FFEDD5", "Status", "Open, in progress or done.")],
          "Screenshot: Service Calls."),
        S(False, "cafm_ui_2.jpg", "AMC register", "AMC", "Contracts on", "the AMC register",
          "Contracts sit with the client, site, dates, visit frequency and invoice status.",
          [P("📄", "#DCFCE7", "Client and site", "Who the contract is for, and where."),
           P("📅", "#DBEAFE", "Contract dates", "Start and end stay on the register."),
           P("🔁", "#EDE9FE", "Visit frequency", "How often the site is attended."),
           P("💶", "#FFEDD5", "Invoice status", "See whether the contract invoice is still open.")],
          "Screenshot: AMC register."),
        S(True, "cafm_ui_3.jpg", "PPM schedule", "PPM", "Planned work", "on the calendar",
          "Planned visits for equipment such as AHU, pumps and generators show by day, with the upcoming list beside the week.",
          [P("📅", "#DCFCE7", "Week view", "See the planned visits on the calendar."),
           P("🛠️", "#DBEAFE", "Asset on the visit", "The equipment is named on the plan."),
           P("📍", "#EDE9FE", "Site", "Each visit keeps its site."),
           P("📋", "#FFEDD5", "Upcoming list", "The next visits sit beside the calendar.")],
          "Screenshot: PPM calendar."),
        S(False, "cafm_ui_4.jpg", "Project units", "Projects", "Towers, floors", "and tenants",
          "A facility project lists towers, floors, unit numbers and tenants on one form.",
          [P("🏢", "#DCFCE7", "Project", "The facility project is the parent record."),
           P("🏗️", "#DBEAFE", "Tower and floor", "Units are grouped by building and floor."),
           P("🚪", "#EDE9FE", "Unit number", "Each unit has its own number."),
           P("👤", "#FFEDD5", "Tenant", "The tenant is stored on the unit.")],
          "Screenshot: project units."),
        S(True, "cafm_ui_5.jpg", "Monthly billing", "Billing", "Monthly billing", "by contract",
          "Each contract period shows the amount, the invoice and whether it is still draft or invoiced.",
          [P("📅", "#DCFCE7", "Contract period", "Billing follows the contract month."),
           P("💶", "#DBEAFE", "Amount", "The period amount is on the line."),
           P("🧾", "#EDE9FE", "Customer invoice", "The invoice is linked from the billing line."),
           P("📌", "#FFEDD5", "Draft or invoiced", "The line shows which stage the invoice is in.")],
          "Screenshot: monthly billing."),
    ],
    cards_intro="The operating screens a facilities contract team uses.",
    cards=[
        P("📞", "#DCFCE7", "Service calls", "Register a call with site, unit, category and priority."),
        P("📄", "#DBEAFE", "AMC register", "Keep contract dates, visit frequency and invoice status."),
        P("📅", "#EDE9FE", "PPM", "Plan preventive visits on a calendar."),
        P("🏢", "#FFEDD5", "Project units", "Towers, floors, units and tenants."),
        P("💶", "#CCFBF1", "Monthly billing", "Raise the period invoice from the contract."),
        P("📦", "#FCE7F3", "Variation and stock", "Variation work, stock issue and client statement screens are included."),
    ],
    steps_intro="From the contract to the call, the planned visit and the invoice.",
    steps=[
        {"title": "Register the contract", "text": "Create the AMC with client, site and dates."},
        {"title": "Plan the visits", "text": "Put PPM visits on the calendar for the equipment."},
        {"title": "Close the call", "text": "Work the service call through open, in progress and done."},
        {"title": "Bill the period", "text": "Create the invoice for the contract period."},
    ],
    compat_intro="This release is built for Odoo 14. Later Odoo versions are not part of this module.",
    depends=["Maintenance", "Project", "Accounting", "Sales"],
    requirement_note="Python library openpyxl is required. It is used by the import screens.",
)

add(
    "faff_cpa",
    category="Fire safety",
    title="Fire Alarm and Fire Fighting",
    summary="One fire-safety job moves from the lead through inspection, estimate, quotation, project, testing, handover and invoice.",
    hero_points=[
        ("#22C55E", "Jobs from CRM to closed"),
        ("#3B82F6", "Inspection and technical estimate"),
        ("#8B5CF6", "Quotation and project"),
        ("#F59E0B", "Testing with pass or fail"),
        ("#14B8A6", "Handover, invoice and payment"),
    ],
    hero_card={
        "kicker": "One job",
        "title": "Start to finish",
        "emphasis": "on one job",
        "body": "The pipeline keeps fire alarm and fire fighting work in stages, from the lead to closed.",
        "points": [
            P("🔥", "#DCFCE7", "Job pipeline", "CRM, inspection, estimate, quotation and project."),
            P("🔍", "#DBEAFE", "Inspection", "Record the site visit before pricing."),
            P("🧪", "#EDE9FE", "Testing", "Pass or fail on each device."),
            P("🧾", "#FFEDD5", "Invoice", "Handover and the customer invoice stay on the job."),
        ],
    },
    hero_image="banner_store.jpg",
    hero_alt="Fire alarm and fire fighting store banner",
    words="INSPECT  ·  TEST  ·  HANDOVER",
    sections=[
        S(True, "faff_ui_1.jpg", "Job pipeline", "Pipeline", "Jobs from CRM", "to closed",
          "Stages run from CRM through inspection, estimate, quotation, project, testing, invoice and closed.",
          [P("📥", "#DCFCE7", "CRM", "The lead starts on the pipeline."),
           P("🔍", "#DBEAFE", "Inspection and estimate", "The visit and the technical price are stages."),
           P("📑", "#EDE9FE", "Quotation and project", "The quoted job becomes project work."),
           P("✅", "#FFEDD5", "Invoice and closed", "The job stays visible until it is closed.")],
          "Screenshot: job pipeline."),
        S(False, "faff_ui_2.jpg", "New fire safety job", "New job", "Start a job", "with the site",
          "Pick the customer, site, job type, contact and expected date, then confirm.",
          [P("👤", "#DCFCE7", "Customer", "The job is opened for a customer."),
           P("📍", "#DBEAFE", "Site", "The site is stored on the job."),
           P("🔥", "#EDE9FE", "Job type", "Fire alarm or fire fighting work."),
           P("📅", "#FFEDD5", "Expected date", "The date the job is expected to move.")],
          "Screenshot: new job."),
        S(True, "faff_ui_3.jpg", "Inspection and estimate", "Estimate", "Inspection and", "technical estimate",
          "Record the inspection, then price detectors, panels and extinguishers on the same job.",
          [P("🔍", "#DCFCE7", "Inspection notes", "What was found on site."),
           P("📦", "#DBEAFE", "Materials", "Detectors, panels, extinguishers and related lines."),
           P("💶", "#EDE9FE", "Estimate", "Prices stay on the job."),
           P("📑", "#FFEDD5", "Ready to quote", "The estimate is the base for the quotation.")],
          "Screenshot: inspection and estimate."),
        S(False, "faff_ui_4.jpg", "Device testing", "Testing", "Pass or fail", "on each device",
          "Each device gets a location, a pass or fail, and a remark. Materials stay on the job.",
          [P("📍", "#DCFCE7", "Location", "Where the device was tested."),
           P("✅", "#DBEAFE", "Pass or fail", "The result is stored on the line."),
           P("📝", "#EDE9FE", "Remark", "A note when the result needs context."),
           P("📦", "#FFEDD5", "Materials", "Material lines remain on the same job.")],
          "Screenshot: testing."),
        S(True, "faff_ui_5.jpg", "Handover and invoice", "Handover", "Handover, invoice", "and payment",
          "A completed job shows handover, the customer invoice and whether it is paid.",
          [P("🤝", "#DCFCE7", "Handover", "The completed job records the handover."),
           P("🧾", "#DBEAFE", "Customer invoice", "The invoice is raised from the job."),
           P("💶", "#EDE9FE", "Payment", "The job shows whether the invoice is paid."),
           P("📁", "#FFEDD5", "One record", "The history stays on the job.")],
          "Screenshot: handover and invoice."),
    ],
    cards_intro="The path from the enquiry to a paid fire-safety job.",
    cards=[
        P("🔥", "#DCFCE7", "One job", "CRM, inspection, estimate, project, test and invoice on one record."),
        P("🔍", "#DBEAFE", "Inspection", "Capture the site findings before the price."),
        P("💶", "#EDE9FE", "Estimate and quote", "Price the devices, then issue the quotation."),
        P("🧪", "#FFEDD5", "Testing", "Pass or fail, with a location and a remark."),
        P("🤝", "#CCFBF1", "Handover", "Close the technical work with a handover."),
        P("🧾", "#FCE7F3", "Invoice", "Invoice the customer from the completed job."),
    ],
    steps_intro="The job wizard follows the site, not a separate spreadsheet.",
    steps=[
        {"title": "Open the job", "text": "Start from CRM with the customer, site and job type."},
        {"title": "Inspect and estimate", "text": "Record the visit and price the devices."},
        {"title": "Test and hand over", "text": "Mark each device and complete the handover."},
        {"title": "Invoice", "text": "Raise the customer invoice and follow it to payment."},
    ],
    compat_intro="This release is built for Odoo 14. Later Odoo versions are not part of this module.",
    depends=["CRM", "Sales", "Project", "Purchase", "Inventory", "Accounting", "Employees", "Invoice Sequence Numbering"],
    requirement_note="Invoice Sequence Numbering (sequences_cpa) must be installed first. It is a module dependency.",
)

add(
    "field_service_cpa",
    category="Field service",
    title="Field Service",
    summary="Register a complaint, visit the site, issue a quotation, do the work, invoice and close. One service order covers the job.",
    hero_points=[
        ("#22C55E", "Register the complaint"),
        ("#3B82F6", "Visit the site"),
        ("#8B5CF6", "Quotation before the work"),
        ("#F59E0B", "Do the job, then invoice"),
        ("#14B8A6", "Close when it is invoiced"),
    ],
    hero_card={
        "kicker": "Service order",
        "title": "One order",
        "emphasis": "for the visit",
        "body": "Customer, site, service type and visit date start the job. Later stages stay on the same order.",
        "points": [
            P("📝", "#DCFCE7", "Complaint", "Customer, site and service type."),
            P("📍", "#DBEAFE", "Site visit", "The technician works the visit on the job."),
            P("📑", "#EDE9FE", "Quotation", "Labour and parts are priced first."),
            P("🧾", "#FFEDD5", "Invoice", "The customer invoice is created from the job."),
        ],
    },
    hero_image="banner_store.jpg",
    hero_alt="Field service store banner",
    words="VISIT  ·  QUOTE  ·  INVOICE",
    sections=[
        S(True, "ui_1.jpg", "New service order", "Register", "Register", "the complaint",
          "A new service starts with the customer, the site, the service type and the visit date.",
          [P("👤", "#DCFCE7", "Customer", "Who reported the job."),
           P("📍", "#DBEAFE", "Site", "Where the technician is going."),
           P("🛠️", "#EDE9FE", "Service type", "The kind of work, such as air conditioning."),
           P("📅", "#FFEDD5", "Scheduled date", "When the visit is planned.")],
          "Screenshot: new service order."),
        S(False, "ui_2.jpg", "Site visit", "Visit", "Visit", "the site",
          "The technician opens the job, sees the address and marks the visit in progress.",
          [P("📍", "#DCFCE7", "Address on the job", "The site address is on the order."),
           P("👷", "#DBEAFE", "Assigned work", "The visit is carried on the same record."),
           P("▶️", "#EDE9FE", "In progress", "The stage shows that the visit has started."),
           P("📝", "#FFEDD5", "What was found", "Notes stay with the service order.")],
          "Screenshot: site visit."),
        S(True, "ui_3.jpg", "Service quotation", "Quotation", "Quotation", "before the work",
          "Lines for labour and parts are priced on a quotation before the job starts.",
          [P("👷", "#DCFCE7", "Labour", "Time is priced on the quotation."),
           P("📦", "#DBEAFE", "Parts", "Materials are lines on the same quote."),
           P("💶", "#EDE9FE", "Price first", "The customer sees the price before the work."),
           P("🔗", "#FFEDD5", "Linked order", "The quotation belongs to the service order.")],
          "Screenshot: quotation."),
        S(False, "ui_4.jpg", "Invoice after the job", "Invoice", "Do the job,", "then invoice",
          "When the work is done the stage moves to Done and a customer invoice is created from the same job.",
          [P("✅", "#DCFCE7", "Done", "The stage records that the work is finished."),
           P("🧾", "#DBEAFE", "Customer invoice", "The invoice is created from the job."),
           P("📦", "#EDE9FE", "Parts used", "Materials issued for the job stay linked."),
           P("⏱️", "#FFEDD5", "Time", "Timesheets can be kept on the job.")],
          "Screenshot: completed job and invoice."),
        S(True, "ui_5.jpg", "Invoiced service orders", "Close", "Close when", "it is invoiced",
          "The list shows the job as invoiced once the customer invoice is raised.",
          [P("📋", "#DCFCE7", "Order list", "Every service order stays on one list."),
           P("🧾", "#DBEAFE", "Invoiced", "The list marks jobs that have an invoice."),
           P("🔎", "#EDE9FE", "Find the job", "Search the list instead of a separate sheet."),
           P("📁", "#FFEDD5", "History", "The visit, quote and invoice remain together.")],
          "Screenshot: invoiced jobs."),
    ],
    cards_intro="The service order is the file for the whole visit.",
    cards=[
        P("📝", "#DCFCE7", "Complaint", "Customer, site, service type and visit date."),
        P("📍", "#DBEAFE", "Site visit", "The technician updates the job on site."),
        P("📑", "#EDE9FE", "Quotation", "Labour and parts before the work starts."),
        P("📦", "#FFEDD5", "Materials", "Parts issued, returned and consumed on the job."),
        P("⏱️", "#CCFBF1", "Timesheets", "Employee time can be recorded on the service order."),
        P("🧾", "#FCE7F3", "Invoice", "Create the customer invoice when the work is done."),
    ],
    steps_intro="Complaint, visit, price, work, invoice.",
    steps=[
        {"title": "Register", "text": "Open the service order with customer, site and date."},
        {"title": "Visit and quote", "text": "Attend the site and price labour and parts."},
        {"title": "Do the work", "text": "Move the job through in progress to done."},
        {"title": "Invoice", "text": "Create the customer invoice from the same order."},
    ],
    compat_intro="This release is built for Odoo 14. Later Odoo versions are not part of this module.",
    depends=["Project", "Sales", "Inventory", "Purchase", "Accounting", "Employees", "Timesheets"],
    requirement_note="Uses project tasks as the service order, with sales, stock and employee timesheets.",
)

add(
    "switchgear_cpa",
    category="Switchgear manufacturing",
    title="Switchgear Manufacturing",
    summary="A panel job runs from enquiry and quotation through design, bill of materials, manufacturing, purchase, quality, delivery and invoice.",
    hero_points=[
        ("#22C55E", "Enquiry, estimate and quotation"),
        ("#3B82F6", "Design, BoM and manufacturing"),
        ("#8B5CF6", "Purchase and quality check"),
        ("#F59E0B", "Delivery, invoice and payment"),
        ("#14B8A6", "One list for the whole job"),
    ],
    hero_card={
        "kicker": "Panel job",
        "title": "Enquiry to",
        "emphasis": "delivery",
        "body": "The customer, the project and the panel stay on one manufacturing cycle.",
        "points": [
            P("📥", "#DCFCE7", "Enquiry", "Customer, project and expected delivery."),
            P("🧩", "#DBEAFE", "BoM and MO", "Bill of materials and manufacturing order."),
            P("✅", "#EDE9FE", "Quality", "Pass or fail on the finished panel."),
            P("🧾", "#FFEDD5", "Invoice", "The job reference is on the customer invoice."),
        ],
    },
    hero_image="banner_store.jpg",
    hero_alt="Switchgear manufacturing store banner",
    words="DESIGN  ·  BUILD  ·  DELIVER",
    sections=[
        S(True, "ui_1.jpg", "New switchgear enquiry", "Enquiry", "Enquiry, estimate", "and quotation",
          "A panel enquiry starts with the customer and the project, then moves to a quotation.",
          [P("👤", "#DCFCE7", "Customer", "Who asked for the panel."),
           P("📁", "#DBEAFE", "Project", "The panel project, such as a main panel."),
           P("📅", "#EDE9FE", "Expected delivery", "The date the panel is expected."),
           P("📑", "#FFEDD5", "Quotation stage", "The enquiry moves on to a quotation.")],
          "Screenshot: new enquiry."),
        S(False, "ui_2.jpg", "Design, bill of materials and manufacturing", "Manufacturing", "Design, BoM", "and manufacturing",
          "The confirmed job opens a bill of materials and a manufacturing order for the panel.",
          [P("✏️", "#DCFCE7", "Design", "Design documents stay with the job."),
           P("🧩", "#DBEAFE", "Bill of materials", "Components for the panel."),
           P("🏭", "#EDE9FE", "Manufacturing order", "The panel is produced from that BoM."),
           P("📁", "#FFEDD5", "Job reference", "Design and production keep the same job.")],
          "Screenshot: design, BoM and manufacturing."),
        S(True, "ui_3.jpg", "Quality check", "Quality", "Purchase and", "quality check",
          "The finished panel gets a quality check, with a pass or fail on each test.",
          [P("🛒", "#DCFCE7", "Purchase", "Materials can be requested for the job."),
           P("🧪", "#DBEAFE", "Quality tests", "Each test is recorded on the panel."),
           P("✅", "#EDE9FE", "Pass or fail", "The result is visible on the check."),
           P("🏷️", "#FFEDD5", "Panel identity", "The check stays with the manufacturing job.")],
          "Screenshot: quality check."),
        S(False, "ui_4.jpg", "Customer invoice", "Invoice", "Stock, invoice", "and payment",
          "The finished panel is invoiced to the customer, with the job reference on the invoice.",
          [P("📦", "#DCFCE7", "Finished panel", "Stock follows the completed panel."),
           P("🧾", "#DBEAFE", "Customer invoice", "The invoice is raised for that job."),
           P("🔗", "#EDE9FE", "Job reference", "The panel job is named on the invoice."),
           P("💶", "#FFEDD5", "Payment", "Payment is followed from the same cycle.")],
          "Screenshot: invoice."),
        S(True, "ui_5.jpg", "Switchgear job list", "Jobs", "One list for", "the full cycle",
          "The list keeps every panel job, from quotation through manufacturing to done.",
          [P("📋", "#DCFCE7", "Every panel", "Quotation, manufacturing and done on one list."),
           P("🏭", "#DBEAFE", "Stage", "See how far the panel has moved."),
           P("🔎", "#EDE9FE", "Find a job", "Search the list by the panel job."),
           P("📁", "#FFEDD5", "Same record", "Enquiry, build, quality and invoice stay related.")],
          "Screenshot: job list."),
    ],
    cards_intro="The manufacturing cycle for a switchgear panel.",
    cards=[
        P("📥", "#DCFCE7", "Enquiry and quote", "Customer, project, estimate and quotation."),
        P("✏️", "#DBEAFE", "Design", "Design documents on the job."),
        P("🧩", "#EDE9FE", "BoM and manufacturing", "Components and the manufacturing order."),
        P("🛒", "#FFEDD5", "Purchase", "Purchase requisition for job materials."),
        P("✅", "#CCFBF1", "Quality", "Pass or fail before the panel moves on."),
        P("🧾", "#FCE7F3", "Delivery and invoice", "Deliver the panel and invoice the customer."),
    ],
    steps_intro="From the panel enquiry to a paid delivery.",
    steps=[
        {"title": "Enquire and quote", "text": "Open the enquiry and send the quotation."},
        {"title": "Design and build", "text": "Release the BoM and the manufacturing order."},
        {"title": "Check quality", "text": "Record pass or fail on the finished panel."},
        {"title": "Deliver and invoice", "text": "Ship the panel and invoice the customer."},
    ],
    compat_intro="This release is built for Odoo 14. Later Odoo versions are not part of this module.",
    depends=["CRM", "Sales", "Manufacturing", "Inventory", "Purchase", "Accounting", "Project", "Employees", "Timesheets"],
    requirement_note="Uses standard Odoo CRM, Sales, Manufacturing, Inventory, Purchase, Accounting and Project.",
)


def main():
    for mod in MODULES:
        target = ROOT / mod["technical"] / "static" / "description" / "index.html"
        html_out = render(mod)
        target.write_text(html_out, encoding="utf-8")
        print("wrote", target.relative_to(ROOT), "bytes", target.stat().st_size)


if __name__ == "__main__":
    main()
