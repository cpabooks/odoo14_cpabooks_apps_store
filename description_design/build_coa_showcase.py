# -*- coding: utf-8 -*-
"""Build the Apps Store page of cpabooks_chart_of_accounts in the cpabooks.org showcase design.

Same layout as https://cpabooks.org/apps/chart-of-accounts: proof row, intro with
call-to-action buttons, key features grid, eight alternating 40/60 text and
screenshot bands, and a navy call-to-action band.

Odoo 14 html_sanitize removes <style>, so every rule is inline. Columns are
inline-block with a min-width, so they stack on a narrow screen.

    python3 build_coa_showcase.py
"""
from pathlib import Path

from build_descriptions import FONT, _dark_card, e

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "cpabooks_chart_of_accounts" / "static" / "description" / "index.html"

NAVY = "#102A52"
BLUE = "#2166C1"
MUTED = "#5B6B82"
LINE = "#DCE8F7"
LIGHT = "#EEF5FD"
WA_NUMBER = "971562568128"
TITLE = "Chart of Accounts Management"
SUMMARY = (
    "Build a clean, IFRS-coded chart of accounts in Odoo. Recode with a preview, merge duplicate "
    "ledgers, remove unused ones and post opening balances, all from one place."
)

KEYS = [
    ("fa-sitemap", "IFRS 3-level coding", "Type, group and ledger codes, such as 1 Assets, 15 Cash and Bank, 1501 Bank."),
    ("fa-refresh", "Reset and recode", "Preview every new code before you apply it."),
    ("fa-compress", "Merge duplicate ledgers", "Move journal items into the right account."),
    ("fa-trash-o", "Clean up unused ledgers", "Delete them, or archive when Odoo blocks a delete."),
    ("fa-balance-scale", "Opening balance", "The offset goes to Retained Earnings automatically."),
    ("fa-building-o", "Multi-company view", "Branch code, company and balances in one list."),
]

