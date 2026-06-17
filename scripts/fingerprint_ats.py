"""
Diagnostic: fingerprint the ATS platform behind every company whose careers page
we currently can't classify (ats=unknown with a careers_url). Tells us which
*unsupported* ATSes recur, to prioritize new puller development.

For each company: fetch careers_url (follow redirects), match final URL + HTML
against known ATS signatures, and bucket. Self-hosted sites are sub-classified
(wordpress / nextjs / wix-webflow / unknown).

Run: uv run python3 scripts/fingerprint_ats.py
Writes /tmp/ats_fingerprint.json and prints a ranked summary.
"""
import asyncio
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import httpx

H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

SUPPORTED = {"greenhouse", "comeet", "lever", "ashby", "workable", "workday",
             "breezy", "getro", "teamtailor", "jobvite", "successfactors",
             "eightfold", "talentbrew"}

# platform -> signature regex (checked against final URL + HTML)
SIGS = {
    "greenhouse":      r"greenhouse\.io|boards\.greenhouse|job-boards\.[\w.]*greenhouse",
    "comeet":          r"comeet\.(co|com)",
    "lever":           r"jobs\.lever\.co|//[\w.]*lever\.co",
    "ashby":           r"ashbyhq\.com|jobs\.ashby",
    "workable":        r"workable\.com",
    "workday":         r"myworkdayjobs\.com|wd\d+\.myworkday|\.workday\.com",
    "breezy":          r"breezy\.hr",
    "getro":           r"getro\.(com|co)",
    "teamtailor":      r"teamtailor\.com",
    "jobvite":         r"jobvite\.com",
    "successfactors":  r"successfactors|sapsf|jobs\.sap\.com",
    "eightfold":       r"eightfold\.ai|\.eightfold\.",
    # --- unsupported below ---
    "smartrecruiters": r"smartrecruiters\.com|jobs\.smartrecruiters",
    "hibob":           r"careers\.hibob\.com|\.hibob\.com",
    "rippling":        r"ats\.rippling\.com|app\.rippling\.com/[\w-]+/jobs|rippling\.com/careers",
    "bamboohr":        r"\.bamboohr\.com|bamboohr\.com/(jobs|careers)",
    "recruitee":       r"\.recruitee\.com|recruitee\.com",
    "personio":        r"jobs\.personio|personio\.(com|de)",
    "jazzhr":          r"applytojob\.com|jazz\.co/",
    "icims":           r"icims\.com",
    "taleo":           r"taleo\.net",
    "oracle_hcm":      r"oraclecloud\.com.*(recruit|CandidateExperience)|/hcmUI/CandidateExperience",
    "pinpoint":        r"pinpointhq\.com",
    "wellfound":       r"wellfound\.com|angel\.co",
    "gohire":          r"gohire\.io",
    "join":            r"join\.com/companies",
    "freshteam":       r"freshteam\.com",
    "zoho_recruit":    r"zoho\.(com|eu)/recruit|zohorecruit",
    "ripplematch":     r"ripplematch\.com",
    "notion":          r"notion\.(site|so)",
}
COMPILED = {k: re.compile(v, re.I) for k, v in SIGS.items()}


def classify(final_url: str, html: str) -> str:
    blob = final_url + "\n" + html[:120_000]
    for name, pat in COMPILED.items():
        if pat.search(blob):
            return name
    # self-hosted sub-classification
    if "wp-json" in html or "wp-content" in html:
        return "self_hosted:wordpress"
    if '__NEXT_DATA__' in html:
        return "self_hosted:nextjs"
    if re.search(r"wix\.com|_wixCssStates|webflow", html, re.I):
        return "self_hosted:wix_webflow"
    return "unknown"


async def probe(client, e):
    url = e.get("careers_url")
    try:
        r = await client.get(url, follow_redirects=True)
        if r.status_code >= 400:
            return {"name": e["name"], "platform": f"dead:{r.status_code}", "url": url}
        return {"name": e["name"], "vc": e.get("source_vc"), "tier": e.get("vc_tier"),
                "platform": classify(str(r.url), r.text), "url": url, "final": str(r.url)}
    except Exception as ex:
        return {"name": e["name"], "platform": f"dead:{type(ex).__name__}", "url": url}


async def main():
    rows = json.loads(Path("companies.json").read_text(encoding="utf-8"))
    targets = [e for e in rows if (e.get("ats") or "unknown") == "unknown"
               and e.get("careers_url") and e.get("skip_reason") != "manual_verified"]
    print(f"Fingerprinting {len(targets)} unknown-ATS careers pages...\n")
    sem = asyncio.Semaphore(24)
    results = []
    async with httpx.AsyncClient(headers=H, timeout=8.0, verify=False) as client:
        async def run(e):
            async with sem:
                return await probe(client, e)
        tasks = [asyncio.ensure_future(run(e)) for e in targets]
        done = 0
        for fut in asyncio.as_completed(tasks):
            results.append(await fut)
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(targets)}")

    Path("/tmp/ats_fingerprint.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = Counter(r["platform"] for r in results)
    print("\n=== platform counts (unknown-ATS pool) ===")
    for plat, n in counts.most_common():
        base = plat.split(":")[0]
        tag = "SUPPORTED(detect-miss)" if base in SUPPORTED else (
            "self-hosted" if base == "self_hosted" else
            "dead" if base == "dead" else "UNSUPPORTED")
        print(f"  {n:>4}  {plat:24} {tag}")

    print("\n=== UNSUPPORTED platforms ranked (companies) ===")
    unsup = [(p, n) for p, n in counts.most_common()
             if p.split(":")[0] not in SUPPORTED
             and not p.startswith(("dead", "self_hosted", "unknown"))]
    examples = defaultdict(list)
    for r in results:
        if any(r["platform"] == p for p, _ in unsup):
            examples[r["platform"]].append(r["name"])
    for p, n in unsup:
        print(f"  {n:>4}  {p:18} e.g. {', '.join(examples[p][:5])}")


if __name__ == "__main__":
    asyncio.run(main())
