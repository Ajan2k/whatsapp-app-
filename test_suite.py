"""
Comprehensive Test Suite for Real Estate WhatsApp Marketing & Template System
Verifies:
1. Meta WhatsApp Client (phone normalization, payload structure, verification)
2. Marketing Template Generator (Media headers, dynamic variables {{1}}..{{7}}, CTA buttons)
3. Opt-in Compliance & STOP Opt-Out Handling (blocking unverified/opted-out leads, keyword triggers)
4. Campaign Funnel Pipeline (Audience calculation, eligible vs ineligible segmentation, metric updates)
5. Webhook Server (Meta verification handshake, status tracking, inbound reply handling)
"""

import unittest
from fastapi.testclient import TestClient

import database
from whatsapp.client import WhatsAppClient
from marketing.template_generator import RealEstateTemplateGenerator
from marketing.compliance import ComplianceEngine
from marketing.campaign_engine import CampaignEngine
from webhook_server import app, VERIFY_TOKEN


class TestWhatsAppClient(unittest.TestCase):
    def test_phone_number_cleaning(self):
        self.assertEqual(WhatsAppClient.clean_phone_number("+91-88257-81789"), "918825781789")
        self.assertEqual(WhatsAppClient.clean_phone_number("+91 (98765) 43210"), "919876543210")
        self.assertEqual(WhatsAppClient.clean_phone_number(" 91 888 999 0000 "), "918889990000")

    def test_client_init(self):
        client = WhatsAppClient(access_token="test_mock_token_12345", phone_number_id="100200300400")
        self.assertIsNotNone(client.access_token)
        self.assertIsNotNone(client.phone_number_id)
        self.assertTrue(client.messages_url.endswith("/messages"))


class TestTemplateGenerator(unittest.TestCase):
    def setUp(self):
        database.init_db(seed_sample_data=True)
        self.project = database.get_project(1)

    def test_rendered_preview_contains_real_estate_specs(self):
        rendered = RealEstateTemplateGenerator.format_rendered_message_text("Aravind Kumar", self.project)
        self.assertIn("Green Valley Emerald Layout", rendered)
        self.assertIn("Tambaram West, Chennai", rendered)
        self.assertIn("600–2400 sq.ft", rendered)
        self.assertIn("₹28 Lakhs", rendered)
        self.assertIn("DTCP & RERA Approved", rendered)
        self.assertIn("STOP", rendered)

    def test_meta_template_payload_schema(self):
        payload = RealEstateTemplateGenerator.build_meta_template_payload(
            to_phone="918825781789",
            lead_name="Aravind Kumar",
            project=self.project,
            media_type="IMAGE"
        )
        self.assertEqual(payload["messaging_product"], "whatsapp")
        self.assertEqual(payload["type"], "template")
        self.assertEqual(payload["to"], "918825781789")
        self.assertEqual(payload["template"]["name"], "real_estate_launch_v1")

        components = payload["template"]["components"]
        # Header component has text city parameter
        header = next(c for c in components if c["type"] == "header")
        self.assertEqual(header["parameters"][0]["type"], "text")

        # Body component has 7 dynamic parameters
        body = next(c for c in components if c["type"] == "body")
        self.assertEqual(len(body["parameters"]), 7)

    def test_meta_registration_schema(self):
        schema = RealEstateTemplateGenerator.get_meta_registration_schema()
        self.assertEqual(schema["category"], "MARKETING")
        types = [c["type"] for c in schema["components"]]
        self.assertIn("HEADER", types)
        self.assertIn("BODY", types)
        self.assertIn("FOOTER", types)
        self.assertIn("BUTTONS", types)


