"""
Vertex Ventures Israel portfolio adapter.

URL: https://www.vertexventures.co.il/portfolio/
Structure: JavaScript-rendered React/Gatsby app with two main display modes:
  1. Carousel (slick-slider) with logo buttons - company name from filename, no links
  2. ProjectWrapper cards - company name from filename, optional external link

Both sections use storyblok CDN for images (a.storyblok.com/f/121246/...).
Company name is derived from image filename since alt attributes are always empty.
"""
import re
from urllib.parse import urlparse, unquote

from playwright.sync_api import sync_playwright

PORTFOLIO_URL = "https://www.vertexventures.co.il/portfolio/"
VERTEX_DOMAIN = "vertexventures.co.il"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}

# Vertex own fund/ecosystem/infra domains to skip
SKIP_DOMAINS = {
    "vertexgrowth.com", "vertexventures.jp", "vertexventures.cn",
    "vertexventures.sg", "vertexventureshc.com", "vertex.vcmdataroom.com",
    "vvus.com", "jobs.vertexventures.co.il", "startupcompass.vertexventures.co.il",
    "lu.ma", "medium.com", "storyblok.com", "img2.storyblok.com",
}

# Regex: words in storyblok filenames indicating noise (not a company logo)
NOISE_RE = re.compile(
    r'\b(whatsapp|screenshot|dsc|copy[\s-]of|ai[\s-]product|ai[\s-]first|'
    r'r[\s-]d|g2m|data[\s-]room|team|office|event|conference|staff|portrait)\b',
    re.IGNORECASE,
)

# Known good company-name stems that need special handling
KNOWN_CORRECTIONS = {
    "d-fend": "D-Fend",
    "navina": "Navina",
    "dot-compliance": "Dot Compliance",
    "cyberark": "CyberArk",
    "solaredge": "SolarEdge",
    "waze": "Waze",
    "axonius": "Axonius",
    "zenity": "Zenity",
    "datarails": "DataRails",
    "anecdotes": "Anecdotes",
    "classiq": "Classiq",
    "apono": "Apono",
    "adaptive": "Adaptive Shield",
    "goapprentice": "Apprentice",
    "atidot": "Atidot",
    "augury": "Augury",
    "base": "Base",
    "visitt": "Visitt",
    "cymbio": "Cymbio",
    "feminai": "Feminai",
    "yotpo": "Yotpo",
    "blink": "Blink",
    "spot": "Spot",
}


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    for s in SOCIAL_DOMAINS | SKIP_DOMAINS | {VERTEX_DOMAIN}:
        if clean == s or clean.endswith("." + s):
            return True
    return False


def _name_from_storyblok_src(src: str) -> str | None:
    """Extract company name from a storyblok image filename."""
    try:
        path = unquote(urlparse(src).path)
        filename = path.rstrip("/").split("/")[-1]
        stem = filename.rsplit(".", 1)[0] if "." in filename else filename

        # Normalize: replace _ with -
        stem = stem.replace("_", "-").lower()

        # Skip UUID/timestamp-named files
        if re.match(r'^\d{10,}', stem):
            return None
        if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}', stem):
            return None

        # Strip leading "NNNpx-" dimension prefix
        stem = re.sub(r'^\d+px-', '', stem)

        # Skip files that start with noise keywords (like "copy-of-own-...")
        if re.match(r'^(copy|own|screenshot|whatsapp|dsc)\b', stem):
            return None

        # Strip descriptor keywords and everything after them
        stem = re.sub(
            r'[-](?:logo|icon|white|black|color|colour|dark|light|blue|green|red|'
            r'highres|highreslogo|rectangle|square|horizontal|vertical|mono|'
            r'transparent|double|secondary|primary|full|compact|stacked|'
            r'brigh|bright|rom|carmel|nav|badge|mark|wordmark|lockup|'
            r'horizontal|default|copy|of|own|rgb|cmyk).*$',
            '',
            stem,
        )

        # Strip trailing version numbers/hashes
        stem = re.sub(r'[-\d]+$', '', stem)
        stem = stem.strip("-_ ")

        if not stem or len(stem) < 2:
            return None

        # Skip generic / noise filenames
        if NOISE_RE.search(stem):
            return None
        if stem in {"logo", "image", "img", "photo", "banner", "hero", "icon",
                    "picture", "bitmap", "asset", "brand", "mark", "dsc",
                    "screenshot", "whatsapp", "stealth", "data", "copy",
                    "vertex-israel-il", "vertex-israel", "vertex"}:
            return None

        # Skip vertex own brand/fund logos
        if stem.startswith("vertex-"):
            return None

        # Check known corrections
        if stem in KNOWN_CORRECTIONS:
            return KNOWN_CORRECTIONS[stem]

        # Title-case from hyphen-separated parts
        parts = stem.split("-")
        return " ".join(p.capitalize() for p in parts if p)
    except Exception:
        return None


