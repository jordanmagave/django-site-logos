#!/usr/bin/env python3
"""Otimiza imagens do site com Pillow: WebP (q85) + srcset 4 breakpoints.

Uso:
    python scripts/optimize_images.py
    python scripts/optimize_images.py --min-size 100  # só imagens > 100KB
"""

from __future__ import annotations

import argparse
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

IMG_DIR = Path("static/images")
OUT_DIR = Path("static/images-optimized")
QUALITY = 85
BREAKPOINTS = [640, 960, 1280, 1920]
SKIP_EXTS = {".svg", ".gif"}
MIN_SIZE_KB = 50  # ignora imagens menores (icons, shapes)

# ---------------------------------------------------------------------------


def fmt_size(n: int) -> str:
    if n > 1024 * 1024:
        return f"{n / 1024 / 1024:.1f}MB"
    return f"{n // 1024}KB"


def process_one(src: Path, min_size: int, force: bool) -> tuple[str, int, int]:
    """Processa uma imagem: gera WebP + srcset. Retorna (rel, orig_size, new_size)."""
    ext = src.suffix.lower()
    if ext in SKIP_EXTS:
        return (str(src.relative_to(IMG_DIR)), 0, 0)

    orig_size = src.stat().st_size
    if orig_size < min_size * 1024:
        return (str(src.relative_to(IMG_DIR)), orig_size, orig_size)

    out_stem = OUT_DIR / src.relative_to(IMG_DIR).with_suffix("")
    out_stem.parent.mkdir(parents=True, exist_ok=True)

    try:
        im = Image.open(src)
        im = im.convert("RGB") if im.mode in ("RGBA", "P") else im
        w, h = im.size
    except Exception:
        return (str(src.relative_to(IMG_DIR)), orig_size, orig_size)

    total_new = 0

    # WebP principal
    webp_path = out_stem.with_suffix(".webp")
    if force or not webp_path.exists():
        im.save(webp_path, "WEBP", quality=QUALITY, method=6)
    if webp_path.exists():
        total_new += webp_path.stat().st_size

    # Srcset: versões redimensionadas
    for bp in BREAKPOINTS:
        if w <= bp:
            continue
        webp_bp = out_stem.with_name(f"{out_stem.stem}_{bp}").with_suffix(".webp")
        if not (force or not webp_bp.exists()):
            if webp_bp.exists():
                total_new += webp_bp.stat().st_size
            continue
        ratio = bp / w
        new_h = int(h * ratio)
        resized = im.resize((bp, new_h), Image.LANCZOS)
        resized.save(webp_bp, "WEBP", quality=QUALITY, method=6)
        total_new += webp_bp.stat().st_size

    return (str(src.relative_to(IMG_DIR)), orig_size, total_new)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-size", type=int, default=MIN_SIZE_KB, help="Tamanho minimo em KB")
    parser.add_argument("--force", action="store_true", help="Regera mesmo se existir")
    parser.add_argument("--dry-run", action="store_true", help="So mostra o que faria")
    args = parser.parse_args()

    images = sorted(
        Path(r) / f
        for r, _d, fs in os.walk(IMG_DIR)
        for f in fs
        if (Path(r) / f).suffix.lower() not in SKIP_EXTS
    )
    images = [
        p
        for p in images
        if not (OUT_DIR / p.relative_to(IMG_DIR)).with_suffix(".webp").exists() or args.force
    ]
    images = [p for p in images if p.stat().st_size >= args.min_size * 1024 or args.force]

    if args.dry_run:
        for img in images:
            print(f"  {img.relative_to(IMG_DIR)} ({fmt_size(img.stat().st_size)})")
        print(f"\nTotal: {len(images)} imagens a processar")
        return 0

    print(f"Processando {len(images)} imagens (>= {args.min_size}KB)...")

    with ProcessPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        results = pool.map(
            process_one, images, [args.min_size] * len(images), [args.force] * len(images)
        )

    total_orig = 0
    total_new = 0
    processed = 0
    for rel, orig, new in results:
        if orig == new:
            continue
        total_orig += orig
        total_new += new
        processed += 1
        saved_pct = (1 - new / orig) * 100 if orig else 0
        print(f"  ✓ {rel} {fmt_size(orig)} -> {fmt_size(new)} ({saved_pct:.0f}%)")

    if total_orig:
        pct = (1 - total_new / total_orig) * 100
        print(
            f"\nProcessadas: {processed} | Original: {fmt_size(total_orig)} | Otimizado: {fmt_size(total_new)} | Economia: {pct:.0f}%"
        )
    else:
        print("Nada a processar.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
