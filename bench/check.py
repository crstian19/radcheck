"""Independent verification pass (spec §7.5).

Receives ONLY `informe`, with a different prompt and a different model family from the
generator. Items where the checker disagrees with the label go to bench/review.jsonl with the
reason; they are never dropped silently.

    RADCHECK_CHECK_KEY=... python bench/check.py --workers 6
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import threading
from pathlib import Path

import generate as g

BENCH = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--model", default=os.environ.get("RADCHECK_BENCH_CHECK_MODEL"))
    ap.add_argument("--limit", type=int)
    ap.add_argument("--ids", help="comma-separated ids")
    ap.add_argument("--out", help="write reviews here (default: review.jsonl; partial runs never overwrite it)")
    args = ap.parse_args()

    items = [json.loads(line) for line in (BENCH / "raw.jsonl").open(encoding="utf-8") if line.strip()]
    if args.ids:
        wanted = set(args.ids.split(","))
        items = [i for i in items if i["id"] in wanted]
    elif args.limit:
        items = items[: args.limit]

    client = g._client(g.CHECK_BASE_URL, g.CHECK_KEY_VAR)
    system = g._template("checker_system.txt")
    lock = threading.Lock()
    counters = {"agree": 0, "disagree": 0, "failed": 0}

    def one(item: dict):
        user = g._template("checker_user.txt").format(informe=item["informe"])
        for attempt in range(3):
            try:
                return item, g._parse_json(
                    g._chat(client, args.model, system, user, temperature=0.1,
                            seed=g._seed_for(item["id"], attempt))
                ), None
            except Exception as exc:  # noqa: BLE001
                err = str(exc)[:200]
        return item, None, err

    reviews: list[dict] = []
    with cf.ThreadPoolExecutor(args.workers) as pool:
        for n, (item, found, err) in enumerate(pool.map(one, items), 1):
            with lock:
                if found is None:
                    counters["failed"] += 1
                    reviews.append({"id": item["id"], "motivo": "check_failed", "detalle": err})
                else:
                    # Some servers answer with a bare list or wrap it differently.
                    if isinstance(found, list):
                        found = {"incoherencias": found}
                    errs = found.get("incoherencias") or []
                    gold = {e["tipo"] for e in item["errores"]}
                    pred = {e.get("tipo") for e in errs if isinstance(e, dict)}
                    if gold == pred:
                        counters["agree"] += 1
                    else:
                        counters["disagree"] += 1
                        reviews.append({"id": item["id"], "motivo": "check_disagrees",
                                        "gold": sorted(gold), "checker": errs})
                if n % 25 == 0:
                    print(f"{n}/{len(items)} {counters}", flush=True)

    out = Path(args.out) if args.out else (
        BENCH / "review.jsonl" if not (args.ids or args.limit) else BENCH / "review_partial.jsonl"
    )
    out.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in reviews), encoding="utf-8"
    )
    print(json.dumps({**counters, "of": len(items)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
