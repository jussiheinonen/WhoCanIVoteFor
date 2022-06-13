from django.test import TestCase
from django.shortcuts import reverse
from django.test.utils import override_settings


@override_settings(USE_I18N=True, LANGUAGE_CODE="cy")
class TestTranslatedURL(TestCase):
    def test_translated_about_url(self):
        response = self.client.get(reverse("about_view"))
        self.assertContains(
            response,
            "<h1>Ynglŷn â WhoCaniVoteFor</h1>",
        )

    def test_translated_standing_url(self):
        response = self.client.get(reverse("standing_as_a_candidate"))
        self.assertContains(
            response,
            "<h2>Ydych chi’n sefyll etholiad yn y DU? Diweddarwch eich proffil ymgeisydd!</h2>",
        )

    def test_translated_stv(self):
        response = self.client.get(reverse("stv_voting_system_view"))
        self.assertContains(
            response,
            "<h2>Pleidlais Sengl Drosglwyddadwy (PSD)</h2>",
        )
