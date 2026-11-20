#!/usr/bin/env python3
"""Generate static Reste Propre town pages from data/towns.json."""
import json, re, html
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "templates" / "town-page.html").read_text(encoding="utf-8")
TOWNS = json.loads((ROOT / "data" / "towns.json").read_text(encoding="utf-8"))
CONFIG = json.loads((ROOT / "data" / "site_config.json").read_text(encoding="utf-8"))
OUT = ROOT / ""


def esc(value):
    return html.escape(str(value), quote=True)


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def render(town):
    name, county = town["name"], town["county"]
    slug = town.get("slug") or f"cleaning-services-{slugify(name)}"
    title = f"Cleaning Services in {name} | {CONFIG['business_name']}"
    desc = f"Explore residential and commercial cleaning services in {name}, {county}. Ask {CONFIG['business_name']} about home, deep and office cleaning and request a tailored quote."
    nearby = " · ".join(town["nearby_areas"])
    properties = ", ".join(town["property_types"])
    area_links = "".join(f'<div class="location-item"><span class="location-index">{i:02d}</span><span>{esc(area)}</span><span class="location-arrow">·</span></div>' for i, area in enumerate(town["nearby_areas"], 1))
    other_towns = [item for item in TOWNS if item["name"] != name]
    town_links = "".join(f'<a class="location-item" href="../{esc(item.get("slug") or ("cleaning-services-" + slugify(item["name"])))}/"><span class="location-index">↗</span><span>Cleaning services in {esc(item["name"])}</span><span class="location-arrow">↗</span></a>' for item in other_towns)
    links = area_links + town_links
    faqs = "".join(f'<details><summary>{esc(item["q"])}<span>+</span></summary><p>{esc(item["a"])}</p></details>' for item in town["local_faq"])
    schema = {
        "@context": "https://schema.org", "@type": CONFIG.get("business_type", "CleaningService"),
        "name": CONFIG["business_name"], "areaServed": {"@type": "City", "name": name},
        "url": CONFIG["website_url"].rstrip("/") + "/" + slug + "/",
        "description": desc
    }
    if CONFIG.get("phone"): schema["telephone"] = CONFIG["phone"]
    if CONFIG.get("email"): schema["email"] = CONFIG["email"]
    replacements = {
        "{{META_DESCRIPTION}}": esc(desc), "{{PAGE_TITLE}}": esc(title),
        "{{CANONICAL_URL}}": esc(schema["url"]), "{{SCHEMA}}": json.dumps(schema, ensure_ascii=False).replace("</", "<\\/"),
        "{{TOWN}}": esc(name), "{{TOWN_UPPER}}": esc(name.upper()), "{{COUNTY}}": esc(county),
        "{{LOCAL_INTRO}}": esc(town["local_intro"]), "{{LOCAL_NOTE}}": esc(town["local_note"]),
        "{{PROPERTY_TYPES}}": esc(properties), "{{NEARBY_LINKS}}": links, "{{LOCAL_FAQS}}": faqs,
        "{{PHONE_DISPLAY}}": esc(CONFIG.get("phone") or "Contact details to be confirmed"),
        "{{EMAIL_DISPLAY}}": esc(CONFIG.get("email") or "Email to be confirmed")
    }
    page = TEMPLATE
    for key, value in replacements.items(): page = page.replace(key, value)
    if "{{" in page: raise ValueError(f"Unfilled placeholder in {name}")
    target = OUT / slug / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")
    return slug, re.sub(r"<[^>]+>", " ", page).lower()


def main():
    rendered = [render(t) for t in TOWNS]
    # Compare page text to catch accidentally duplicated location copy.
    warnings = []
    for slug, page_text in rendered:
        word_count = len(page_text.split())
        if word_count < 250: warnings.append(f"SHORT PAGE: {slug} has only {word_count} words")
    for i, (slug_a, text_a) in enumerate(rendered):
        for slug_b, text_b in rendered[i+1:]:
            ratio = SequenceMatcher(None, text_a, text_b).ratio()
            if ratio > 0.82: warnings.append(f"HIGH SIMILARITY: {slug_a} vs {slug_b} ({ratio:.0%})")
    urls = [CONFIG["website_url"].rstrip("/") + "/" + slug + "/" for slug, _ in rendered]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{html.escape(url)}</loc></url>\n" for url in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    domain = CONFIG["website_url"].rstrip("/")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {domain}/sitemap.xml\n", encoding="utf-8")
    print(f"Generated {len(rendered)} town pages:")
    for slug, _ in rendered: print(f" - {slug}/index.html")
    print("Sitemap and robots.txt generated.")
    if warnings:
        print("\nCONTENT WARNINGS:")
        for warning in warnings: print(" - " + warning)
    else: print("\nSimilarity check passed (no pair exceeded 82%).")
    if "YOUR-DOMAIN-HERE" in CONFIG["website_url"]: print("\nACTION REQUIRED: Set the real website_url in data/site_config.json before publishing.")
    if not CONFIG.get("phone") or not CONFIG.get("whatsapp") or not CONFIG.get("email"):
        print("ACTION REQUIRED: Add real contact details in data/site_config.json before launch.")

if __name__ == "__main__": main()
