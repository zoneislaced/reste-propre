import json
import re
import difflib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOWNS_FILE = ROOT / "data" / "towns.json"
CONFIG_FILE = ROOT / "data" / "site_config.json"
TEMPLATE_FILE = ROOT / "templates" / "town-page.html"
INDEX_FILE = ROOT / "index.html"

FEATURED_SLUGS = [
    "cleaning-services-nairobi",
    "cleaning-services-ruiru",
    "cleaning-services-kikuyu",
    "cleaning-services-thika",
    "cleaning-services-mombasa",
    "cleaning-services-nakuru",
]


def strip_html(html_text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html_text)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sync_homepage(towns: list) -> None:
    if not INDEX_FILE.exists():
        return
    html_text = INDEX_FILE.read_text(encoding="utf-8")
    if "<!-- PSEO_TOWNS_START -->" not in html_text or "<!-- PSEO_TOWNS_END -->" not in html_text:
        return

    by_slug = {t["slug"]: t for t in towns}
    featured = [by_slug[s] for s in FEATURED_SLUGS if s in by_slug]

    featured_links = "\n        ".join(
        f'<a href="{t[\"slug\"]}/" class="location-item"><span class="location-index">{i+1:02d}</span><span>{t[\"name\"]}</span><span class="location-arrow">↗</span></a>'
        for i, t in enumerate(featured)
    )
    all_links = "\n          ".join(
        f'<a href="{t[\"slug\"]}/" class="location-item"><span class="location-index">{i+1:02d}</span><span>{t[\"name\"]} <small>({t.get(\"county\", \"\")})</small></span><span class="location-arrow">↗</span></a>'
        for i, t in enumerate(towns)
    )
    towns_block = (
        "<!-- PSEO_TOWNS_START -->\n"
        f"        {featured_links}\n"
        f'        <details class="all-towns-drawer" style="margin-top: 0.75rem;">\n'
        f'          <summary style="cursor: pointer; font-weight: 600; padding: 0.65rem 0; list-style: none;">Browse all {len(towns)} towns across Kenya <span>+</span></summary>\n'
        f'          <div class="all-towns-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 0.4rem; max-height: 360px; overflow-y: auto; padding-top: 0.5rem;">\n'
        f"          {all_links}\n"
        "          </div>\n"
        "        </details>\n"
        "        <!-- PSEO_TOWNS_END -->"
    )
    html_text = re.sub(
        r"<!-- PSEO_TOWNS_START -->.*?<!-- PSEO_TOWNS_END -->",
        towns_block,
        html_text,
        flags=re.DOTALL,
    )

    if "<!-- PSEO_TOWN_SELECT_START -->" in html_text and "<!-- PSEO_TOWN_SELECT_END -->" in html_text:
        opts = "\n              ".join(f'<option value="{t[\"name\"]}">{t[\"name\"]}</option>' for t in towns)
        select_block = (
            "<!-- PSEO_TOWN_SELECT_START -->\n"
            f'            <select name="town" required><option value="">Select town</option>{opts}<option value="Other / Not listed">Other / Not listed</option></select>\n'
            "            <!-- PSEO_TOWN_SELECT_END -->"
        )
        html_text = re.sub(
            r"<!-- PSEO_TOWN_SELECT_START -->.*?<!-- PSEO_TOWN_SELECT_END -->",
            select_block,
            html_text,
            flags=re.DOTALL,
        )

    INDEX_FILE.write_text(html_text, encoding="utf-8")


def main():
    with open(TOWNS_FILE, "r", encoding="utf-8") as f:
        towns = json.load(f)

    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

    domain = config.get("domain", "https://YOUR-DOMAIN-HERE.example").rstrip("/")
    phone = config.get("phone", "0706855633")
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
            "{{meta_title}}": town.get("meta_title", f"Cleaning Services in {name} | EverClean Services"),
            "{{meta_description}}": town.get("meta_description", ""),
            "{{hero_eyebrow}}": town.get("hero_eyebrow", f"CLEANING IN {name.upper()}"),
            "{{hero_headline}}": town.get("hero_headline", f"Cleaning services in {name}."),
            "{{hero_intro}}": town.get("hero_intro", ""),
            "{{property_focus}}": town.get("property_focus", "homes and commercial offices"),
            "{{local_challenge_focus}}": town.get("local_challenge_focus", "everyday dust and upkeep"),
            "{{local_context_heading}}": town.get("local_context_heading", f"Local care in {name} · Consistent Quality. Lasting Cleanliness"),
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

    sync_homepage(towns)

    sitemap_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitemap_urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap_content, encoding="utf-8")

    robots_content = f"User-agent: *\nAllow: /\nSitemap: {domain}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots_content, encoding="utf-8")

    warnings = 0
    for i in range(len(rendered_texts)):
        for j in range(i + 1, len(rendered_texts)):
            if difflib.SequenceMatcher(None, rendered_texts[i][1], rendered_texts[j][1]).quick_ratio() > 0.82:
                ratio = difflib.SequenceMatcher(None, rendered_texts[i][1], rendered_texts[j][1]).ratio()
                if ratio > 0.82:
                    print(f"WARNING: {rendered_texts[i][0]} and {rendered_texts[j][0]} are {ratio:.1%} similar.")
                    warnings += 1

    print(f"Generated {len(towns)} town pages, synced index.html, sitemap.xml, and robots.txt ({warnings} similarity warnings).")


if __name__ == "__main__":
    main()
