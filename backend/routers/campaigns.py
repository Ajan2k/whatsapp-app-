"""
Marketing Campaigns & Throttled Dispatching Router
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any

import database
from marketing.campaign_engine import CampaignEngine
from whatsapp.client import WhatsAppClient
from backend import events

router = APIRouter(tags=["Campaigns"])

# Initialize campaign engine with fallback
try:
    _whatsapp_client = WhatsAppClient()
except Exception:
    _whatsapp_client = None

campaign_engine = CampaignEngine(whatsapp_client=_whatsapp_client)


class LaunchCampaignRequest(BaseModel):
    name: str
    project_id: int
    audience_city: str = "All"
    media_type: str = "IMAGE"
    dry_run: bool = False
    throttle_seconds: float = 0.2


@router.get("/api/campaigns")
def list_campaigns():
    """Lists marketing campaigns and their funnel metrics."""
    return database.get_campaigns()


@router.get("/api/campaigns/audience-preview")
def preview_audience(project_id: int = 1, city: str = "All"):
    """Calculates campaign audience breakdown before launching."""
    return campaign_engine.prepare_campaign_audience(project_id=project_id, city_filter=city)


@router.post("/api/campaigns")
def launch_campaign(req: LaunchCampaignRequest):
    """
    Creates and triggers a Real Estate WhatsApp marketing campaign.
    Applies strict opt-in filtering and rate-limiting.
    """
    # 1. Create campaign record
    campaign_id = database.create_campaign(
        name=req.name,
        project_id=req.project_id,
        audience_city=req.audience_city,
        status="RUNNING",
    )

    events.broadcast("campaign_started", {"campaign_id": campaign_id, "name": req.name})

    # 2. Run campaign
    result = campaign_engine.run_campaign(
        campaign_id=campaign_id,
        dry_run=req.dry_run,
        throttle_seconds=req.throttle_seconds,
        media_type=req.media_type,
    )

    # 3. Broadcast campaign completion & stats update
    events.broadcast("campaign_completed", {"campaign_id": campaign_id, "result": result})
    events.broadcast("stats_updated", database.get_overall_stats())
    events.broadcast("logs_updated", {})

    return {"success": True, "result": result}
