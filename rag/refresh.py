#!/usr/bin/env python3
"""Refresh the RAG store after new_jobs.json / companies.json updates.

Re-runs ingest. Idempotent by content hash: document IDs are sha256 hashes of
document text, so unchanged docs already in the store are skipped and never
re-embedded - only new or changed documents cost quota.

Usage:
    uv run python rag/refresh.py             # full refresh
    uv run python rag/refresh.py --limit 40  # bounded refresh (smoke test)
"""

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.ingest import ingest


def main():
    parser = argparse.ArgumentParser(description="Refresh the RAG vector store.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Refresh only the first N jobs and N companies (smoke test).")
    args = parser.parse_args()
    stats = ingest(limit=args.limit)
    if stats["embedded"] == 0:
        print("[refresh] store is up to date - nothing re-embedded")
    else:
        print(f"[refresh] {stats['embedded']} new/changed documents embedded, "
              f"{stats['skipped']} unchanged skipped")


if __name__ == "__main__":
    main()
