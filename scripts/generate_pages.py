import json, os, re, zipfile

with open("pkg/data/towns.json", "r", encoding="utf-8") as f:
    towns = json.load(f)

with open("pkg/index.html", "r", encoding="utf-8") as f:
    src_html = f.read()

with open("pkg/templates/town-page.html", "r", encoding="utf-8") as f:
    src_tpl = f.read()

phone = "0706855633"
tel_href = "tel:+254706855633"
brand_name = "EverClean Services"
tagline = "Consistent Quality. Lasting Cleanliness"
logo_url = "https://raw.githubusercontent.com/zoneislaced/reste-propre/refs/heads/main/Professionals%20Cleaners%20Service%20Logo%20-%20Made%20with%20PosterMyWall.jpg"

def apply_branding_to_html(html_str: str) -> str:
    h = html_str
    # Title & meta description
    h = h.replace("Reste Propre | A Higher Standard of Clean", f"{brand_name} | {tagline}")
    h = h.replace("Reste Propre", brand_name)
    h = h.replace("reste <b>propre</b>", f"<b>{brand_name}</b>")
    h = h.replace("CLEANING & FACILITIES", tagline)
    h = h.replace("A HIGHER STANDARD OF CLEAN", tagline.upper())
    h = h.replace("Designed with care.", tagline)

    # Logo image in header and footer brands
    logo_img = (
        f'<img src="{logo_url}" alt="{brand_name} logo" '
        f'style="height: 36px; width: auto; border-radius: 6px; object-fit: contain; flex-shrink: 0;">'
    )
    # Replace header brand mark
    h = re.sub(
        r'(<a class="brand"[^>]*>)\s*<span class="brand-mark"[^>]*>.*?</span>',
        r'\1\n      ' + logo_img,
        h,
        count=1,
        flags=re.DOTALL,
    )
    # Replace footer brand mark
    h = re.sub(
        r'(<a class="brand brand-footer"[^>]*>)\s*<span class="brand-mark"[^>]*>.*?</span>',
        r'\1\n        ' + logo_img,
        h,
        count=1,
        flags=re.DOTALL,
    )

    # Update contact details block in #contact
    h = h.replace("<strong>Contact details coming soon</strong>", f'<strong><a href="{tel_href}" style="color: inherit; text-decoration: none;">{phone}</a></strong>')
    h = h.replace("placeholder=\"+254 ...\"", f"placeholder=\"{phone}\"")
    return h

updated_index = apply_branding_to_html(src_html)
with open("pkg/index.html", "w", encoding="utf-8") as f:
    f.write(updated_index)

with open("index_updated.html", "w", encoding="utf-8") as f:
    f.write(updated_index)

# Update town-page.html template too so generated town pages use EverClean Services, tagline, logo, and 0706855633
updated_tpl = apply_branding_to_html(src_tpl)
updated_tpl = updated_tpl.replace("{{phone}}", f'<a href="{tel_href}" style="color: inherit; text-decoration: none;">{phone}</a>')
with open("pkg/templates/town-page.html", "w", encoding="utf-8") as f:
    f.write(updated_tpl)

# Update site_config.json
site_cfg = {
    "domain": "https://YOUR-DOMAIN-HERE.example",
    "phone": phone,
    "email": "Contact details coming soon"
}
os.makedirs("pkg/data", exist_ok=True)
with open("pkg/data/site_config.json", "w", encoding="utf-8") as f:
    json.dump(site_cfg, f, indent=2)

# Update towns.json titles/descriptions/copy referencing Reste Propre
updated_towns = []
for t in towns:
    t_copy = json.loads(json.dumps(t))
    for k, v in list(t_copy.items()):
        if isinstance(v, str):
            t_copy[k] = v.replace("Reste Propre", brand_name)
        elif isinstance(v, list):
            new_list = []
            for item in v:
                if isinstance(item, dict):
                    item = {ik: (iv.replace("Reste Propre", brand_name) if isinstance(iv, str) else iv) for ik, iv in item.items()}
                elif isinstance(item, str):
                    item = item.replace("Reste Propre", brand_name)
                new_list.append(item)
            t_copy[k] = new_list
    updated_towns.append(t_copy)

with open("pkg/data/towns.json", "w", encoding="utf-8") as f:
    json.dump(updated_towns, f, indent=2, ensure_ascii=False)

# Update scripts/generate_pages.py with new defaults & branding
with open("pkg/scripts/generate_pages.py", "r", encoding="utf-8") as f:
    gen_code = f.read()

gen_code = gen_code.replace('phone = config.get("phone", "Contact details coming soon")', f'phone = config.get("phone", "{phone}")')
gen_code = gen_code.replace('f"Cleaning Services in {name} | Reste Propre"', f'f"Cleaning Services in {{name}} | {brand_name}"')
gen_code = gen_code.replace('f"Local care in {name}"', f'f"Local care in {{name}} · {tagline}"')

with open("pkg/scripts/generate_pages.py", "w", encoding="utf-8") as f:
    f.write(gen_code)

zip_v3 = "everclean_services_84_towns_v3.zip"
with zipfile.ZipFile(zip_v3, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write("pkg/index.html", "index.html")
    zf.write("pkg/data/towns.json", "data/towns.json")
    zf.write("pkg/data/site_config.json", "data/site_config.json")
    zf.write("pkg/templates/town-page.html", "templates/town-page.html")
    zf.write("pkg/scripts/generate_pages.py", "scripts/generate_pages.py")

print("Updated v3 bundle:", zip_v3, "Size:", os.path.getsize(zip_v3))
print("Phone present in index_updated.html:", phone in updated_index)
print("Brand present in index_updated.html:", brand_name in updated_index)
print("Tagline present in index_updated.html:", tagline in updated_index)
print("Logo present in index_updated.html:", logo_url in updated_index)
