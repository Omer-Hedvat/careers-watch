"""
Hyperwise Ventures portfolio adapter.

URL: https://hyperwise.vc/portfolio/
Structure: server-side rendered; each company block has a logo image (filename = company name),
           a tagline heading (<h3>), and links to the company website and social profiles.
           The company NAME is in the logo image filename (e.g. "Pontera.png"), not the h3.
"""
import re
from urllib.parse import urlparse, unquote

import httpx

PORTFOLIO_URL = "https://hyperwise.vc/portfolio/"
HYPERWISE_DOMAIN = "hyperwise.vc"

SOCIAL_DOMAINS = {"linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Logo suffixes to strip from filenames
LOGO_SUFFIXES = ["-logo", "_logo", "-Logo", "_Logo", "-white", "-White",
                 "-color", "-Color", "-dark", "-Dark", "-light", "-Light",
                 "-1", "-2", "-3"]


def _is_filtered(netloc: str) -> bool:
    clean = netloc.lower().lstrip("www.")
    for s in SOCIAL_DOMAINS | {HYPERWISE_DOMAIN}:
        if clean == s or clean.endswith("." + s):
            return True
    return False


def _name_from_img_src(src: str) -> str | None:
    """Extract company name from image src URL filename."""
    try:
        path = unquote(urlparse(src).path)
        filename = path.rstrip("/").split("/")[-1]
        stem = filename.rsplit(".", 1)[0] if "." in filename else filename
        if not stem or len(stem) < 2:
            return None

        # Strip @2x / @3x retina suffixes
        stem = re.sub(r'@\d+x$', '', stem)
        # Strip trailing digits that look like version numbers (Logo2, Logo3)
        stem = re.sub(r'(?i)(logo|icon)\d+$', lambda m: m.group(1), stem)
        # Strip known logo suffixes (case-insensitive)
        stem = re.sub(r'(?i)[-_]?(logo|icon|white|color|dark|light|blue|on[-_]white|transparent).*$', '', stem)
        # Strip trailing numbers/dashes from version strings like "01", "-01"
        stem = re.sub(r'[-_]\d+$', '', stem)
        # Strip remaining @Nx if any
        stem = re.sub(r'@\d+x$', '', stem)

        stem = stem.strip("-_ ")
        if not stem or len(stem) < 2:
            return None

        # Skip generic names
        if stem.lower() in {"logo", "image", "img", "photo", "banner", "hero", "icon", "picture", "bitmap"}:
            return None

        return stem.strip()
    except Exception:
        return None


def fetch_portfolio() -> list[dict]:
    """Scrape Hyperwise Ventures portfolio page and return list of {company_name, company_website}."""
    try:
        resp = httpx.get(PORTFOLIO_URL, follow_redirects=True, timeout=30, headers=HEADERS)
        resp.raise_for_status()
        html = resp.text

        # Each company block: logo image followed by links (website + socials).
        # We find all img tags with a src pointing to company logos, then find the
        # nearest following external link (before the next img).
        # Pattern to match: <img ...src="...CompanyName.png"...> ... <a href="https://company.com">

        # Find all img tags with their positions
        img_re = re.compile(
            r'<img\s[^>]*src="([^"]+\.(png|svg|jpg|jpeg|webp))"[^>]*/?>',
            re.IGNORECASE,
        )
        img_matches = list(img_re.finditer(html))

        seen_websites: set[str] = set()
        results: list[dict] = []

        for i, img_m in enumerate(img_matches):
            src = img_m.group(1)
            name = _name_from_img_src(src)
            if not name:
                continue

            # Scan from this img to the next img (or window of 2000 chars)
            block_start = img_m.start()
            block_end = img_matches[i + 1].start() if i + 1 < len(img_matches) else block_start + 2000
            block = html[block_start:block_end]

            website = None
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
                    break

            if website:
                seen_websites.add(website)
                results.append({"company_name": name, "company_website": website})

        print(f"Hyperwise Ventures: found {len(results)} portfolio companies")
        return results

    except Exception as e:
        print(f"Hyperwise Ventures: error fetching portfolio - {e}")
        return []


if __name__ == "__main__":
    import json
    companies = fetch_portfolio()
    print(json.dumps(companies, ensure_ascii=False, indent=2))
