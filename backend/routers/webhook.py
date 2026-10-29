"""
Meta WhatsApp Business Cloud API Webhook Router
Handles:
- Verification handshake (GET /webhook)
- Status callbacks (Delivered, Read, Failed) & Inbound Message Processing (POST /webhook)
- Automatic STOP opt-out compliance & START reactivation
- Live SSE event broadcasting to update connected dashboards
"""

import os
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Query, Response, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse

import database
from whatsapp.client import WhatsAppClient
from marketing.compliance import ComplianceEngine
from backend import events

logger = logging.getLogger("WebhookRouter")
router = APIRouter(tags=["Webhook"])

VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "whatsapp_realestate_verify_token_123")


def process_inbound_webhook_event(body: Dict[str, Any]):
    """
    Background worker that processes Meta WhatsApp Cloud API webhooks:
    1. Delivery status updates (sent, delivered, read, failed)
    2. Inbound messages (text, quick-reply button clicks, STOP opt-outs)
    """
    entry_list = body.get("entry", [])
    for entry in entry_list:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})

            # 1. Handle Message Status Updates (Delivered, Read, Failed)
            statuses = value.get("statuses", [])
            for status_obj in statuses:
                wa_msg_id = status_obj.get("id")
                new_status = status_obj.get("status")  # 'sent', 'delivered', 'read', 'failed'
                recipient_id = status_obj.get("recipient_id")
                logger.info("Webhook Status Update: Msg %s -> %s (Recipient: %s)", wa_msg_id, new_status, recipient_id)

                if wa_msg_id and new_status:
                    database.update_message_log_status(wa_msg_id, new_status)
                    # Increment corresponding counter in active campaigns
                    if new_status in ("delivered", "read", "failed"):
                        campaigns = database.get_campaigns()
                        if campaigns:
                            database.increment_campaign_counter(campaigns[0]["id"], new_status)

                    # Broadcast real-time status update to dashboard
                    events.broadcast("message_status_updated", {
                        "whatsapp_message_id": wa_msg_id,
                        "status": new_status,
                        "recipient": recipient_id,
                    })
                    events.broadcast("stats_updated", database.get_overall_stats())
                    events.broadcast("logs_updated", {})

            # 2. Handle Inbound Customer Messages & Button Responses
            messages = value.get("messages", [])
            for msg in messages:
                sender_phone = msg.get("from")
                msg_type = msg.get("type")
                text_body = ""
                button_id = None

                if msg_type == "text":
                    text_body = msg.get("text", {}).get("body", "")
                elif msg_type == "button":
                    button_payload = msg.get("button", {})
                    button_id = button_payload.get("payload")
                    text_body = button_payload.get("text", "")
                elif msg_type == "interactive":
                    interactive = msg.get("interactive", {})
                    if interactive.get("type") == "button_reply":
                        button_reply = interactive.get("button_reply", {})
                        button_id = button_reply.get("id")
                        text_body = button_reply.get("title", "")

                logger.info("Webhook Inbound Message from %s (type: %s): '%s' (btn: %s)",
                            sender_phone, msg_type, text_body, button_id)

                # Process through Real Estate Compliance Engine
                result = ComplianceEngine.check_and_handle_inbound(
                    phone=sender_phone,
                    text=text_body,
                    button_id=button_id
                )

                if result:
                    reply_text = result.get("reply")
                    intent = result.get("intent")
                    action = result.get("action")

                    # Update campaign interaction metrics
                    campaigns = database.get_campaigns()
                    if campaigns:
                        top_campaign = campaigns[0]
                        database.increment_campaign_counter(top_campaign["id"], "replied")
                        if intent == "INTERESTED":
                            database.increment_campaign_counter(top_campaign["id"], "interested")
                        elif intent == "BOOKED":
                            database.increment_campaign_counter(top_campaign["id"], "booked")

                    # Broadcast inbound event to dashboard
                    lead_record = database.get_lead_by_phone(sender_phone)
                    events.broadcast("inbound_message", {
                        "phone": sender_phone,
                        "text": text_body,
                        "action": action,
                        "intent": intent,
                        "lead": lead_record,
                    })
                    events.broadcast("stats_updated", database.get_overall_stats())
                    events.broadcast("lead_updated", {"lead": lead_record})

                    # Send automated response back to lead via WhatsApp
                    if reply_text:
                        try:
                            client = WhatsAppClient()
                            send_res = client.send_text_message(to=sender_phone, message=reply_text)
                            if send_res.get("success"):
                                msgs = send_res.get("data", {}).get("messages", [{}])
                                wa_id = msgs[0].get("id") if msgs else None
                                database.log_message(
                                    phone=sender_phone,
                                    lead_id=lead_record["id"] if lead_record else None,
                                    whatsapp_message_id=wa_id,
                                    template_name=f"inbound_reply_{action.lower()}",
                                    status="SENT",
                                    media_type="TEXT",
                                )
                                events.broadcast("logs_updated", {})
                        except Exception as ex:
                            logger.error("Failed to send webhook automated response: %s", ex)


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Webhook verification handshake for Meta Developer Portal.
    Configure this URL in Meta Dashboard: https://your-domain.com/webhook
    """
    logger.info("Meta Webhook verification requested. Mode: %s, Token: %s", hub_mode, hub_verify_token)
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("Meta Webhook verification succeeded!")
        return PlainTextResponse(content=hub_challenge, status_code=200)

    logger.warning("Meta Webhook verification failed: token mismatch")
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receives incoming WhatsApp events from Meta Cloud API
    (Delivery receipts, customer replies, opt-out requests, button clicks).
    Returns HTTP 200 within 3 seconds as required by Meta.
    """
    try:
        body: Dict[str, Any] = await request.json()
    except Exception:
        return Response(content="Invalid JSON", status_code=400)

    background_tasks.add_task(process_inbound_webhook_event, body)
    return {"status": "EVENT_RECEIVED"}
