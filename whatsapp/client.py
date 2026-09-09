import os
import re
import logging
from typing import Optional, Dict, Any, List
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("WhatsAppClient")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class WhatsAppClient:
    """
    Client for Meta WhatsApp Business Cloud API.
    Supports sending text messages, marketing templates with media headers/buttons,
    interactive CTA cards, and media assets.
    """

    DEFAULT_API_VERSION = "v21.0"
    GRAPH_API_BASE_URL = "https://graph.facebook.com"

    def __init__(
        self,
        access_token: Optional[str] = None,
        phone_number_id: Optional[str] = None,
        waba_id: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        self.access_token = (
            access_token
            or os.getenv("WHATSAPP_API_KEY")
            or os.getenv("WHATSAPP_ACCESS_TOKEN")
        )
        self.phone_number_id = phone_number_id or os.getenv("PHONE_NUMBER_ID")
        self.waba_id = waba_id or os.getenv("WHATSAPP_BUSSINESS_ACCOUNT_ID") or os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
        self.api_version = api_version or os.getenv("WHATSAPP_API_VERSION", self.DEFAULT_API_VERSION)

        if not self.access_token:
            raise ValueError(
                "WhatsApp access token is missing! Please set WHATSAPP_API_KEY in your .env file."
            )
        if not self.phone_number_id:
            raise ValueError(
                "WhatsApp phone number ID is missing! Please set PHONE_NUMBER_ID in your .env file."
            )

        # Clean any whitespace or quotes
        self.access_token = self.access_token.strip().strip("'\"")
        self.phone_number_id = str(self.phone_number_id).strip().strip("'\"")
        if self.waba_id:
            self.waba_id = str(self.waba_id).strip().strip("'\"")

        self.messages_url = (
            f"{self.GRAPH_API_BASE_URL}/{self.api_version}/{self.phone_number_id}/messages"
        )
        self._access_token = self.access_token

    @property
    def headers(self) -> Dict[str, str]:
        """Dynamic headers that always pick up the active token from environment."""
        load_dotenv(override=True)
        active_token = os.getenv("WHATSAPP_API_KEY") or self._access_token or ""
        clean_token = active_token.strip().strip("'\"")
        return {
            "Authorization": f"Bearer {clean_token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """
        Normalize phone number by removing spaces, dashes, plus sign, and parentheses.
        WhatsApp API requires international format without '+' (e.g., '919876543210' or '15551234567').
        """
        cleaned = re.sub(r"[^\d]", "", str(phone))
        if not cleaned:
            raise ValueError(f"Invalid phone number provided: {phone}")
        return cleaned

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse response and handle standard WhatsApp Cloud API errors."""
        try:
            data = response.json()
        except Exception:
            data = {"status_code": response.status_code, "text": response.text}

        if response.status_code in (200, 201):
            logger.info("WhatsApp API request succeeded: %s", data)
            return {"success": True, "data": data}

        # Error handling
        error_obj = data.get("error", {})
        error_code = error_obj.get("code")
        error_subcode = error_obj.get("error_subcode")
        error_msg = error_obj.get("message", response.text)
        error_user_msg = error_obj.get("error_user_msg")

        diagnostic_hint = ""
        if error_code == 190:
            diagnostic_hint = (
                "Your WhatsApp API Key (Access Token) has expired. "
                "Generate a new User or System User token in the Meta Developer Portal."
            )
        elif error_code == 131030:
            diagnostic_hint = (
                "Recipient phone number is not in your allowed test recipient list. "
                "For test numbers, add the recipient's phone number under WhatsApp > API Setup > Step 1: Select phone numbers."
            )
        elif error_code == 132000:
            diagnostic_hint = (
                "Template does not exist or language/parameters do not match the approved template in your Meta WhatsApp Manager."
            )
        elif error_code == 131047:
            diagnostic_hint = (
                "More than 24 hours have passed since the customer last replied. "
                "You must use a pre-approved template message to initiate a conversation."
            )

        full_error = {
            "success": False,
            "status_code": response.status_code,
            "error_code": error_code,
            "error_subcode": error_subcode,
            "message": error_msg,
            "error_user_msg": error_user_msg,
            "diagnostic_hint": diagnostic_hint,
            "raw_response": data,
        }

        logger.error("WhatsApp API request failed: %s", full_error)
        return full_error

    def verify_credentials(self) -> Dict[str, Any]:
        """
        Check the status of the configured Phone Number ID against Meta Graph API.
        """
        url = f"{self.GRAPH_API_BASE_URL}/{self.api_version}/{self.phone_number_id}"
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            return self._handle_response(res)
        except requests.RequestException as e:
            logger.error("Network error during credential verification: %s", e)
            return {"success": False, "message": str(e)}

    def send_raw_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends an arbitrary Meta WhatsApp Cloud API messages payload
        (e.g., pre-built template or interactive message).
        """
        if "to" in payload:
            payload["to"] = self.clean_phone_number(payload["to"])

        logger.info("Sending Meta WhatsApp Cloud API payload to %s (type: %s)", payload.get("to"), payload.get("type"))
        try:
            res = requests.post(
                self.messages_url,
                headers=self.headers,
                json=payload,
                timeout=15,
            )
            return self._handle_response(res)
        except requests.RequestException as e:
            return {"success": False, "message": str(e)}

    def send_template_message(
        self,
        to: str,
        template_name: str = "hello_world",
        language_code: str = "en_US",
        components: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send a pre-approved template message.
        Supports components (Header media, Body variables, Buttons).
        """
        clean_to = self.clean_phone_number(to)
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }

        if components:
            payload["template"]["components"] = components

        return self.send_raw_payload(payload)

    def send_text_message(
        self,
        to: str,
        message: str,
        preview_url: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a regular free-form text message (for customer service 24h window).
        """
        clean_to = self.clean_phone_number(to)
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "text",
            "text": {
                "body": message,
                "preview_url": preview_url,
            },
        }
        return self.send_raw_payload(payload)

    def send_image(
        self,
        to: str,
        image_url: str,
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send an image with optional caption."""
        clean_to = self.clean_phone_number(to)
        img_payload: Dict[str, Any] = {"link": image_url}
        if caption:
            img_payload["caption"] = caption
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "image",
            "image": img_payload,
        }
        return self.send_raw_payload(payload)

    def send_video(
        self,
        to: str,
        video_url: str,
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a video walkthrough with optional caption."""
        clean_to = self.clean_phone_number(to)
        vid_payload: Dict[str, Any] = {"link": video_url}
        if caption:
            vid_payload["caption"] = caption
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "video",
            "video": vid_payload,
        }
        return self.send_raw_payload(payload)

    def send_document(
        self,
        to: str,
        document_url: str,
        filename: str,
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a document/PDF brochure via publicly accessible URL."""
        clean_to = self.clean_phone_number(to)
        doc_payload: Dict[str, Any] = {
            "link": document_url,
            "filename": filename,
        }
        if caption:
            doc_payload["caption"] = caption
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "document",
            "document": doc_payload,
        }
        return self.send_raw_payload(payload)

    def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: List[Dict[str, str]],
        header_image_url: Optional[str] = None,
        footer_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sends an interactive button message (up to 3 buttons).
        Example buttons: [{"id": "view_layout", "title": "View Layout"}, ...]
        """
        clean_to = self.clean_phone_number(to)
        btn_objs = []
        for btn in buttons[:3]:
            btn_objs.append({
                "type": "reply",
                "reply": {
                    "id": btn.get("id", "btn"),
                    "title": btn.get("title", "Select")[:20],
                }
            })

        interactive: Dict[str, Any] = {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": btn_objs},
        }

        if header_image_url:
            interactive["header"] = {
                "type": "image",
                "image": {"link": header_image_url}
            }

        if footer_text:
            interactive["footer"] = {"text": footer_text}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "interactive",
            "interactive": interactive,
        }
        return self.send_raw_payload(payload)
