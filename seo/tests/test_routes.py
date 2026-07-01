from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(ALLOWED_HOSTS=["testserver"])
class ContatoRouteTest(TestCase):
    """A rota canônica é /contato/; /contato_logos/ deve redirecionar 301."""

    def test_contato_name_resolves_to_hyphen_free_slug(self):
        self.assertEqual(reverse("contato"), "/contato/")

    def test_legacy_contato_logos_redirects_301(self):
        resp = self.client.get("/contato_logos/")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp["Location"], "/contato/")
