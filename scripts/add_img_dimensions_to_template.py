#!/usr/bin/env python3
"""Add width and height attributes to all <img> tags in templates (CLS fix)."""

import os
import re
import sys

# Map of image src (relative to static/) to (width, height)
# Pre-populated from known image dimensions
KNOWN_DIMS = {
    "images/banner/shape/01.webp": (311, 1296),
    "images/banner/shape/06.webp": (288, 238),
    "images/banner/shape/07.webp": (248, 291),
    "images/banner/shape/08.webp": (298, 298),
    "images/banner/shape/10.webp": (268, 287),
    "images/brand/1.png": (140, 60),
    "images/brand/2.png": (140, 60),
    "images/brand/3.png": (140, 60),
    "images/brand/4.png": (140, 60),
    "images/brand/5.png": (140, 60),
    "images/testimonials/avatars/familia_3_circulo.png": (60, 60),
    "images/testimonials/avatars/07.png": (60, 60),
    "images/testimonials/avatars/jamily_testem.png": (60, 60),
    "images/testimonials/avatars/paulo_igor_testem.png": (58, 58),
    "images/testimonials/avatars/familia_3.png": (60, 60),
    "images/product/shape/11.webp": (279, 253),
    "images/service/shape/06.webp": (288, 238),
    "images/service/shape/07.webp": (248, 291),
    "images/service/shape/08.webp": (298, 298),
    "images/service/shape/10.webp": (268, 287),
    "images-optimized/banner/frente_escola.webp": (1000, 666),
    "images-optimized/product/alunos_formatura.webp": (2400, 1600),
    "images-optimized/product/fd1_pousada1.webp": (1829, 1829),
    "images-optimized/product/fd2_pousada1.webp": (2713, 2713),
    "images-optimized/product/infantil_pousada1.webp": (2687, 2687),
    "images-optimized/product/integral_karate.webp": (1889, 1889),
    "images-optimized/product/integral_posada1.webp": (3057, 3057),
    "images-optimized/product/med_posada1.webp": (537, 537),
    "images-optimized/product/medio_resultado.webp": (3328, 2496),
    "images-optimized/product/IMG_6316 (1).webp": (5829, 3886),
}

# Gallery images (600x600)
for i in range(1, 21):
    KNOWN_DIMS[f"images/gallery/{i:02d}.webp"] = (600, 600)
KNOWN_DIMS["images/gallery/foto_aluno_orando.png"] = (600, 600)

# Service images
KNOWN_DIMS["images-optimized/service/criancas_brincando.webp"] = (1741, 1175)
KNOWN_DIMS["images-optimized/service/pascoa_infantil.webp"] = (2952, 2214)
KNOWN_DIMS["images-optimized/service/infantil_estudando.webp"] = (4160, 3121)
KNOWN_DIMS["images-optimized/service/infantil_exercicio.webp"] = (830, 830)
KNOWN_DIMS["images-optimized/service/caca_tesouro.webp"] = (830, 830)
KNOWN_DIMS["images-optimized/service/brinquedoteca_comida.webp"] = (800, 1664)
KNOWN_DIMS["images-optimized/service/fd1_criancas_juntas.webp"] = (1665, 1248)
KNOWN_DIMS["images-optimized/service/fd1_criancas.webp"] = (832, 832)
KNOWN_DIMS["images-optimized/service/fd1_visita_utinga.webp"] = (472, 472)
KNOWN_DIMS["images-optimized/service/fd1_matematica.webp"] = (774, 774)
KNOWN_DIMS["images-optimized/service/fd1_maker.webp"] = (880, 880)
KNOWN_DIMS["images-optimized/service/fd1_experimento.webp"] = (1784, 3416)
KNOWN_DIMS["images-optimized/service/fd2_alunos.webp"] = (2048, 1357)
KNOWN_DIMS["images-optimized/service/fd2_aluna.webp"] = (2048, 2048)
KNOWN_DIMS["images-optimized/service/orando_fd2.webp"] = (1576, 1576)
KNOWN_DIMS["images-optimized/service/fd2_aluno_cartaz.webp"] = (2047, 2048)
KNOWN_DIMS["images-optimized/service/fd2_professora.webp"] = (2047, 2048)
KNOWN_DIMS["images-optimized/service/fd2_aluno_maker.webp"] = (1091, 2048)
KNOWN_DIMS["images-optimized/service/med_cadernao.webp"] = (2048, 1247)
KNOWN_DIMS["images-optimized/service/med_sas_enem.webp"] = (2768, 2769)
KNOWN_DIMS["images-optimized/service/med_aluna_prova.webp"] = (1931, 1931)
KNOWN_DIMS["images-optimized/service/integral_banner.webp"] = (2048, 1536)
KNOWN_DIMS["images-optimized/service/integral_menino.webp"] = (2214, 2214)
KNOWN_DIMS["images/about/aluno_formando.jpg"] = (1473, 2210)

