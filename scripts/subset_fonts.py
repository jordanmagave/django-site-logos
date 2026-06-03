#!/usr/bin/env python3
"""Subconjunto de Font Awesome usando fonttools diretamente."""

from __future__ import annotations

from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

FONTS_DIR = Path("static/fonts")
OUT_DIR = Path("static/fonts-subset")

UNICODES = [
    0xF007,
    0xF00C,
    0xF00D,
    0xF054,
    0xF061,
    0xF086,
    0xF08C,
    0xF099,
    0xF09D,
    0xF0E0,
    0xF124,
    0xF133,
    0xF167,
    0xF186,
    0xF232,
    0xF27A,
    0xF39E,
    0xF14F,
    0xF0D7,
    0xF0D8,
    0xF0D9,
    0xF0DA,
    0xF078,
    0xF077,
    0xF053,
    0xF2BD,
]

WEIGHTS = ["fa-solid-900", "fa-regular-400", "fa-light-300", "fa-brands-400"]

total_orig = 0
total_new = 0

print(f"Subconjunto com {len(UNICODES)} codepoints...\n")

for weight in WEIGHTS:
    src = FONTS_DIR / f"{weight}.ttf"
    if not src.exists():
        src = FONTS_DIR / f"{weight}.woff2"
    if not src.exists():
        print(f"  ? {weight}: arquivo nao encontrado")
        continue

    orig_size = src.stat().st_size
    total_orig += orig_size

    try:
        from fontTools.ttLib import TTFont

        font = TTFont(str(src))

        opts = Options()
        opts.flavor = "woff2"
        opts.drop_tables = []
        opts.notdef_outline = True
        opts.recalc_bounds = True
        opts.recalc_timestamp = False
        opts.canonical_order = True

        subsetter = Subsetter(options=opts)
        subsetter.populate(unicodes=UNICODES)
        subsetter.subset(font)

        out_path = OUT_DIR / f"{weight}.woff2"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        font.save(str(out_path))

        new_size = out_path.stat().st_size
        total_new += new_size
        pct = (1 - new_size / orig_size) * 100
        print(f"  ✓ {weight}: {orig_size//1024}KB -> {new_size//1024}KB ({pct:.0f}%)")

    except Exception as e:
        print(f"  ! {weight}: erro: {e}")

css_content = """@font-face {
  font-family: 'Font Awesome 6 Pro';
  font-style: normal;
  font-weight: 900;
  font-display: swap;
  src: url('/static/fonts-subset/fa-solid-900.woff2') format('woff2');
}
@font-face {
  font-family: 'Font Awesome 6 Pro';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/static/fonts-subset/fa-regular-400.woff2') format('woff2');
}
@font-face {
  font-family: 'Font Awesome 6 Pro';
  font-style: normal;
  font-weight: 300;
  font-display: swap;
  src: url('/static/fonts-subset/fa-light-300.woff2') format('woff2');
}
@font-face {
  font-family: 'Font Awesome 6 Brands';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/static/fonts-subset/fa-brands-400.woff2') format('woff2');
}
"""

css_path = OUT_DIR / "fontawesome-subset.css"
css_path.write_text(css_content)
print(f"\nCSS gerado: {css_path}")

if total_orig:
    pct = (1 - total_new / total_orig) * 100
    print(f"Total: {total_orig//1024}KB -> {total_new//1024}KB ({pct:.0f}% economia)")
else:
    print("Nenhum arquivo processado.")
