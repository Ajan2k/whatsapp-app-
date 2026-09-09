#!/usr/bin/env python3
"""
Real Estate WhatsApp Marketing & Template Webhook Server
Integrated with Meta WhatsApp Cloud API:
- Webhook handshake (GET /webhook)
- Status callbacks (Delivered, Read, Failed) & Inbound Message Processing (POST /webhook)
- Automatic STOP opt-out compliance
- Campaign dispatching & funnel analytics (Total -> Eligible -> Sent -> Delivered -> Read -> Replied -> Interested -> Booked)
- Interactive Real Estate Admin Dashboard & WhatsApp Phone Simulator
"""

import os
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Query, Response, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

import database
from whatsapp.client import WhatsAppClient
from marketing.template_generator import RealEstateTemplateGenerator
from marketing.compliance import ComplianceEngine
from marketing.campaign_engine import CampaignEngine

load_dotenv()
logger = logging.getLogger("RealEstateWhatsAppServer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Ensure database is initialized on startup
database.init_db(seed_sample_data=True)

app = FastAPI(
    title="Real Estate WhatsApp Marketing Platform",
    description="Meta WhatsApp Cloud API Marketing, Template Generation, Opt-in Compliance, and Campaign Funnel Engine",
    version="2.0.0",
)

VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "whatsapp_realestate_verify_token_123")

# Initialize clients
try:
    whatsapp_client = WhatsAppClient()
except Exception as e:
    logger.warning("WhatsAppClient initialized in mock/fallback mode: %s", e)
    whatsapp_client = None

campaign_engine = CampaignEngine(whatsapp_client=whatsapp_client)


# ---------------- Pydantic Request Models ---------------- #

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


class LaunchCampaignRequest(BaseModel):
    name: str
    project_id: int
    audience_city: str = "All"
    media_type: str = "IMAGE"
    dry_run: bool = False


class SendTestTemplateRequest(BaseModel):
    phone: str
    project_id: int
    lead_name: Optional[str] = None
    media_type: str = "IMAGE"
    dry_run: bool = False


# ---------------- Webhook Event Processing ---------------- #

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
                        # Update latest campaign metric
                        campaigns = database.get_campaigns()
                        if campaigns:
                            database.increment_campaign_counter(campaigns[0]["id"], new_status)

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
                    # Quick reply button clicked
                    button_payload = msg.get("button", {})
                    button_id = button_payload.get("payload")
                    text_body = button_payload.get("text", "")
                elif msg_type == "interactive":
                    # Interactive reply button
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

                    # Update campaign interaction metrics
                    campaigns = database.get_campaigns()
                    if campaigns:
                        top_campaign = campaigns[0]
                        database.increment_campaign_counter(top_campaign["id"], "replied")
                        if intent == "INTERESTED":
                            database.increment_campaign_counter(top_campaign["id"], "interested")
                        elif intent == "BOOKED":
                            database.increment_campaign_counter(top_campaign["id"], "booked")

                    # Send automated response back to lead via WhatsApp
                    if reply_text:
                        try:
                            client_to_use = whatsapp_client or WhatsAppClient()
                            send_res = client_to_use.send_text_message(to=sender_phone, message=reply_text)
                            if send_res.get("success"):
                                msgs = send_res.get("data", {}).get("messages", [{}])
                                wa_id = msgs[0].get("id") if msgs else None
                                lead_record = database.get_lead_by_phone(sender_phone)
                                database.log_message(
                                    phone=sender_phone,
                                    lead_id=lead_record["id"] if lead_record else None,
                                    whatsapp_message_id=wa_id,
                                    template_name=f"inbound_reply_{result.get('action', 'reply').lower()}",
                                    status="SENT",
                                    media_type="TEXT",
                                )
                        except Exception as ex:
                            logger.error("Failed to send webhook automated response: %s", ex)


# ---------------- Webhook Endpoints ---------------- #

@app.get("/webhook")
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


@app.post("/webhook")
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


# ---------------- REST API Endpoints ---------------- #

@app.get("/api/stats")
def get_dashboard_stats():
    """Returns top-level campaign funnel statistics."""
    return database.get_overall_stats()


@app.get("/api/projects")
def list_projects():
    """Lists all real estate projects and layouts."""
    return database.get_projects()


@app.get("/api/projects/{project_id}")
def get_project_details(project_id: int):
    project = database.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/api/leads")
def list_leads(opt_in: Optional[bool] = None, city: Optional[str] = None, search: Optional[str] = None):
    """Lists leads with filter by opt-in status, city, or search term."""
    return database.get_leads(opt_in_only=opt_in, city=city, search=search)


