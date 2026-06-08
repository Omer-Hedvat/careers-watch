"""
Import hand-verified careers/ATS details into companies.json and lock them.

For companies where auto-discovery failed (skip_reason=no_careers) but a human
found the real ATS, this writes the resolved careers_url + ats + ats_params and
marks the entry skip_reason=manual_verified. The lock matters: a manual_verified
entry is never re-discovered by refresh_companies.py (which would otherwise fail
again and clobber the hand-entered values) and is preserved by mark_skips.py.

Reads a JSON list of {name, careers_url, ats, ats_params} from --file, verifies
each ATS actually returns positions, then patches companies.json by name.

Run: uv run python3 scripts/import_careers.py --file /tmp/verified.json [--dry-run]
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ats import ATS_PULLERS

COMPANIES_FILE = Path("companies.json")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True, help="JSON list of verified entries")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    verified = json.loads(Path(args.file).read_text(encoding="utf-8"))
    rows = json.loads(COMPANIES_FILE.read_text(encoding="utf-8"))
    by_name = {e["name"]: e for e in rows}
    now = datetime.now(timezone.utc).isoformat()

    patched = 0
    for v in verified:
        name, ats, params = v["name"], v["ats"], v.get("ats_params", {})
        entry = by_name.get(name)
        if not entry:
            print(f"  {name}: NOT FOUND in companies.json - skipping")
            continue
        # verify the puller actually returns jobs before committing
        try:
            n = len(ATS_PULLERS[ats](params))
        except Exception as e:
            print(f"  {name}: puller failed ({ats}): {e} - NOT importing")
            continue
        print(f"  {name}: {ats} -> {n} positions"
              + (" [dry-run]" if args.dry_run else ""))
        if args.dry_run:
            continue
        entry.update(
            careers_url=v.get("careers_url"),
            ats=ats,
            ats_params=params,
            skip_discovery=True,
            skip_reason="manual_verified",
            consecutive_failures=0,
            last_verified_at=now,
            careers_url_source="manual",
        )
        if v.get("location_filter"):
            entry["location_filter"] = v["location_filter"]
        patched += 1

    if args.dry_run:
        print("\n--dry-run: no changes written.")
        return
    COMPANIES_FILE.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nImported {patched} entries -> {COMPANIES_FILE}")


if __name__ == "__main__":
    main()
