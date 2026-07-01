from django.test import TestCase, override_settings


@override_settings(ALLOWED_HOSTS=["celogos.com.br", "www.celogos.com.br", "testserver"])
class CanonicalHostMiddlewareTest(TestCase):
    """www deve redirecionar 301 para o host canônico sem www, em https."""

    def test_www_redirects_301_to_non_www_https(self):
        resp = self.client.get(
            "/about/?utm_source=x", HTTP_HOST="www.celogos.com.br"
        )
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(
            resp["Location"], "https://celogos.com.br/about/?utm_source=x"
        )

    def test_www_root_redirects_preserving_nothing_extra(self):
        resp = self.client.get("/", HTTP_HOST="www.celogos.com.br")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp["Location"], "https://celogos.com.br/")

    def test_canonical_host_is_not_redirected(self):
        # host canônico não deve entrar em loop de redirect por causa deste middleware
        resp = self.client.get("/", HTTP_HOST="celogos.com.br")
        self.assertNotEqual(
            resp.get("Location", ""), "https://celogos.com.br/"
        )
