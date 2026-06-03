#!/usr/bin/env python3
"""Extrai oportunidades de otimização de cada relatório Lighthouse."""

from __future__ import annotations

import json
import sys
from pathlib import Path

KEY_AUDITS = [
    "unused-css-rules",
    "unused-javascript",
    "render-blocking-resources",
    "uses-responsive-images",
    "offscreen-images",
    "unminified-css",
    "unminified-javascript",
    "uses-optimized-images",
    "uses-webp-images",
    "uses-text-compression",
    "uses-rel-preconnect",
    "server-response-time",
    "uses-rel-preload",
    "font-display",
    "modern-image-formats",
    "duplicated-javascript",
    "legacy-javascript",
]


def main(base_dir: Path) -> None:
    rows: list[tuple[str, str, str, int, int]] = []
    for jp in sorted(base_dir.glob("*.report.json")):
        name = jp.stem.replace(".report", "")
        d = json.loads(jp.read_text())
        audits = d.get("audits", {})
        for key in KEY_AUDITS:
            a = audits.get(key, {})
            score = a.get("score")
            if score is None or score >= 0.9:
                continue
            details = a.get("details", {}) or {}
            ms = int(details.get("overallSavingsMs") or 0)
            kb = int((details.get("overallSavingsBytes") or 0) / 1024)
            if ms == 0 and kb == 0:
                continue
            rows.append((name, key, a.get("title", ""), ms, kb))

    rows.sort(key=lambda r: (r[3] + r[4] * 10), reverse=True)

    print("# Oportunidades por rota (ordenadas por impacto)\n")
    print("| Rota | Audit | Savings ms | Savings KiB |")
    print("|------|-------|-----------:|------------:|")
    for name, key, _title, ms, kb in rows:
        print(f"| {name} | `{key}` | {ms} | {kb} |")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("reports/lighthouse/baseline"))
