import re
from urllib.parse import urljoin, urlparse

import httpx
from playwright.sync_api import sync_playwright

from ats.utils import HEADERS

CAREERS_PATTERNS = re.compile(
    r"(careers?|jobs?|open.positions?|join.us|work.with.us|we.re.hiring|join-us)",
    re.IGNORECASE,
)
ANCHOR_RE = re.compile(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)

# comeet.com/jobs/{company-name}/{company-uid}  — direct link
COMEET_DIRECT = re.compile(
    r"comeet\.com/jobs/([^/\s\"'?#]+)/([^/\s\"'?#]+)",
    re.IGNORECASE,
)
# comeet.co embedded iframe patterns: jobs-ui-2/{uid}/{token}, jobs-iframe/{uid}/{token}
COMEET_IFRAME = re.compile(
    r"comeet\.co/(?:jobs-ui-2|jobs-iframe|jobs)/([^/\s\"'?#]+)/([^/\s\"'?#]+)",
    re.IGNORECASE,
)
# comeet.co/careers-api/... — API URL embedded directly in page JS
COMEET_API = re.compile(
    r"comeet\.co/careers-api/[^/]+/company/([^/\s\"'?#]+)/positions[?&]token=([A-Fa-f0-9]{20,})",
    re.IGNORECASE,
)
# COMEET.init({...}) — JS-call embed used by many Israeli companies
COMEET_INIT = re.compile(
    r"COMEET[._]init\s*\(\s*\{(?P<body>[^)]{0,2000}?)\}\s*\)",
    re.IGNORECASE | re.DOTALL,
)
COMEET_INIT_TOKEN = re.compile(r"""["']token["']\s*:\s*["']([A-Fa-f0-9]{20,})["']""")
COMEET_INIT_UID   = re.compile(r"""["']company[-_]uid["']\s*:\s*["']([^"']+)["']""")
COMEET_INIT_NAME  = re.compile(r"""["']company[-_]name["']\s*:\s*["']([^"']+)["']""")

# Ashby hosted job boards: jobs.ashbyhq.com/<org_name>
ASHBY_JOBS = re.compile(r"jobs\.ashbyhq\.com/([a-zA-Z0-9_.-]+)", re.IGNORECASE)

# Breezy HR: <slug>.breezy.hr
BREEZY_RE = re.compile(r"([a-zA-Z0-9_-]+)\.breezy\.hr", re.IGNORECASE)

# Workable: apply.workable.com/<slug> in URL or page HTML
WORKABLE_RE = re.compile(r"apply\.workable\.com/([a-zA-Z0-9_-]+)", re.IGNORECASE)

# Lever: jobs.lever.co/<company_slug>
LEVER_JOBS = re.compile(r"jobs\.lever\.co/([a-zA-Z0-9_.-]+)", re.IGNORECASE)

# Teamtailor: <sub>.teamtailor.com (canonical), or career.<domain>.com which is a CNAME alias
TEAMTAILOR_RE = re.compile(r"([a-zA-Z0-9_-]+)\.teamtailor\.com", re.IGNORECASE)
TEAMTAILOR_GENERIC_SUBS = {"app", "api", "www", "support", "blog", "careers", "career", "help"}

# Getro VC job boards: custom domains (careers.viola-group.com) and getro.com subdomains
# The WAF anti-bot response also contains "getro.com", so this catches both cases
GETRO_RE = re.compile(r"getro\.com", re.IGNORECASE)

# TalentBrew (Radancy) careers platform: page assets are served from tbcdn.talentbrew.com/company/<id>
# and job links follow the /job/<city>/<slug>/<org_id>/<job_id> pattern
TALENTBREW_RE = re.compile(r"tbcdn\.talentbrew\.com/company/(\d+)", re.IGNORECASE)
TALENTBREW_JOB_RE = re.compile(r'href="/job/[^"/]+/[^"/]+/\d+/\d+"', re.IGNORECASE)

# Amazon Jobs: amazon.jobs/en/jobs/<id>/...
AMAZON_JOBS_RE = re.compile(r"amazon\.jobs/en/jobs/", re.IGNORECASE)

# Microsoft Careers: jobs.careers.microsoft.com/global/en/job/<id>,
# apply.careers.microsoft.com/careers (new Eightfold PCSX SPA), or either API host.
MICROSOFT_CAREERS_RE = re.compile(
    r"(jobs\.careers\.microsoft\.com/global/en/job/\d+"
    r"|apply\.careers\.microsoft\.com"
    r"|gcsservices\.careers\.microsoft\.com)",
    re.IGNORECASE,
)

# Google Careers (proprietary SPA - no ATS API, HTML-scrape only)
GOOGLE_CAREERS_RE = re.compile(r"google\.com/about/careers/applications/jobs/results", re.IGNORECASE)

# Jobvite: jobs.jobvite.com/<slug>
JOBVITE_RE = re.compile(r"jobs\.jobvite\.com/([a-zA-Z0-9_.-]+)", re.IGNORECASE)
JOBVITE_GENERIC_PATHS = {"api", "static", "assets", "cdn", "favicon-2024.ico"}