# Also try SVG logos
KNOWN_DIMS["images/logo/logo-horizontal-colorida-azul.svg"] = (4500, 1250)
KNOWN_DIMS["images/logo/logo-horizontal-colorida-branca.svg"] = (4500, 1250)
KNOWN_DIMS["images/logo/logo-1.svg"] = (4500, 1250)
KNOWN_DIMS["images/logo/logo-one-dark.svg"] = (4500, 1250)

# Team photos
for t in ["marcia", "missi", "synnara", "antolila", "thiago", "raquel", "katia", "odazilma"]:
    KNOWN_DIMS[f"images/team/{t}.png"] = (263, 364)


def _static_to_path(src):
    """Convert src attribute to filesystem path relative to static/."""
    src = src.strip("'\"")
    if src.startswith("/static/"):
        return src[len("/static/") :]
    if src.startswith("static/"):
        return src[len("static/") :]
    if src.startswith("\\static\\"):
        return src.replace("\\", "/")[len("/static/") :]
    return src


def add_dims_to_template(template_path, skip_attrs=True):
    """Add width/height to img tags missing them."""
    with open(template_path) as f:
        content = f.read()

    # Match the FULL <img ... > tag (multi-line supported via [^>]*)
    img_re = re.compile(r"<img\s[^>]*>", re.IGNORECASE)

    def _replace_img(match):
        tag = match.group(0)

        # Skip if already has width AND height
        if skip_attrs and "width=" in tag and "height=" in tag:
            return tag

        # Extract src
        src_match = re.search(r'src=(["\'])(.*?)\1', tag)
        if not src_match:
            return tag
        src = src_match.group(2)
        path = _static_to_path(src)

        # Check known dims
        if path in KNOWN_DIMS:
            w, h = KNOWN_DIMS[path]
            # Remove existing width/height if any
            tag = re.sub(r'\s*width\s*=\s*["\'][^"\']*["\']', "", tag)
            tag = re.sub(r'\s*height\s*=\s*["\'][^"\']*["\']', "", tag)
            # Insert before closing >
            tag = tag.rstrip()
            if tag.endswith("/>"):
                tag = tag[:-2] + f' width="{w}" height="{h}" />'
            else:
                tag = tag[:-1] + f' width="{w}" height="{h}" >'
            print(f"  {os.path.basename(template_path)}: Added {w}x{h} to {os.path.basename(src)}")
        else:
            print(f"  {os.path.basename(template_path)}: SKIP (unknown dims) {src}")

        return tag

    result = img_re.sub(_replace_img, content)

    with open(template_path, "w") as f:
        f.write(result)
    return True


if __name__ == "__main__":
    templates = (
        sys.argv[1:]
        if len(sys.argv) > 1
        else [
            "templates/home/index.html",
            "templates/services/servico_infantil.html",
            "templates/services/servico_fundamental1.html",
            "templates/services/servico_fundamental2.html",
            "templates/services/servico_medio.html",
            "templates/services/servico_integral.html",
            "templates/partials/header.html",
            "templates/partials/footer.html",
            "templates/pages/about.html",
            "templates/landing/medio.html",
            "templates/landing/integral.html",
            "templates/pages/privacyPolicy.html",
            "templates/partials/cta_visita.html",
            "templates/partials/progress.html",
        ]
    )
    for tpl in templates:
        if os.path.exists(tpl):
            print(f"Processing {tpl}...")
            add_dims_to_template(tpl)
        else:
            print(f"SKIP (not found): {tpl}")
