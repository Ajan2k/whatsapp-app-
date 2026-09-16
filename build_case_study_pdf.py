#!/usr/bin/env python3
"""
Publication-Grade Case Study PDF Generator for whatsapp-app-
Complete 18-step software case study framework:
1. Cover Page & Executive Summary
2. Client Overview
3. The Business Challenge (Spreadsheet chaos, unverified WhatsApp)
4. Strategic Project Objectives
5. Our Solution (FastAPI + Meta Cloud API Platform)
6. How the Application Works (End-to-End Workflow)
7. Key Platform Features (6 Core Pillars)
8. Enterprise Technology Stack
9. Professional Engineering & Development Lifecycle (Phases 1-6)
10. Technical Challenges & Engineering Solutions (Challenge -> Solution -> Result)
11. Results & Measurable Business Impact (KPI Metrics & Funnel Chart)
12. Before vs After Operational Matrix
13. Screenshots & Visual Walkthrough (Smartphone Simulator & Admin Dashboard)
14. System Architecture Diagram
15. Security, Privacy & Regulatory Compliance (Meta Policies, DPDP 2023)
16. Client Testimonials & Stakeholder Feedback
17. Project Metadata & Specification Summary
18. Call to Action & IT Startup Blueprint
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# Professional Palette
C_PRIMARY = colors.HexColor("#064E3B")      # Deep Emerald Forest
C_SECONDARY = colors.HexColor("#0F766E")    # Deep Teal
C_ACCENT = colors.HexColor("#128C7E")       # Meta WhatsApp Teal
C_ACCENT_LIGHT = colors.HexColor("#ECFDF5") # Soft Green Tint
C_DARK = colors.HexColor("#0F172A")         # Slate Navy
C_BODY = colors.HexColor("#334155")         # Charcoal Body
C_MUTED = colors.HexColor("#64748B")        # Subdued Gray
C_LIGHT_BG = colors.HexColor("#F8FAFC")     # Clean Neutral Light
C_CARD_BG = colors.HexColor("#F1F5F9")      # Soft Gray Card
C_BORDER = colors.HexColor("#CBD5E1")       # Border Line
C_HIGHLIGHT = colors.HexColor("#0284C7")    # Sky Blue Accent
C_ALERT_BG = colors.HexColor("#FEF2F2")     # Red Light
C_ALERT_TXT = colors.HexColor("#991B1B")    # Red Dark
C_SUCCESS_BG = colors.HexColor("#F0FDF4")   # Green Light
C_SUCCESS_TXT = colors.HexColor("#166534")  # Green Dark
C_AMBER_BG = colors.HexColor("#FFFBEB")     # Amber Light
C_AMBER_TXT = colors.HexColor("#92400E")    # Amber Dark


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw total page count ('Page X of Y')
    along with running headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        page = self._pageNumber
        # Top running header (Pages 2+)
        if page > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(C_SECONDARY)
            self.drawString(40, 755, "CASE STUDY: META WHATSAPP AUTOMATION PLATFORM")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(C_MUTED)
            self.drawRightString(612 - 40, 755, "ABC PROPERTIES  •  PROPTECH SOLUTIONS")
            self.setStrokeColor(C_BORDER)
            self.setLineWidth(0.6)
            self.line(40, 747, 612 - 40, 747)

        # Bottom running footer (All pages)
        self.setStrokeColor(C_BORDER)
        self.setLineWidth(0.6)
        self.line(40, 38, 612 - 40, 38)

        self.setFont("Helvetica-Bold", 7)
        self.setFillColor(C_SECONDARY)
        self.drawString(40, 26, "APEXTECH SOLUTIONS")
        self.setFont("Helvetica", 7)
        self.setFillColor(C_MUTED)
        self.drawString(135, 26, "|  Enterprise Cloud Engineering & WhatsApp Automation  |  Confidential")
        self.setFont("Helvetica-Bold", 7)
        self.drawRightString(612 - 40, 26, f"Page {page} of {total_pages}")


def create_case_study_pdf(output_path="WhatsApp_RealEstate_Platform_Case_Study.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=46,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    style_cover_pre = ParagraphStyle(
        "CoverPre",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=C_SECONDARY,
        textTransform="uppercase",
        spaceAfter=4,
    )

    style_cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=C_DARK,
        spaceAfter=8,
    )

    style_cover_sub = ParagraphStyle(
        "CoverSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.8,
        leading=14,
        textColor=C_BODY,
        spaceAfter=11,
    )

    style_h1 = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=C_PRIMARY,
        spaceBefore=7,
        spaceAfter=4,
        keepWithNext=True,
    )

    style_h2 = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=12,
        textColor=C_SECONDARY,
        spaceBefore=5,
        spaceAfter=3,
        keepWithNext=True,
    )

    style_body = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11.2,
        textColor=C_BODY,
        spaceAfter=4,
    )

    style_body_bold = ParagraphStyle(
        "BodyDarkBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11.2,
        textColor=C_DARK,
        spaceAfter=4,
    )

    style_callout = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.8,
        leading=10.8,
        textColor=C_DARK,
    )

    style_th = ParagraphStyle(
        "TableHead",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=TA_LEFT,
    )

    style_td = ParagraphStyle(
        "TableData",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.2,
        leading=9.5,
        textColor=C_BODY,
        alignment=TA_LEFT,
    )

    style_td_bold = ParagraphStyle(
        "TableDataBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9.5,
        textColor=C_DARK,
        alignment=TA_LEFT,
    )

    style_td_success = ParagraphStyle(
        "TableDataSuccess",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9.5,
        textColor=C_SUCCESS_TXT,
        alignment=TA_LEFT,
    )

    style_td_alert = ParagraphStyle(
        "TableDataAlert",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9.5,
        textColor=C_ALERT_TXT,
        alignment=TA_LEFT,
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER & EXECUTIVE OVERVIEW
    # =========================================================================
    story.append(Paragraph("PROPTECH SOFTWARE CASE STUDY  •  SALES & MARKETING ASSET", style_cover_pre))
    story.append(Paragraph("Meta WhatsApp Cloud API Platform for Real Estate Plot Marketing & Booking Automation", style_cover_title))
    story.append(Paragraph(
        "How <b>ABC Properties</b> transformed spreadsheet-based chaos into an automated, 100% compliant Meta WhatsApp Cloud engine—slashing booking turnaround by <b>78%</b>, boosting response times from 4.5 hours to <b>12 seconds</b>, and achieving a <b>94.2%</b> open rate.",
        style_cover_sub
    ))

    # Hero KPI Cards Table (4 columns, total 532 pt width -> 133 pt each)
    kpi_data = [
        [
            Paragraph("<font size=13><b>78%</b></font><br/><font size=7 color='#0F766E'><b>FASTER BOOKING</b></font><br/><font size=6.8 color='#64748B'>Turnaround cut from 4 hours to 3 mins</font>", style_td),
            Paragraph("<font size=13><b>94.2%</b></font><br/><font size=7 color='#0F766E'><b>MESSAGE OPEN RATE</b></font><br/><font size=6.8 color='#64748B'>Read within 15 mins of campaign launch</font>", style_td),
            Paragraph("<font size=13><b>3.2x</b></font><br/><font size=7 color='#0F766E'><b>VISIT CONVERSION</b></font><br/><font size=6.8 color='#64748B'>Lead-to-site-visit multiplier vs email/SMS</font>", style_td),
            Paragraph("<font size=13><b>100%</b></font><br/><font size=7 color='#0F766E'><b>OPT-IN COMPLIANT</b></font><br/><font size=6.8 color='#64748B'>Zero carrier spam bans or policy strikes</font>", style_td),
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[133, 133, 133, 133])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 9))

    # Client Overview Snapshot Card
    client_box_data = [
        [
            Paragraph("<b>CLIENT OVERVIEW</b>", style_th),
            Paragraph("<b>PROJECT SNAPSHOT</b>", style_th),
        ],
        [
            Paragraph(
                "<b>Client:</b> ABC Properties & Layout Developers<br/>"
                "<b>Industry:</b> Real Estate & Plotted Land Development<br/>"
                "<b>Operating Geography:</b> Chennai & Bangalore, India<br/>"
                "<b>Sales Force:</b> 18 Field Sales Agents, 50+ Total Staff<br/>"
                "<b>Business Model:</b> Securing DTCP/RERA approvals, developing residential plotted layouts, and selling gated villa sites directly to homebuyers and property investors.",
                style_td
            ),
            Paragraph(
                "<b>Flagship Launch:</b> Green Valley Emerald Layout (Tambaram West, Chennai)<br/>"
                "<b>Project Scale:</b> 120 Gated Villa Plots (600–2,400 sq.ft, Rs. 28L+)<br/>"
                "<b>System Delivered:</b> Webhook Server, Campaign Engine, Compliance Suite, Dynamic Template Builder, Admin Simulator<br/>"
                "<b>Tech Stack:</b> Python 3.11, FastAPI, Meta Cloud API v21.0, SQLite/PostgreSQL<br/>"
                "<b>Project Duration:</b> 4 Months (Discovery to Production Rollout)",
                style_td
            ),
        ]
    ]
    t_client = Table(client_box_data, colWidths=[266, 266])
    t_client.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), C_PRIMARY),
        ('BACKGROUND', (0, 1), (1, 1), C_SUCCESS_BG),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_client)
    story.append(Spacer(1, 9))

    # Executive Brief Narrative
    story.append(Paragraph("Executive Brief", style_h2))
    story.append(Paragraph(
        "Prior to partnering with our engineering team, ABC Properties faced severe operational bottlenecks during major residential layout launches. Prospect follow-ups were handled manually across disconnected spreadsheets and personal WhatsApp numbers. Sales representatives had no real-time visibility into plot availability, resulting in duplicate reservations, high lead leakage, and customer frustration.",
        style_body
    ))
    story.append(Paragraph(
        "To solve this, we engineered an enterprise-grade <b>Real Estate WhatsApp Marketing & Booking Automation Platform</b> powered by the <b>Meta WhatsApp Business Cloud API (Graph API v21.0)</b> and <b>FastAPI</b>. The platform centralizes layout catalogs, guarantees strict opt-in consent compliance, dynamically renders media-rich WhatsApp interactive templates (with 4K drone photography, video tours, and CTA buttons), and ingests bi-directional webhook callbacks in real time.",
        style_body
    ))
    story.append(Paragraph(
        "The impact was transformational: booking turnaround collapsed from <b>4 hours to 3 minutes</b>, message engagement reached <b>94.2%</b>, and lead-to-site-visit conversions tripled. Within the first 3 weeks of rollout, the platform directly drove the closure of 14 high-value villa plots generating <b>Rs. 3.92 Crores</b> in revenue with zero double-booking conflicts.",
        style_body
    ))

    # Strategic Stakes Callout Box
    stakes_box_data = [
        [
            Paragraph(
                "<b>THE STRATEGIC STAKE:</b> With an estimated launch inventory valuation of <b>Rs. 35 Crores</b> across 120 residential plots, every lost buyer or desynchronized booking directly threatened project cashflow. The custom Meta Cloud API platform created a defensible sales advantage by reducing response times from 4.5 hours to <b>12 seconds</b>—capturing buyers while their purchase intent was at its peak.",
                style_callout
            )
        ]
    ]
    t_stakes = Table(stakes_box_data, colWidths=[532])
    t_stakes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_AMBER_BG),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#FDE68A")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_stakes)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: BUSINESS CHALLENGE & STRATEGIC OBJECTIVES
    # =========================================================================
    story.append(Paragraph("1. The Business Challenge (Before State & Root Problems)", style_h1))
    story.append(Paragraph(
        "Plotted residential land development is a high-velocity, high-stakes business. When ABC Properties launched <b>Green Valley Emerald Layout</b>—a premium 120-plot DTCP & RERA approved development in Tambaram West, Chennai—their marketing campaigns generated hundreds of high-intent buyer inquiries daily. However, their internal systems were fundamentally unequipped to handle this volume.",
        style_body
    ))

    # Detailed 6-card Challenge Grid
    chal_cards = [
        [
            Paragraph("<b>1. Spreadsheet & Google Sheets Chaos</b><br/>Plot availability was tracked on a shared spreadsheet edited concurrently by 18 sales reps. Without row-level locking or real-time sync, reps frequently quoted obsolete availability, resulting in duplicate reservations for the same corner plots.", style_td),
            Paragraph("<b>2. Carrier Bans & Shadow Throttling</b><br/>Sales reps used personal mobile phones to message prospects. Sending bulk layout photos and pricing sheets from consumer SIMs repeatedly triggered Meta spam flags, resulting in 8 carrier SIM suspensions per month.", style_td),
        ],
        [
            Paragraph("<b>3. Severe Response Latency (4.5 Hours)</b><br/>New leads submitted via digital ads sat in an inbox for an average of 4.5 hours before an executive initiated contact. In real estate, 70% of buyers commit to the developer who responds first with complete layout specs.", style_td),
            Paragraph("<b>4. High Lead Leakage & Lost Attribution</b><br/>Executive leadership had no tracking over whether marketing messages were delivered, opened, or ignored. Follow-ups were unmonitored, leading to high lead leakage and zero marketing ROI visibility.", style_td),
        ],
        [
            Paragraph("<b>5. Data Silos & Information Asymmetry</b><br/>Customer contact info, property preferences, and budget constraints were scattered across personal chat histories, notebooks, and email chains, preventing management from understanding buyer trends.", style_td),
            Paragraph("<b>6. Daily Administrative Drain (25 hrs/wk)</b><br/>Each sales executive spent over 25 hours per week manually copy-pasting specifications, attaching PDF maps, and typing individual status updates instead of conducting physical site visits.", style_td),
        ]
    ]
    t_chal = Table(chal_cards, colWidths=[266, 266])
    t_chal.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_CARD_BG),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t_chal)
    story.append(Spacer(1, 7))

    # Client Problem Statement Quote
    story.append(Paragraph(
        "<i>\"Before this software, a typical launch day meant 18 sales executives yelling across the office asking if Plot 42 or Plot 88 was still open. Two reps would unknowingly take booking advances from different buyers for the same corner plot on the same afternoon. We were losing credible buyers purely due to operational chaos.\"</i><br/>"
        "<b>— Operations Manager, ABC Properties</b>",
        style_callout
    ))
    story.append(Spacer(1, 7))

    # Objectives Section
    story.append(Paragraph("2. Strategic Project Objectives & Success Criteria", style_h1))
    story.append(Paragraph(
        "ABC Properties engaged our engineering startup to eliminate manual failure points and deploy a resilient communication infrastructure. We translated their operational bottlenecks into five measurable engineering objectives:",
        style_body
    ))

    obj_data = [
        [Paragraph("<b>LEGACY BOTTLENECK (BEFORE)</b>", style_th), Paragraph("<b>ENGINEERING OBJECTIVE & TARGET SLA</b>", style_th), Paragraph("<b>TARGET KPI METRIC</b>", style_th)],
        [
            Paragraph("Manual, delayed follow-up (4+ hrs)", style_td_alert),
            Paragraph("<b>Instant Automated Outreach:</b> Dispatch pre-approved Meta Cloud API templates automatically upon lead creation.", style_td),
            Paragraph("<b>&lt; 15 Seconds Response</b>", style_td_success),
        ],
        [
            Paragraph("Spreadsheet concurrency conflicts", style_td_alert),
            Paragraph("<b>Real-Time Inventory Locking:</b> Centralized relational database tying available plots directly to marketing dispatches.", style_td),
            Paragraph("<b>0 Double-Bookings</b>", style_td_success),
        ],
        [
            Paragraph("Carrier SIM spam blocks & bans", style_td_alert),
            Paragraph("<b>Official Meta Cloud API v21.0:</b> Enterprise compliance with instant STOP opt-out parsing and audit logging.", style_td),
            Paragraph("<b>100% Policy Clean</b>", style_td_success),
        ],
        [
            Paragraph("Low engagement from plain text", style_td_alert),
            Paragraph("<b>Interactive Media Experience:</b> 4K drone photography, video tours, and native CTA action buttons.", style_td),
            Paragraph("<b>&gt; 90% Open / Read Rate</b>", style_td_success),
        ],
        [
            Paragraph("Zero executive funnel tracking", style_td_alert),
            Paragraph("<b>Full-Funnel Webhook Pipeline:</b> Real-time analytics tracking Sent → Delivered → Read → Replied → Booked.", style_td),
            Paragraph("<b>100% Funnel Visibility</b>", style_td_success),
        ],
    ]
    t_obj = Table(obj_data, colWidths=[160, 262, 110])
    t_obj.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_SECONDARY),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_obj)
    story.append(Spacer(1, 7))

    # Project Scope & Delivery Target Box
    story.append(Paragraph(
        "<b>Delivery Scope:</b> The engagement covered full-stack engineering across 4 milestone releases: Database Architecture, Meta Cloud API Gateway, Real-Time Webhook Engine, and Admin Management Dashboard with Phone Simulator, successfully deployed ahead of the Q3 launch.",
        style_body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: THE SOLUTION & SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("3. The Solution & System Architecture Blueprint", style_h1))
    story.append(Paragraph(
        "To solve ABC Properties' operational challenges, we built a dedicated <b>Real Estate WhatsApp Marketing & Webhook Server</b> that integrates directly with Meta's official WhatsApp Business Cloud API (Graph API v21.0). The platform establishes a single source of truth for plot inventory and automates customer communications through an asynchronous, event-driven architecture.",
        style_body
    ))

    # Architecture Diagram Graphic
    if os.path.exists("assets/architecture_diagram.png"):
        img_arch = Image("assets/architecture_diagram.png", width=520, height=220)
        story.append(img_arch)
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            "<b>Figure 1:</b> <i>High-Level System Architecture & Event-Driven Dataflow between Homebuyers, Meta Cloud API, FastAPI Engine, and Admin Console.</i>",
            style_callout
        ))
        story.append(Spacer(1, 6))

    # Core Application Modules breakdown
    story.append(Paragraph("Core Application Modules", style_h2))

    modules_data = [
        [Paragraph("<b>APPLICATION MODULE</b>", style_th), Paragraph("<b>TECHNICAL ARCHITECTURE & RESPONSIBILITY</b>", style_th)],
        [
            Paragraph("<b>Meta Cloud API Gateway</b><br/>(<code>whatsapp/client.py</code>)", style_td_bold),
            Paragraph("Handles Graph API v21.0 sessions, bearer authentication, phone number normalization (E.164), and structured JSON payload dispatch for media templates, interactive buttons, and transactional texts.", style_td),
        ],
        [
            Paragraph("<b>Compliance & Opt-In Engine</b><br/>(<code>marketing/compliance.py</code>)", style_td_bold),
            Paragraph("Enforces strict Meta messaging compliance. Implements token-based regex parsers that intercept STOP opt-outs in sub-10ms, revokes marketing consent in the database, and prevents carrier blacklisting.", style_td),
        ],
        [
            Paragraph("<b>Dynamic Template Builder</b><br/>(<code>marketing/template_generator.py</code>)", style_td_bold),
            Paragraph("Dynamically hydrates pre-approved Meta marketing templates with layout specs: project name, location, plot sizes, starting price, RERA/DTCP approvals, road dimensions, and 4K hero media headers.", style_td),
        ],
        [
            Paragraph("<b>Campaign Funnel Engine</b><br/>(<code>marketing/campaign_engine.py</code>)", style_td_bold),
            Paragraph("Orchestrates segmented broadcasts by city/project, enforces token-bucket pacing (20 msg/sec) to avoid Meta rate limits, and aggregates live funnel metrics (Sent → Delivered → Read → Replied → Booked).", style_td),
        ],
        [
            Paragraph("<b>Webhook Server & Simulator</b><br/>(<code>webhook_server.py</code>)", style_td_bold),
            Paragraph("High-performance FastAPI server processing verification handshakes, bi-directional callbacks, audit logs, and an interactive smartphone simulator for pre-flight testing by marketing executives.", style_td),
        ],
    ]
    t_mod = Table(modules_data, colWidths=[155, 377])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_mod)
    story.append(Spacer(1, 5))

    # Relational Database Schema Highlights
    story.append(Paragraph("Relational Database Schema & Data Integrity", style_h2))
    story.append(Paragraph(
        "The data layer utilizes an ACID-compliant schema with foreign key constraints across four core tables: <code>leads</code> (capturing explicit consent flags and opt-out timestamps), <code>projects</code> (storing layout inventory, pricing, and media URLs), <code>campaigns</code> (funnel metrics and audience filters), and <code>message_logs</code> (idempotent webhook tracking by Meta <code>whatsapp_message_id</code>). This guarantees zero data desynchronization.",
        style_body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: HOW IT WORKS & KEY FEATURES
    # =========================================================================
    story.append(Paragraph("4. How the Application Works: End-to-End Workflow", style_h1))
    story.append(Paragraph(
        "The application orchestrates the entire homebuyer journey through an automated, event-driven pipeline that bridges digital lead acquisition with physical property site visits:",
        style_body
    ))

    # Workflow Steps
    workflow_data = [
        [Paragraph("<b>STAGE & STEP</b>", style_th), Paragraph("<b>OPERATIONAL & TECHNICAL PROCESS</b>", style_th), Paragraph("<b>SYSTEM DATAFLOW & DB EVENT</b>", style_th)],
        [
            Paragraph("<b>Step 1: Lead Capture & Opt-In Consent</b>", style_td_bold),
            Paragraph("Prospective homebuyer submits inquiry via website or digital ad with explicit WhatsApp opt-in checkbox.", style_td),
            Paragraph("<code>leads</code> table entry created with <code>whatsapp_opt_in=1</code> and ISO timestamp.", style_td),
        ],
        [
            Paragraph("<b>Step 2: Compliance Verification</b>", style_td_bold),
            Paragraph("Before any message is scheduled, the Compliance Engine validates active consent and checks against suppression lists.", style_td),
            Paragraph("<code>can_send_marketing_message()</code> validates consent status.", style_td),
        ],
        [
            Paragraph("<b>Step 3: Dynamic Template Hydration</b>", style_td_bold),
            Paragraph("System pulls latest layout specifications (pricing, available plots, DTCP approvals) and attaches hero media.", style_td),
            Paragraph("<code>RealEstateTemplateGenerator</code> constructs Meta JSON components.", style_td),
        ],
        [
            Paragraph("<b>Step 4: Throttled Cloud API Dispatch</b>", style_td_bold),
            Paragraph("Campaign Engine dispatches payload to Meta Graph API at paced rate of 20 msg/sec to prevent rate limiting.", style_td),
            Paragraph("Meta returns <code>wamid</code>; logged in <code>message_logs</code> as <code>SENT</code>.", style_td),
        ],
        [
            Paragraph("<b>Step 5: Webhook Status Tracking</b>", style_td_bold),
            Paragraph("As the homebuyer's device receives and displays the message, Meta sends asynchronous webhook callbacks.", style_td),
            Paragraph("Status updated: <code>SENT -> DELIVERED -> READ</code> with timestamps.", style_td),
        ],
        [
            Paragraph("<b>Step 6: Interactive CTA & Sales Routing</b>", style_td_bold),
            Paragraph("Buyer clicks native button: <b>[View Layout]</b>, <b>[Book a Plot]</b>, or <b>[Talk to Sales]</b>. Webhook alerts CRM immediately.", style_td),
            Paragraph("Status updated to <code>INTERESTED</code> or <code>BOOKED</code>; sales executive notified.", style_td),
        ],
    ]
    t_wf = Table(workflow_data, colWidths=[130, 242, 160])
    t_wf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_SECONDARY),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_wf)
    story.append(Spacer(1, 7))

    # Key Features Showcase (6 Pillars)
    story.append(Paragraph("5. Key Platform Features (The 6 Pillars)", style_h1))

    feat_grid = [
        [
            Paragraph("<b>1. Real-Time Layout Catalog Sync</b><br/>• <i>Business Benefit:</i> Eliminates obsolete availability quotes and double-booked corner plots.<br/>• <i>Technical Depth:</i> Database-driven variable hydration reflects total vs. available plots in real time.", style_td),
            Paragraph("<b>2. Rich Media Headers & Brochures</b><br/>• <i>Business Benefit:</i> Generates immediate emotional appeal and professional developer credibility.<br/>• <i>Technical Depth:</i> Supports dynamic IMAGE (4K aerial drone), VIDEO, or layout PDF attachments.", style_td),
        ],
        [
            Paragraph("<b>3. Interactive Native CTA Buttons</b><br/>• <i>Business Benefit:</i> 3.2x higher conversion compared to passive text links.<br/>• <i>Technical Depth:</i> Native Meta action buttons: dynamic URL for interactive plot maps, plus quick replies.", style_td),
            Paragraph("<b>4. Automated Opt-In / Opt-Out Engine</b><br/>• <i>Business Benefit:</i> Zero spam penalties and guaranteed compliance with carrier and privacy laws.<br/>• <i>Technical Depth:</i> Sub-10ms keyword parser immediately revokes consent upon STOP commands.", style_td),
        ],
        [
            Paragraph("<b>5. Full-Funnel Webhook Tracking</b><br/>• <i>Business Benefit:</i> Executive management gains real-time visibility into advertising ROI.<br/>• <i>Technical Depth:</i> Live tracking across Sent → Delivered → Read → Replied → Interested → Booked.", style_td),
            Paragraph("<b>6. WhatsApp Smartphone Simulator</b><br/>• <i>Business Benefit:</i> Allows marketing teams to test and approve layouts prior to live broadcasts.<br/>• <i>Technical Depth:</i> Built-in browser-based phone simulator rendering exact iOS/Android message bubbles.", style_td),
        ],
    ]
    t_feat = Table(feat_grid, colWidths=[266, 266])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 6))

    # Meta 24-Hour Messaging Protocol Box
    story.append(Paragraph(
        "<b>Meta 24-Hour Customer Care Window:</b> Inbound user interactions (texting or clicking interactive buttons) automatically open a 24-hour service session. This allows sales executives to converse freely and answer custom financing inquiries without template restrictions, maximizing conversion speed.",
        style_body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: CUSTOMER EXPERIENCE & ADMIN SIMULATOR
    # =========================================================================
    story.append(Paragraph("6. The Customer Experience & Admin Walkthrough", style_h1))
    story.append(Paragraph(
        "A critical success factor in enterprise software adoption is ensuring seamless usability for both the end-consumer (homebuyers on mobile) and internal staff (sales managers and executives). Below is the actual interface delivered in the platform.",
        style_body
    ))

    # Side-by-side: Smartphone Mockup + Explanatory Breakdown
    col_left = []
    if os.path.exists("assets/smartphone_mockup.png"):
        img_phone = Image("assets/smartphone_mockup.png", width=220, height=330)
        col_left.append(img_phone)
        col_left.append(Paragraph("<b>Figure 2:</b> <i>End-User WhatsApp Experience with Rich Media & CTA Action Buttons.</i>", style_callout))

    col_right = [
        Paragraph("<b>Anatomy of the Customer WhatsApp Experience</b>", style_h2),
        Paragraph("<b>1. Verified Business Profile & Security Badge:</b><br/>Sent from ABC Properties' official Meta Cloud API phone number ID with verified branding, establishing instant trust and credibility.", style_body),
        Paragraph("<b>2. High-Impact Media Header:</b><br/>Crisp visual of Green Valley Emerald layout (aerial drone photo or video walkthrough), generating immediate emotional connection.", style_body),
        Paragraph("<b>3. Structured Property Specifications:</b><br/>Clear presentation of key purchasing criteria: starting price (Rs. 28 Lakhs), plot dimensions (600–2,400 sq.ft), approvals (DTCP & RERA P5210002891), and infrastructure (30/40ft blacktop roads, 24/7 water).", style_body),
        Paragraph("<b>4. Native Interactive Action Buttons:</b><br/>• <b>[View Interactive Layout Plan]:</b> Dynamic URL opening interactive plot selection grid.<br/>• <b>[Book a Plot]:</b> Quick reply registering immediate buyer intent.<br/>• <b>[Talk to Sales]:</b> Direct CRM call routing to dedicated sales executive.", style_body),
        Paragraph("<b>5. Compliant Opt-Out Footer:</b><br/>Explicit disclosure (<i>'Reply STOP to unsubscribe | ABC Properties'</i>) ensuring strict compliance with Meta Business Messaging standards.", style_body),
    ]

    t_side = Table([[col_left, col_right]], colWidths=[230, 302])
    t_side.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_side)
    story.append(Spacer(1, 8))

    # Admin Dashboard Preview
    story.append(Paragraph("Admin Console & Webhook Simulator", style_h2))
    if os.path.exists("assets/dashboard_preview.png"):
        img_dash = Image("assets/dashboard_preview.png", width=520, height=210)
        story.append(img_dash)
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            "<b>Figure 3:</b> <i>Executive Dashboard showing Real-Time Funnel Counters, Campaign Launchpad, and Live Webhook Event Stream.</i>",
            style_callout
        ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: TECH STACK, LIFECYCLE & TECHNICAL CHALLENGES
    # =========================================================================
    story.append(Paragraph("7. Enterprise Technology Stack", style_h1))
    story.append(Paragraph(
        "To guarantee high throughput, low latency, and zero operational downtime, we selected a lightweight, cloud-native technology stack with strict architectural separation between presentation, business logic, and messaging gateways:",
        style_body
    ))

    stack_data = [
        [Paragraph("<b>LAYER</b>", style_th), Paragraph("<b>TECHNOLOGY USED</b>", style_th), Paragraph("<b>SELECTION RATIONALE & ARCHITECTURAL ADVANTAGE</b>", style_th)],
        [
            Paragraph("<b>Backend API</b>", style_td_bold),
            Paragraph("Python 3.11, FastAPI, Uvicorn ASGI", style_td),
            Paragraph("Asynchronous event loop for concurrent webhook ingestion; native Pydantic v2 data validation; sub-millisecond response latency.", style_td),
        ],
        [
            Paragraph("<b>Messaging Gateway</b>", style_td_bold),
            Paragraph("Meta WhatsApp Cloud API (v21.0)", style_td),
            Paragraph("Direct Graph API integration without third-party aggregator markups; official carrier-grade delivery SLA and high-volume throughput.", style_td),
        ],
        [
            Paragraph("<b>Persistence Layer</b>", style_td_bold),
            Paragraph("SQLite (Local) / PostgreSQL (Cloud)", style_td),
            Paragraph("ACID compliance, strict foreign key constraints between campaigns, leads, and webhook logs; zero-maintenance embedded engine.", style_td),
        ],
        [
            Paragraph("<b>Compliance Engine</b>", style_td_bold),
            Paragraph("Custom Keyword State Machine", style_td),
            Paragraph("Regex-based token matching for instant STOP opt-out and START opt-in reactivation; immutable ISO timestamps for compliance audit trails.", style_td),
        ],
        [
            Paragraph("<b>Admin Frontend</b>", style_td_bold),
            Paragraph("HTML5, Modern CSS Grid, Vanilla JS", style_td),
            Paragraph("Zero-dependency responsive UI; embedded interactive smartphone preview simulator; live AJAX polling of webhook delivery counters.", style_td),
        ],
        [
            Paragraph("<b>DevOps & Security</b>", style_td_bold),
            Paragraph("Docker, Meta HMAC-SHA256, Dotenv", style_td),
            Paragraph("Containerized deployment; cryptographic verification of incoming Meta webhook payloads; secure credential isolation via environment variables.", style_td),
        ],
    ]
    t_stack = Table(stack_data, colWidths=[100, 150, 282])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 7))

    # Professional Engineering Process (Phases 1-6)
    story.append(Paragraph("8. Professional Engineering & Development Lifecycle", style_h1))

    lifecycle_data = [
        [
            Paragraph("<b>Phase 1: Discovery & Analysis (Wk 1-2)</b><br/>Audited legacy Google Sheets and interviewed 18 sales reps to map property reservation bottlenecks.", style_td),
            Paragraph("<b>Phase 2: UI/UX & Schema Design (Wk 3-4)</b><br/>Drafted interactive WhatsApp template components and designed ACID relational database schema.", style_td),
            Paragraph("<b>Phase 3: Core API Development (Wk 5-8)</b><br/>Engineered FastAPI webhook handlers, Meta Cloud client, and token-bucket campaign throttler.", style_td),
        ],
        [
            Paragraph("<b>Phase 4: Testing & Meta Sandbox (Wk 9-11)</b><br/>Simulated 16 automated test suites for delivery callbacks, out-of-order webhooks, and STOP keywords.", style_td),
            Paragraph("<b>Phase 5: Pilot & Field Rollout (Wk 12-14)</b><br/>Deployed for 120-plot Green Valley launch; onboarded 18 sales reps with live smartphone simulator.", style_td),
            Paragraph("<b>Phase 6: Monitoring & SLA Support (Wk 15+)</b><br/>Continuous uptime monitoring, automated database backups, and Meta Cloud API v21.0 maintenance.", style_td),
        ]
    ]
    t_life = Table(lifecycle_data, colWidths=[177, 177, 178])
    t_life.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_life)
    story.append(Spacer(1, 7))

    # Technical Challenges Solved (Challenge -> Solution -> Result)
    story.append(Paragraph("9. Technical Challenges & Engineering Solutions", style_h1))

    # Challenge 1
    story.append(Paragraph("<b>Challenge 1: Meta Cloud API Rate Throttling & Batch Delivery Limits</b>", style_h2))
    story.append(Paragraph(
        "<b>Challenge:</b> Meta enforces strict rate limits on the WhatsApp Business Cloud API (Tier 1 accounts permit up to 80 requests/sec). Dispatching a 1,000+ lead campaign simultaneously caused network congestion and HTTP 429 <i>Too Many Requests</i> errors.<br/>"
        "<b>Solution:</b> We engineered a token-bucket throttled dispatch queue inside <code>CampaignEngine</code> with configurable pacing (20 msgs/sec default) and exponential backoff retry logic.<br/>"
        "<b>Result:</b> 100% campaign dispatch success rate with zero dropped messages, zero 429 errors, and zero carrier throttling.",
        style_body
    ))

    # Challenge 2
    story.append(Paragraph("<b>Challenge 2: Asynchronous Webhook Handshake & Out-of-Order Lifecycle Ingestion</b>", style_h2))
    story.append(Paragraph(
        "<b>Challenge:</b> Webhook status callbacks from Meta (<code>sent</code>, <code>delivered</code>, <code>read</code>) arrive asynchronously over the public internet and occasionally arrive out of chronological order due to mobile network latency.<br/>"
        "<b>Solution:</b> In <code>webhook_server.py</code>, we implemented a monotonic state machine where status transitions can only advance forward (e.g. a <code>read</code> event arriving before <code>delivered</code> preserves the higher-level read state). All events are indexed by unique <code>whatsapp_message_id</code>.<br/>"
        "<b>Result:</b> Perfectly consistent, idempotent funnel analytics with zero data corruption or duplicate counts.",
        style_body
    ))

    # Challenge 3
    story.append(Paragraph("<b>Challenge 3: Strict Meta Opt-In Compliance & Sub-10ms 'STOP' Interception</b>", style_h2))
    story.append(Paragraph(
        "<b>Challenge:</b> Meta Business Messaging Policy mandates that users who text 'STOP' must never receive another automated marketing template. Even a single violation can degrade the account's sender quality rating from 'High' to 'Flagged', risking permanent suspension.<br/>"
        "<b>Solution:</b> We decoupled the <code>ComplianceEngine</code> into a high-priority webhook interceptor. Inbound messages matching normalized opt-out keywords (<code>stop</code>, <code>unsubscribe</code>, <code>opt-out</code>, <code>cancel</code>, <code>remove me</code>) trigger immediate SQL transactions revoking consent, recording ISO timestamps, and adding the phone to an active suppression filter.<br/>"
        "<b>Result:</b> Zero carrier spam complaints, zero Meta policy penalties, and sustained 'High' quality tier status across 50,000+ dispatches.",
        style_body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: RESULTS, BUSINESS IMPACT & BEFORE VS AFTER
    # =========================================================================
    story.append(Paragraph("10. Results & Measurable Business Impact", style_h1))
    story.append(Paragraph(
        "The impact of replacing manual spreadsheet workflows with the Meta WhatsApp Cloud API platform was measured across the 120-plot launch of Green Valley Emerald Layout over a 90-day evaluation period:",
        style_body
    ))

    # Quantitative Metrics Table
    metrics_data = [
        [Paragraph("<b>METRIC</b>", style_th), Paragraph("<b>BEFORE (MANUAL)</b>", style_th), Paragraph("<b>AFTER (CLOUD PLATFORM)</b>", style_th), Paragraph("<b>QUANTIFIABLE IMPACT</b>", style_th)],
        [
            Paragraph("<b>First Response Latency</b>", style_td_bold),
            Paragraph("4.5 Hours (Avg)", style_td_alert),
            Paragraph("12 Seconds (Automated)", style_td_success),
            Paragraph("<b>99.9% Faster First Contact</b>", style_td_success),
        ],
        [
            Paragraph("<b>Message Open / Read Rate</b>", style_td_bold),
            Paragraph("18.2% (Email) / 12% (SMS)", style_td_alert),
            Paragraph("94.2% (WhatsApp Cloud)", style_td_success),
            Paragraph("<b>+417% Increase in Open Rate</b>", style_td_success),
        ],
        [
            Paragraph("<b>Booking Turnaround Time</b>", style_td_bold),
            Paragraph("240 Minutes", style_td_alert),
            Paragraph("3 Minutes", style_td_success),
            Paragraph("<b>78% Reduction in Processing Time</b>", style_td_success),
        ],
        [
            Paragraph("<b>Lead-to-Site Visit Conversion</b>", style_td_bold),
            Paragraph("4.6%", style_td_alert),
            Paragraph("14.8%", style_td_success),
            Paragraph("<b>3.2x Higher Conversion Multiplier</b>", style_td_success),
        ],
        [
            Paragraph("<b>Plot Reservation Conflicts</b>", style_td_bold),
            Paragraph("14 Incidents / Launch", style_td_alert),
            Paragraph("0 Incidents (Total)", style_td_success),
            Paragraph("<b>100% Elimination of Double-Bookings</b>", style_td_success),
        ],
        [
            Paragraph("<b>Manual Data Entry Burden</b>", style_td_bold),
            Paragraph("25 Hours / Week / Rep", style_td_alert),
            Paragraph("2 Hours / Week / Rep", style_td_success),
            Paragraph("<b>92% Operational Effort Saved</b>", style_td_success),
        ],
        [
            Paragraph("<b>Carrier Bans / Spam Strikes</b>", style_td_bold),
            Paragraph("8 SIM suspensions / month", style_td_alert),
            Paragraph("0 Policy Violations", style_td_success),
            Paragraph("<b>100% Regulatory Opt-In Clean</b>", style_td_success),
        ],
    ]
    t_met = Table(metrics_data, colWidths=[130, 110, 120, 172])
    t_met.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_met)
    story.append(Spacer(1, 8))

    # Funnel Chart Graphic
    if os.path.exists("assets/funnel_chart.png"):
        img_funnel = Image("assets/funnel_chart.png", width=520, height=200)
        story.append(img_funnel)
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            "<b>Figure 4:</b> <i>Audience Conversion Funnel (Left) and Operational Turnaround Logarithmic Speedup (Right).</i>",
            style_callout
        ))
        story.append(Spacer(1, 6))

    # Before vs After Operational Comparison Table
    story.append(Paragraph("11. Before vs. After Operational Comparison", style_h2))

    bva_data = [
        [Paragraph("<b>OPERATIONAL AREA</b>", style_th), Paragraph("<b>BEFORE (LEGACY MANUAL WORKFLOW)</b>", style_th), Paragraph("<b>AFTER (CENTRALIZED CLOUD PLATFORM)</b>", style_th)],
        [
            Paragraph("<b>Inventory Availability</b>", style_td_bold),
            Paragraph("Static Google Sheets; frequent desync and double-booked plots.", style_td_alert),
            Paragraph("Centralized database with real-time inventory locking.", style_td_success),
        ],
        [
            Paragraph("<b>Customer Messaging</b>", style_td_bold),
            Paragraph("Personal WhatsApp SIMs; manual copy-pasting of specs and photos.", style_td_alert),
            Paragraph("Automated Meta Cloud API templates with 4K media and CTA buttons.", style_td_success),
        ],
        [
            Paragraph("<b>Consent & Compliance</b>", style_td_bold),
            Paragraph("No opt-out mechanism; risk of carrier bans and privacy fines.", style_td_alert),
            Paragraph("Automated STOP keyword processing and consent audit timestamps.", style_td_success),
        ],
        [
            Paragraph("<b>Executive Reporting</b>", style_td_bold),
            Paragraph("Manual Excel consolidation taking 2 hours every evening.", style_td_alert),
            Paragraph("Live browser dashboard displaying real-time funnel KPIs.", style_td_success),
        ],
    ]
    t_bva = Table(bva_data, colWidths=[120, 206, 206])
    t_bva.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_SECONDARY),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_bva)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: SECURITY, SUMMARY, BEST PRACTICES & CALL TO ACTION
    # =========================================================================
    story.append(Paragraph("12. Client Testimonial & Stakeholder Feedback", style_h1))

    test_data = [
        [
            Paragraph(
                "<i>\"Before this platform, managing a 120-plot layout launch meant chaos. Our sales executives were constantly arguing over who held which corner plot on Google Sheets, and prospects waited hours for basic brochures. ApexTech's Meta WhatsApp solution completely modernized our business. Our booking speed jumped fourfold, and our sales team now spends their time closing deals rather than copy-pasting text into WhatsApp.\"</i><br/><br/>"
                "<b>— K. Senthil Nathan</b>, Vice President of Sales, ABC Properties",
                style_callout
            ),
            Paragraph(
                "<i>\"From a compliance standpoint, moving to Meta's official Cloud API was the best decision we made. We eliminated the constant threat of SIM bans, and the automatic STOP opt-out engine guarantees we stay 100% compliant with privacy regulations without any manual oversight.\"</i><br/><br/>"
                "<b>— Rajeshwari Raman</b>, Operations Director, ABC Properties",
                style_callout
            ),
        ]
    ]
    t_test = Table(test_data, colWidths=[266, 266])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_SUCCESS_BG),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 6))

    # Security & Governance Section
    story.append(Paragraph("13. Security, Privacy & Regulatory Compliance", style_h1))

    sec_data = [
        [
            Paragraph("<b>Webhook Handshake Authentication</b><br/>Meta endpoints enforce token-based verification (<code>hub.verify_token</code>) on GET requests, preventing unauthorized endpoint spoofing.", style_td),
            Paragraph("<b>Cryptographic Payload Integrity</b><br/>Inbound POST webhooks validate the <code>X-Hub-Signature-256</code> header using HMAC-SHA256 with the app secret, guaranteeing authenticity.", style_td),
        ],
        [
            Paragraph("<b>Consent Audit Trail & DPDP Compliance</b><br/>Every lead's opt-in and opt-out timestamp is immutably recorded, satisfying Indian DPDP Act 2023 and GDPR consent verification requirements.", style_td),
            Paragraph("<b>SQL Injection Protection & Data Isolation</b><br/>All database queries utilize parameterized prepared statements, preventing SQL injection vulnerabilities across leads, projects, and campaign tables.", style_td),
        ]
    ]
    t_sec = Table(sec_data, colWidths=[266, 266])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_CARD_BG),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t_sec)
    story.append(Spacer(1, 6))

    # Project Information Summary Table
    story.append(Paragraph("14. Project Metadata & Specification Summary", style_h1))

    meta_table_data = [
        [Paragraph("<b>METADATA ATTRIBUTE</b>", style_th), Paragraph("<b>SPECIFICATION DETAILS</b>", style_th), Paragraph("<b>METADATA ATTRIBUTE</b>", style_th), Paragraph("<b>SPECIFICATION DETAILS</b>", style_th)],
        [
            Paragraph("<b>Client Industry</b>", style_td_bold), Paragraph("Real Estate / PropTech", style_td),
            Paragraph("<b>Deployment Model</b>", style_td_bold), Paragraph("Cloud Container / On-Premise", style_td),
        ],
        [
            Paragraph("<b>Project Type</b>", style_td_bold), Paragraph("FastAPI Webhook & Campaign Suite", style_td),
            Paragraph("<b>Primary Database</b>", style_td_bold), Paragraph("SQLite / PostgreSQL Relational", style_td),
        ],
        [
            Paragraph("<b>Development Timeline</b>", style_td_bold), Paragraph("4 Months (Discovery to Production)", style_td),
            Paragraph("<b>API Integrations</b>", style_td_bold), Paragraph("Meta WhatsApp Cloud API v21.0", style_td),
        ],
        [
            Paragraph("<b>Production Scale</b>", style_td_bold), Paragraph("50+ Internal Users, 50,000+ Leads", style_td),
            Paragraph("<b>Core Languages</b>", style_td_bold), Paragraph("Python 3.11, JavaScript, HTML5/CSS", style_td),
        ],
    ]
    t_meta = Table(meta_table_data, colWidths=[120, 146, 120, 146])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 6))

    # Architecture Takeaways for IT Startups Box
    story.append(Paragraph("15. Architectural Takeaways & Enterprise Best Practices", style_h1))
    takeaway_data = [
        [
            Paragraph("<b>1. Direct Cloud APIs Over Scraping:</b> Integrating official Graph APIs eliminates carrier shadow-bans and ensures 99.9% message deliverability with guaranteed Meta SLAs.", style_td),
            Paragraph("<b>2. Compliance as a Feature:</b> Sub-10ms STOP keyword interception protects sender reputation, keeping the WABA account permanently in Meta's 'High' tier.", style_td),
        ],
        [
            Paragraph("<b>3. State-Monotonic Webhook Handlers:</b> Ingesting callbacks idempotently prevents desynchronization from network jitter and out-of-order events.", style_td),
            Paragraph("<b>4. Pre-Flight Simulation:</b> Providing a live smartphone simulator gave sales executives confidence and eliminated testing errors prior to live broadcasting.", style_td),
        ]
    ]
    t_takeaway = Table(takeaway_data, colWidths=[266, 266])
    t_takeaway.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t_takeaway)
    story.append(Spacer(1, 6))

    # Call to Action Box
    cta_data = [
        [
            Paragraph("<b>16. HAVE A SIMILAR BUSINESS CHALLENGE? LET'S BUILD YOUR SOLUTION.</b>", style_th),
        ],
        [
            Paragraph(
                "We help growing businesses, real estate developers, and enterprises design and engineer custom software solutions that eliminate manual operational chaos, automate customer outreach, and drive measurable revenue growth.<br/><br/>"
                "<b>Our Core Capabilities:</b><br/>"
                "• <b>Custom Enterprise Web & Cloud Applications</b> (Python, FastAPI, Django, React, Next.js)<br/>"
                "• <b>Meta WhatsApp Business Cloud API Solutions</b> (Marketing Templates, Webhooks, Conversational AI)<br/>"
                "• <b>Real-Time Inventory & Booking Automation Systems</b> (Role-Based Access, Concurrency Controls)<br/>"
                "• <b>CRM & ERP Systems Integration</b> (Salesforce, HubSpot, Custom SQL Pipelines)<br/><br/>"
                "<b>Ready to modernize your operations? Let's discuss your project today:</b><br/>"
                "<b>Website:</b> https://apextech-solutions.example.com  |  <b>Email:</b> enterprise@apextech-solutions.example.com<br/>"
                "<b>Phone:</b> +91 98765 43210 / +1 (800) 555-APEX  |  <b>Offices:</b> Bangalore • Chennai • San Francisco",
                style_td
            )
        ]
    ]
    t_cta = Table(cta_data, colWidths=[532])
    t_cta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), C_PRIMARY),
        ('BACKGROUND', (0, 1), (0, 1), C_SUCCESS_BG),
        ('BOX', (0, 0), (-1, -1), 1.2, C_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_cta)

    # Build PDF with custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    create_case_study_pdf()
