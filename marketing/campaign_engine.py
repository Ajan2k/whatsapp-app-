"""
Campaign Execution Engine for Real Estate WhatsApp Marketing
Handles audience segmentation, opt-in compliance filtering, throttled dispatching,
and campaign metrics aggregation.
"""

import time
import datetime
import logging
from typing import Dict, Any, Optional
import database
from whatsapp.client import WhatsAppClient
from .template_generator import RealEstateTemplateGenerator
from .compliance import ComplianceEngine

logger = logging.getLogger("CampaignEngine")


class CampaignEngine:
    """
    Orchestrates real estate WhatsApp marketing campaigns with strict opt-in filtering,
    throttled batch delivery, and comprehensive funnel tracking.
    """

    def __init__(self, whatsapp_client: Optional[WhatsAppClient] = None):
        self.whatsapp_client = whatsapp_client

    def _get_client(self) -> WhatsAppClient:
        if not self.whatsapp_client:
            self.whatsapp_client = WhatsAppClient()
        return self.whatsapp_client

    def prepare_campaign_audience(self, project_id: int, city_filter: str = "All") -> Dict[str, Any]:
        """
        Calculates campaign audience breakdown before launching:
        Total leads in pool vs. Eligible opted-in leads vs. Ineligible/Opted-out.
        """
        leads = database.get_leads(city=city_filter if city_filter != "All" else None)
        total_count = len(leads)
        eligible_leads = []
        ineligible_leads = []

        for lead in leads:
            is_eligible, reason = ComplianceEngine.can_send_marketing_message(lead)
            if is_eligible:
                eligible_leads.append(lead)
            else:
                ineligible_leads.append({"lead": lead, "reason": reason})

        return {
            "total_leads": total_count,
            "eligible_count": len(eligible_leads),
            "ineligible_count": len(ineligible_leads),
            "eligible_leads": eligible_leads,
            "ineligible_leads": ineligible_leads,
        }

    def run_campaign(
        self,
        campaign_id: int,
        dry_run: bool = False,
        throttle_seconds: float = 0.2,
        media_type: str = "IMAGE",
    ) -> Dict[str, Any]:
        """
        Executes a WhatsApp marketing campaign against opted-in leads.
        Includes rate-limiting/throttling to respect Meta's messaging tier limits.
        """
        campaign = database.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")

        project = database.get_project(campaign.get("project_id", 1))
        if not project:
            raise ValueError(f"Project with ID {campaign.get('project_id')} not found")

        # Mark campaign as running
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        database.update_campaign_metrics(campaign_id, status="RUNNING", launched_at=now_iso)

        audience = self.prepare_campaign_audience(
            project_id=project["id"],
            city_filter=campaign.get("audience_city", "All")
        )

        total_leads = audience["total_leads"]
        eligible_leads = audience["eligible_leads"]
        eligible_count = len(eligible_leads)

        sent_count = 0
        failed_count = 0
        dispatched_logs = []

        logger.info(
            "Starting Campaign '%s' (ID %d). Total Leads: %d | Eligible (Opted-In): %d",
            campaign["name"], campaign_id, total_leads, eligible_count
        )

        client = None if dry_run else self._get_client()

        for lead in eligible_leads:
            phone = lead["phone"]
            lead_name = lead["name"]

            # Construct compliant template payload
            payload = RealEstateTemplateGenerator.build_meta_template_payload(
                to_phone=phone,
                lead_name=lead_name,
                project=project,
                media_type=media_type,
                template_name=campaign.get("template_name") or RealEstateTemplateGenerator.TEMPLATE_NAME,
                language_code=campaign.get("language_code", "en_US"),
            )

            if dry_run:
                simulated_wa_id = f"wamid.SIMULATED_{int(time.time()*1000)}_{phone[-4:]}"
                database.log_message(
                    phone=phone,
                    campaign_id=campaign_id,
                    lead_id=lead["id"],
                    whatsapp_message_id=simulated_wa_id,
                    template_name=campaign.get("template_name"),
                    status="SENT",
                    media_type=media_type,
                    media_url=project.get("hero_image_url"),
                )
                sent_count += 1
                dispatched_logs.append({"phone": phone, "status": "SENT (Simulated)", "wa_id": simulated_wa_id})
            else:
                send_result = client.send_raw_payload(payload)
                if send_result.get("success"):
                    wa_data = send_result.get("data", {})
                    wa_messages = wa_data.get("messages", [])
                    wa_id = wa_messages[0].get("id") if wa_messages else None

                    database.log_message(
                        phone=phone,
                        campaign_id=campaign_id,
                        lead_id=lead["id"],
                        whatsapp_message_id=wa_id,
                        template_name=campaign.get("template_name"),
                        status="SENT",
                        media_type=media_type,
                        media_url=project.get("hero_image_url"),
                    )
                    sent_count += 1
                    dispatched_logs.append({"phone": phone, "status": "SENT", "wa_id": wa_id})
                else:
                    err_msg = send_result.get("message", "Unknown error")
                    database.log_message(
                        phone=phone,
                        campaign_id=campaign_id,
                        lead_id=lead["id"],
                        template_name=campaign.get("template_name"),
                        status="FAILED",
                        media_type=media_type,
                        error_message=err_msg,
                    )
                    failed_count += 1
                    dispatched_logs.append({"phone": phone, "status": "FAILED", "error": err_msg})

            # Throttling to prevent rate-limit throttling by Meta Cloud API
            if throttle_seconds > 0:
                time.sleep(throttle_seconds)

        # Update final campaign metrics
        database.update_campaign_metrics(
            campaign_id,
            total_leads=total_leads,
            eligible=eligible_count,
            sent=sent_count,
            failed=failed_count,
            status="COMPLETED",
        )

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "project": project["name"],
            "total_leads": total_leads,
            "eligible_leads": eligible_count,
            "sent": sent_count,
            "failed": failed_count,
            "dispatches": dispatched_logs,
            "ineligible_skipped": len(audience["ineligible_leads"]),
        }

    def send_single_project_template(
        self,
        phone: str,
        project_id: int,
        lead_name: Optional[str] = None,
        media_type: str = "IMAGE",
        dry_run: bool = False,
        direct: bool = False,
        template_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sends a single project marketing template with strict opt-in check.
        If the custom template does not exist yet in Meta WhatsApp Business Account (Error 132001),
        it automatically falls back to sending the rich Real Estate Layout message with Hero Image,
        plot specifications, and booking links.
        """
        lead = database.get_lead_by_phone(phone)
        project = database.get_project(project_id)
        if not project:
            return {"success": False, "message": f"Project ID {project_id} does not exist"}

        # Opt-in compliance check
        if lead:
            is_eligible, reason = ComplianceEngine.can_send_marketing_message(lead)
            if not is_eligible:
                return {
                    "success": False,
                    "compliance_blocked": True,
                    "message": f"Marketing send blocked by Compliance: {reason}"
                }
            name = lead["name"]
        else:
            name = lead_name or "Valued Customer"

        client = None if dry_run else self._get_client()
        rendered_text = RealEstateTemplateGenerator.format_rendered_message_text(name, project)

        # Direct Rich Real Estate Media Mode
        if direct:
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "mode": "DIRECT_MEDIA",
                    "rendered_text": rendered_text,
                }
            hero_img = project.get("hero_image_url")
            if media_type == "IMAGE" and hero_img:
                res = client.send_image(to=phone, image_url=hero_img, caption=rendered_text)
            elif media_type == "VIDEO" and project.get("walkthrough_video_url"):
                res = client.send_video(to=phone, video_url=project.get("walkthrough_video_url"), caption=rendered_text)
            else:
                res = client.send_text_message(to=phone, message=rendered_text)

            if res.get("success"):
                database.log_message(
                    phone=phone,
                    lead_id=lead["id"] if lead else None,
                    whatsapp_message_id=(res.get("data", {}).get("messages", [{}])[0]).get("id"),
                    template_name="direct_real_estate_media",
                    status="SENT",
                    media_type=media_type,
                    media_url=hero_img,
                )
            return res

        # Template Mode
        tmpl = template_name or RealEstateTemplateGenerator.TEMPLATE_NAME

        # Special handling for Meta's built-in hello_world template (expects 0 parameters)
        if tmpl == "hello_world":
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "mode": "TEMPLATE",
                    "template_name": "hello_world",
                    "rendered_text": "Hello World test template",
                }
            result = client.send_template_message(to=phone, template_name="hello_world", language_code="en_US")
            if result.get("success"):
                wa_data = result.get("data", {})
                msgs = wa_data.get("messages", [])
                wa_id = msgs[0].get("id") if msgs else None
                database.log_message(
                    phone=phone,
                    lead_id=lead["id"] if lead else None,
                    whatsapp_message_id=wa_id,
                    template_name="hello_world",
                    status="SENT",
                    media_type="TEMPLATE",
                )
            return result

        payload = RealEstateTemplateGenerator.build_meta_template_payload(
            to_phone=phone,
            lead_name=name,
            project=project,
            media_type=media_type,
            template_name=tmpl,
        )

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "mode": "TEMPLATE",
                "payload": payload,
                "rendered_text": rendered_text,
            }

        result = client.send_raw_payload(payload)

        # Automatic Fallback: If template is not registered in Meta yet (Error 132001)
        if not result.get("success") and result.get("error_code") == 132001:
            logger.info(
                "Template '%s' is not yet approved in Meta WhatsApp Manager. "
                "Automatically falling back to direct Real Estate Layout message...", tmpl
            )
            hero_img = project.get("hero_image_url")
            if media_type == "IMAGE" and hero_img:
                fallback_res = client.send_image(to=phone, image_url=hero_img, caption=rendered_text)
            elif media_type == "VIDEO" and project.get("walkthrough_video_url"):
                fallback_res = client.send_video(to=phone, video_url=project.get("walkthrough_video_url"), caption=rendered_text)
            else:
                fallback_res = client.send_text_message(to=phone, message=rendered_text)

            if fallback_res.get("success"):
                fallback_res["fallback_used"] = True
                fallback_res["note"] = (
                    f"Template '{tmpl}' is not yet created in your Meta WhatsApp Manager. "
                    "Successfully delivered via direct Real Estate Layout message with Hero Image and project specifications!"
                )
                wa_data = fallback_res.get("data", {})
                wa_id = (wa_data.get("messages", [{}])[0]).get("id")
                database.log_message(
                    phone=phone,
                    lead_id=lead["id"] if lead else None,
                    whatsapp_message_id=wa_id,
                    template_name="direct_fallback_media",
                    status="SENT",
                    media_type=media_type,
                    media_url=hero_img,
                )
                return fallback_res

        # Log template dispatch
        if result.get("success"):
            wa_data = result.get("data", {})
            wa_id = (wa_data.get("messages", [{}])[0]).get("id")
            database.log_message(
                phone=phone,
                lead_id=lead["id"] if lead else None,
                whatsapp_message_id=wa_id,
                template_name=tmpl,
                status="SENT",
                media_type=media_type,
            )

        return result
