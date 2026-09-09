"""
Compliance and Opt-In / Opt-Out Engine for Meta WhatsApp Marketing
Ensures strict compliance with Meta's Business Messaging Opt-In policies,
per-user throttling, and automatic opt-out (STOP) handling.
"""

import logging
from typing import Dict, Any, Tuple, Optional
import database

logger = logging.getLogger("ComplianceEngine")


class ComplianceEngine:
    """
    Guarantees strict opt-in verification and opt-out processing.
    Meta mandates: Businesses must obtain opt-in before sending WhatsApp message templates.
    """

    OPT_OUT_KEYWORDS = {
        "stop",
        "unsubscribe",
        "optout",
        "opt-out",
        "opt out",
        "cancel",
        "halt",
        "revoke",
        "remove me",
    }

    OPT_IN_KEYWORDS = {
        "start",
        "optin",
        "opt-in",
        "opt in",
        "subscribe",
        "join",
    }

    INTERACTION_KEYWORDS = {
        "interested": "INTERESTED",
        "book a plot": "BOOKING_REQUEST",
        "book plot": "BOOKING_REQUEST",
        "view layout": "LAYOUT_REQUEST",
        "talk to sales": "SALES_REQUEST",
        "call": "SALES_REQUEST",
        "price": "PRICING_REQUEST",
    }

    @classmethod
    def can_send_marketing_message(cls, lead: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates whether a lead has given explicit consent and is eligible
        to receive marketing templates.
        """
        if not lead:
            return False, "Lead record not found"

        # Check opt-in flag
        opt_in = lead.get("whatsapp_opt_in")
        if not opt_in or int(opt_in) != 1:
            return False, "Lead has not provided explicit WhatsApp opt-in consent (Opt-In is False)"

        # Check opt-out timestamp
        if lead.get("opt_out_timestamp"):
            return False, f"Lead previously opted out on {lead.get('opt_out_timestamp')}"

        # Check status
        status = str(lead.get("status", "")).upper()
        if status in ("OPTED_OUT", "UNVERIFIED", "BLOCKED"):
            return False, f"Lead status is {status}; marketing messages are blocked"

        return True, "Eligible for WhatsApp marketing"

    @classmethod
    def check_and_handle_inbound(cls, phone: str, text: str, button_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Inspects incoming message or button clicks for compliance keywords (STOP/START)
        or buyer interaction events (Interested, Book a Plot, Talk to Sales).
        """
        raw_text = (text or "").strip().lower()
        btn = (button_id or "").strip().lower()

        # 1. Check Opt-Out ('STOP', 'UNSUBSCRIBE', etc.)
        if raw_text in cls.OPT_OUT_KEYWORDS or "stop" in raw_text:
            logger.info("Compliance: Opt-out triggered for phone %s with text '%s'", phone, text)
            database.set_lead_opt_out(phone, reason=f"Replied: '{text}'")
            return {
                "action": "OPT_OUT",
                "reply": (
                    "✅ You have been successfully unsubscribed from ABC Properties WhatsApp updates. "
                    "You will not receive further promotional messages from us.\n\n"
                    "Reply *START* at any time if you wish to re-subscribe."
                )
            }

        # 2. Check Opt-In Reactivation ('START', etc.)
        if raw_text in cls.OPT_IN_KEYWORDS:
            logger.info("Compliance: Opt-in reactivation triggered for phone %s", phone)
            database.set_lead_opt_in(phone, source="Replied: START")
            return {
                "action": "OPT_IN",
                "reply": (
                    "🎉 Welcome back! You have successfully re-subscribed to ABC Properties WhatsApp updates. "
                    "You will receive exclusive early-bird layout launches, plot booking discounts, and project approvals."
                )
            }

        # 3. Check Real Estate Interactive Actions
        lead = database.get_lead_by_phone(phone)
        lead_name = lead.get("name", "Sir/Madam") if lead else "Sir/Madam"

        # Action: Book a Plot / Reserve / Token (Option 2)
        if any(k in btn for k in ["book_plot", "book", "reserve"]) or \
           any(k in raw_text for k in [
               "book a plot", "book plot", "book", "booking", "reserve", "reserve plot",
               "block plot", "token", "buy", "purchase", "advance", "how to book"
           ]) or raw_text == "2":
            return {
                "action": "BOOK_PLOT",
                "intent": "BOOKED",
                "reply": (
                    f"📍 *Reserve Your Plot – Fast-Track Booking*\n\n"
                    f"Great decision, {lead_name}! Follow these 3 simple steps to lock in your plot:\n\n"
                    f"1️⃣ *Choose Your Plot Number:* Plots #12, #18 (East Facing), #24 (Corner), and #35 are currently available.\n"
                    f"2️⃣ *Refundable Token Booking:* Pay ₹10,000 to hold the plot for 7 days (100% refundable).\n"
                    f"3️⃣ *Bank Loan Tie-Ups:* Pre-approved 80% home/plot loans via SBI, HDFC & ICICI.\n\n"
                    f"🔗 *Online Booking Portal:* https://realestate-demo.example.com/book/green-valley\n\n"
                    f"Our Senior Relationship Manager is reserving your slot and will connect with you in 10 minutes to assist with documentation!"
                )
            }

        # Action: View Layout / View Plot / Master Plan (Option 1)
        if any(k in btn for k in ["view_layout", "view_plot", "layout"]) or \
           any(k in raw_text for k in [
               "view layout", "view plot", "view plots", "layout", "plot map",
               "master plan", "site plan", "map", "layout plan", "plot plan", "plot layout",
               "dimensions", "plot availability", "layout map"
           ]) or raw_text in ["plot", "plots", "1"]:
            return {
                "action": "VIEW_LAYOUT",
                "intent": "INTERESTED",
                "reply": (
                    f"🗺️ *Layout Master Plan & Plot Availability*\n\n"
                    f"Hi {lead_name}, here is the layout breakdown for *Green Valley Emerald (Tambaram West, Chennai)*:\n\n"
                    f"📐 *Available Plot Dimensions:*\n"
                    f" • 600 sq.ft (20x30) – ₹14 Lakhs\n"
                    f" • 1200 sq.ft (30x40) – ₹28 Lakhs [Popular]\n"
                    f" • 1500 sq.ft (30x50) – ₹35 Lakhs\n"
                    f" • 2400 sq.ft (40x60 Corner) – ₹56 Lakhs\n\n"
                    f"🏛️ *Approvals:* 100% DTCP & RERA Approved with Clear Title Deed\n"
                    f"🛣️ *Infrastructure:* 30ft & 40ft Blacktop Tar Roads, Avenue Trees, Underground Water & Electricity\n\n"
                    f"📄 *Download Master Plan PDF:* https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf\n"
                    f"🌐 *Interactive Plot Viewer:* https://realestate-demo.example.com/layout-map\n\n"
                    f"👉 Reply *BOOK* to reserve a plot, or *PLANS* to see other project locations!"
                )
            }

        # Action: Other Plans / Other Projects / Portfolio (Option 3)
        if any(k in btn for k in ["other_plans", "plans", "projects"]) or \
           any(k in raw_text for k in [
               "other plans", "other plan", "plans", "plan", "other projects", "all projects",
               "projects", "more projects", "options", "different plots", "other layouts",
               "locations", "bangalore", "chennai"
           ]) or raw_text == "3":
            return {
                "action": "OTHER_PLANS",
                "intent": "INTERESTED",
                "reply": (
                    f"🏘️ *ABC Properties – Active Layout Projects & Master Plans*\n\n"
                    f"Hi {lead_name}, explore our full portfolio of approved residential layouts:\n\n"
                    f"1️⃣ *Green Valley Emerald* – Tambaram West, Chennai\n"
                    f"   • Plots: 600–2400 sq.ft | Starting: ₹28 Lakhs\n"
                    f"   • Status: DTCP Approved • Ready to Build\n\n"
                    f"2️⃣ *Sunrise Palm Meadows* – Sarjapur Road, Bangalore\n"
                    f"   • Plots: 1200–3000 sq.ft | Starting: ₹45 Lakhs\n"
                    f"   • Status: BDA & RERA Approved • Gated Luxury Layout\n\n"
                    f"3️⃣ *ECR Grand Ocean Breeze* – East Coast Road, Chennai\n"
                    f"   • Plots: 1500–3200 sq.ft | Starting: ₹38 Lakhs\n"
                    f"   • Status: CMDA Approved • Beachside Villa Plots\n\n"
                    f"👉 Reply with *1*, *2*, or *3* to get the complete layout plan & price sheet for that project!"
                )
            }

        # Action: Talk to Sales / Schedule Site Visit (Option 4)
        if any(k in btn for k in ["talk_sales", "sales", "call"]) or \
           any(k in raw_text for k in [
               "talk to sales", "talk to sale", "sales", "call", "contact", "speak",
               "representative", "advisor", "agent", "site visit", "visit", "phone"
           ]) or raw_text == "4":
            return {
                "action": "TALK_TO_SALES",
                "intent": "INTERESTED",
                "reply": (
                    f"📞 *Sales Priority Desk – ABC Properties*\n\n"
                    f"Hello {lead_name}, our Senior Property Advisor is assigned to you:\n\n"
                    f"👤 *Advisor:* Rajesh Verma (Senior Plot Specialist)\n"
                    f"📱 *Direct Hotline:* +91 98765 00000\n"
                    f"🕒 *Working Hours:* Mon–Sun, 9:00 AM – 7:00 PM\n\n"
                    f"🚗 *Complimentary Site Visit:* We provide free cab pickup and drop from your home for you and your family!\n\n"
                    f"Would you like us to schedule your visit for this Saturday or Sunday?"
                )
            }

        # General inquiry or interest
        if any(k in raw_text for k in ["interested", "yes", "price", "pricing", "cost", "details", "info"]):
            return {
                "action": "GENERAL_INTEREST",
                "intent": "INTERESTED",
                "reply": (
                    f"Thank you for your interest, {lead_name}! 🏡\n\n"
                    f"Green Valley Emerald is offering launch-day benefits including:\n"
                    f"✨ Free DTCP registration fees\n"
                    f"✨ Free clubhouse 2-year membership\n"
                    f"✨ Instant 5% booking discount\n\n"
                    f"How would you like to proceed?\n"
                    f"1️⃣ View Layout & Plot Dimensions\n"
                    f"2️⃣ Reserve a Plot with ₹10,000 token\n"
                    f"3️⃣ View Other Projects (Bangalore / ECR)\n"
                    f"4️⃣ Speak with Sales Representative\n\n"
                    f"👉 Reply with *1, 2, 3, or 4*!"
                )
            }

        # Smart Interactive Menu Fallback for any other message
        return {
            "action": "MENU",
            "intent": "INTERESTED",
            "reply": (
                f"👋 Hello {lead_name}! Welcome to ABC Properties.\n\n"
                f"How can we assist you with your plot investment today?\n\n"
                f"1️⃣ *View Layout* – Master plan, dimensions & plot availability\n"
                f"2️⃣ *Book a Plot* – Reserve your plot online with ₹10,000 token\n"
                f"3️⃣ *Other Plans* – Explore Bangalore & ECR layout projects\n"
                f"4️⃣ *Talk to Sales* – Free site visit with cab pickup & drop\n\n"
                f"👉 Simply reply with *1, 2, 3, or 4* (or type your question)!"
            )
        }
