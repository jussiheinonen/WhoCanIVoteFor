from django.test import TestCase
from django.shortcuts import reverse
from django.conf import settings

settings.USE_I18N = True
settings.LANGUAGE_CODE = "cy"


class TestTranslatedURL(TestCase):
    def test_translated_ams_url(self):
        response = self.client.get(reverse("ams_voting_system_view"))
        self.assertContains(response, "<h2>Y System Aelodau Ychwanegol</h2>")

    def test_fptp_page_url(self):
        response = self.client.get(reverse("fptp_voting_system_view"))
        self.assertContains(response, "<h2>Cyntaf i'r felin (FPTP)</h2>")

    def test_translated_sv_url(self):
        response = self.client.get(reverse("sv_voting_system_view"))
        self.assertContains(response, "<h2>Pleidlais Atodol</h2>")
