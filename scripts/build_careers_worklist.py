"""
Maintenance: export the "no careers page found" companies as a hand-research
worklist (careers_to_find.md).

These have a website but auto-discovery could not find their careers page, so
they need a human to locate the real careers/ATS URL. Fill the "Careers URL"
column, then feed it back (scripts/import_careers_worklist.py - todo) to run ATS
detection and lock the entry so refresh stops auto-discovering it.

Sorted by VC tier (tier 1 cyber-pure first) so the highest-value companies for
the search are at the top - work top-down and stop when the value drops off.

Run: uv run python3 scripts/build_careers_worklist.py
"""
import json
from pathlib import Path

COMPANIES_FILE = Path("companies.json")
OUTPUT_FILE = Path("careers_to_find.md")
RESOLVED_NONE = ("", "unknown", None)


def _has(v) -> bool:
    return bool(v and str(v).strip())


def is_no_careers(e: dict) -> bool:
    if e.get("status") == "inactive" or e.get("inactive_reason"):
        return False
    if (e.get("ats") or "").lower() not in RESOLVED_NONE:
        return False
    return _has(e.get("website")) and not _has(e.get("careers_url"))


def main() -> None:
    entries = json.loads(COMPANIES_FILE.read_text(encoding="utf-8"))
    rows = [e for e in entries if is_no_careers(e)]
    rows.sort(key=lambda e: (e.get("vc_tier") or 9, e.get("source_vc") or "", e["name"]))

    lines = [
        "# Careers pages to find by hand",
        "",
        f"{len(rows)} companies have a website but auto-discovery could not find a "
        "careers page. Find the real careers/ATS URL and paste it in the last column.",
        "",
        "Sorted by VC tier (tier 1 = cyber-pure, highest priority). Work top-down.",
        "Comeet is the most common Israeli ATS - check there first.",
        "",
        "| # | Company | VC | Tier | Website | Careers URL (fill in) |",
        "|---|---------|----|------|---------|------------------------|",
    ]
    for i, e in enumerate(rows, 1):
        lines.append(
            f"| {i} | {e['name']} | {e.get('source_vc') or ''} | "
            f"{e.get('vc_tier') or ''} | {e.get('website') or ''} |  |"
        )
    lines.append("")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(rows)} companies to {OUTPUT_FILE}")
    by_tier = {}
    for e in rows:
        by_tier[e.get("vc_tier") or "?"] = by_tier.get(e.get("vc_tier") or "?", 0) + 1
    print("By tier: " + "  ".join(f"tier{k}={v}" for k, v in sorted(by_tier.items(), key=str)))


if __name__ == "__main__":
    main()