FEATURES = [
    {
        "image": "coa_ui_1.jpg",
        "title": "Every Ledger in One Clean List",
        "text": "Type, group code, group name and ledger code sit side by side, with one-click buttons "
                "and an Actions menu for every bulk task.",
        "points": [
            ("fa-sitemap", "3-level IFRS codes", "Type (1 digit), group (2 digits) and ledger (4 digits), such as 1501."),
            ("fa-bolt", "One-click resets", "Reset All, Reset Groups, Update all Groups, Reset AFG and Reset CTG."),
            ("fa-list-ul", "Bulk actions menu", "Archive or delete unused, merge, IFRS recode, fix duplicate codes and create a JV."),
        ],
    },
    {
        "image": "coa_ui_2.jpg",
        "title": "Browse Accounts by Type and Group Code",
        "text": "Group the chart by type and group code to review the whole structure, from Assets to "
                "Expenses, in seconds.",
        "points": [
            ("fa-object-group", "Grouped by type", "Assets, Liabilities, Equity, Income and Expenses, each with a count."),
            ("fa-folder-open-o", "Group code drill-down", "Open 11, 13, 15 and more to see every ledger in that group."),
            ("fa-filter", "Flexible grouping", "Group by type, group code, group or company and branch."),
        ],
    },
    {
        "image": "coa_ui_3.jpg",
        "title": "Multi-Company Ledgers With Live Balances",
        "text": "See the branch code, company and opening and closing balance for every ledger in the "
                "same list, with totals at the bottom.",
        "points": [
            ("fa-building-o", "Multi-company ready", "BC and Company / Branch columns on each ledger."),
            ("fa-balance-scale", "Opening and closing balances", "Check balances without opening a report."),
            ("fa-columns", "Optional columns", "Show or hide BC, company, proposed group, balances and account type."),
        ],
    },
    {
        "image": "coa_ui_4.jpg",
        "title": "Full Ledger Details With Related Accounts",
        "text": "Each ledger keeps its group code, account group, previous code and previous name, so "
                "old references are never lost.",
        "points": [
            ("fa-history", "Previous code kept", "The old account code and ledger name stay on the record after recoding."),
            ("fa-link", "Related ledgers", "Link similar ledgers, such as bank and petty cash accounts."),
            ("fa-book", "Journal items", "Open the ledger's journal items straight from the form."),
        ],
    },
    {
        "image": "coa_ui_5.jpg",
        "title": "Reset and Recode With IFRS Preview",
        "text": "See the old code, new code, group and suggested name for every ledger before anything "
                "changes, then apply in one click.",
        "points": [
            ("fa-eye", "Preview first", "Each row shows whether the code will change or is already OK."),
            ("fa-refresh", "Automatic IFRS codes", "New codes follow the group: 1501 Bank, 1301 Receivable, 4101 Sales."),
            ("fa-check-circle-o", "Apply or refresh", "Apply the recode, refresh the preview or cancel."),
        ],
    },
    {
        "image": "coa_ui_6.jpg",
        "title": "Merge Duplicate Ledgers Into One Account",
        "text": "Move journal items from duplicate ledgers into the right account, with usage and "
                "balance shown for each one.",
        "points": [
            ("fa-compress", "Merge from and into", "Pick the old ledgers; the target ledger is suggested for you."),
            ("fa-info-circle", "Usage at a glance", "Journal items, balance and used or unused status per ledger."),
            ("fa-archive", "Merge, archive or delete", "Act on the selected rows from the same window."),
        ],
    },
    {
        "image": "coa_ui_7.jpg",
        "title": "Remove Unused Ledgers in a Few Clicks",
        "text": "List the ledgers with no journal items and a zero balance, then delete them. If Odoo "
                "blocks a delete, the ledger is archived instead.",
        "points": [
            ("fa-search", "Only unused ledgers", "Ledgers with no entries and a zero balance are listed."),
            ("fa-check-square-o", "Quick selection", "Select all unused, select all on the page or clear the selection."),
            ("fa-shield", "Safe clean-up", "Delete, or archive when a delete is not allowed."),
        ],
    },
    {
        "image": "coa_ui_8.jpg",
        "title": "Post Opening Balances With Auto Offset",
        "text": "Enter opening balances by ledger. The difference goes to Retained Earnings "
                "automatically, so the entry always balances.",
        "points": [
            ("fa-pencil-square-o", "Simple entry", "Debit and credit by account, with a date and journal."),
            ("fa-exchange", "Auto offset", "A Retained Earnings line balances the entry for you."),
            ("fa-paper-plane-o", "Draft, then post", "Review the entry in draft and post it when ready."),
        ],
    },
]


def wa_link(text):
    return "https://wa.me/%s?text=%s" % (WA_NUMBER, text.replace(" ", "%20").replace(",", "%2C"))


def kicker(text, color=BLUE, center=False):
    return (
        '<div style="color:%s;font-size:12px;font-weight:800;letter-spacing:0.1em;'
        'text-transform:uppercase;margin:0 0 8px;%s">%s</div>'
    ) % (color, "text-align:center;" if center else "", e(text))


def split_heading(title, tail_words, size, center=False):
    words = title.split()
    head, tail = " ".join(words[:-tail_words]), " ".join(words[-tail_words:])
    return (
        '<h2 style="font-size:%dpx;line-height:1.18;font-weight:800;letter-spacing:-0.02em;'
        'color:%s;margin:0 0 14px;%s">%s <span style="color:%s;">%s</span></h2>'
    ) % (size, NAVY, "text-align:center;" if center else "", e(head), BLUE, e(tail))


def icon_tile(icon):
    return (
        '<span style="display:inline-block;width:44px;height:44px;line-height:44px;text-align:center;'
        'border-radius:12px;background-color:#DFEBFB;color:%s;font-size:18px;vertical-align:top;'
        'margin-right:14px;"><i class="fa %s"></i></span>'
    ) % (BLUE, icon)


def icon_row(icon, title, text, divider):
    return (
        '<div style="padding:12px 0;%s">'
        '%s<span style="display:inline-block;vertical-align:top;width:calc(100%% - 62px);">'
        '<span style="display:block;font-size:16px;font-weight:800;color:%s;line-height:1.35;">%s</span>'
        '<span style="display:block;font-size:14px;line-height:1.5;color:%s;margin-top:2px;">%s</span>'
        '</span></div>'
    ) % ("border-top:1px solid %s;" % LINE if divider else "", icon_tile(icon), NAVY, e(title), MUTED, e(text))


