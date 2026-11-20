# Reste Propre — town-page generator

## What this adds
- `data/towns.json`: town information. Start with Nairobi and Machakos; add one object per town.
- `data/site_config.json`: central business details used by every generated page.
- `templates/town-page.html`: one reusable town page design.
- `scripts/generate_pages.py`: builds one folder/page per town, plus `sitemap.xml` and `robots.txt`.

## Generate pages on Windows
1. Install Python 3 if it is not already installed.
2. Open the `reste_propre_website` folder in VS Code.
3. Open Terminal → New Terminal.
4. Run: `python scripts/generate_pages.py`
5. Open `cleaning-services-nairobi/index.html` or `cleaning-services-machakos/index.html` in Chrome.

## Before publishing
- Replace `YOUR-DOMAIN-HERE.example` in `data/site_config.json` with the real HTTPS domain.
- Add the real phone, WhatsApp number and email. Do not publish invented contact details.
- Verify the actual service areas and local details in `data/towns.json`. The starter neighbourhood/property descriptions are editable draft copy, not proof that services are available there.
- Connect the quote form to a real enquiry destination. It is still a demo form.
- Update the homepage location links to point to the generated pages if your hosting setup requires explicit `.html` paths. The current generated folder URLs work on common static hosts that serve folder `index.html` files.

## Add a town
Copy an existing object in `data/towns.json`, change every field, save, then run the generator again. Give each town its own genuinely useful intro, local FAQs, nearby areas and property context. Do not simply swap the town name in duplicated text.

## Quality check
The generator compares generated page text and warns when two pages are more than 82% similar. This is a simple warning, not a guarantee of SEO quality. Review the pages manually and ensure all local claims are accurate and useful.
