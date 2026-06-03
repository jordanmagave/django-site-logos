#!/usr/bin/env python3
"""Gera página HTML de comparação visual: original vs otimizado."""

from __future__ import annotations

from pathlib import Path

IMG_DIR = Path("static/images")
OPT_DIR = Path("static/images-optimized")
OUTPUT = Path("templates/pages/comparacao_imagens.html")

# Imagens principais usadas nos templates (mais impactantes)
KEY_IMAGES = [
    "banner/frente_escola.png",
    "product/alunos_formatura.JPG",
    "product/IMG_6316 (1).jpg",
    "product/medio_resultado.JPG",
    "product/infantil_pousada1.png",
    "product/fd1_pousada1.png",
    "product/fd2_pousada1.png",
    "product/med_posada1.png",
    "product/integral_posada1.png",
    "product/integral_karate.png",
    "product/familia_alunos.png",
    "about/aluno_formando.jpg",
    "service/med_sas_enem.png",
    "service/fd1_experimento.png",
    "service/integral_banner.png",
    "service/integral_orando.png",
    "service/integral_menino.png",
    "gallery/01.png",
    "gallery/02.png",
    "gallery/04.png",
    "gallery/05.png",
    "gallery/06.png",
    "gallery/07.png",
    "gallery/10.png",
    "gallery/12.png",
    "gallery/16.png",
    "gallery/18.png",
    "gallery/19.png",
]

rows: list[str] = []
for rel in KEY_IMAGES:
    orig = IMG_DIR / rel
    opt = OPT_DIR / Path(rel).with_suffix(".webp")
    if not orig.exists():
        continue
    orig_size = orig.stat().st_size
    opt_size = opt.stat().st_size if opt.exists() else 0
    saved = (1 - opt_size / orig_size) * 100 if opt_size else 0
    rows.append(f"""    <div class="comparison-item">
      <div class="image-pair">
        <div class="image-box original">
          <h3>Original</h3>
          <img src="/static/images/{rel}" alt="Original" loading="lazy" />
          <span class="size">{orig_size // 1024}KB</span>
        </div>
        <div class="image-box optimized">
          <h3>Otimizado</h3>
          <img src="/static/images-optimized/{Path(rel).with_suffix('.webp')}" alt="Otimizado" loading="lazy" />
          <span class="size">{opt_size // 1024}KB ({saved:.0f}% menor)</span>
        </div>
      </div>
    </div>""")

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comparação de Imagens - Original vs Otimizado</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }}
h1 {{ text-align: center; margin-bottom: 30px; color: #333; }}
h2 {{ text-align: center; margin: 20px 0; color: #666; font-weight: normal; }}
.comparison-item {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; overflow: hidden; }}
.image-pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; }}
.image-box {{ padding: 15px; text-align: center; }}
.image-box.original {{ background: #fff5f5; }}
.image-box.optimized {{ background: #f0fff4; }}
.image-box h3 {{ margin-bottom: 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
.image-box img {{ max-width: 100%; height: auto; border-radius: 4px; }}
.size {{ display: block; margin-top: 8px; font-size: 13px; color: #666; }}
.optimized .size {{ color: #2f855a; font-weight: bold; }}
.summary {{ text-align: center; margin: 30px 0; padding: 20px; background: #ebf8ff; border-radius: 8px; }}
.summary h2 {{ color: #2b6cb0; }}
@media (max-width: 768px) {{ .image-pair {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<h1>Comparação Visual — Imagens Otimizadas</h1>
<p style="text-align:center;color:#666;margin-bottom:30px;">WebP qualidade 85 com srcset (640/960/1280/1920px)</p>
<div class="comparison-container">
{chr(10).join(rows)}
</div>
<script>
// Toggle para comparar lado a lado
document.querySelectorAll('.image-pair').forEach(pair => {{
  pair.addEventListener('click', () => {{
    pair.classList.toggle('overlay');
  }});
}});
</script>
</body>
</html>"""

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(html)
print(f"Página de comparação gerada: {OUTPUT}")
print(f"Total de imagens: {len(rows)}")
