#!/usr/bin/env python3
"""
Generates high-resolution graphical assets for the WhatsApp Real Estate Case Study PDF:
1. architecture_diagram.png - System & Dataflow Architecture
2. smartphone_mockup.png - Authentic WhatsApp Interactive Message Simulation
3. funnel_chart.png - Campaign Funnel & Turnaround Metrics Visualization
4. dashboard_preview.png - Enterprise Admin Dashboard & Simulator UI Preview
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs("assets", exist_ok=True)

# ----------------- 1. ARCHITECTURE DIAGRAM ----------------- #
def build_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=250)
    ax.set_facecolor('#F8FAFC')
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    c_meta = '#128C7E'       # Meta WhatsApp Teal
    c_engine = '#0369A1'     # Ocean Blue
    c_db = '#7C3AED'         # Royal Violet
    c_admin = '#059669'      # Emerald Green
    c_user = '#1E293B'       # Dark Slate

    # 1. External Homebuyers Box (Left)
    rect1 = patches.FancyBboxPatch((3, 18), 16, 26, boxstyle="round,pad=0.8,rounding_size=1.5",
                                  facecolor='#F1F5F9', edgecolor='#94A3B8', linewidth=1.5)
    ax.add_patch(rect1)
    ax.text(11, 40, "HOMEBUYERS", fontsize=10, fontweight='bold', color=c_user, ha='center')
    ax.text(11, 36.5, "WhatsApp Mobile Clients", fontsize=7.5, color='#64748B', ha='center')
    ax.text(11, 28, "• Receive Layout Cards\n• Click CTA Action Buttons\n• Inquire on Plot Pricing\n• Send 'STOP' / 'START'\n• Request Site Visits",
            fontsize=7.2, color='#334155', ha='center', va='center', family='sans-serif')

    # 2. Meta WhatsApp Cloud API Box (Middle-Left)
    rect2 = patches.FancyBboxPatch((24, 16), 18, 30, boxstyle="round,pad=0.8,rounding_size=1.5",
                                  facecolor='#ECFDF5', edgecolor=c_meta, linewidth=2)
    ax.add_patch(rect2)
    ax.text(33, 42.5, "META CLOUD API", fontsize=10.5, fontweight='bold', color=c_meta, ha='center')
    ax.text(33, 39, "WhatsApp Business v21.0", fontsize=7.5, fontweight='bold', color='#047857', ha='center')
    ax.text(33, 28.5, "• Graph API v21.0 Gateway\n• Pre-Approved Templates\n• Real-Time Webhooks\n• Delivery Status Handlers\n  (Sent, Delivered, Read)\n• Rate Limit Throttling",
            fontsize=7.2, color='#065F46', ha='center', va='center')

    # 3. Core Webhook Server & Engines (Middle-Right)
    rect3 = patches.FancyBboxPatch((47, 6), 28, 50, boxstyle="round,pad=0.8,rounding_size=2",
                                  facecolor='#F0F9FF', edgecolor=c_engine, linewidth=2)
    ax.add_patch(rect3)
    ax.text(61, 52.5, "FASTAPI WEBHOOK SERVER", fontsize=11, fontweight='bold', color=c_engine, ha='center')
    ax.text(61, 49, "Core Application Layer (Python 3.11)", fontsize=8, color='#0284C7', ha='center')

    # Sub-boxes inside FastAPI
    # a. Template Generator
    sb1 = patches.FancyBboxPatch((49, 37.5), 24, 9, boxstyle="round,pad=0.5,rounding_size=1",
                                facecolor='#FFFFFF', edgecolor='#BAE6FD', linewidth=1.2)
    ax.add_patch(sb1)
    ax.text(61, 43, "Dynamic Template Engine", fontsize=8.5, fontweight='bold', color='#0369A1', ha='center')
    ax.text(61, 39.5, "Payload Builder • Media Headers (Image/Video)\nInteractive CTA Buttons & Quick Replies", fontsize=6.8, color='#475569', ha='center')

    # b. Compliance Engine
    sb2 = patches.FancyBboxPatch((49, 24.5), 24, 10.5, boxstyle="round,pad=0.5,rounding_size=1",
                                facecolor='#FFFFFF', edgecolor='#BAE6FD', linewidth=1.2)
    ax.add_patch(sb2)
    ax.text(61, 31.5, "Compliance & Opt-In Engine", fontsize=8.5, fontweight='bold', color='#B45309', ha='center')
    ax.text(61, 27, "Meta Opt-In Enforcement • STOP Keyword Parser\nAuto Opt-Out • START Consent Reactivation\nConsent Audit Log Timestamps", fontsize=6.8, color='#475569', ha='center')

    # c. Campaign Funnel Engine
    sb3 = patches.FancyBboxPatch((49, 9.5), 24, 12, boxstyle="round,pad=0.5,rounding_size=1",
                                facecolor='#FFFFFF', edgecolor='#BAE6FD', linewidth=1.2)
    ax.add_patch(sb3)
    ax.text(61, 18, "Campaign & Funnel Pipeline", fontsize=8.5, fontweight='bold', color='#059669', ha='center')
    ax.text(61, 13.5, "Audience City Segmentation • Batch Throttler\nFunnel Metrics Aggregator: Sent ->\nDelivered -> Read -> Replied -> Booked", fontsize=6.8, color='#475569', ha='center')

    # 4. Database Layer (Top Right)
    rect4 = patches.FancyBboxPatch((80, 33), 17, 23, boxstyle="round,pad=0.8,rounding_size=1.5",
                                  facecolor='#FAF5FF', edgecolor=c_db, linewidth=1.8)
    ax.add_patch(rect4)
    ax.text(88.5, 52, "DATABASE LAYER", fontsize=9.5, fontweight='bold', color=c_db, ha='center')
    ax.text(88.5, 48.5, "SQLite / PostgreSQL", fontsize=7.5, color='#6B21A8', ha='center')
    ax.text(88.5, 40, "• leads (Opt-in tracking)\n• projects (Layout specs)\n• campaigns (Funnel KPIs)\n• message_logs (Webhooks)",
            fontsize=7, color='#4A044E', ha='center', va='center')

    # 5. Admin Dashboard & Simulator (Bottom Right)
    rect5 = patches.FancyBboxPatch((80, 6), 17, 23, boxstyle="round,pad=0.8,rounding_size=1.5",
                                  facecolor='#F0FDF4', edgecolor=c_admin, linewidth=1.8)
    ax.add_patch(rect5)
    ax.text(88.5, 25, "ADMIN CONSOLE", fontsize=9.5, fontweight='bold', color=c_admin, ha='center')
    ax.text(88.5, 21.5, "Web UI & Live Simulator", fontsize=7.5, color='#047857', ha='center')
    ax.text(88.5, 14, "• Real-Time Funnel Cards\n• Phone Preview Simulator\n• One-Click Campaign Run\n• Opt-In / Opt-Out Toggles",
            fontsize=7, color='#064E3B', ha='center', va='center')

    # Connections / Arrows
    def draw_arrow(x1, y1, x2, y2, label="", color='#475569', offset_y=1.5):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=1.6, shrinkA=3, shrinkB=3))
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + offset_y, label, fontsize=6.8, fontweight='bold',
                    color=color, ha='center', backgroundcolor='#F8FAFC',
                    bbox=dict(boxstyle='square,pad=0.1', facecolor='#F8FAFC', edgecolor='none'))

    draw_arrow(19, 31, 24, 31, "WhatsApp\nNetwork", color=c_meta, offset_y=2.5)
    draw_arrow(42, 35, 47, 35, "REST API &\nWebhooks", color='#0284C7', offset_y=2.5)
    draw_arrow(75, 44, 80, 44, "SQL Queries\n& Audit Logs", color=c_db, offset_y=2.2)
    draw_arrow(75, 18, 80, 18, "REST API\nJSON Stats", color=c_admin, offset_y=2.2)

    plt.tight_layout()
    plt.savefig("assets/architecture_diagram.png", dpi=250, bbox_inches='tight')
    plt.close()
    print("Generated assets/architecture_diagram.png")


# ----------------- 2. SMARTPHONE MOCKUP ----------------- #
def build_smartphone_mockup():
    fig, ax = plt.subplots(figsize=(6, 9.2), dpi=250)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 150)
    ax.axis('off')

    # Phone outer frame
    phone_outline = patches.FancyBboxPatch((12, 4), 76, 142, boxstyle="round,pad=0,rounding_size=8",
                                          facecolor='#0F172A', edgecolor='#334155', linewidth=3)
    ax.add_patch(phone_outline)

    # Phone screen inner area
    phone_screen = patches.FancyBboxPatch((15, 8), 70, 134, boxstyle="round,pad=0,rounding_size=6",
                                         facecolor='#ECE5DD', edgecolor='#0F172A', linewidth=1)
    ax.add_patch(phone_screen)

    # Speaker notch & camera
    notch = patches.FancyBboxPatch((38, 137), 24, 3, boxstyle="round,pad=0,rounding_size=1.5",
                                  facecolor='#1E293B', edgecolor='none')
    ax.add_patch(notch)
    cam = plt.Circle((66, 138.5), 1.2, color='#334155')
    ax.add_patch(cam)

    # WhatsApp Top Bar
    wa_header = patches.Rectangle((15, 122), 70, 16, facecolor='#075E54')
    ax.add_patch(wa_header)

    # Back arrow & Avatar
    ax.text(18, 130, "<-", fontsize=11, color='white', fontweight='bold', va='center')
    avatar = plt.Circle((27, 130), 4.5, color='#128C7E')
    ax.add_patch(avatar)
    ax.text(27, 130, "ABC", fontsize=6, color='white', fontweight='bold', ha='center', va='center')

    # Contact Name & Verified Badge
    ax.text(34, 132, "ABC Properties", fontsize=9, color='white', fontweight='bold')
    chk = plt.Circle((62, 133.5), 2.2, color='#25D366')
    ax.add_patch(chk)
    ax.text(62, 133.5, "v", fontsize=6, color='white', fontweight='bold', ha='center', va='center')
    ax.text(34, 126, "Official Business Account", fontsize=6.2, color='#A7F3D0')

    # Icons on header right
    ax.text(78, 130, "[Call]", fontsize=6.5, color='white', fontweight='bold', va='center')

    # Date bubble
    date_box = patches.FancyBboxPatch((38, 115), 24, 4.5, boxstyle="round,pad=0,rounding_size=2",
                                     facecolor='#E1F5FE', edgecolor='none')
    ax.add_patch(date_box)
    ax.text(50, 117.2, "TODAY", fontsize=6, color='#546E7A', fontweight='bold', ha='center', va='center')

    # WhatsApp Message Card (White Bubble)
    msg_card = patches.FancyBboxPatch((18, 22), 64, 90, boxstyle="round,pad=0,rounding_size=3",
                                     facecolor='#FFFFFF', edgecolor='#CFD8DC', linewidth=1)
    ax.add_patch(msg_card)

    # Media Header (Hero Property Graphic Box)
    media_box = patches.FancyBboxPatch((20, 77), 60, 32, boxstyle="round,pad=0,rounding_size=2",
                                      facecolor='#065F46', edgecolor='none')
    ax.add_patch(media_box)
    ax.text(50, 99, "GREEN VALLEY EMERALD LAYOUT", fontsize=8, color='#F0FDF4', fontweight='bold', ha='center')
    ax.text(50, 93, "TAMBARAM WEST, CHENNAI", fontsize=7, color='#BBF7D0', fontweight='bold', ha='center')
    ax.text(50, 87, "DTCP & RERA APPROVED (P5210002891)", fontsize=5.8, color='#FEF08A', fontweight='bold', ha='center')
    ax.text(50, 81, "Starting Rs. 28 Lakhs | 600 - 2,400 sq.ft", fontsize=6.5, color='#FFFFFF', fontweight='bold', ha='center')

    # Message Text Body
    text_content = (
        "Hello Aravind Kumar,\n\n"
        "[Project] Green Valley Emerald Layout\n"
        "[Location] Tambaram West, Chennai\n"
        "[Plot Sizes] 600 - 2,400 sq.ft Villa Plots\n"
        "[Starting] Rs. 28 Lakhs Only\n"
        "[Approvals] DTCP & RERA Approved\n"
        "[Road Specs] 30ft & 40ft Blacktop Roads\n"
        "[Amenities] Gated Park, 24/7 Water, Power\n\n"
        "Interested in reserving your preferred corner plot?"
    )
    ax.text(21, 53, text_content, fontsize=5.8, color='#1E293B', family='sans-serif', va='center')

    # Opt-out footer text
    ax.text(21, 38, "Reply STOP to unsubscribe | ABC Properties", fontsize=4.8, color='#64748B', style='italic')
    ax.text(78, 38, "10:42 AM  vv", fontsize=4.8, color='#0284C7', ha='right', fontweight='bold')

    # Interactive Action Buttons (Meta Cloud API Buttons)
    btn1 = patches.FancyBboxPatch((20, 31), 60, 5, boxstyle="round,pad=0,rounding_size=1.5",
                                 facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=1)
    ax.add_patch(btn1)
    ax.text(50, 33.5, ">>  View Interactive Layout Plan", fontsize=6.2, color='#0284C7', fontweight='bold', ha='center', va='center')

    btn2 = patches.FancyBboxPatch((20, 25), 29, 5, boxstyle="round,pad=0,rounding_size=1.5",
                                 facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=1)
    ax.add_patch(btn2)
    ax.text(34.5, 27.5, "[*] Book a Plot", fontsize=6, color='#059669', fontweight='bold', ha='center', va='center')

    btn3 = patches.FancyBboxPatch((51, 25), 29, 5, boxstyle="round,pad=0,rounding_size=1.5",
                                 facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=1)
    ax.add_patch(btn3)
    ax.text(65.5, 27.5, "[+] Talk to Sales", fontsize=6, color='#0369A1', fontweight='bold', ha='center', va='center')

    # Inbound Customer Quick Reply simulation
    user_bubble = patches.FancyBboxPatch((42, 11), 40, 8, boxstyle="round,pad=0,rounding_size=2.5",
                                        facecolor='#DCF8C6', edgecolor='#C5E1A5', linewidth=0.8)
    ax.add_patch(user_bubble)
    ax.text(44, 15.5, "Book a Plot - Green Valley", fontsize=6, color='#1E293B', fontweight='bold')
    ax.text(80, 12.5, "10:43 AM vv", fontsize=4.5, color='#4B5563', ha='right')

    plt.tight_layout()
    plt.savefig("assets/smartphone_mockup.png", dpi=250, bbox_inches='tight')
    plt.close()
    print("Generated assets/smartphone_mockup.png")


# ----------------- 3. FUNNEL & METRICS CHART ----------------- #
def build_funnel_and_metrics_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=250)
    fig.patch.set_facecolor('#F8FAFC')
    ax1.set_facecolor('#FFFFFF')
    ax2.set_facecolor('#FFFFFF')

    # Chart 1: WhatsApp Campaign Funnel
    stages = [
        "1. Total Leads",
        "2. Opted-In (Eligible)",
        "3. Delivered (Meta)",
        "4. Message Read",
        "5. Inbound Replied",
        "6. Plot Interested",
        "7. Site Visit / Booked"
    ]
    counts = [1000, 857, 842, 807, 356, 244, 127]
    pcts = ["100%", "85.7%", "98.2%", "94.2%", "41.6%", "28.5%", "14.8%"]
    colors = ['#0F766E', '#0D9488', '#14B8A6', '#2DD4BF', '#0284C7', '#3B82F6', '#6366F1']

    y_pos = np.arange(len(stages))
    ax1.barh(y_pos, counts, color=colors, height=0.6, edgecolor='none')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(stages, fontsize=8, fontweight='bold', color='#1E293B')
    ax1.invert_yaxis()
    ax1.set_xlim(0, 1150)
    ax1.set_xlabel("Number of Leads (Green Valley Pilot Cohort)", fontsize=8, fontweight='bold', color='#475569')
    ax1.set_title("Real Estate Campaign Funnel Performance", fontsize=9.5, fontweight='bold', color='#0F172A', pad=10)

    for i, (count, pct) in enumerate(zip(counts, pcts)):
        ax1.text(count + 20, i, f"{count:,} ({pct})", va='center', fontsize=7.5, fontweight='bold', color='#0F172A')

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#CBD5E1')
    ax1.spines['bottom'].set_color('#CBD5E1')
    ax1.grid(axis='x', linestyle='--', alpha=0.4, color='#94A3B8')

    # Chart 2: Turnaround Time Comparison (Before vs After)
    metrics = [
        "First Response\nTime (Mins)",
        "Brochure\nDispatch (Mins)",
        "Plot Hold\nConfirm (Hrs)",
        "Daily Report\nPrep (Mins)"
    ]
    before_vals = [240, 180, 24, 120]
    after_vals = [0.2, 0.1, 0.5, 3]

    x = np.arange(len(metrics))
    width = 0.35

    ax2.bar(x - width/2, before_vals, width, label='Before (Manual Sheets & WA)', color='#EF4444', alpha=0.9)
    ax2.bar(x + width/2, after_vals, width, label='After (Automated Cloud Platform)', color='#10B981', alpha=0.9)

    ax2.set_ylabel("Duration", fontsize=8, fontweight='bold', color='#475569')
    ax2.set_title("Operational Turnaround Times: Before vs. After", fontsize=9.5, fontweight='bold', color='#0F172A', pad=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(metrics, fontsize=7.5, fontweight='bold', color='#1E293B')
    ax2.set_yscale('log')
    ax2.legend(fontsize=7.5, loc='upper right', frameon=True, facecolor='#F8FAFC', edgecolor='#CBD5E1')

    ax2.text(0, 300, "99.9% Faster", ha='center', fontsize=7, fontweight='bold', color='#B91C1C')
    ax2.text(1, 220, "Instant API", ha='center', fontsize=7, fontweight='bold', color='#B91C1C')
    ax2.text(2, 30, "48x Faster", ha='center', fontsize=7, fontweight='bold', color='#B91C1C')
    ax2.text(3, 140, "40x Faster", ha='center', fontsize=7, fontweight='bold', color='#B91C1C')

    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#CBD5E1')
    ax2.spines['bottom'].set_color('#CBD5E1')
    ax2.grid(axis='y', linestyle='--', alpha=0.4, color='#94A3B8')

    plt.tight_layout()
    plt.savefig("assets/funnel_chart.png", dpi=250, bbox_inches='tight')
    plt.close()
    print("Generated assets/funnel_chart.png")


# ----------------- 4. DASHBOARD PREVIEW ----------------- #
def build_dashboard_preview():
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=250)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#0F172A')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    # Top App Bar
    app_bar = patches.Rectangle((0, 52), 100, 8, facecolor='#1E293B')
    ax.add_patch(app_bar)
    ax.text(3, 56, "Real Estate WhatsApp Marketing Suite", fontsize=10.5, color='#F8FAFC', fontweight='bold', va='center')
    ax.text(50, 56, "Meta Cloud API v21.0 | Webhook Engine Active", fontsize=8, color='#38BDF8', fontweight='bold', va='center')
    ax.text(97, 56, "[LIVE PRODUCTION]", fontsize=7.5, color='#4ADE80', fontweight='bold', ha='right', va='center')

    # Metric KPI Cards Row
    kpi_configs = [
        ("TOTAL LEADS", "1,248", "Chennai & BLR", '#38BDF8', 3),
        ("CONSENT VERIFIED", "1,070", "85.7% Opt-In", '#4ADE80', 19),
        ("SENT DISPATCH", "1,070", "100% Rate", '#818CF8', 35),
        ("DELIVERY CONFIRMED", "1,051", "98.2% Webhook", '#2DD4BF', 51),
        ("OPEN / READ RATE", "1,008", "94.2% Read", '#FBBF24', 67),
        ("BOOKINGS / VISITS", "158", "14.8% Conv.", '#F472B6', 83),
    ]

    for label, val, sub, col, x_start in kpi_configs:
        card = patches.FancyBboxPatch((x_start, 40), 14, 10, boxstyle="round,pad=0.4,rounding_size=1",
                                     facecolor='#1E293B', edgecolor='#334155', linewidth=1)
        ax.add_patch(card)
        ax.text(x_start + 7, 47.5, label, fontsize=5.5, fontweight='bold', color='#94A3B8', ha='center')
        ax.text(x_start + 7, 44, val, fontsize=10, fontweight='bold', color=col, ha='center')
        ax.text(x_start + 7, 41.5, sub, fontsize=5.2, color='#64748B', ha='center')

    # Left Section: Campaign Launchpad & Project Catalog
    left_box = patches.FancyBboxPatch((3, 4), 45, 34, boxstyle="round,pad=0.5,rounding_size=1.5",
                                     facecolor='#1E293B', edgecolor='#334155', linewidth=1)
    ax.add_patch(left_box)
    ax.text(5, 35, "Campaign Launchpad & Layout Catalog", fontsize=9, fontweight='bold', color='#F8FAFC')

    proj_card = patches.FancyBboxPatch((5, 17), 41, 15, boxstyle="round,pad=0.4,rounding_size=1",
                                      facecolor='#0F172A', edgecolor='#0284C7', linewidth=1.2)
    ax.add_patch(proj_card)
    ax.text(7, 29, "Selected Project: Green Valley Emerald Layout", fontsize=7.5, fontweight='bold', color='#38BDF8')
    ax.text(7, 26, "* Location: Tambaram West, Chennai | DTCP & RERA Approved", fontsize=6.2, color='#CBD5E1')
    ax.text(7, 23.5, "* Inventory: 84 / 120 Plots Available | Price: Rs. 28 Lakhs", fontsize=6.2, color='#CBD5E1')
    ax.text(7, 21, "* Header Media: Hero Aerial Drone Photo (4K)", fontsize=6.2, color='#CBD5E1')
    ax.text(7, 18.5, "* Target Segment: Chennai Leads (524 Opted-in Buyers)", fontsize=6.2, color='#FCD34D')

    btn_launch = patches.FancyBboxPatch((5, 7), 20, 7.5, boxstyle="round,pad=0.4,rounding_size=1",
                                       facecolor='#059669', edgecolor='none')
    ax.add_patch(btn_launch)
    ax.text(15, 10.7, ">> Launch Meta Campaign", fontsize=6.5, fontweight='bold', color='white', ha='center')

    btn_test = patches.FancyBboxPatch((26, 7), 20, 7.5, boxstyle="round,pad=0.4,rounding_size=1",
                                     facecolor='#0284C7', edgecolor='none')
    ax.add_patch(btn_test)
    ax.text(36, 10.7, "[*] Dispatch Live Test Lead", fontsize=6.5, fontweight='bold', color='white', ha='center')

    # Right Section: Real-Time Webhook Activity & Consent Feed
    right_box = patches.FancyBboxPatch((51, 4), 46, 34, boxstyle="round,pad=0.5,rounding_size=1.5",
                                      facecolor='#1E293B', edgecolor='#334155', linewidth=1)
    ax.add_patch(right_box)
    ax.text(53, 35, "Live Webhook Event Stream & Opt-In Tracker", fontsize=9, fontweight='bold', color='#F8FAFC')

    log_entries = [
        ("10:44:12", "[BOOKING_CLICK]", "Aravind Kumar clicked [Book a Plot] -> Alert sent to Sales CRM", '#4ADE80'),
        ("10:43:55", "[WEBHOOK_READ]", "Message wamid.HBgLM... read by 919876543210 (Aravind K)", '#38BDF8'),
        ("10:43:02", "[DELIVERED]", "Template delivered via Meta Cloud Gateway to 919812345678", '#2DD4BF'),
        ("10:42:15", "[COMPLIANCE_STOP]", "919999888877 texted 'STOP'. Consent revoked instantly. 0 Spam risk.", '#F87171'),
        ("10:41:40", "[CAMPAIGN_BATCH]", "Dispatched batch #1 (50 messages) throttled at 20 msg/sec", '#C084FC'),
        ("10:40:10", "[OPT_IN_VERIFIED]", "Web Lead Suresh Raina verified opt-in. Added to target pool.", '#FBBF24'),
    ]

    y_log = 30
    for time_str, evt, desc, evt_col in log_entries:
        ax.text(53, y_log, time_str, fontsize=5.8, color='#64748B', family='monospace')
        ax.text(61, y_log, evt, fontsize=5.8, color=evt_col, fontweight='bold', family='monospace')
        ax.text(53, y_log - 2.2, desc[:62], fontsize=5.2, color='#CBD5E1')
        y_log -= 4.8

    plt.tight_layout()
    plt.savefig("assets/dashboard_preview.png", dpi=250, bbox_inches='tight')
    plt.close()
    print("Generated assets/dashboard_preview.png")

if __name__ == "__main__":
    build_architecture_diagram()
    build_smartphone_mockup()
    build_funnel_and_metrics_chart()
    build_dashboard_preview()
    print("All assets successfully built with clean fonts.")
