# CPA Books — Odoo Apps Store description prompt

Saved from the design brief used to rebuild `static/description/index.html`.

The attached reference image is the primary visual inspiration. Recreate that design with Odoo Apps Store-compatible HTML and CSS. Do not insert the reference image as the page.

## Objective

Create one modern, premium, reusable Apps Store description for every CPA Books module in this folder. Same typography, palette, spacing, section structure, feature cards, screenshot frames, and support footer. Each module keeps its own title, features, workflow, screenshots, and verified compatibility.

## Structure

1. Hero: CPA Books branding, module name, tagline, short purpose, corporate blue gradient, verified Odoo versions only, existing banner or screenshot.
2. Feature band, image left and text right: rounded screenshot, uppercase label, heading with a highlighted keyword, short copy, 3–4 colored icon points.
3. Feature band, text left and image right, on a pastel blue or lavender background.
4. Keep alternating image/text bands for the major features. Neighbouring sections must not share the same background.
5. Key features: two- or three-column cards with icon, title, short explanation, border, and shadow.
6. How it works: 3 or 4 numbered steps specific to the module.
7. Compatibility: verified Odoo version, useful dependencies, Community/Enterprise only when confirmed. Do not invent compatibility.
8. Why CPA Books: verified company information only. No invented customer counts, ratings, rankings, awards, partnerships, or certifications.
9. Support footer: CPA Books, technical support, info@cpabooks.org, https://www.cpabooks.org, and other contact details only when already verified.

## Visual system

- Navy `#102A52`, primary `#2166C1`, accent `#3B82F6`, light blue `#EAF3FF`, lavender `#F2EDFF`, white `#FFFFFF`, text `#14213D`.
- Rounded corners, soft shadows, gradient section backgrounds, clear separation, readable type.
- No JavaScript, no external CSS, no CDN. Inline CSS only, because Odoo 14 `html_sanitize` removes `<style>` tags.
- Relative image paths. Do not delete screenshots. Do not invent Odoo screenshots. Do not change module code, manifests, or technical names.

## Rebuild

```bash
python3 description_design/build_descriptions.py
```

Previous description HTML is in `description_design/backup/`.