# Eightfold AI: <tenant>.eightfold.ai (PayPal, Cisco, Bayer, Hilton, etc.)
EIGHTFOLD_RE = re.compile(r"([a-zA-Z0-9_-]+)\.eightfold\.ai", re.IGNORECASE)
EIGHTFOLD_GENERIC_SUBS = {"www", "api", "app", "static"}

# Greenhouse embed/boards patterns — check JOBBOARDS and EMBED before BOARDS (BOARDS is more general)
GREENHOUSE_JOBBOARDS = re.compile(r"job-boards\.greenhouse\.io/([a-zA-Z0-9_-]+)", re.IGNORECASE)
GREENHOUSE_EMBED = re.compile(r"greenhouse\.io/embed/job_board[?&]for=([a-zA-Z0-9_-]+)", re.IGNORECASE)
GREENHOUSE_BOARDS = re.compile(r"boards\.greenhouse\.io/(?:embed/job_board\?for=)?([a-zA-Z0-9_-]+)", re.IGNORECASE)


def find_careers_url(company_website: str) -> str | None:
    """Fetch company homepage and return the first careers-like link, or None."""
    try:
        resp = httpx.get(company_website, follow_redirects=True, timeout=10, headers=HEADERS)
    except Exception:
        return None

    base = str(resp.url)
    html = resp.text
    for m in ANCHOR_RE.finditer(html):
        href, text = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if CAREERS_PATTERNS.search(href) or CAREERS_PATTERNS.search(text):
            return urljoin(base, href)

    # SPA shell: static HTML has no anchors at all — retry with Playwright
    if len(html) < 20_000 and not re.search(r"<a\s", html, re.IGNORECASE):
        pw_html, pw_url = _fetch_playwright(company_website)
        base = pw_url
        for m in ANCHOR_RE.finditer(pw_html):
            href, text = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if CAREERS_PATTERNS.search(href) or CAREERS_PATTERNS.search(text):
                return urljoin(base, href)

    return None


def _fetch_simple(url: str) -> tuple[str, str]:
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=10, headers=HEADERS)
        return resp.text, str(resp.url)
    except Exception:
        return "", url


def _fetch_playwright(url: str) -> tuple[str, str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=35000)
        except Exception:
            pass  # TimeoutError or nav error — grab whatever DOM we have
        try:
            return page.content(), page.url
        except Exception:
            return "", url
        finally:
            browser.close()


def _extract_comeet_token(comeet_page_html: str) -> str | None:
    """Extract the API token embedded in a Comeet jobs page."""
    m = re.search(r'"token"\s*:\s*"([A-Fa-f0-9]{20,})"', comeet_page_html)
    return m.group(1) if m else None


