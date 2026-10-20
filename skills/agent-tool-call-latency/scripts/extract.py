#!/usr/bin/env python3
"""Run the harness adapters and write one normalized call record per line (references/SCHEMA.md).

    extract.py --list                         which adapters find data on this machine
    extract.py --out calls.jsonl [--since YYYY-MM-DD] [--only claude-code,codex]
               [--adapter path/to/my_harness.py ...] [--exclude-cwd /bench-runs/ ...]

Built-in adapters live in adapters/; --adapter loads one written for another harness. Reads
harness data read-only and writes only --out.
"""
import argparse
import glob
import importlib.util
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Context, since_ms  # noqa: E402


def load(path):
    name = "adapter_" + os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for attr in ("NAME", "detect", "records"):
        if not hasattr(mod, attr):
            raise SystemExit(f"{path}: an adapter must define {attr} (references/ADAPTERS.md)")
    return mod


def builtin():
    return [load(p) for p in sorted(glob.glob(os.path.join(HERE, "adapters", "*.py"))) if not p.endswith("__init__.py")]


def apply_claims(calls, claims):
    by_session = {c["session"]: c["frontend"] for c in claims if "session" in c}
    by_id = {c["id"]: c["frontend"] for c in claims if "id" in c}
    by_cwd = [(c["cwd"], c["frontend"]) for c in claims if "cwd" in c]
    for call in calls:
        frontend = by_id.get(call["id"]) or by_session.get(call["session"])
        if not frontend:
            frontend = next((f for sub, f in by_cwd if sub in call.get("_cwd", "")), None)
        if frontend and not call["harness"].startswith(frontend):
            call["harness"] = f"{frontend} → {call['agent']}"
            call["claimed"] = True


def dedupe(calls):
    """Resumed and forked sessions copy earlier history into a new file; keep one copy per call,
    preferring the copy a frontend claimed."""
    unique = {}
    for call in calls:
        key = (call["agent"], call["id"], round(call["ts"]))
        if key not in unique or call.get("claimed"):
            unique[key] = call
    return list(unique.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    default_since = (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat()
    ap.add_argument("--since", default=default_since, help="first day to include (UTC), default 30 days ago")
    ap.add_argument("--out", help="calls.jsonl to write")
    ap.add_argument("--only", help="comma-separated adapter names")
    ap.add_argument("--adapter", action="append", default=[], help="extra adapter file")
    ap.add_argument("--exclude-cwd", action="append", default=[], help="drop sessions whose cwd contains this")
    ap.add_argument("--home", default=os.path.expanduser("~"), help=argparse.SUPPRESS)
    ap.add_argument("--list", action="store_true", help="show which adapters find data, then exit")
    args = ap.parse_args()

    ctx = Context(args.home, since_ms(args.since), args.exclude_cwd)
    adapters = builtin() + [load(p) for p in args.adapter]
    if args.only:
        wanted = set(args.only.split(","))
        adapters = [a for a in adapters if a.NAME in wanted]

    if args.list:
        for a in adapters:
            found = a.detect(ctx)
            print(f"{a.NAME:14} {len(found):6} source(s){'  e.g. ' + found[0] if found else ''}")
        return
    if not args.out:
        ap.error("--out is required unless --list is given")

    calls, claims = [], []
    for a in adapters:
        got = list(a.records(ctx))
        calls += got
        if hasattr(a, "claims"):
            claims += list(a.claims(ctx))
        print(f"{a.NAME:14} {len(got):7} calls", file=sys.stderr)
    apply_claims(calls, claims)
    before = len(calls)
    calls = dedupe(calls)
    with open(args.out, "w") as fh:
        for call in calls:
            fh.write(json.dumps({k: v for k, v in call.items() if not k.startswith("_") and k != "claimed"}) + "\n")
    print(f"dropped {before - len(calls)} duplicate copies; {len(calls)} calls since {args.since} -> {args.out}",
          file=sys.stderr)
    for harness, n in Counter(c["harness"] for c in calls).most_common():
        print(f"  {harness:40} {n:7}", file=sys.stderr)


if __name__ == "__main__":
    main()