def button(label, icon, href, bg, fg, border):
    return (
        '<a href="%s" target="_blank" rel="noopener" style="display:inline-block;background-color:%s;'
        'color:%s;border:2px solid %s;border-radius:999px;padding:12px 24px;margin:5px;font-size:15px;'
        'font-weight:800;text-decoration:none;"><i class="fa %s"></i>&#160; %s</a>'
    ) % (e(href), bg, fg, border, icon, e(label))


def cta_buttons(dark=False):
    demo = wa_link("Hello CPA Books, I would like a demo of %s." % TITLE)
    support = wa_link("Hello CPA Books, I need support for %s." % TITLE)
    if dark:
        first = button("Request Demo", "fa-play-circle", demo, "#FFFFFF", NAVY, "#FFFFFF")
        second = button("Contact Us", "fa-envelope-o", "https://cpabooks.org/contactus", NAVY, "#FFFFFF", "#7F95B8")
    else:
        first = button("Request Demo", "fa-play-circle", demo, BLUE, "#FFFFFF", BLUE)
        second = button("Contact Us", "fa-envelope-o", "https://cpabooks.org/contactus", "#FFFFFF", NAVY, LINE)
    third = button("WhatsApp Support", "fa-whatsapp", support, "#25D366", "#FFFFFF", "#25D366")
    return '<div style="text-align:center;">%s%s%s</div>' % (first, second, third)


def proof_block():
    purple = "#7C6BF2"
    gold = "#F5B400"
    cards = "".join([
        _dark_card(
            '<div style="color:%s;font-size:26px;font-weight:800;line-height:1.1;">#1</div>'
            '<div style="color:#FFFFFF;font-size:13px;font-weight:600;margin-top:8px;">Since 2014</div>' % purple
        ),
        _dark_card(
            '<div style="color:%s;font-size:16px;font-weight:800;line-height:1.2;">Trusted in</div>'
            '<div style="color:%s;font-size:11px;font-weight:600;line-height:1.35;margin-top:6px;">'
            'Singapore, Saudi Arabia, Thailand, India, UAE</div>' % (purple, purple)
        ),
        _dark_card(
            '<div style="color:%s;font-size:18px;letter-spacing:2px;line-height:1;">&#9733;&#9733;&#9733;&#9733;&#9733;</div>'
            '<div style="color:#FFFFFF;font-size:13px;font-weight:700;margin-top:8px;">Most Rated</div>' % gold
        ),
        _dark_card(
            '<div style="color:%s;font-size:26px;font-weight:800;line-height:1;">&#8599;</div>'
            '<div style="color:#FFFFFF;font-size:13px;font-weight:700;margin-top:8px;">Most Selling</div>' % purple
        ),
        _dark_card(
            '<div style="color:#FFFFFF;font-size:22px;font-weight:800;line-height:1;">odoo</div>'
            '<div style="margin-top:8px;"><span style="display:inline-block;background-color:%s;color:#1A1400;'
            'font-size:11px;font-weight:800;border-radius:4px;padding:3px 7px;">Gold Partner</span></div>' % gold
        ),
        _dark_card(
            '<div style="color:%s;font-size:26px;font-weight:800;line-height:1.1;">10K+</div>'
            '<div style="color:#FFFFFF;font-size:13px;font-weight:600;margin-top:8px;">Customers</div>' % purple
        ),
    ])
    return (
        '<div style="background-color:#F4F6F8;border-radius:18px;padding:22px 10px 14px;margin:0 0 22px;">'
        '<h2 style="text-align:center;font-size:30px;font-weight:800;color:#14213D;margin:0 0 14px;">%s</h2>'
        '<table width="100%%" cellpadding="0" cellspacing="0" style="border-collapse:separate;'
        'background-color:#F4F6F8;"><tr>%s</tr></table></div>'
    ) % (e(TITLE), cards)


