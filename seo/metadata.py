# seo/metadata.py
"""Metadados de SEO por página, indexados pelo ``url_name`` da rota.

Cada página do site precisa de title/description únicos (o Semrush penaliza
duplicatas). Editar aqui é a forma central de ajustar títulos/descrições sem
tocar em cada template.
"""

DEFAULT_METADATA = {
    "title": "Centro Educacional Logos | Escola Cristã em Ananindeua",
    "description": (
        "Centro Educacional Logos: educação cristã integral em Ananindeua, "
        "da Educação Infantil ao Ensino Médio. Agende uma visita."
    ),
}

SEO_METADATA = {
    "index": {
        "title": "Centro Educacional Logos | Escola Cristã em Ananindeua",
        "description": (
            "Escola cristã em Ananindeua com formação integral da Educação "
            "Infantil ao Ensino Médio. Conheça o Logos e agende uma visita."
        ),
    },
    "about": {
        "title": "Sobre o Logos | Educação Cristã que Transforma",
        "description": (
            "Conheça a história, a proposta pedagógica e os valores cristãos do "
            "Centro Educacional Logos, referência em Ananindeua."
        ),
    },
    "contato": {
        "title": "Agende uma Visita | Centro Educacional Logos",
        "description": (
            "Agende uma visita ao Centro Educacional Logos em Ananindeua. Fale "
            "com nossa equipe e conheça a escola de perto."
        ),
    },
    "educacaoInfantil": {
        "title": "Educação Infantil | Centro Educacional Logos",
        "description": (
            "Educação Infantil no Logos: acolhimento, ludicidade e base cristã "
            "para os primeiros anos, em Ananindeua."
        ),
    },
    "ensinoFundamental": {
        "title": "Ensino Fundamental 1 | Centro Educacional Logos",
        "description": (
            "Ensino Fundamental 1 no Logos: alfabetização sólida e formação de "
            "caráter com valores cristãos, em Ananindeua."
        ),
    },
    "ensinoFundamental2": {
        "title": "Ensino Fundamental 2 | Centro Educacional Logos",
        "description": (
            "Ensino Fundamental 2 no Logos: aprofundamento acadêmico e "
            "protagonismo do aluno com base cristã, em Ananindeua."
        ),
    },
    "ensinoMedio": {
        "title": "Ensino Médio | Centro Educacional Logos",
        "description": (
            "Ensino Médio no Logos: preparação para o vestibular e para a vida, "
            "com excelência acadêmica e valores cristãos, em Ananindeua."
        ),
    },
    "ensinoIntegral": {
        "title": "Ensino Integral | Centro Educacional Logos",
        "description": (
            "Ensino Integral no Logos: jornada ampliada com reforço, atividades "
            "e formação cristã ao longo do dia, em Ananindeua."
        ),
    },
}


def get_metadata(url_name):
    """Retorna o metadado da rota, com fallback para o padrão."""
    data = dict(DEFAULT_METADATA)
    data.update(SEO_METADATA.get(url_name, {}))
    return data
