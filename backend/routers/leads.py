"""
Leads & Meta Opt-In Compliance Router
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import database
from backend import events

router = APIRouter(tags=["Leads"])


class CreateLeadRequest(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    city: str = "Chennai"
    project_interest: str = "Green Valley Emerald"
    whatsapp_opt_in: bool = True
    source: str = "Website Lead Form"
    notes: Optional[str] = None


class ToggleOptInRequest(BaseModel):
    phone: str
    opt_in: bool
    reason: Optional[str] = None


@router.get("/api/leads")
def list_leads(opt_in: Optional[bool] = None, city: Optional[str] = None, search: Optional[str] = None):
    """Lists leads with filter by opt-in status, city, or search term."""
    return database.get_leads(opt_in_only=opt_in, city=city, search=search)


@router.post("/api/leads")
def create_lead(req: CreateLeadRequest):
    """
    Registers or updates a lead with mandatory WhatsApp Opt-In recording.
    Complies with Meta WhatsApp Opt-In requirements.
    """
    lead = database.add_or_update_lead(
        name=req.name,
        phone=req.phone,
        email=req.email,
        city=req.city,
        project_interest=req.project_interest,
        whatsapp_opt_in=req.whatsapp_opt_in,
        source=req.source,
        notes=req.notes,
    )
    # Broadcast live sync event
    events.broadcast("lead_updated", {"lead": lead, "action": "created_or_updated"})
    events.broadcast("stats_updated", database.get_overall_stats())
    return {"success": True, "lead": lead}


@router.post("/api/leads/toggle-opt-in")
def toggle_lead_opt_in(req: ToggleOptInRequest):
    """Toggles WhatsApp opt-in state for a phone number."""
    if req.opt_in:
        success = database.set_lead_opt_in(req.phone, source=req.reason or "Admin Dashboard Manual Toggle")
    else:
        success = database.set_lead_opt_out(req.phone, reason=req.reason or "Admin Dashboard Manual Opt-out")

    updated_lead = database.get_lead_by_phone(req.phone)
    events.broadcast("lead_updated", {"lead": updated_lead, "phone": req.phone, "opt_in": req.opt_in, "action": "toggle_opt_in"})
    events.broadcast("stats_updated", database.get_overall_stats())
    return {"success": success, "phone": req.phone, "opt_in": req.opt_in, "lead": updated_lead}


@router.delete("/api/leads/{lead_id}")
def remove_lead(lead_id: int):
    """Deletes a lead from the CRM."""
    success = database.delete_lead(lead_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")

    events.broadcast("lead_updated", {"lead_id": lead_id, "action": "deleted"})
    events.broadcast("stats_updated", database.get_overall_stats())
    return {"success": True, "lead_id": lead_id}
