"""
Maintenance: flag dead-end companies in companies.json with skip_discovery so
refresh_companies.py stops re-running Playwright discovery on them every cycle.

A company is a dead-end (auto-discovery has nothing left to find) when it is:
  - inactive    : acquired / shut down (status=inactive or inactive_reason set)
  - no_website  : no website to discover from
  - unknown_ats : careers page found, but ATS type undetected (custom/unsupported)
  - no_careers  : has a website, but no careers page could be found

These are skipped from auto-discovery. The no_careers set is also exported as a
manual worklist (scripts/build_careers_worklist.py) for hand research.

Entries marked skip_reason=manual_verified are left untouched - those are
careers URLs verified by hand and must not be recomputed/clobbered.

This is authoritative: it recomputes skip status for every entry on each run,
so a company that has since resolved to a real ATS gets un-skipped automatically.

Run: uv run python3 scripts/mark_skips.py [--dry-run]
"""
import argparse
import json
from collections import Counter
from pathlib import Path

COMPANIES_FILE = Path("companies.json")
RESOLVED_NONE = ("", "unknown", None)
MANUAL = "manual_verified"


def _has(v) -> bool:
    return bool(v and str(v).strip())


def classify(entry: dict) -> str | None:
    """Return skip_reason for a dead-end entry, or None if it should re-verify."""
    if entry.get("skip_reason") == MANUAL:
        return MANUAL  # hand-verified, never recompute
    if entry.get("status") == "inactive" or entry.get("inactive_reason"):
        return "inactive"
    if (entry.get("ats") or "").lower() not in RESOLVED_NONE:
        return None  # has a usable ATS - keep re-verifying
    if not _has(entry.get("website")):
        return "no_website"
    if _has(entry.get("careers_url")):
        return "unknown_ats"
    return "no_careers"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would change without writing")
    args = parser.parse_args()

    entries = json.loads(COMPANIES_FILE.read_text(encoding="utf-8"))

    reasons = Counter()
    skipped = unskipped = unchanged = 0
    for e in entries:
        reason = classify(e)
        if reason == MANUAL:
            reasons[MANUAL] += 1
            continue
        was = bool(e.get("skip_discovery"))
        if reason:
            reasons[reason] += 1
            if not was:
                skipped += 1
            else:
                unchanged += 1
            e["skip_discovery"] = True
            e["skip_reason"] = reason
        else:
            if was:
                unskipped += 1
                e.pop("skip_discovery", None)
                e.pop("skip_reason", None)

    total_skip = sum(v for k, v in reasons.items() if k != MANUAL)
    print(f"Total companies: {len(entries)}")
    print(f"Skip set: {total_skip}  " + "  ".join(
        f"{k}={v}" for k, v in sorted(reasons.items())))
    print(f"  newly skipped: {skipped} | un-skipped (now resolved): {unskipped} "
          f"| already skipped: {unchanged}")
    print(f"  re-verifying (resolved ATS): {len(entries) - total_skip - reasons.get(MANUAL, 0)}")

    if args.dry_run:
        print("\n--dry-run: no changes written.")
        return

    COMPANIES_FILE.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved to {COMPANIES_FILE}")


if __name__ == "__main__":
    main()
