#!/usr/bin/env python3
"""Orchestrator: new_jobs.json + profile.md + cv.md → digest.md via Gemini."""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from matcher.gemini_scorer import build_prompt, score_job

load_dotenv()

TIERS = [
    (9, 10, "9–10: Top matches — reach out today"),
    (7, 8, "7–8: Strong fit — worth a closer look"),
    (5, 6, "5–6: Adjacent fit — worth knowing about"),
    (3, 4, "3–4: Tangential"),
]


def main():
    parser = argparse.ArgumentParser(description="Score jobs and write digest.md")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt for first job and exit")
    parser.add_argument("--input", default="new_jobs.json", help="Input jobs JSON file")
    parser.add_argument("--sample", action="store_true", help="Use tests/sample_jobs.json instead")
    parser.add_argument("--include-low", action="store_true", help="Include 0-2 scores in digest")
    args = parser.parse_args()

    input_file = "tests/sample_jobs.json" if args.sample else args.input
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found. Run collect_jobs.py first.", file=sys.stderr)
        sys.exit(1)

    with open(input_file, encoding="utf-8") as f:
        jobs = json.load(f)

    if not jobs:
        print("No jobs to score.")
        return

    profile_md = Path("profile.md").read_text(encoding="utf-8")
    cv_md = Path("cv.md").read_text(encoding="utf-8")

    if args.dry_run:
        print("=== DRY RUN — prompt for first job ===\n")
        print(build_prompt(jobs[0], profile_md, cv_md))
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set in environment.", file=sys.stderr)
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=api_key)

    scored = []
    for i, job in enumerate(jobs, 1):
        label = f"{job.get('company', '?')} — {job.get('title', '?')}"
        result = score_job(job, profile_md, cv_md, client)
        score = result["score"]
        print(f"[{i}/{len(jobs)}] {label}: score={score}")
        scored.append({**job, **result})

    _write_digest(scored, args.include_low)
    print("\nWrote digest.md")


def _write_digest(scored: list[dict], include_low: bool):
    lines = ["# Job Digest\n"]

    tiers_to_show = list(TIERS)
    if include_low:
        tiers_to_show.append((0, 2, "0–2: Low fit"))

    for lo, hi, header in tiers_to_show:
        bucket = [j for j in scored if lo <= j["score"] <= hi]
        if not bucket:
            continue
        bucket.sort(key=lambda j: j["score"], reverse=True)

        lines.append(f"## {header}\n")
        for job in bucket:
            title = job.get("title", "")
            company = job.get("company", "")
            apply_url = job.get("apply_url", "")
            location = job.get("location", "unknown location")
            score = job["score"]
            reasoning = job.get("reasoning", "")
            flags = job.get("flags", [])

            title_link = f"[{title}]({apply_url})" if apply_url else title
            flag_str = f" `{'` `'.join(flags)}`" if flags else ""

            lines.append(f"### **{company}** — {title_link}")
            lines.append(f"**Score:** {score}/10 | **Location:** {location}")
            lines.append(f"**Reasoning:** {reasoning}{flag_str}")
            lines.append("")

    Path("digest.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
