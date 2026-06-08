"""
Diagnostic: second-chance careers-page discovery for the no_careers companies.

find_careers_url() only scans the homepage for anchor links (Playwright fallback
only when HTML < 20KB). That misses: careers pages not linked from the homepage,
JS-heavy marketing sites, and ATS embeds on sub-paths. This probe directly tries
common careers paths and scans for ATS signatures, then scores how confident we
are that a careers page actually exists (i.e. discovery just missed it).

Confidence:
  5  ATS embed found (comeet/greenhouse/lever/ashby/getro/workable/smartrecruiters)
  4  a /careers or /jobs path returns 200 with careers-ish content
  3  homepage HTML has a careers anchor (discovery should have caught it)
  2  homepage live (200) but no careers found via httpx (likely JS-rendered)
  1  homepage redirects off-domain / parked / minimal
  0  dead (timeout / 4xx / 5xx / DNS) -> probably defunct, weak candidate

Run: uv run python3 scripts/probe_no_careers.py
Writes full results to /tmp/careers_probe.json and prints the ranked top 50.
"""
import asyncio
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

COMPANIES_FILE = Path("companies.json")
OUT = Path("careers_recovery.json")  # canonical snapshot; queried by scripts/careers_queue.py
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

PATHS = ["/careers", "/careers/", "/jobs", "/jobs/", "/company/careers",
         "/about/careers", "/join-us", "/join", "/careers/jobs", "/career"]
CAREERS_HINT = re.compile(r"career|job|position|hiring|open role|join (our|the) team|we'?re hiring", re.I)
ANCHOR = re.compile(r"""<a[^>]+href=["']([^"']+)["'][^>]*>(.*?)</a>""", re.I | re.S)
CAREERS_HREF = re.compile(r"career|/jobs|/positions|join-us|comeet|greenhouse|lever\.co|ashbyhq|workable", re.I)
ATS_SIG = {
    "comeet": re.compile(r"comeet\.(com|co)", re.I),
    "greenhouse": re.compile(r"greenhouse\.io|boards\.greenhouse", re.I),
    "lever": re.compile(r"jobs\.lever\.co|lever\.co/", re.I),
    "ashby": re.compile(r"ashbyhq\.com|jobs\.ashby", re.I),
    "getro": re.compile(r"getro\.com|jobs\.getro", re.I),
    "workable": re.compile(r"workable\.com|apply\.workable", re.I),
    "smartrecruiters": re.compile(r"smartrecruiters\.com", re.I),
    "comeet_embed": re.compile(r"comeet-embed|data-comeet", re.I),
}


def find_ats(text: str) -> str | None:
    for name, pat in ATS_SIG.items():
        if pat.search(text):
            return name.replace("_embed", "")
    return None


async def probe(client, e: dict) -> dict:
    name, site = e["name"], (e.get("website") or "").strip()
    res = {"name": name, "vc": e.get("source_vc"), "tier": e.get("vc_tier"),
           "website": site, "conf": 0, "careers_url": None, "ats": None, "note": ""}
    if not site:
        res["note"] = "no website"
        return res
    if not site.startswith("http"):
        site = "https://" + site
    try:
        r = await client.get(site, follow_redirects=True)
    except Exception as ex:
        res["note"] = f"dead: {type(ex).__name__}"
        return res
    if r.status_code >= 400:
        res["note"] = f"dead: {r.status_code}"
        return res

    home_host = urlparse(str(r.url)).netloc.replace("www.", "")
    orig_host = urlparse(site).netloc.replace("www.", "")
    html = r.text
    res["conf"] = 2  # live at least

    ats = find_ats(html)
    if ats:
        res.update(conf=5, ats=ats, careers_url=str(r.url), note="ATS embed on homepage")
        return res

    # careers anchor on homepage?
    for m in ANCHOR.finditer(html):
        href, txt = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        if CAREERS_HREF.search(href) or CAREERS_HINT.search(txt):
            res.update(conf=3, careers_url=urljoin(str(r.url), href),
                       note="careers link in homepage HTML")
            break

    # try common careers paths directly
    base = f"{urlparse(str(r.url)).scheme}://{urlparse(str(r.url)).netloc}"
    for p in PATHS:
        try:
            pr = await client.get(base + p, follow_redirects=True)
        except Exception:
            continue
        if pr.status_code != 200:
            continue
        ats = find_ats(pr.text)
        if ats:
            res.update(conf=5, ats=ats, careers_url=str(pr.url), note=f"ATS embed at {p}")
            return res
        if CAREERS_HINT.search(pr.text[:6000]) and res["conf"] < 4:
            res.update(conf=4, careers_url=str(pr.url), note=f"careers content at {p}")

    if res["conf"] == 2 and home_host != orig_host:
        res.update(conf=1, note=f"redirects to {home_host}")
    return res


async def main() -> None:
    rows = json.loads(COMPANIES_FILE.read_text(encoding="utf-8"))
    nc = [e for e in rows if e.get("skip_reason") == "no_careers"]
    print(f"Probing {len(nc)} no_careers companies...")
    sem = asyncio.Semaphore(24)
    results = []
    async with httpx.AsyncClient(headers=HEADERS, timeout=8.0, verify=False) as client:
        async def run(e):
            async with sem:
                try:
                    return await probe(client, e)
                except Exception as ex:
                    return {"name": e["name"], "conf": 0, "note": f"err: {ex}"}
        done = 0
        tasks = [asyncio.ensure_future(run(e)) for e in nc]
        for fut in asyncio.as_completed(tasks):
            results.append(await fut)
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(nc)}")

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    from collections import Counter
    print("\nConfidence distribution:", dict(sorted(Counter(r["conf"] for r in results).items(), reverse=True)))

    ranked = sorted(results, key=lambda r: (-r["conf"], r.get("tier") or 9, r["name"]))
    print("\n=== TOP 50 (most likely to have a findable careers page) ===")
    print(f"{'#':>2}  {'conf':>4} {'tier':>4}  {'company':28} {'found careers/ats':40} note")
    for i, r in enumerate(ranked[:50], 1):
        found = r.get("careers_url") or ""
        print(f"{i:>2}  {r['conf']:>4} {str(r.get('tier') or '?'):>4}  "
              f"{r['name'][:28]:28} {found[:40]:40} {r['note']}")
    print(f"\nFull results: {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
