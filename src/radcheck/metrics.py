"""Score predicted errors against the injected (gold) ones."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from radcheck.inject import ALL_ERROR_TYPES, ERROR_TYPES


def locate(fragment: str, report: str) -> tuple[int, int] | None:
    """Find a predicted fragment in the report, tolerating case and whitespace changes."""
    if not fragment:
        return None
    i = report.find(fragment)
    if i != -1:
        return i, i + len(fragment)
    pattern = r"\s+".join(re.escape(tok) for tok in fragment.split())
    m = re.search(pattern, report, re.IGNORECASE)
    return (m.start(), m.end()) if m else None


def _matches(pred: dict, gold: dict, report: str) -> bool:
    if pred.get("tipo") != gold["tipo"]:
        return False
    span = locate(str(pred.get("fragmento", "")), report)
    if span is not None:
        targets = [(gold["start"], gold["end"])]
        if gold.get("counterpart"):
            targets.append(tuple(gold["counterpart"]))
        return any(span[0] < e and s < span[1] for s, e in targets)
    # Fragment not found verbatim: accept it if it at least contains the changed text.
    changed = report[gold["start"] : gold["end"]].lower()
    return bool(changed) and changed in str(pred.get("fragmento", "")).lower()


@dataclass
class Scores:
    tp: Counter = field(default_factory=Counter)
    fp: Counter = field(default_factory=Counter)
    fn: Counter = field(default_factory=Counter)
    examples: int = 0
    invalid_json: int = 0
    clean: int = 0
    clean_flagged: int = 0
    corrupted: int = 0
    corrupted_flagged: int = 0

    def add(self, report: str, gold: list[dict], pred: list[dict] | None) -> None:
        self.examples += 1
        if pred is None:
            self.invalid_json += 1
            pred = []
        if gold:
            self.corrupted += 1
            self.corrupted_flagged += bool(pred)
        else:
            self.clean += 1
            self.clean_flagged += bool(pred)
        unmatched = list(gold)
        for p in pred:
            hit = next((g for g in unmatched if _matches(p, g, report)), None)
            tipo = p.get("tipo") if p.get("tipo") in ALL_ERROR_TYPES else "otro"
            if hit is None:
                self.fp[tipo] += 1
            else:
                unmatched.remove(hit)
                self.tp[tipo] += 1
        for g in unmatched:
            self.fn[g["tipo"]] += 1

    def summary(self) -> dict:
        def prf(tp: int, fp: int, fn: int) -> dict:
            p = tp / (tp + fp) if tp + fp else 0.0
            r = tp / (tp + fn) if tp + fn else 0.0
            f1 = 2 * p * r / (p + r) if p + r else 0.0
            return {
                "precision": round(p, 3),
                "recall": round(r, 3),
                "f1": round(f1, 3),
                "support": tp + fn,
            }

        # Extended types only appear when the data or the model uses them.
        seen = set(self.tp) | set(self.fp) | set(self.fn)
        types = ERROR_TYPES + tuple(t for t in ALL_ERROR_TYPES[len(ERROR_TYPES) :] if t in seen)
        per_type = {t: prf(self.tp[t], self.fp[t], self.fn[t]) for t in types}
        overall = prf(sum(self.tp.values()), sum(self.fp.values()), sum(self.fn.values()))
        return {
            "examples": self.examples,
            "overall": overall,
            "per_type": per_type,
            "false_alarm_rate": round(self.clean_flagged / self.clean, 3) if self.clean else None,
            "detection_rate": round(self.corrupted_flagged / self.corrupted, 3)
            if self.corrupted
            else None,
            "invalid_json_rate": round(self.invalid_json / self.examples, 3)
            if self.examples
            else None,
        }
