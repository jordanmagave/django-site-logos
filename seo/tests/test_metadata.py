from django.test import TestCase, override_settings


PAGES = [
    "/",
    "/about/",
    "/contato/",
    "/servicos-educacionais/educacao-infantil",
    "/servicos-educacionais/ensino-fundamental-1",
    "/servicos-educacionais/ensino-fundamental-2",
    "/servicos-educacionais/ensino-medio",
    "/servicos-educacionais/integral",
]


@override_settings(ALLOWED_HOSTS=["testserver"])
class SeoMetadataTest(TestCase):
    """Cada página deve ter title/description/canonical únicos e no host canônico."""

    def _content(self, path):
        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 200, f"{path} -> {resp.status_code}")
        return resp.content.decode("utf-8")

    def test_titles_are_unique_per_page(self):
        titles = {}
        for path in PAGES:
            html = self._content(path)
            start = html.index("<title>") + len("<title>")
            end = html.index("</title>", start)
            titles[path] = html[start:end].strip()
        self.assertEqual(
            len(set(titles.values())), len(PAGES), f"títulos repetidos: {titles}"
        )

    def test_meta_descriptions_are_unique_per_page(self):
        descs = {}
        for path in PAGES:
            html = self._content(path)
            marker = '<meta\n    name="description"'
            # descrição agora vem de variável; basta que sejam distintas entre páginas
            self.assertIn('name="description"', html)
            # extrai o content da primeira meta description
            idx = html.index('name="description"')
            c_idx = html.index('content="', idx) + len('content="')
            c_end = html.index('"', c_idx)
            descs[path] = html[c_idx:c_end]
        self.assertEqual(
            len(set(descs.values())), len(PAGES), f"descrições repetidas: {descs}"
        )

    def test_canonical_tag_uses_non_www_and_path(self):
        html = self._content("/about/")
        self.assertIn(
            '<link rel="canonical" href="https://celogos.com.br/about/"', html
        )

    def test_canonical_never_www(self):
        for path in PAGES:
            html = self._content(path)
            self.assertNotIn("https://www.celogos.com.br", html, f"www em {path}")
