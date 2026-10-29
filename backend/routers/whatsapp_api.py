"""
WhatsApp Cloud API Router
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import database
from whatsapp.client import WhatsAppClient
from marketing.campaign_engine import CampaignEngine
from backend import events

logger = logging.getLogger("WhatsAppRouter")
router = APIRouter(tags=["WhatsApp API"])


class SendTemplateRequest(BaseModel):
    phone: str
    project_id: int = 1
    lead_name: Optional[str] = None
    media_type: str = "IMAGE"
    dry_run: bool = False
    direct: bool = False
    template_name: Optional[str] = None


def get_client() -> Optional[WhatsAppClient]:
    try:
        return WhatsAppClient()
    except Exception as e:
        logger.warning("Could not initialize WhatsAppClient: %s", e)
        return None


@router.get("/api/whatsapp/verify")
def verify_whatsapp_credentials():
    """
    Validates Meta WhatsApp Cloud API credentials against Meta Graph API.
    """
    client = get_client()
    if not client:
        return {
            "success": False,
            "message": "WhatsApp credentials missing in .env. Please set WHATSAPP_API_KEY and PHONE_NUMBER_ID.",
            "diagnostic_hint": "Check your .env file in the root directory.",
        }

    res = client.verify_credentials()
    return res


@router.post("/api/whatsapp/send")
@router.post("/api/send-test")
def send_marketing_template(req: SendTemplateRequest):
    """
    Sends a real estate template or direct rich media message to a lead.
    Supports:
    - Standard Meta Template mode
    - Direct Rich Media layout fallback
    - Custom templates (e.g. hello_world)
    - Dry-run simulation
    - Automatic Opt-In compliance check
    """
    client = get_client()
    engine = CampaignEngine(whatsapp_client=client)

    result = engine.send_single_project_template(
        phone=req.phone,
        project_id=req.project_id,
        lead_name=req.lead_name,
        media_type=req.media_type,
        dry_run=req.dry_run,
        direct=req.direct,
        template_name=req.template_name,
    )

    # Broadcast event so dashboard syncs live
    events.broadcast("message_sent", {"phone": req.phone, "result": result})
    events.broadcast("stats_updated", database.get_overall_stats())
    events.broadcast("logs_updated", {})

    return result


@router.get("/api/logs")
def list_message_logs(limit: int = 50):
    """Lists recent WhatsApp message logs, delivery receipts, and status timestamps."""
    return database.get_message_logs(limit=limit)