def intro_block():
    pill = (
        '<span style="display:inline-block;background-color:%s;color:#FFFFFF;border-radius:999px;'
        'padding:5px 14px;font-size:13px;font-weight:700;margin:3px;">%s</span>'
    )
    pills = pill % ("#1AA6A6", "Community") + pill % ("#7A4EA3", "Enterprise") + pill % ("#6D4C9A", "Odoo.sh")
    return (
        '<div style="background-color:#F5F9FF;border:1px solid %s;border-radius:18px;'
        'padding:40px 22px 34px;margin:0 0 30px;text-align:center;">'
        '<div style="margin:0 0 18px;">%s</div>'
        '%s%s'
        '<p style="max-width:720px;margin:0 auto 22px;font-size:17px;line-height:1.7;color:%s;">%s</p>'
        '%s</div>'
    ) % (LINE, pills, kicker("By CPA Books · Accounting", center=True),
         split_heading(TITLE, 1, 42, center=True), MUTED, e(SUMMARY), cta_buttons())


def keys_block():
    cards = "".join(
        '<div style="display:inline-block;width:33.33%%;min-width:260px;vertical-align:top;'
        'box-sizing:border-box;padding:8px;font-size:15px;text-align:left;">'
        '<div style="background-color:#FFFFFF;border:1px solid %s;border-radius:16px;padding:18px 16px;'
        'box-shadow:0 8px 22px rgba(16,42,82,0.06);min-height:112px;">'
        '%s<span style="display:inline-block;vertical-align:top;width:calc(100%% - 62px);">'
        '<span style="display:block;font-size:16px;font-weight:800;color:%s;margin-bottom:3px;">%s</span>'
        '<span style="display:block;font-size:14px;line-height:1.5;color:%s;">%s</span>'
        '</span></div></div>' % (LINE, icon_tile(icon), NAVY, e(title), MUTED, e(text))
        for icon, title, text in KEYS
    )
    return (
        '<div style="padding:14px 0 10px;margin:0 0 10px;">%s%s'
        '<div style="font-size:0;text-align:center;">%s</div></div>'
    ) % (kicker("Key Features", center=True), split_heading("Everything You Need, in One App", 3, 38, center=True), cards)


def feature_block(index, feature):
    reverse = index % 2 == 1
    points = "".join(icon_row(icon, title, text, n > 0) for n, (icon, title, text) in enumerate(feature["points"]))
    copy = (
        '<div style="display:inline-block;width:40%%;min-width:300px;vertical-align:middle;box-sizing:border-box;'
        'padding:10px %s 10px %s;font-size:16px;text-align:left;">'
        '%s<p style="font-size:16px;line-height:1.7;color:%s;margin:0 0 14px;">%s</p>%s</div>'
    ) % ("10px" if reverse else "28px", "28px" if reverse else "10px",
         split_heading(feature["title"], 2, 38),
         MUTED, e(feature["text"]), points)
    media = (
        '<div style="display:inline-block;width:60%%;min-width:300px;vertical-align:middle;box-sizing:border-box;'
        'padding:10px;font-size:16px;">'
        '<div style="background-color:#E4EEFB;border-radius:18px;padding:9px;'
        'box-shadow:0 18px 48px rgba(16,42,82,0.14);">'
        '<img src="%s" alt="%s – %s" style="width:100%%;max-width:100%%;height:auto;display:block;'
        'border:1px solid #D3E0F2;border-radius:13px;background-color:#FFFFFF;"/>'
        '</div></div>'
    ) % (feature["image"], e(TITLE), e(feature["title"]))
    columns = media + copy if reverse else copy + media
    return (
        '<div style="background-color:%s;border:1px solid %s;border-radius:18px;padding:34px 22px;'
        'margin:0 0 22px;"><div style="font-size:0;">%s</div></div>'
    ) % (LIGHT if reverse else "#FFFFFF", "#D6E6FA" if reverse else LINE, columns)


