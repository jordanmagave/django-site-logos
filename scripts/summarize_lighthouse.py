#!/usr/bin/env python3
"""Sumariza relatórios Lighthouse de um diretório e gera Markdown comparativo.

Uso:
    python scripts/summarize_lighthouse.py reports/lighthouse/baseline > reports/baseline.md
    python scripts/summarize_lighthouse.py reports/lighthouse/baseline reports/lighthouse/final \
        > reports/comparison.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def metric(report: dict[str, Any], key: str) -> tuple[str, float | None]:
    audit = report.get("audits", {}).get(key, {})
    return audit.get("displayValue", "—"), audit.get("numericValue")


def category(report: dict[str, Any], key: str) -> int | None:
    cat = report.get("categories", {}).get(key, {})
    score = cat.get("score")
    return int(score * 100) if score is not None else None


def summarize_one(dir_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for json_path in sorted(dir_path.glob("*.report.json")):
        name_full = json_path.stem.replace(".report", "")
        if "-" in name_full:
            route, form = name_full.rsplit("-", 1)
        else:
            route, form = name_full, "mobile"
        report = load(json_path)
        rows.append(
            {
                "route": route,
                "form": form,
                "perf": category(report, "performance"),
                "a11y": category(report, "accessibility"),
                "bp": category(report, "best-practices"),
                "seo": category(report, "seo"),
                "fcp": metric(report, "first-contentful-paint"),
                "lcp": metric(report, "largest-contentful-paint"),
                "tbt": metric(report, "total-blocking-time"),
                "cls": metric(report, "cumulative-layout-shift"),
                "si": metric(report, "speed-index"),
                "tti": metric(report, "interactive"),
                "bytes": metric(report, "total-byte-weight"),
            }
        )
    return rows


def fmt_score(s: int | None) -> str:
    if s is None:
        return "—"
    if s >= 90:
        emoji = "🟢"
    elif s >= 50:
        emoji = "🟡"
    else:
        emoji = "🔴"
    return f"{emoji} {s}"


def render(rows: list[dict[str, Any]], label: str) -> str:
    out: list[str] = []
    out.append(f"# Lighthouse — {label}\n")
    out.append("Convenção de cores: 🟢 ≥ 90 (bom) · 🟡 50–89 (precisa melhorar) · 🔴 < 50 (ruim)\n")
    out.append("## Scores\n")
    out.append("| Rota | Form | Perf | A11y | BP | SEO |")
    out.append("|------|------|------|------|----|-----|")
    for r in rows:
        out.append(
            f"| {r['route']} | {r['form']} | {fmt_score(r['perf'])} | "
            f"{fmt_score(r['a11y'])} | {fmt_score(r['bp'])} | {fmt_score(r['seo'])} |"
        )

    out.append("\n## Métricas de performance\n")
    out.append("| Rota | Form | FCP | LCP | TBT | CLS | SI | TTI | Total Bytes |")
    out.append("|------|------|-----|-----|-----|-----|-----|-----|-------------|")
    for r in rows:
        out.append(
            f"| {r['route']} | {r['form']} | {r['fcp'][0]} | {r['lcp'][0]} | "
            f"{r['tbt'][0]} | {r['cls'][0]} | {r['si'][0]} | {r['tti'][0]} | "
            f"{r['bytes'][0]} |"
        )

    # Médias
    def avg_score(field: str, form: str) -> int | None:
        vals = [r[field] for r in rows if r["form"] == form and r[field] is not None]
        return round(sum(vals) / len(vals)) if vals else None

    out.append("\n## Médias por form-factor\n")
    out.append("| Form | Perf | A11y | BP | SEO |")
    out.append("|------|------|------|----|-----|")
    for form in ("mobile", "desktop"):
        out.append(
            f"| {form} | {fmt_score(avg_score('perf', form))} | "
            f"{fmt_score(avg_score('a11y', form))} | "
            f"{fmt_score(avg_score('bp', form))} | "
            f"{fmt_score(avg_score('seo', form))} |"
        )

    return "\n".join(out) + "\n"


def render_comparison(
    base_rows: list[dict[str, Any]], final_rows: list[dict[str, Any]], label: str
) -> str:
    out: list[str] = []
    out.append(f"# Lighthouse — {label} (comparativo)\n")

    def lookup(rows: list[dict[str, Any]], route: str, form: str) -> dict[str, Any] | None:
        for r in rows:
            if r["route"] == route and r["form"] == form:
                return r
        return None

    def delta(a: int | None, b: int | None) -> str:
        if a is None or b is None:
            return "—"
        d = b - a
        sign = "+" if d > 0 else ""
        return f"{sign}{d}"

    out.append("## Performance score (delta = final − baseline)\n")
    out.append("| Rota | Form | Baseline | Final | Δ |")
    out.append("|------|------|----------|-------|---|")
    routes = sorted({r["route"] for r in base_rows})
    for route in routes:
        for form in ("mobile", "desktop"):
            b = lookup(base_rows, route, form)
            f = lookup(final_rows, route, form)
            if not b or not f:
                continue
            out.append(
                f"| {route} | {form} | {fmt_score(b['perf'])} | "
                f"{fmt_score(f['perf'])} | **{delta(b['perf'], f['perf'])}** |"
            )

    out.append("\n## LCP (ms numérico)\n")
    out.append("| Rota | Form | Baseline LCP | Final LCP | Δ ms |")
    out.append("|------|------|--------------|-----------|------|")
    for route in routes:
        for form in ("mobile", "desktop"):
            b = lookup(base_rows, route, form)
            f = lookup(final_rows, route, form)
            if not b or not f:
                continue
            b_lcp = b["lcp"][1]
            f_lcp = f["lcp"][1]
            delta_ms = (
                f"{int(f_lcp - b_lcp):+}" if (b_lcp is not None and f_lcp is not None) else "—"
            )
            out.append(f"| {route} | {form} | {b['lcp'][0]} | {f['lcp'][0]} | **{delta_ms}** |")

    return "\n".join(out) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    base_dir = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        final_dir = Path(sys.argv[2])
        base = summarize_one(base_dir)
        final = summarize_one(final_dir)
        print(render_comparison(base, final, f"{base_dir.name} → {final_dir.name}"))
    else:
        rows = summarize_one(base_dir)
        print(render(rows, base_dir.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