def fetch_portfolio() -> list[dict]:
    """Scrape Vertex Ventures Israel portfolio page and return list of {company_name, company_website}."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(PORTFOLIO_URL, wait_until="networkidle", timeout=45000)

            # Scroll to trigger lazy loading
            page.evaluate("""
                async () => {
                    for (let i = 0; i < 20; i++) {
                        window.scrollBy(0, window.innerHeight);
                        await new Promise(r => setTimeout(r, 400));
                    }
                    window.scrollTo(0, 0);
                }
            """)
            page.wait_for_timeout(3000)

            html = page.content()
            browser.close()

        results: list[dict] = []
        seen_name_keys: set[str] = set()
        seen_websites: set[str] = set()

        # --- PASS 1: projectWrapper cards (newer/featured companies) ---
        # These have storyblok logo + optional external link per company
        wrapper_re = re.compile(r'styles-module--projectWrapper--\w+')
        wrapper_positions = [m.start() for m in wrapper_re.finditer(html)]

        for i, pos in enumerate(wrapper_positions):
            next_pos = wrapper_positions[i + 1] if i + 1 < len(wrapper_positions) else pos + 3000
            block = html[pos:next_pos]

            # Must have a storyblok logo image (otherwise it's a tab/filter button)
            img_m = re.search(
                r'src="(https://a\.storyblok\.com/f/121246/[^"]+)"',
                block,
            )
            if not img_m:
                continue

            src = img_m.group(1)
            name = _name_from_storyblok_src(src)
            if not name:
                continue

            name_key = name.lower().replace(" ", "")
            if name_key in seen_name_keys:
                continue
            seen_name_keys.add(name_key)

            # Find external website link in this block
            website = ""
            for m in re.finditer(r'href="(https?://[^"]+)"', block):
                href = m.group(1)
                parsed = urlparse(href)
                netloc = parsed.netloc
                if not netloc or _is_filtered(netloc):
                    continue
                path_parts = [p for p in parsed.path.strip("/").split("/") if p]
                if len(path_parts) > 2:
                    continue
                candidate = f"{parsed.scheme}://{parsed.netloc}"
                if candidate not in seen_websites:
                    website = candidate
                    seen_websites.add(candidate)
                    break

            results.append({"company_name": name, "company_website": website})

        # --- PASS 2: carousel/slider logos (older portfolio) ---
        # These appear in <button class="each__logo__wrapper"> inside the slick-slider
        # No external links, names from storyblok filenames only
        # Find all storyblok images NOT already captured in projectWrappers
        all_storyblok = re.findall(
            r'src="(https://a\.storyblok\.com/f/121246/[^"]+)"',
            html,
        )
        for src in all_storyblok:
            name = _name_from_storyblok_src(src)
            if not name:
                continue
            name_key = name.lower().replace(" ", "")
            if name_key in seen_name_keys:
                continue
            seen_name_keys.add(name_key)
            results.append({"company_name": name, "company_website": ""})

        print(f"Vertex Ventures Israel: found {len(results)} portfolio companies")
        return results

    except Exception as e:
        print(f"Vertex Ventures Israel: error fetching portfolio - {e}")
        return []


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