def final_block():
    contact = (
        '<a href="mailto:info@cpabooks.org" style="color:#CFE0F7;font-weight:700;text-decoration:none;margin:0 14px;">'
        '<i class="fa fa-envelope"></i>&#160; info@cpabooks.org</a>'
        '<a href="https://wa.me/%s" target="_blank" rel="noopener" style="color:#CFE0F7;font-weight:700;'
        'text-decoration:none;margin:0 14px;"><i class="fa fa-whatsapp"></i>&#160; +971 56 256 8128</a>'
        '<a href="https://cpabooks.org/contactus" target="_blank" rel="noopener" style="color:#CFE0F7;'
        'font-weight:700;text-decoration:none;margin:0 14px;"><i class="fa fa-globe"></i>&#160; cpabooks.org/contactus</a>'
    ) % WA_NUMBER
    return (
        '<div style="background-color:%s;border-radius:18px;padding:46px 22px 40px;margin:8px 0 22px;'
        'text-align:center;">%s'
        '<h2 style="font-size:38px;line-height:1.2;font-weight:800;color:#FFFFFF;margin:0 0 10px;">Get %s Today</h2>'
        '<p style="font-size:17px;color:#D2E2F7;margin:0 0 22px;">Free for Odoo 14. Other Odoo versions are available on request.</p>'
        '%s<div style="margin-top:22px;font-size:15px;line-height:2;">%s</div></div>'
    ) % (NAVY, kicker("Ready to clean up your books?", color="#A9C9F2", center=True), e(TITLE), cta_buttons(dark=True), contact)


VERSION_TILES = [
    ("14", "#F4EEFF", "#A855F7"),
    ("15", "#EAF6FF", "#0EA5E9"),
    ("16", "#ECFAF1", "#16A34A"),
    ("17", "#FFF7E6", "#F59E0B"),
    ("18", "#FFEEF2", "#F43F5E"),
    ("19", "#F5EEFF", "#9333EA"),
    ("20", "#EAF2FF", "#3B82F6"),
]


def label_pill(text, bg, fg):
    return (
        '<span style="display:inline-block;background-color:%s;color:%s;border-radius:999px;'
        'padding:5px 14px;font-size:12px;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;">%s</span>'
    ) % (bg, fg, e(text))


def contact_card(href, icon, circle, title, detail, bg, border, arrow):
    return (
        '<a href="%s" target="_blank" rel="noopener" style="display:block;background-color:%s;'
        'border:1px solid %s;border-radius:14px;padding:14px 16px;margin:0 0 12px;text-decoration:none;">'
        '<span style="display:inline-block;width:46px;height:46px;line-height:46px;text-align:center;'
        'border-radius:46px;background-color:%s;color:#FFFFFF;font-size:20px;vertical-align:middle;'
        'margin-right:14px;"><i class="fa %s"></i></span>'
        '<span style="display:inline-block;vertical-align:middle;width:calc(100%% - 96px);">'
        '<span style="display:block;font-size:16px;font-weight:800;color:%s;">%s</span>'
        '<span style="display:block;font-size:14px;color:%s;margin-top:2px;">%s</span></span>'
        '<span style="display:inline-block;vertical-align:middle;color:%s;font-size:18px;">'
        '<i class="fa fa-arrow-right"></i></span></a>'
    ) % (e(href), bg, border, circle, icon, NAVY, e(title), MUTED, e(detail), arrow)