@app.post("/api/leads")
def create_lead(req: CreateLeadRequest):
    """
    Registers a new lead with mandatory opt-in checkbox recording.
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
    return {"success": True, "lead": lead}


@app.post("/api/leads/toggle-opt-in")
def toggle_lead_opt_in(req: ToggleOptInRequest):
    """Toggles WhatsApp opt-in state for a phone number."""
    if req.opt_in:
        success = database.set_lead_opt_in(req.phone, source="Admin Dashboard Manual Toggle")
    else:
        success = database.set_lead_opt_out(req.phone, reason="Admin Dashboard Manual Opt-out")
    return {"success": success, "phone": req.phone, "opt_in": req.opt_in}


@app.get("/api/campaigns")
def list_campaigns():
    """Lists marketing campaigns and their funnel metrics."""
    return database.get_campaigns()


@app.get("/api/logs")
def list_message_logs(limit: int = 50):
    """Lists recent WhatsApp message logs and delivery statuses."""
    return database.get_message_logs(limit=limit)


@app.post("/api/campaigns")
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

    # 2. Run campaign
    result = campaign_engine.run_campaign(
        campaign_id=campaign_id,
        dry_run=req.dry_run,
        media_type=req.media_type,
    )
    return {"success": True, "result": result}


@app.post("/api/send-test")
def send_test_template(req: SendTestTemplateRequest):
    """
    Sends a test marketing template message to a specific phone number.
    Verifies opt-in status before sending.
    """
    result = campaign_engine.send_single_project_template(
        phone=req.phone,
        project_id=req.project_id,
        lead_name=req.lead_name,
        media_type=req.media_type,
        dry_run=req.dry_run,
    )
    return result


@app.get("/api/templates/preview")
def preview_template(project_id: int = 1, lead_name: str = "Aravind Kumar", media_type: str = "IMAGE"):
    """
    Returns rendered text preview, Meta Cloud API JSON payload,
    and WhatsApp Business Manager registration schema.
    """
    project = database.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    text_preview = RealEstateTemplateGenerator.format_rendered_message_text(lead_name, project)
    meta_payload = RealEstateTemplateGenerator.build_meta_template_payload(
        to_phone="919876543210",
        lead_name=lead_name,
        project=project,
        media_type=media_type,
    )
    interactive_payload = RealEstateTemplateGenerator.build_meta_interactive_message(
        to_phone="919876543210",
        lead_name=lead_name,
        project=project,
        media_type=media_type,
    )
    registration_schema = RealEstateTemplateGenerator.get_meta_registration_schema()

    return {
        "text_preview": text_preview,
        "meta_cloud_api_payload": meta_payload,
        "meta_interactive_payload": interactive_payload,
        "meta_registration_schema": registration_schema,
    }


# ---------------- Interactive Admin Dashboard UI ---------------- #

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard():
    """
    Sleek, modern Real Estate WhatsApp Marketing Dashboard.
    Features:
    - Funnel Metrics (Total Leads, Eligible, Sent, Delivered, Read, Replied, Interested, Booked)
    - Interactive WhatsApp Smartphone Simulator with hero media & CTA buttons
    - Campaign Launchpad
    - Lead Consent & Opt-In Compliance Manager
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Real Estate WhatsApp Marketing Platform • Meta Cloud API</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-primary: #0a1014;
      --bg-card: #111b21;
      --bg-card-hover: #182229;
      --bg-surface: #202c33;
      --accent-green: #00a884;
      --accent-bright: #25D366;
      --accent-gold: #f59e0b;
      --accent-blue: #3b82f6;
      --accent-red: #ef4444;
      --text-main: #e9edef;
      --text-muted: #8696a0;
      --border-subtle: #222e35;
      --border-focus: #00a884;
      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
    body { background-color: var(--bg-primary); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }

    /* Top Navigation */
    header {
      background: var(--bg-card);
      border-bottom: 1px solid var(--border-subtle);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .brand-group { display: flex; align-items: center; gap: 14px; }
    .brand-icon {
      background: linear-gradient(135deg, #00a884 0%, #25D366 100%);
      width: 42px; height: 42px; border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      font-size: 22px; box-shadow: 0 4px 14px rgba(0,168,132,0.35);
    }
    .brand-text h1 { font-size: 18px; font-weight: 700; letter-spacing: -0.3px; }
    .brand-text p { font-size: 12px; color: var(--accent-bright); font-weight: 500; display: flex; align-items: center; gap: 6px; }
    .status-dot { width: 7px; height: 7px; background: var(--accent-bright); border-radius: 50%; display: inline-block; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

    .header-actions { display: flex; gap: 10px; align-items: center; }
    .btn {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 8px 16px;
      border-radius: var(--radius-sm);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
    }
    .btn:hover { background: var(--border-subtle); border-color: var(--border-focus); }
    .btn-primary {
      background: linear-gradient(135deg, #00a884 0%, #008f6f 100%);
      border: none;
      color: #fff;
      box-shadow: 0 2px 10px rgba(0,168,132,0.3);
    }
    .btn-primary:hover { background: #00bf96; transform: translateY(-1px); }

    /* Main Container */
    main {
      flex: 1;
      max-width: 1480px;
      width: 100%;
      margin: 0 auto;
      padding: 24px 28px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    /* Top Funnel KPI Grid */
    .funnel-container {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 20px 24px;
    }
    .funnel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }
    .funnel-header h2 { font-size: 15px; font-weight: 700; color: var(--text-main); text-transform: uppercase; letter-spacing: 0.5px; }
    .funnel-badge { font-size: 11px; background: rgba(0,168,132,0.15); color: var(--accent-bright); padding: 4px 10px; border-radius: 20px; font-weight: 600; }

    .funnel-grid {
      display: grid;
      grid-template-columns: repeat(8, 1fr);
      gap: 12px;
    }
    .funnel-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 14px 12px;
      text-align: center;
      position: relative;
      transition: transform 0.2s;
    }
    .funnel-card:hover { transform: translateY(-2px); border-color: var(--accent-green); }
    .funnel-label { font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; margin-bottom: 6px; }
    .funnel-val { font-size: 22px; font-weight: 800; color: var(--text-main); }
    .funnel-sub { font-size: 10px; color: var(--accent-bright); margin-top: 4px; font-weight: 600; }
    .card-booked .funnel-val { color: #f59e0b; }
    .card-eligible .funnel-val { color: var(--accent-bright); }

    /* Two-Column Grid */
    .dashboard-layout {
      display: grid;
      grid-template-columns: 1fr 440px;
      gap: 24px;
    }

    /* Left Column */
    .left-col { display: flex; flex-direction: column; gap: 24px; }

    /* Card Box */
    .panel {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 22px 24px;
    }
    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 18px;
    }
    .panel-header h3 { font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; }

    /* Campaign Launchpad Form */
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 16px;
      margin-bottom: 18px;
    }
    .form-group { display: flex; flex-direction: column; gap: 6px; }
    .form-group label { font-size: 12px; font-weight: 600; color: var(--text-muted); }
    .form-control {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      color: var(--text-main);
      padding: 10px 12px;
      font-size: 13px;
      outline: none;
    }
    .form-control:focus { border-color: var(--border-focus); }

    /* Compliance Banner */
    .compliance-alert {
      background: rgba(0, 168, 132, 0.08);
      border: 1px solid rgba(0, 168, 132, 0.3);
      border-radius: var(--radius-sm);
      padding: 12px 16px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      font-size: 12px;
      line-height: 1.5;
      color: #98e2d1;
      margin-bottom: 18px;
    }
    .compliance-alert b { color: var(--accent-bright); }

    /* Leads Table */
    .table-container {
      overflow-x: auto;
      max-height: 380px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
    }
    table { width: 100%; border-collapse: collapse; font-size: 12.5px; text-align: left; }
    th {
      background: var(--bg-surface);
      color: var(--text-muted);
      font-weight: 600;
      padding: 12px 14px;
      position: sticky;
      top: 0;
      z-index: 10;
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.4px;
    }
    td { padding: 12px 14px; border-bottom: 1px solid var(--border-subtle); }
    tr:hover td { background: var(--bg-card-hover); }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 700;
    }
    .badge-opted-in { background: rgba(37, 211, 102, 0.15); color: #25D366; }
    .badge-opted-out { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
    .badge-unverified { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }

    /* Right Column: Interactive Smartphone WhatsApp Simulator */
    .right-col { display: flex; flex-direction: column; gap: 20px; }

    .phone-wrapper {
      background: #111b21;
      border: 8px solid #2a3942;
      border-radius: 36px;
      overflow: hidden;
      box-shadow: 0 20px 50px rgba(0,0,0,0.6);
      display: flex;
      flex-direction: column;
      height: 700px;
      position: relative;
    }
    .phone-notch {
      background: #2a3942;
      width: 140px;
      height: 18px;
      margin: 0 auto;
      border-bottom-left-radius: 12px;
      border-bottom-right-radius: 12px;
    }
    .phone-header {
      background: #202c33;
      padding: 10px 14px;
      display: flex;
      align-items: center;
      gap: 10px;
      border-bottom: 1px solid #222e35;
    }
    .wa-avatar {
      width: 38px; height: 38px; border-radius: 50%;
      background: #00a884; display: flex; align-items: center; justify-content: center;
      font-size: 18px; font-weight: 700; color: white;
    }
    .wa-header-meta h4 { font-size: 14px; font-weight: 600; color: #e9edef; }
    .wa-header-meta p { font-size: 11px; color: #25D366; font-weight: 500; }

    .wa-chat-canvas {
      flex: 1;
      background: #0b141a;
      background-image: radial-gradient(#182229 1.2px, transparent 1.2px);
      background-size: 18px 18px;
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    /* WhatsApp Template Message Bubble */
    .wa-bubble {
      background: #202c33;
      border-radius: 14px;
      border-top-left-radius: 2px;
      max-width: 96%;
      align-self: flex-start;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      display: flex;
      flex-direction: column;
    }
    .wa-media-header {
      position: relative;
      width: 100%;
      height: 160px;
      overflow: hidden;
      background: #111b21;
    }
    .wa-media-header img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .wa-media-badge {
      position: absolute;
      top: 10px;
      left: 10px;
      background: rgba(0,0,0,0.65);
      backdrop-filter: blur(4px);
      color: #fff;
      font-size: 10px;
      font-weight: 600;
      padding: 4px 8px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .wa-bubble-body {
      padding: 12px 14px;
      font-size: 12.5px;
      line-height: 1.45;
      color: #d1d7db;
      white-space: pre-wrap;
    }
    .wa-bubble-footer {
      font-size: 10.5px;
      color: #8696a0;
      padding: 0 14px 10px 14px;
      border-bottom: 1px solid #2a3942;
    }
    .wa-buttons-container {
      display: flex;
      flex-direction: column;
    }
    .wa-btn {
      padding: 11px;
      text-align: center;
      font-size: 13px;
      font-weight: 600;
      color: #00a884;
      background: transparent;
      border: none;
      border-top: 1px solid #2a3942;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: background 0.15s;
    }
    .wa-btn:hover { background: #2a3942; }

    .modal-overlay {
      position: fixed; inset: 0; background: rgba(0,0,0,0.7);
      display: none; align-items: center; justify-content: center; z-index: 1000;
    }
    .modal-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 24px;
      width: 480px;
      max-width: 90vw;
    }
  </style>
</head>
<body>

  <!-- Top Bar -->
  <header>
    <div class="brand-group">
      <div class="brand-icon">🏡</div>
      <div class="brand-text">
        <h1>Real Estate WhatsApp Marketing Platform</h1>
        <p><span class="status-dot"></span> Meta WhatsApp Business Cloud API • Real-Time Engine</p>
      </div>
    </div>
    <div class="header-actions">
      <button class="btn" onclick="openMetaPayloadModal()">📋 Meta JSON Schema</button>
      <button class="btn" onclick="openAddLeadModal()">➕ Add Lead with Consent</button>
      <button class="btn btn-primary" onclick="launchCampaignFromUI()">🚀 Launch Marketing Campaign</button>
    </div>
  </header>

  <!-- Main Container -->
  <main>

    <!-- Top Real-Time Marketing Funnel Dashboard -->
    <section class="funnel-container">
      <div class="funnel-header">
        <h2>📊 Real-Estate Campaign Funnel Performance</h2>
        <span class="funnel-badge">Active Campaign: Green Valley Emerald</span>
      </div>
      <div class="funnel-grid">
        <div class="funnel-card">
          <div class="funnel-label">Total Leads</div>
          <div class="funnel-val" id="kpi-total">2,500</div>
          <div class="funnel-sub">Audience Pool</div>
        </div>
        <div class="funnel-card card-eligible">
          <div class="funnel-label">Eligible (Opt-In)</div>
          <div class="funnel-val" id="kpi-eligible">2,100</div>
          <div class="funnel-sub">84.0% Consent</div>
        </div>
        <div class="funnel-card">
          <div class="funnel-label">Sent</div>
          <div class="funnel-val" id="kpi-sent">2,050</div>
          <div class="funnel-sub">Meta Cloud API</div>
        </div>
        <div class="funnel-card">
          <div class="funnel-label">Delivered</div>
          <div class="funnel-val" id="kpi-delivered">1,980</div>
          <div class="funnel-sub">96.5% Delivery</div>
        </div>
        <div class="funnel-card">
          <div class="funnel-label">Read</div>
          <div class="funnel-val" id="kpi-read">1,720</div>
          <div class="funnel-sub">86.8% Open Rate</div>
        </div>
        <div class="funnel-card">
          <div class="funnel-label">Replied</div>
          <div class="funnel-val" id="kpi-replied">340</div>
          <div class="funnel-sub">19.7% Response</div>
        </div>
        <div class="funnel-card">
          <div class="funnel-label">Interested</div>
          <div class="funnel-val" id="kpi-interested">125</div>
          <div class="funnel-sub">Site Visits / Maps</div>
        </div>
        <div class="funnel-card card-booked">
          <div class="funnel-label">Booked</div>
          <div class="funnel-val" id="kpi-booked">18</div>
          <div class="funnel-sub">Plot Blocked 🎉</div>
        </div>
      </div>
    </section>

    <!-- 2-Column Split: Controls + Phone Simulator -->
    <div class="dashboard-layout">

      <!-- Left Column: Controls & Leads -->
      <div class="left-col">

        <!-- Panel 1: Campaign Launchpad -->
        <section class="panel">
          <div class="panel-header">
            <h3>🚀 Campaign Launchpad & WhatsApp Template Controls</h3>
            <span style="font-size:12px; color:var(--text-muted);">Template: <code>real_estate_launch_v1</code> (Active Approved)</span>
          </div>

          <div class="compliance-alert">
            <span style="font-size:18px;">🛡️</span>
            <div>
              <b>Strict Meta Opt-In Compliance Active:</b> Only leads with confirmed <code>whatsapp_opt_in = true</code> and zero opt-out history will be dispatched. Unverified or opted-out leads are automatically skipped.
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label>Select Project / Layout</label>
              <select class="form-control" id="ctrl-project" onchange="updateSimulator()">
                <option value="1">Green Valley Emerald Layout (Chennai)</option>
                <option value="2">Sunrise Palm Meadows (Bangalore)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Audience Filter (City)</label>
              <select class="form-control" id="ctrl-city">
                <option value="All">All Registered Opted-in Leads</option>
                <option value="Chennai">Chennai Leads Only</option>
                <option value="Bangalore">Bangalore Leads Only</option>
              </select>
            </div>
            <div class="form-group">
              <label>Header Media Asset</label>
              <select class="form-control" id="ctrl-media" onchange="updateSimulator()">
                <option value="IMAGE">Project Hero Image</option>
                <option value="VIDEO">Walkthrough Video (MP4)</option>
                <option value="DOCUMENT">Layout Map & Brochure (PDF)</option>
              </select>
            </div>
          </div>

          <div style="display: flex; gap: 12px; align-items: center;">
            <button class="btn btn-primary" onclick="launchCampaignFromUI()">
              ⚡ Dispatch Marketing Campaign
            </button>
            <button class="btn" onclick="sendTestTemplateMessage()">
              📱 Send Live Test to Phone
            </button>
            <span id="campaign-status" style="font-size:12px; color:var(--accent-bright); font-weight:600;"></span>
          </div>
        </section>

        <!-- Panel 2: Leads & Consent Manager -->
        <section class="panel">
          <div class="panel-header">
            <h3>👥 Lead Management & Opt-In Compliance Records</h3>
            <div style="display:flex; gap:10px;">
              <input type="text" id="lead-search" class="form-control" placeholder="Search phone or name..." oninput="fetchLeads()" style="padding: 6px 10px; width: 180px;">
              <select class="form-control" id="lead-filter-optin" onchange="fetchLeads()" style="padding: 6px 10px;">
                <option value="">All Statuses</option>
                <option value="true">Opted-In Only</option>
                <option value="false">Opted-Out / Unverified</option>
              </select>
            </div>
          </div>

          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Lead Name</th>
                  <th>Phone</th>
                  <th>City</th>
                  <th>Project Interest</th>
                  <th>WhatsApp Consent</th>
                  <th>Consent Timestamp</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody id="leads-table-body">
                <tr><td colspan="7" style="text-align:center; color:var(--text-muted);">Loading leads...</td></tr>
              </tbody>
            </table>
          </div>
        </section>

      </div>

      <!-- Right Column: Interactive WhatsApp Phone Simulator -->
      <div class="right-col">
        <div class="phone-wrapper">
          <div class="phone-notch"></div>
          
          <div class="phone-header">
            <div class="wa-avatar">🏡</div>
            <div class="wa-header-meta">
              <h4>ABC Properties Layouts</h4>
              <p>Verified Business Account • Online</p>
            </div>
          </div>

          <div class="wa-chat-canvas">
            
            <div style="text-align:center; margin-bottom: 6px;">
              <span style="background:#182229; color:#8696a0; font-size:10px; padding:3px 10px; border-radius:8px;">TODAY</span>
            </div>

            <!-- WhatsApp Bubble -->
            <div class="wa-bubble">
              <div class="wa-media-header" id="sim-media-container">
                <img id="sim-hero-img" src="https://images.unsplash.com/photo-1592595896551-12b371d546d5?auto=format&fit=crop&w=1200&q=80" alt="Project Hero">
                <div class="wa-media-badge" id="sim-media-badge">📷 Project Layout Image</div>
              </div>

              <div class="wa-bubble-body" id="sim-bubble-body">
                Loading template preview...
              </div>

              <div class="wa-bubble-footer">
                Reply STOP to unsubscribe • ABC Properties
              </div>

              <div class="wa-buttons-container">
                <button class="wa-btn" onclick="simulateButtonClick('View Layout')">🗺️ View Layout</button>
                <button class="wa-btn" onclick="simulateButtonClick('Book a Plot')">📍 Book a Plot</button>
                <button class="wa-btn" onclick="simulateButtonClick('Talk to Sales')">📞 Talk to Sales</button>
              </div>
            </div>

            <!-- Interactive Reply Demonstration Bubble -->
            <div id="sim-user-reply-container" style="display:none; flex-direction:column; gap:8px;">
              <!-- User selection -->
              <div class="wa-bubble" style="align-self:flex-end; background:#005c4b; color:#fff; border-top-right-radius:2px; border-top-left-radius:14px; padding:8px 12px; font-size:12.5px;" id="sim-user-choice">
                📍 Book a Plot
              </div>
              <!-- Bot instant reply -->
              <div class="wa-bubble" style="padding:10px 12px; font-size:12px; line-height:1.45;" id="sim-bot-reply">
                📍 <b>Reserve Your Plot – Fast-Track Booking</b><br><br>
                Online Reservation Token: ₹10,000 (100% refundable). Our Senior Plot Specialist will connect with you in 15 minutes!
              </div>
            </div>

          </div>
        </div>
      </div>

    </div>

  </main>

  <!-- Add Lead Modal -->
  <div class="modal-overlay" id="addLeadModal">
    <div class="modal-card">
      <h3 style="margin-bottom:16px;">Add New Lead with WhatsApp Opt-In Consent</h3>
      <div class="form-group" style="margin-bottom:12px;">
        <label>Full Name</label>
        <input type="text" id="new-lead-name" class="form-control" placeholder="e.g. Anand R">
      </div>
      <div class="form-group" style="margin-bottom:12px;">
        <label>WhatsApp Phone Number (with Country Code)</label>
        <input type="text" id="new-lead-phone" class="form-control" placeholder="e.g. 919876543210">
      </div>
      <div class="form-group" style="margin-bottom:12px;">
        <label>City</label>
        <input type="text" id="new-lead-city" class="form-control" value="Chennai">
      </div>
      <div class="form-group" style="margin-bottom:16px;">
        <label>Project Interest</label>
        <select class="form-control" id="new-lead-project">
          <option value="Green Valley Emerald">Green Valley Emerald</option>
          <option value="Sunrise Palm Meadows">Sunrise Palm Meadows</option>
        </select>
      </div>
      <div style="background:var(--bg-surface); padding:10px 12px; border-radius:6px; margin-bottom:18px;">
        <label style="display:flex; align-items:flex-start; gap:8px; font-size:12px; cursor:pointer; color:#d1d7db;">
          <input type="checkbox" id="new-lead-optin" checked style="margin-top:2px;">
          <span><b>WhatsApp Marketing Opt-In:</b> Lead explicitly checked the consent box to receive project launches, plot offers, and walkthroughs from ABC Properties.</span>
        </label>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:10px;">
        <button class="btn" onclick="closeAddLeadModal()">Cancel</button>
        <button class="btn btn-primary" onclick="submitNewLead()">Save Lead</button>
      </div>
    </div>
  </div>

  <!-- Meta Payload Schema Modal -->
  <div class="modal-overlay" id="metaModal">
    <div class="modal-card" style="width:680px;">
      <h3 style="margin-bottom:12px;">Meta WhatsApp Cloud API Payload Structure</h3>
      <p style="font-size:12px; color:var(--text-muted); margin-bottom:12px;">Exact JSON dispatched to <code>POST https://graph.facebook.com/v21.0/{phone_number_id}/messages</code>:</p>
      <pre id="meta-json-display" style="background:#0b141a; padding:12px; border-radius:8px; font-family:'JetBrains Mono',monospace; font-size:11px; max-height:360px; overflow-y:auto; color:#25D366;"></pre>
      <div style="display:flex; justify-content:flex-end; margin-top:14px;">
        <button class="btn" onclick="closeMetaModal()">Close</button>
      </div>
    </div>
  </div>

  <script>
    let projectsData = [];

    async function initDashboard() {
      await fetchProjects();
      await fetchStats();
      await fetchLeads();
      updateSimulator();
    }

    async function fetchProjects() {
      const res = await fetch('/api/projects');
      projectsData = await res.json();
    }

    async function fetchStats() {
      try {
        const res = await fetch('/api/stats');
        const d = await res.json();
        document.getElementById('kpi-total').innerText = Number(d.total_leads).toLocaleString();
        document.getElementById('kpi-eligible').innerText = Number(d.eligible_leads).toLocaleString();
        document.getElementById('kpi-sent').innerText = Number(d.sent).toLocaleString();
        document.getElementById('kpi-delivered').innerText = Number(d.delivered).toLocaleString();
        document.getElementById('kpi-read').innerText = Number(d.read).toLocaleString();
        document.getElementById('kpi-replied').innerText = Number(d.replied).toLocaleString();
        document.getElementById('kpi-interested').innerText = Number(d.interested).toLocaleString();
        document.getElementById('kpi-booked').innerText = Number(d.booked).toLocaleString();
      } catch (e) {
        console.error("Error fetching stats:", e);
      }
    }

    async function fetchLeads() {
      const search = document.getElementById('lead-search').value;
      const optin = document.getElementById('lead-filter-optin').value;
      let url = '/api/leads?';
      if (search) url += `search=${encodeURIComponent(search)}&`;
      if (optin !== "") url += `opt_in=${optin}&`;

      const res = await fetch(url);
      const leads = await res.json();

      const tbody = document.getElementById('leads-table-body');
      if (!leads.length) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No leads found.</td></tr>';
        return;
      }

      tbody.innerHTML = leads.map(l => {
        let badgeHtml = '';
        if (l.whatsapp_opt_in === 1 && !l.opt_out_timestamp) {
          badgeHtml = '<span class="badge badge-opted-in">✔ OPTED IN</span>';
        } else if (l.opt_out_timestamp) {
          badgeHtml = '<span class="badge badge-opted-out">✖ OPTED OUT</span>';
        } else {
          badgeHtml = '<span class="badge badge-unverified">⚠ UNVERIFIED</span>';
        }

        const isOptedIn = l.whatsapp_opt_in === 1 && !l.opt_out_timestamp;
        const toggleBtnLabel = isOptedIn ? 'Opt-Out' : 'Opt-In';
        const toggleBtnClass = isOptedIn ? 'color:#ef4444;' : 'color:#25D366;';

        const optInDate = l.opt_in_timestamp ? l.opt_in_timestamp.slice(0,10) : '—';

        return `
          <tr>
            <td><b>${l.name}</b></td>
            <td><code>${l.phone}</code></td>
            <td>${l.city}</td>
            <td>${l.project_interest}</td>
            <td>${badgeHtml}</td>
            <td style="color:var(--text-muted); font-size:11px;">${optInDate}</td>
            <td>
              <button class="btn" style="padding:4px 8px; font-size:11px; ${toggleBtnClass}" onclick="toggleLeadOptIn('${l.phone}', ${!isOptedIn})">
                ${toggleBtnLabel}
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    async function toggleLeadOptIn(phone, newOptInState) {
      await fetch('/api/leads/toggle-opt-in', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ phone, opt_in: newOptInState })
      });
      await fetchStats();
      await fetchLeads();
    }

    async function updateSimulator() {
      const projId = parseInt(document.getElementById('ctrl-project').value);
      const mediaType = document.getElementById('ctrl-media').value;
      const proj = projectsData.find(p => p.id === projId) || projectsData[0];
      if (!proj) return;

      const mediaBadge = document.getElementById('sim-media-badge');
      const heroImg = document.getElementById('sim-hero-img');

      if (mediaType === 'IMAGE') {
        mediaBadge.innerHTML = '📷 Project Hero Image';
        heroImg.src = proj.hero_image_url;
      } else if (mediaType === 'VIDEO') {
        mediaBadge.innerHTML = '🎥 Walkthrough Video Preview (MP4)';
        heroImg.src = proj.hero_image_url;
      } else {
        mediaBadge.innerHTML = '📄 Layout Master Plan (PDF Brochure)';
        heroImg.src = proj.hero_image_url;
      }

      const bodyText = 
        `👋 Hello <b>Aravind Kumar</b>,\\n\\n` +
        `🏡 <b>New Premium Layout – ${proj.name}</b>\\n` +
        `📍 <b>Location:</b> ${proj.location}\\n` +
        `📐 <b>Plot sizes:</b> ${proj.plot_sizes}\\n` +
        `💰 <b>Starting from:</b> ${proj.starting_price}\\n` +
        `✨ <b>Approvals:</b> ${proj.approval_status}\\n` +
        `🛣️ <b>Roads:</b> ${proj.road_specs}\\n` +
        `🌳 <b>Amenities:</b> ${proj.amenities}\\n\\n` +
        `Interested in reserving your preferred corner/prime plot?`;

      document.getElementById('sim-bubble-body').innerHTML = bodyText.replace(/\\n/g, '<br>');
    }

    function simulateButtonClick(action) {
      const container = document.getElementById('sim-user-reply-container');
      const userChoice = document.getElementById('sim-user-choice');
      const botReply = document.getElementById('sim-bot-reply');
      container.style.display = 'flex';

      userChoice.innerText = action;
      if (action.includes('View Layout')) {
        botReply.innerHTML = '🗺️ <b>Layout Master Plan & Plot Map</b><br><br>Available sizes: 600–2400 sq.ft. Download Brochure: <a href="#" style="color:#00a884;">green_valley_masterplan.pdf</a>';
      } else if (action.includes('Book a Plot')) {
        botReply.innerHTML = '📍 <b>Plot Reservation Slot</b><br><br>Token: ₹10,000 (100% refundable). Our Senior Plot Specialist will call you in 15 minutes!';
      } else {
        botReply.innerHTML = '📞 <b>Sales Priority Desk</b><br><br>Property Consultant Rajesh Verma will connect with you directly. Free site visit arranged on request.';
      }
    }

    async function launchCampaignFromUI() {
      const projId = parseInt(document.getElementById('ctrl-project').value);
      const city = document.getElementById('ctrl-city').value;
      const mediaType = document.getElementById('ctrl-media').value;
      const statusEl = document.getElementById('campaign-status');

      statusEl.innerText = "Launching campaign to opted-in leads...";
      try {
        const res = await fetch('/api/campaigns', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            name: `Layout Launch - ${new Date().toLocaleDateString()}`,
            project_id: projId,
            audience_city: city,
            media_type: mediaType,
            dry_run: true // simulated for instantaneous safety
          })
        });
        const data = await res.json();
        statusEl.innerText = `✔ Campaign dispatched to ${data.result.sent} eligible leads! (${data.result.ineligible_skipped} ineligible skipped)`;
        await fetchStats();
      } catch (e) {
        statusEl.innerText = "Error dispatching campaign.";
      }
    }

    async function sendTestTemplateMessage() {
      const phone = prompt("Enter test recipient phone number (e.g. 919876543210):", "919876543210");
      if (!phone) return;
      const projId = parseInt(document.getElementById('ctrl-project').value);
      const res = await fetch('/api/send-test', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ phone, project_id: projId, dry_run: true })
      });
      const data = await res.json();
      alert("Test Send Result:\\n" + JSON.stringify(data, null, 2));
    }

    async function openMetaPayloadModal() {
      const projId = parseInt(document.getElementById('ctrl-project').value);
      const mediaType = document.getElementById('ctrl-media').value;
      const res = await fetch(`/api/templates/preview?project_id=${projId}&media_type=${mediaType}`);
      const data = await res.json();
      document.getElementById('meta-json-display').innerText = JSON.stringify(data.meta_cloud_api_payload, null, 2);
      document.getElementById('metaModal').style.display = 'flex';
    }

    function closeMetaModal() {
      document.getElementById('metaModal').style.display = 'none';
    }

    function openAddLeadModal() {
      document.getElementById('addLeadModal').style.display = 'flex';
    }

    function closeAddLeadModal() {
      document.getElementById('addLeadModal').style.display = 'none';
    }

    async function submitNewLead() {
      const name = document.getElementById('new-lead-name').value.trim();
      const phone = document.getElementById('new-lead-phone').value.trim();
      const city = document.getElementById('new-lead-city').value.trim();
      const project_interest = document.getElementById('new-lead-project').value;
      const whatsapp_opt_in = document.getElementById('new-lead-optin').checked;

      if (!name || !phone) {
        alert("Please enter both Name and Phone.");
        return;
      }

      await fetch('/api/leads', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name, phone, city, project_interest, whatsapp_opt_in })
      });

      closeAddLeadModal();
      await fetchStats();
      await fetchLeads();
    }

    window.onload = initDashboard;
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"\n=======================================================")
    print(f" Real Estate WhatsApp Marketing & Template Server")
    print(f" Meta WhatsApp Cloud API Integration")
    print(f" Webhook URL:    http://0.0.0.0:{port}/webhook")
    print(f" Verify Token:   {VERIFY_TOKEN}")
    print(f" Dashboard UI:   http://127.0.0.1:{port}/")
    print(f"=======================================================\n")
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=port, reload=False)
