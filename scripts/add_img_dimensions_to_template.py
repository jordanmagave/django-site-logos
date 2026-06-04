#!/usr/bin/env python3
"""Add width and height attributes to all <img> tags in templates (CLS fix)."""

import os
import re
import sys

# Map of image src (relative to static/) to (width, height)
KNOWN_DIMS = {
    # Banner
    "images/banner/frente_escola.png": (1000, 666),
    "images/banner/shape/01.webp": (311, 1296),
    "images/banner/shape/06.webp": (288, 238),
    "images/banner/shape/07.webp": (248, 291),
    "images/banner/shape/08.webp": (298, 298),
    "images/banner/shape/10.webp": (268, 287),
    # Brand (PNG reais, templates usam .svg)
    "images/brand/1.png": (140, 60),
    "images/brand/2.png": (140, 60),
    "images/brand/3.png": (140, 60),
    "images/brand/4.png": (140, 60),
    "images/brand/5.png": (140, 60),
    "images/brand/01.svg": (140, 60),
    "images/brand/02.svg": (140, 60),
    "images/brand/03.svg": (140, 60),
    "images/brand/04.svg": (140, 60),
    "images/brand/05.svg": (140, 60),
    "images/brand/21.svg": (140, 60),
    "images/brand/22.svg": (140, 60),
    "images/brand/23.svg": (140, 60),
    "images/brand/24.svg": (140, 60),
    # Testimonials avatars
    "images/testimonials/avatars/familia_3_circulo.png": (60, 60),
    "images/testimonials/avatars/07.png": (60, 60),
    "images/testimonials/avatars/jamily_testem.png": (60, 60),
    "images/testimonials/avatars/paulo_igor_testem.png": (58, 58),
    "images/testimonials/avatars/familia_3.png": (60, 60),
    # Product shapes
    "images/product/shape/01.webp": (311, 1296),
    "images/product/shape/02.webp": (90, 252),
    "images/product/shape/03.webp": (72, 280),
    "images/product/shape/04.webp": (123, 271),
    "images/product/shape/05.webp": (281, 287),
    "images/product/shape/06.webp": (288, 238),
    "images/product/shape/07.webp": (248, 291),
    "images/product/shape/08.webp": (298, 298),
    "images/product/shape/09.webp": (296, 293),
    "images/product/shape/10.webp": (268, 287),
    "images/product/shape/11.webp": (279, 253),
    "images/product/shape/12.webp": (388, 867),
    "images/product/shape/13.webp": (302, 1294),
    "images/product/shape/14.webp": (263, 280),
    "images/product/IMG_6316 (1).jpg": (5829, 3886),
    "images/product/alunos_formatura.JPG": (2400, 1600),
    "images/product/familia_alunos.png": (1248, 832),
    "images/product/fd1_pousada1.png": (1829, 1829),
    "images/product/fd2_pousada1.png": (2713, 2713),
    "images/product/infantil_pousada1.png": (2687, 2687),
    "images/product/integral_karate.png": (1889, 1889),
    "images/product/integral_posada1.png": (3057, 3057),
    "images/product/med_posada1.png": (537, 537),
    "images/product/medio_resultado.JPG": (3328, 2496),
    # Service shapes
    "images/service/shape/01.webp": (311, 1296),
    "images/service/shape/02.webp": (90, 252),
    "images/service/shape/03.webp": (72, 280),
    "images/service/shape/04.webp": (123, 271),
    "images/service/shape/05.webp": (281, 287),
    "images/service/shape/06.webp": (288, 238),
    "images/service/shape/07.webp": (248, 291),
    "images/service/shape/08.webp": (298, 298),
    "images/service/shape/09.webp": (296, 293),
    "images/service/shape/10.webp": (268, 287),
    "images/service/shape/11.webp": (279, 253),
    "images/service/shape/12.webp": (388, 867),
    "images/service/shape/13.webp": (302, 1294),
    "images/service/shape/14.webp": (263, 280),
    "images/service/fd1_experimento.png": (1784, 3416),
    "images/service/integral_banner.png": (2048, 1536),
    "images/service/integral_menino.png": (2214, 2214),
    "images/service/integral_orando.png": (2214, 2214),
    "images/service/med_sas_enem.png": (2768, 2769),
    # Optimized banners
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
    "images-optimized/product/familia_alunos.webp": (1248, 832),
    "images-optimized/about/aluno_formando.webp": (1473, 2210),
    # Optimized services
    "images-optimized/service/criancas_brincando.webp": (1741, 1175),
    "images-optimized/service/pascoa_infantil.webp": (2952, 2214),
    "images-optimized/service/infantil_estudando.webp": (4160, 3121),
    "images-optimized/service/infantil_exercicio.webp": (830, 830),
    "images-optimized/service/caca_tesouro.webp": (830, 830),
    "images-optimized/service/brinquedoteca_comida.webp": (800, 1664),
    "images-optimized/service/fd1_criancas_juntas.webp": (1665, 1248),
    "images-optimized/service/fd1_criancas.webp": (832, 832),
    "images-optimized/service/fd1_visita_utinga.webp": (472, 472),
    "images-optimized/service/fd1_matematica.webp": (774, 774),
    "images-optimized/service/fd1_maker.webp": (880, 880),
    "images-optimized/service/fd1_experimento.webp": (1784, 3416),
    "images-optimized/service/fd2_alunos.webp": (2048, 1357),
    "images-optimized/service/fd2_aluna.webp": (2048, 2048),
    "images-optimized/service/orando_fd2.webp": (1576, 1576),
    "images-optimized/service/fd2_aluno_cartaz.webp": (2047, 2048),
    "images-optimized/service/fd2_professora.webp": (2047, 2048),
    "images-optimized/service/fd2_aluno_maker.webp": (1091, 2048),
    "images-optimized/service/med_cadernao.webp": (2048, 1247),
    "images-optimized/service/med_sas_enem.webp": (2768, 2769),
    "images-optimized/service/med_aluna_prova.webp": (1931, 1931),
    "images-optimized/service/integral_banner.webp": (2048, 1536),
    "images-optimized/service/integral_menino.webp": (2214, 2214),
    "images-optimized/service/integral_orando.webp": (2214, 2214),
    # Gallery thumbnails (600x600)
    **{f"images/gallery/{i:02d}.webp": (600, 600) for i in range(1, 21)},
    # Gallery originals (full size, used in comparacao_imagens)
    **{f"images/gallery/{i:02d}.png": (4160, 4160) for i in [1,2,4,5,6,7,10,12,16,18,19]},
    # Gallery optimized (full size WebP)
    **{f"images-optimized/gallery/{i:02d}.webp": (4160, 4160) for i in [1,2,4,5,6,7,10,12,16,18,19]},
    "images-optimized/gallery/03.webp": (3859, 3859),
    "images-optimized/gallery/08.webp": (4160, 4160),
    "images-optimized/gallery/09.webp": (4160, 4160),
    "images-optimized/gallery/11.webp": (2768, 2768),
    "images-optimized/gallery/13.webp": (3931, 3931),
    "images-optimized/gallery/14.webp": (2768, 2768),
    "images-optimized/gallery/15.webp": (1363, 1363),
    "images-optimized/gallery/17.webp": (2184, 2184),
    "images-optimized/gallery/20.webp": (2768, 2768),
    "images/gallery/foto_aluno_orando.png": (812, 812),
    # Logos (SVG)
    "images/logo/logo-horizontal-colorida-azul.svg": (4500, 1250),
    "images/logo/logo-horizontal-colorida-branca.svg": (4500, 1250),
    "images/logo/logo-1.svg": (4500, 1250),
    "images/logo/logo-one-dark.svg": (4500, 1250),
    # Contact SVGs (viewBox 80x80)
    "images/contact/01.svg": (80, 80),
    "images/contact/02.svg": (80, 80),
    "images/contact/03.svg": (80, 80),
    # Counter SVGs (viewBox 80x80)
    "images/counter/01.svg": (80, 80),
    "images/counter/11.svg": (80, 80),
    "images/counter/12.svg": (80, 80),
    "images/counter/13.svg": (80, 80),
    "images/counter/14.svg": (80, 80),
    # About / FAQ shapes
    "images/about/aluno_formando.jpg": (1473, 2210),
    "images/faq/shape/01.png": (35, 35),
    "images/faq/shape/02.png": (26, 26),
    "images/faq/shape/03.png": (87, 87),
    "images/faq/shape/04.png": (35, 35),
    # Error page
    "images/error.png": (630, 369),
    # Favicon
    "images/fav.png": (25, 25),
    # Product shape PNGs (referenced in templates, WebP equivalents exist)
    "images/product/shape/01.png": (311, 1296),
    "images/product/shape/02.png": (90, 252),
    "images/product/shape/03.png": (72, 280),
    "images/product/shape/04.png": (123, 271),
    # Service shape PNGs (WebP equivalents exist)
    "images/service/shape/02.png": (90, 252),
    "images/service/shape/04.png": (123, 271),
    "images/service/shape/06.png": (288, 238),
    "images/service/shape/10.png": (268, 287),
    "images/service/shape/13.png": (302, 1294),
    "images/service/shape/14.png": (263, 280),
    # Working-process (doesn't exist on disk, estimate 80x80)
    "images/working-process/04.png": (80, 80),
}

# Team photos
for t in ["marcia", "missi", "synnara", "antolila", "thiago", "raquel", "katia", "odazilma", "09", "10", "11", "12", "13", "14", "15", "16"]:
    KNOWN_DIMS[f"images/team/{t}.png"] = (263, 364)


def _static_to_path(src):
    """Convert src attribute to filesystem path relative to static/."""
    src = src.strip("'\"")
    # Handle {% static 'path' %} template tags
    m = re.match(r"\{%\s*static\s+['\"](.+)['\"]\s*%\}", src)
    if m:
        return m.group(1)
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