def footer_block():
    tiles = "".join(
        '<span style="display:inline-block;width:76px;background-color:%s;border-radius:14px;'
        'padding:12px 4px 10px;margin:4px;text-align:center;box-shadow:0 6px 16px rgba(16,42,82,0.06);">'
        '<span style="display:block;font-size:17px;font-weight:700;color:#7C7B8C;letter-spacing:-0.02em;">odoo</span>'
        '<span style="display:block;font-size:22px;font-weight:800;color:%s;line-height:1.3;">%s</span>'
        '<span style="display:block;width:26px;height:3px;border-radius:3px;background-color:%s;'
        'margin:5px auto 0;"></span></span>' % (bg, NAVY, number, bar)
        for number, bg, bar in VERSION_TILES
    )
    edition = (
        '<span style="display:inline-block;text-align:center;padding:0 14px;border-left:1px solid %s;'
        'color:%s;font-size:12px;"><i class="fa %s" style="display:block;font-size:18px;color:#64748B;'
        'margin-bottom:3px;"></i>%s</span>'
    )
    works = (
        '<div style="background-color:#FFFFFF;border:1px solid %s;border-radius:12px;padding:12px 14px;'
        'margin-top:14px;">'
        '<span style="display:inline-block;vertical-align:middle;margin:4px 0;">'
        '<span style="display:inline-block;width:26px;height:26px;line-height:26px;text-align:center;'
        'border-radius:26px;background-color:%s;color:#FFFFFF;font-size:13px;margin-right:10px;">'
        '<i class="fa fa-check"></i></span>'
        '<span style="font-size:14px;color:#14213D;">Works on <strong style="color:%s;">Community</strong>, '
        '<strong style="color:%s;">Enterprise</strong> and <strong style="color:%s;">Odoo.sh</strong></span></span>'
        '<span style="display:inline-block;vertical-align:middle;float:right;margin:2px 0;">%s%s%s</span>'
        '<span style="display:block;clear:both;"></span></div>'
    ) % (LINE, BLUE, BLUE, BLUE, BLUE,
         edition % (LINE, MUTED, "fa-desktop", "Community"),
         edition % (LINE, MUTED, "fa-building-o", "Enterprise"),
         edition % (LINE, MUTED, "fa-cloud", "Odoo.sh"))
    left = (
        '<div style="display:inline-block;width:62%%;min-width:320px;vertical-align:top;box-sizing:border-box;'
        'padding:6px 24px 6px 6px;font-size:16px;text-align:left;">'
        '%s<h2 style="font-size:32px;line-height:1.2;font-weight:800;color:%s;margin:12px 0 6px;">'
        'Available for Multiple Odoo Versions</h2>'
        '<p style="font-size:15px;color:%s;margin:0 0 14px;">This module is available and fully compatible '
        'with the following Odoo versions.</p><div>%s</div>%s</div>'
    ) % (label_pill("Compatibility", "#E3EDFB", NAVY), NAVY, MUTED, tiles, works)
    right = (
        '<div style="display:inline-block;width:38%%;min-width:300px;vertical-align:top;box-sizing:border-box;'
        'padding:6px 6px 6px 24px;border-left:1px solid %s;font-size:16px;text-align:left;">'
        '<span style="float:right;display:inline-block;width:64px;height:64px;line-height:64px;text-align:center;'
        'border-radius:64px;background-color:#DFEBFB;color:%s;font-size:28px;"><i class="fa fa-headphones"></i></span>'
        '%s<h2 style="font-size:30px;line-height:1.2;font-weight:800;color:%s;margin:12px 0 6px;">Get in Touch</h2>'
        '<p style="font-size:14px;line-height:1.55;color:%s;margin:0 0 16px;">Have any questions about this module?'
        '<br/>Our team is ready to assist you.</p>'
        '<span style="display:block;clear:both;"></span>%s%s</div>'
    ) % (LINE, BLUE, label_pill("Need help?", "#DDF7EC", "#0F9D6B"), NAVY, MUTED,
         contact_card("mailto:info.cpabooks@gmail.com", "fa-envelope", BLUE, "Email Us",
                      "info.cpabooks@gmail.com", "#FFFFFF", "#BFD5F5", BLUE),
         contact_card("https://wa.me/%s" % WA_NUMBER, "fa-whatsapp", "#16A34A", "Chat on WhatsApp",
                      "+971 56 256 8128", "#F2FCF5", "#A7E3BE", "#16A34A"))
    return (
        '<div style="background-color:#F5F9FF;border:1px solid %s;border-radius:18px;padding:26px 22px;'
        'margin:6px 0 4px;box-shadow:0 10px 28px rgba(16,42,82,0.06);"><div style="font-size:0;">%s%s</div></div>'
    ) % (LINE, left, right)


def render():
    body = "".join([
        proof_block(),
        intro_block(),
        keys_block(),
        "".join(feature_block(i, f) for i, f in enumerate(FEATURES)),
        final_block(),
        footer_block(),
    ])
    return (
        '<div style="font-family:%s;color:#14213D;background-color:#FFFFFF;padding:8px 4px 20px;line-height:1.5;">\n'
        '<div style="max-width:1180px;margin:0 auto;">\n%s\n</div>\n</div>\n'
    ) % (FONT, body)


def main():
    TARGET.write_text(render(), encoding="utf-8")
    print("wrote", TARGET.relative_to(ROOT), "bytes", TARGET.stat().st_size)


if __name__ == "__main__":
    main()
