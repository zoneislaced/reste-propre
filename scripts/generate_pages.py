import json
import os
import re
import difflib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOWNS_FILE = ROOT / "data" / "towns.json"
CONFIG_FILE = ROOT / "data" / "site_config.json"
TEMPLATE_FILE = ROOT / "templates" / "town-page.html"


def strip_html(html_text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html_text)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def main():
    with open(TOWNS_FILE, "r", encoding="utf-8") as f:
        towns = json.load(f)

    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

    domain = config.get("domain", "https://YOUR-DOMAIN-HERE.example").rstrip("/")
    phone = config.get("phone", "Contact details coming soon")
    email = config.get("email", "Contact details coming soon")

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    rendered_texts = []
    sitemap_urls = [f"  <url><loc>{domain}/</loc></url>"]

    for town in towns:
        slug = town["slug"]
        name = town["name"]
        county = town.get("county", "")
        areas = town.get("areas_served", [])
        faqs = town.get("faqs", [])

        areas_html = "\n".join(
            f'        <div class="location-item"><span class="location-index">{i+1:02d}</span><span>{area}</span><span class="location-arrow">✳</span></div>'
            for i, area in enumerate(areas)
        )

        faqs_html = "\n".join(
            f'        <details><summary>{item["question"]}<span>+</span></summary><p>{item["answer"]}</p></details>'
            for item in faqs
        )

        replacements = {
            "{{domain}}": domain,
            "{{phone}}": phone,
            "{{email}}": email,
            "{{slug}}": slug,
            "{{name}}": name,
            "{{name_upper}}": name.upper(),
            "{{county}}": county,
            "{{county_upper}}": county.upper(),
            "{{region}}": town.get("region", ""),
            "{{meta_title}}": town.get("meta_title", f"Cleaning Services in {name} | Reste Propre"),
            "{{meta_description}}": town.get("meta_description", ""),
            "{{hero_eyebrow}}": town.get("hero_eyebrow", f"CLEANING IN {name.upper()}"),
            "{{hero_headline}}": town.get("hero_headline", f"Cleaning services in {name}."),
            "{{hero_intro}}": town.get("hero_intro", ""),
            "{{property_focus}}": town.get("property_focus", "homes and commercial offices"),
            "{{local_challenge_focus}}": town.get("local_challenge_focus", "everyday dust and upkeep"),
            "{{local_context_heading}}": town.get("local_context_heading", f"Local care in {name}"),
            "{{local_context_body}}": town.get("local_context_body", ""),
            "{{areas_html}}": areas_html,
            "{{faqs_html}}": faqs_html,
        }

        page_html = template
        for key, val in replacements.items():
            page_html = page_html.replace(key, str(val))

        out_dir = ROOT / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(page_html, encoding="utf-8")

        rendered_texts.append((name, strip_html(page_html)))
        sitemap_urls.append(f"  <url><loc>{domain}/{slug}/</loc></url>")

    # Write sitemap.xml and robots.txt
    sitemap_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitemap_urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap_content, encoding="utf-8")

    robots_content = f"User-agent: *\nAllow: /\nSitemap: {domain}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots_content, encoding="utf-8")

    # Similarity audit
    warnings = 0
    for i in range(len(rendered_texts)):
        for j in range(i + 1, len(rendered_texts)):
            if difflib.SequenceMatcher(None, rendered_texts[i][1], rendered_texts[j][1]).quick_ratio() > 0.82:
                ratio = difflib.SequenceMatcher(None, rendered_texts[i][1], rendered_texts[j][1]).ratio()
                if ratio > 0.82:
                    print(f"WARNING: {rendered_texts[i][0]} and {rendered_texts[j][0]} are {ratio:.1%} similar.")
                    warnings += 1

    print(f"Generated {len(towns)} town pages, sitemap.xml, and robots.txt ({warnings} similarity warnings).")


if __name__ == "__main__":
    main()