def detect_ats(careers_url: str) -> tuple[str, dict]:
    """
    Detect the ATS behind a careers page URL.
    Returns (ats_name, params).
      Comeet: {"company_uid": ..., "company_name": ..., "token": ...}
      unknown: {}
    """
    # Fast path: amazon.jobs careers URL — default country to ISR for our use case
    if AMAZON_JOBS_RE.search(careers_url) or "amazon.jobs" in careers_url.lower():
        return "amazon_jobs", {"country_code": "ISR"}

    # Fast path: Microsoft careers SPA or API host — default location to Israel
    if MICROSOFT_CAREERS_RE.search(careers_url):
        return "microsoft_careers", {"location_query": "Israel"}

    # Fast path: Google Careers SPA — HTML-scrape backed puller, no ATS API
    if GOOGLE_CAREERS_RE.search(careers_url):
        return "google_careers", {"location_query": "Israel"}

    # Fast path: <tenant>.eightfold.ai — tenant is the subdomain, default location Israel.
    # Skip generic subdomains (www/api/etc) that aren't real tenants.
    m = EIGHTFOLD_RE.search(careers_url)
    if m and m.group(1).lower() not in EIGHTFOLD_GENERIC_SUBS:
        return "eightfold", {"tenant": m.group(1).lower(), "location_query": "Israel"}

    # Fast path: if the careers URL is itself a direct Comeet jobs link
    m = COMEET_DIRECT.search(careers_url)
    if m:
        company_name, company_uid = m.group(1), m.group(2)
        html, _ = _fetch_simple(careers_url)
        if len(html.strip()) < 500:
            html, _ = _fetch_playwright(careers_url)
        token = _extract_comeet_token(html)
        if token:
            return "comeet", {"company_uid": company_uid, "company_name": company_name, "token": token}

    # General path: fetch the careers page and search for Comeet signatures
    html, final_url = _fetch_simple(careers_url)
    if len(html.strip()) < 500:
        html, final_url = _fetch_playwright(careers_url)

    # Check direct Comeet link in final URL (redirect case)
    m = COMEET_DIRECT.search(final_url)
    if m:
        company_name, company_uid = m.group(1), m.group(2)
        token = _extract_comeet_token(html)
        if token:
            return "comeet", {"company_uid": company_uid, "company_name": company_name, "token": token}

    # Check for Comeet iframe embed in page HTML or final URL
    for text in (html, final_url):
        m = COMEET_IFRAME.search(text)
        if m:
            company_uid, token = m.group(1), m.group(2)
            return "comeet", {"company_uid": company_uid, "company_name": "", "token": token}

    # Check for Comeet careers-api URL directly embedded in page JS
    m = COMEET_API.search(html)
    if m:
        company_uid, token = m.group(1), m.group(2)
        return "comeet", {"company_uid": company_uid, "company_name": "", "token": token}

    # Check for any comeet.com link embedded in the page that we can follow
    m = COMEET_DIRECT.search(html)
    if m:
        company_name, company_uid = m.group(1), m.group(2)
        comeet_url = f"https://www.comeet.com/jobs/{company_name}/{company_uid}"
        comeet_html, _ = _fetch_simple(comeet_url)
        if len(comeet_html.strip()) < 500:
            comeet_html, _ = _fetch_playwright(comeet_url)
        token = _extract_comeet_token(comeet_html)
        if token:
            return "comeet", {"company_uid": company_uid, "company_name": company_name, "token": token}

    # COMEET.init({...}) — JS-call embed pattern used by many Israeli companies
    m = COMEET_INIT.search(html)
    if m:
        body = m.group("body")
        tm = COMEET_INIT_TOKEN.search(body)
        um = COMEET_INIT_UID.search(body)
        nm = COMEET_INIT_NAME.search(body)
        if tm:
            return "comeet", {
                "token": tm.group(1),
                "company_uid": um.group(1) if um else "",
                "company_name": nm.group(1) if nm else "",
            }

    # Check for Greenhouse signatures in page HTML and final URL
    for pattern in (GREENHOUSE_JOBBOARDS, GREENHOUSE_EMBED, GREENHOUSE_BOARDS):
        for text in (html, final_url):
            m = pattern.search(text)
            if m:
                slug = m.group(1)
                return "greenhouse", {"company_slug": slug}

    # gh_jid= in page links — company embeds Greenhouse directly, slug not in static HTML
    if re.search(r"[?&]gh_jid=\d+", html):
        return "greenhouse", {"company_slug": ""}

    # Check for Lever signature in careers URL, final URL, or page HTML
    for text in (careers_url, final_url, html):
        m = LEVER_JOBS.search(text)
        if m:
            return "lever", {"company_slug": m.group(1)}

    # Check for Ashby signature in careers URL, final URL, or page HTML
    for text in (careers_url, final_url, html):
        m = ASHBY_JOBS.search(text)
        if m:
            return "ashby", {"org_name": m.group(1)}

    # Check for Breezy HR signature in careers URL, final URL, or page HTML
    for text in (careers_url, final_url, html):
        m = BREEZY_RE.search(text)
        if m:
            return "breezy", {"company_slug": m.group(1)}

    # Check for Jobvite signature in careers URL, final URL, or page HTML
    for text in (careers_url, final_url, html):
        m = JOBVITE_RE.search(text)
        if m:
            slug = m.group(1)
            if slug not in JOBVITE_GENERIC_PATHS:
                return "jobvite", {"company_slug": slug}

    # Check for Workable signature in careers URL, final URL, or page HTML
    # Covers both apply.workable.com/<slug> direct URLs and custom-domain sites that embed Workable
    for text in (careers_url, final_url, html):
        m = WORKABLE_RE.search(text)
        if m:
            slug = m.group(1)
            # Skip generic Workable paths that are not company slugs
            if slug not in ("api", "j", "static", "assets", "cdn"):
                return "workable", {"company_slug": slug}

    # Check for Eightfold AI signature in final URL or page HTML (redirect/embed case).
    # Skip generic subdomains (www/api/etc) which can appear in script boilerplate.
    for text in (final_url, html):
        for em in EIGHTFOLD_RE.finditer(text):
            sub = em.group(1).lower()
            if sub not in EIGHTFOLD_GENERIC_SUBS:
                return "eightfold", {"tenant": sub, "location_query": "Israel"}

    # Check for Teamtailor signature: <sub>.teamtailor.com in URL or HTML
    # Skip generic subdomains (app/api/www/etc) which appear in page boilerplate but aren't company tenants
    for text in (careers_url, final_url, html):
        for m in TEAMTAILOR_RE.finditer(text):
            sub = m.group(1).lower()
            if sub not in TEAMTAILOR_GENERIC_SUBS:
                return "teamtailor", {"subdomain": sub}

    # Check for Getro signature in URL or page source (the WAF anti-bot response also contains "getro.com")
    for text in (careers_url, final_url, html):
        if GETRO_RE.search(text):
            parsed = urlparse(final_url or careers_url)
            board_host = parsed.netloc or urlparse(careers_url).netloc
            if board_host:
                return "getro", {"board_host": board_host}

    # TalentBrew (Radancy): detect from CDN asset URL or job-link pattern in page HTML
    if TALENTBREW_RE.search(html) or TALENTBREW_JOB_RE.search(html):
        parsed = urlparse(final_url or careers_url)
        host = parsed.netloc or urlparse(careers_url).netloc
        if host:
            return "talentbrew", {"host": host, "facet": "israel"}

    return "unknown", {}
