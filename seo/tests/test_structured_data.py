import json
import re

from django.test import TestCase, override_settings


JSONLD_RE = re.compile(
    r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
    re.DOTALL,
)

PAGES = {
    "/": "index",
    "/about/": "about",
    "/contato/": "contato",
    "/servicos-educacionais/educacao-infantil": "educacaoInfantil",
    "/servicos-educacionais/ensino-fundamental-1": "ensinoFundamental",
    "/servicos-educacionais/ensino-fundamental-2": "ensinoFundamental2",
    "/servicos-educacionais/ensino-medio": "ensinoMedio",
    "/servicos-educacionais/integral": "ensinoIntegral",
}


@override_settings(ALLOWED_HOSTS=["testserver"])
class StructuredDataTest(TestCase):
    """Cada página deve emitir JSON-LD válido com EducationalOrganization + Breadcrumb."""

    def _graph(self, path):
        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 200, f"{path} -> {resp.status_code}")
        html = resp.content.decode("utf-8")
        blocks = JSONLD_RE.findall(html)
        self.assertTrue(blocks, f"nenhum bloco JSON-LD em {path}")
        # Todos os blocos devem ser JSON válido
        parsed = [json.loads(b) for b in blocks]
        # Retorna o @graph consolidado (achatado de todos os blocos)
        nodes = []
        for p in parsed:
            if "@graph" in p:
                nodes.extend(p["@graph"])
            else:
                nodes.append(p)
        return nodes

    def _types(self, nodes):
        return {n.get("@type") for n in nodes}

    def test_jsonld_is_valid_json_on_every_page(self):
        for path in PAGES:
            self._graph(path)  # já valida json.loads

    def test_every_page_has_educational_organization(self):
        for path in PAGES:
            nodes = self._graph(path)
            self.assertIn(
                "EducationalOrganization",
                self._types(nodes),
                f"sem EducationalOrganization em {path}",
            )

    def test_inner_pages_have_breadcrumb(self):
        for path, name in PAGES.items():
            if name == "index":
                continue
            nodes = self._graph(path)
            crumbs = [n for n in nodes if n.get("@type") == "BreadcrumbList"]
            self.assertTrue(crumbs, f"sem BreadcrumbList em {path}")
            items = crumbs[0]["itemListElement"]
            self.assertGreaterEqual(len(items), 2, f"breadcrumb curto em {path}")
            # primeiro item é a Home, último aponta para o path da página (host canônico)
            self.assertEqual(items[0]["position"], 1)
            self.assertTrue(items[-1]["item"].endswith(path))
            self.assertNotIn("www.", items[-1]["item"])

    def test_home_has_no_breadcrumb(self):
        nodes = self._graph("/")
        self.assertNotIn("BreadcrumbList", self._types(nodes))

    def test_organization_uses_canonical_host(self):
        nodes = self._graph("/about/")
        org = next(n for n in nodes if n.get("@type") == "EducationalOrganization")
        self.assertTrue(org["url"].startswith("https://celogos.com.br"))
        self.assertNotIn("www.", org["url"])