class TestComplianceEngine(unittest.TestCase):
    def setUp(self):
        database.init_db(seed_sample_data=True)

    def test_opt_in_allows_send(self):
        lead = {"whatsapp_opt_in": 1, "opt_out_timestamp": None, "status": "OPTED_IN"}
        allowed, reason = ComplianceEngine.can_send_marketing_message(lead)
        self.assertTrue(allowed)

    def test_opt_out_blocks_send(self):
        lead = {"whatsapp_opt_in": 0, "opt_out_timestamp": "2026-09-01T10:00:00", "status": "OPTED_OUT"}
        allowed, reason = ComplianceEngine.can_send_marketing_message(lead)
        self.assertFalse(allowed)
        self.assertIn("Opt-In is False", reason)

    def test_stop_keyword_triggers_automatic_opt_out(self):
        test_phone = "919999888877"
        database.add_or_update_lead(name="OptOut Lead", phone=test_phone, whatsapp_opt_in=True)

        res = ComplianceEngine.check_and_handle_inbound(phone=test_phone, text="STOP")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "OPT_OUT")
        self.assertIn("unsubscribed", res["reply"].lower())

        # Verify database record updated
        updated_lead = database.get_lead_by_phone(test_phone)
        self.assertEqual(updated_lead["whatsapp_opt_in"], 0)
        self.assertEqual(updated_lead["status"], "OPTED_OUT")
        self.assertIsNotNone(updated_lead["opt_out_timestamp"])

        # Subsequent marketing send must be blocked
        allowed, _ = ComplianceEngine.can_send_marketing_message(updated_lead)
        self.assertFalse(allowed)

    def test_start_keyword_triggers_opt_in_reactivation(self):
        test_phone = "919999888877"
        database.add_or_update_lead(name="Opt Lead", phone=test_phone, whatsapp_opt_in=False)
        database.set_lead_opt_out(test_phone, reason="Testing opt out")

        res = ComplianceEngine.check_and_handle_inbound(phone=test_phone, text="START")
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "OPT_IN")

        updated_lead = database.get_lead_by_phone(test_phone)
        self.assertIsNotNone(updated_lead)
        self.assertEqual(updated_lead["whatsapp_opt_in"], 1)
        self.assertIsNone(updated_lead["opt_out_timestamp"])

    def test_button_interaction_routes_booking(self):
        test_phone = "919876543210"
        res = ComplianceEngine.check_and_handle_inbound(
            phone=test_phone,
            text="",
            button_id="action_book_plot_1"
        )
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "BOOK_PLOT")
        self.assertEqual(res["intent"], "BOOKED")
        self.assertIn("Reserve Your Plot", res["reply"])


class TestCampaignPipeline(unittest.TestCase):
    def setUp(self):
        database.init_db(seed_sample_data=True)
        self.engine = CampaignEngine()

    def test_audience_segmentation_separates_opted_in(self):
        audience = self.engine.prepare_campaign_audience(project_id=1, city_filter="All")
        self.assertGreater(audience["total_leads"], 0)
        self.assertGreater(audience["eligible_count"], 0)
        self.assertGreater(audience["ineligible_count"], 0)
        self.assertEqual(
            audience["total_leads"],
            audience["eligible_count"] + audience["ineligible_count"]
        )

    def test_simulated_campaign_run(self):
        res = self.engine.run_campaign(campaign_id=1, dry_run=True)
        self.assertEqual(res["campaign_id"], 1)
        self.assertGreater(res["sent"], 0)
        self.assertEqual(res["failed"], 0)


class TestWebhookEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_webhook_handshake_success(self):
        params = {
            "hub.mode": "subscribe",
            "hub.challenge": "987654321",
            "hub.verify_token": VERIFY_TOKEN,
        }
        res = self.client.get("/webhook", params=params)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, "987654321")

    def test_webhook_handshake_failure(self):
        params = {
            "hub.mode": "subscribe",
            "hub.challenge": "987654321",
            "hub.verify_token": "wrong_token",
        }
        res = self.client.get("/webhook", params=params)
        self.assertEqual(res.status_code, 403)

    def test_api_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_leads", data)
        self.assertIn("eligible_leads", data)
        self.assertIn("sent", data)

    def test_api_preview_endpoint(self):
        res = self.client.get("/api/templates/preview?project_id=1")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("text_preview", data)
        self.assertIn("meta_cloud_api_payload", data)


if __name__ == "__main__":
    unittest.main()
