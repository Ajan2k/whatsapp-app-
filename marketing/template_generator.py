"""
Meta WhatsApp Cloud API Marketing Template Generator
Generates Meta-compliant template payloads, media components, interactive buttons,
and Meta WhatsApp Manager registration structures for Real Estate layouts.
"""

from typing import Dict, Any, List, Optional


class RealEstateTemplateGenerator:
    """
    Generates Meta WhatsApp Cloud API template message payloads specifically tailored
    for Real Estate plot/layout launches and block booking.
    """

    TEMPLATE_NAME = "real_estate_launch_v1"
    DEFAULT_LANGUAGE = "en_US"

    @classmethod
    def format_rendered_message_text(cls, lead_name: str, project: Dict[str, Any]) -> str:
        """
        Renders the human-readable text preview of the real estate marketing template.
        """
        name = lead_name or "Valued Customer"
        p_name = project.get("name", "Green Valley")
        loc = project.get("location", "Tambaram, Chennai")
        sizes = project.get("plot_sizes", "600-2400 sq.ft")
        price = project.get("starting_price", "28 Lakhs")
        approvals = project.get("approval_status", "DTCP Approved")
        roads = project.get("road_specs", "30ft roads")
        amenities = project.get("amenities", "Park, Water")
        city = project.get("city", "Chennai")

        return (
            f"*New Layout Launch - {city}*\n\n"
            f"Hello {name},\n\n"
            f"🏡 New Premium Layout: {p_name}\n"
            f"📍 Location: {loc}\n"
            f"📐 Plot sizes: {sizes}\n"
            f"💰 Starting: {price}\n"
            f"✨ Approvals: {approvals}\n"
            f"🛣️ Roads & Amenities: {roads}, {amenities}\n\n"
            f"Interested in booking your preferred plot?\n"
            f"Reply STOP to unsubscribe • ABC Properties"
        )

    @classmethod
    def build_meta_template_payload(
        cls,
        to_phone: str,
        lead_name: str,
        project: Dict[str, Any],
        media_type: str = "IMAGE",
        template_name: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Constructs the exact Meta WhatsApp Business Cloud API JSON payload
        for sending a pre-approved Marketing Template message.
        """
        tmpl_name = template_name or cls.TEMPLATE_NAME
        lang_code = language_code or cls.DEFAULT_LANGUAGE

        # Specific handler for the approved 'real_estate_launch_v1' Meta template
        if tmpl_name == "real_estate_launch_v1":
            city_val = project.get("city") or "Chennai"
            amenities_val = f"{project.get('road_specs', '30ft roads')}, {project.get('amenities', 'Park, Water')}"
            components = [
                {
                    "type": "header",
                    "parameters": [
                        {"type": "text", "text": str(city_val)}
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(lead_name or "Aravind")},
                        {"type": "text", "text": str(project.get("name", "Green Valley"))},
                        {"type": "text", "text": str(project.get("location", "Tambaram, Chennai"))},
                        {"type": "text", "text": str(project.get("plot_sizes", "600-2400 sq.ft"))},
                        {"type": "text", "text": str(project.get("starting_price", "28 Lakhs"))},
                        {"type": "text", "text": str(project.get("approval_status", "DTCP Approved"))},
                        {"type": "text", "text": str(amenities_val[:100])},
                    ]
                }
            ]
            return {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": "template",
                "template": {
                    "name": tmpl_name,
                    "language": {"code": lang_code},
                    "components": components,
                },
            }

        # Generic / Media Header Component (Media: IMAGE, VIDEO, or DOCUMENT)
        components: List[Dict[str, Any]] = []

        clean_media = (media_type or "IMAGE").upper()
        if clean_media == "IMAGE":
            img_url = project.get("hero_image_url") or "https://images.unsplash.com/photo-1592595896551-12b371d546d5?auto=format&fit=crop&w=1200&q=80"
            components.append({
                "type": "header",
                "parameters": [
                    {
                        "type": "image",
                        "image": {"link": img_url}
                    }
                ]
            })
        elif clean_media == "VIDEO":
            video_url = project.get("walkthrough_video_url") or "https://www.w3schools.com/html/mov_bbb.mp4"
            components.append({
                "type": "header",
                "parameters": [
                    {
                        "type": "video",
                        "video": {"link": video_url}
                    }
                ]
            })
        elif clean_media == "DOCUMENT":
            doc_url = project.get("brochure_pdf_url") or "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
            components.append({
                "type": "header",
                "parameters": [
                    {
                        "type": "document",
                        "document": {
                            "link": doc_url,
                            "filename": f"{project.get('name', 'Project')}_Layout_Brochure.pdf"
                        }
                    }
                ]
            })

        # Body Component (Dynamic parameter placeholders {{1}} to {{7}})
        body_params = [
            {"type": "text", "text": lead_name or "Homebuyer"},
            {"type": "text", "text": str(project.get("name", "Premium Layout"))},
            {"type": "text", "text": str(project.get("location", "Prime Area"))},
            {"type": "text", "text": str(project.get("plot_sizes", "600–2400 sq.ft"))},
            {"type": "text", "text": str(project.get("starting_price", "Best in Market"))},
            {"type": "text", "text": str(project.get("approval_status", "Approved"))},
            {"type": "text", "text": f"{project.get('road_specs', 'Wide Roads')} | {project.get('amenities', 'Clubhouse')}"},
        ]

        components.append({
            "type": "body",
            "parameters": body_params,
        })

        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": tmpl_name,
                "language": {"code": lang_code},
                "components": components,
            },
        }

    @classmethod
    def build_meta_interactive_message(
        cls,
        to_phone: str,
        lead_name: str,
        project: Dict[str, Any],
        media_type: str = "IMAGE",
    ) -> Dict[str, Any]:
        """
        Builds a Meta Cloud API Interactive Button message (valid for 24-hour service window
        or testing). Directly displays clickable buttons: [View Layout] [Book a Plot] [Talk to Sales]
        """
        header_payload: Dict[str, Any] = {}
        clean_media = (media_type or "IMAGE").upper()
        if clean_media == "IMAGE":
            header_payload = {
                "type": "image",
                "image": {
                    "link": project.get("hero_image_url") or "https://images.unsplash.com/photo-1592595896551-12b371d546d5?auto=format&fit=crop&w=1200&q=80"
                }
            }
        elif clean_media == "VIDEO":
            header_payload = {
                "type": "video",
                "video": {
                    "link": project.get("walkthrough_video_url") or "https://www.w3schools.com/html/mov_bbb.mp4"
                }
            }

        body_text = (
            f"🏡 *New Premium Layout Launch – {project.get('name')}*\n"
            f"📍 *Location:* {project.get('location')}\n"
            f"📐 *Plot sizes:* {project.get('plot_sizes')}\n"
            f"💰 *Starting from:* {project.get('starting_price')}\n"
            f"✨ *Approvals:* {project.get('approval_status')}\n"
            f"🛣️ *Roads:* {project.get('road_specs')}\n"
            f"🌳 *Amenities:* {project.get('amenities')}\n\n"
            f"Interested in reserving your plot, {lead_name}?"
        )

        interactive_payload = {
            "type": "button",
            "body": {"text": body_text},
            "footer": {"text": "Reply STOP to unsubscribe • ABC Properties"},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": f"action_view_layout_{project.get('id', 1)}",
                            "title": "🗺️ View Layout"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": f"action_book_plot_{project.get('id', 1)}",
                            "title": "📍 Book a Plot"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": f"action_talk_sales_{project.get('id', 1)}",
                            "title": "📞 Talk to Sales"
                        }
                    }
                ]
            }
        }

        if header_payload:
            interactive_payload["header"] = header_payload

        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": interactive_payload,
        }

    @classmethod
    def get_meta_registration_schema(cls) -> Dict[str, Any]:
        """
        Returns the official JSON schema required when creating/registering this template
        in Meta WhatsApp Business Manager or via Graph API POST /{waba_id}/message_templates.
        """
        return {
            "name": cls.TEMPLATE_NAME,
            "category": "MARKETING",
            "language": cls.DEFAULT_LANGUAGE,
            "components": [
                {
                    "type": "HEADER",
                    "format": "IMAGE",
                    "example": {
                        "header_handle": ["https://images.unsplash.com/photo-1592595896551-12b371d546d5?auto=format&fit=crop&w=1200&q=80"]
                    }
                },
                {
                    "type": "BODY",
                    "text": (
                        "Hello {{1}},\n\n"
                        "🏡 New Premium Layout Launch – {{2}}\n"
                        "📍 Location: {{3}}\n"
                        "📐 Plot sizes: {{4}}\n"
                        "💰 Starting from: {{5}}\n"
                        "✨ Approvals: {{6}}\n"
                        "🛣️ Roads & Amenities: {{7}}\n\n"
                        "Interested in reserving your preferred corner/prime plot?"
                    ),
                    "example": {
                        "body_text": [
                            [
                                "Aravind Kumar",
                                "Green Valley Emerald",
                                "Tambaram West, Chennai",
                                "600–2400 sq.ft",
                                "₹28 Lakhs",
                                "DTCP Approved",
                                "30 ft / 40 ft roads, Children Park, 24/7 Water"
                            ]
                        ]
                    }
                },
                {
                    "type": "FOOTER",
                    "text": "Reply STOP to unsubscribe • ABC Properties"
                },
                {
                    "type": "BUTTONS",
                    "buttons": [
                        {
                            "type": "URL",
                            "text": "View Layout",
                            "url": "https://realestate-demo.example.com/book/{{1}}",
                            "example": ["green-valley"]
                        },
                        {
                            "type": "QUICK_REPLY",
                            "text": "Book a Plot"
                        },
                        {
                            "type": "QUICK_REPLY",
                            "text": "Talk to Sales"
                        }
                    ]
                }
            ]
        }
