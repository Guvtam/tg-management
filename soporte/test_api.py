from django.test import SimpleTestCase, override_settings
from django.urls import reverse


class SupportEndpointSecurityTests(SimpleTestCase):
    @override_settings(TG_SUPPORT_API_TOKEN="test-secret")
    def test_missing_token_rejected(self):
        response = self.client.post(reverse("soporte:api_tickets"), data="{}", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    @override_settings(TG_SUPPORT_API_TOKEN="test-secret")
    def test_wrong_token_rejected(self):
        response = self.client.post(reverse("soporte:api_tickets"), data="{}", content_type="application/json", HTTP_AUTHORIZATION="Bearer wrong")
        self.assertEqual(response.status_code, 401)

    @override_settings(TG_SUPPORT_API_TOKEN="test-secret")
    def test_invalid_payload_rejected(self):
        response = self.client.post(reverse("soporte:api_tickets"), data="{}", content_type="application/json", HTTP_AUTHORIZATION="Bearer test-secret")
        self.assertEqual(response.status_code, 422)
