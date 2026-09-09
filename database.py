"""
Database Layer for Real Estate WhatsApp Marketing System
Embedded SQLite database for Leads (with strict opt-in compliance),
Projects/Layouts, Marketing Campaigns, and Webhook Message Logs.
"""

import os
import sqlite3
import datetime
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("Database")

DB_PATH = os.getenv("SQLITE_DB_PATH", "real_estate_marketing.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(seed_sample_data: bool = True):
    """Initializes tables and optionally seeds realistic real-estate demonstration data."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Leads Table (with strict opt-in and consent tracking)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            email TEXT,
            city TEXT DEFAULT 'Chennai',
            project_interest TEXT DEFAULT 'Green Valley Emerald',
            whatsapp_opt_in INTEGER NOT NULL DEFAULT 0,
            opt_in_timestamp TEXT,
            opt_out_timestamp TEXT,
            source TEXT DEFAULT 'Website Booking Form',
            status TEXT DEFAULT 'OPTED_IN',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 2. Real Estate Projects / Layout Catalog
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            plot_sizes TEXT NOT NULL,
            starting_price TEXT NOT NULL,
            approval_status TEXT NOT NULL,
            road_specs TEXT NOT NULL,
            amenities TEXT NOT NULL,
            hero_image_url TEXT,
            walkthrough_video_url TEXT,
            brochure_pdf_url TEXT,
            booking_url TEXT,
            total_plots INTEGER DEFAULT 120,
            available_plots INTEGER DEFAULT 84,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 3. Marketing Campaigns Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_id INTEGER,
            template_name TEXT NOT NULL DEFAULT 'real_estate_launch_v1',
            language_code TEXT DEFAULT 'en_US',
            audience_city TEXT DEFAULT 'All',
            status TEXT DEFAULT 'COMPLETED',
            total_leads INTEGER DEFAULT 0,
            eligible INTEGER DEFAULT 0,
            sent INTEGER DEFAULT 0,
            delivered INTEGER DEFAULT 0,
            read INTEGER DEFAULT 0,
            replied INTEGER DEFAULT 0,
            interested INTEGER DEFAULT 0,
            booked INTEGER DEFAULT 0,
            failed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            launched_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """)

        # 4. Message & Webhook Event Logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            lead_id INTEGER,
            phone TEXT NOT NULL,
            whatsapp_message_id TEXT,
            template_name TEXT,
            status TEXT DEFAULT 'SENT',
            media_type TEXT DEFAULT 'IMAGE',
            media_url TEXT,
            error_message TEXT,
            sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
            delivered_at TEXT,
            read_at TEXT,
            replied_at TEXT,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
        """)

        conn.commit()

    if seed_sample_data:
        _seed_data_if_empty()


def _seed_data_if_empty():
    """Seeds baseline projects, opt-in/opt-out leads, and demo campaign metrics."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Seed Projects
        cursor.execute("SELECT COUNT(*) FROM projects")
        if cursor.fetchone()[0] == 0:
            projects = [
                (
                    1,
                    "Green Valley Emerald Layout",
                    "Tambaram West, Chennai",
                    "600–2400 sq.ft",
                    "₹28 Lakhs",
                    "DTCP & RERA Approved (P5210002891)",
                    "30 ft & 40 ft Blacktop Roads",
                    "Gated Community, Children's Play Park, 24/7 Potable Water, Underground Electricity, Avenue Trees",
                    "https://images.unsplash.com/photo-1592595896551-12b371d546d5?auto=format&fit=crop&w=1200&q=80",
                    "https://www.w3schools.com/html/mov_bbb.mp4",
                    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                    "https://realestate-demo.example.com/book/green-valley",
                    120,
                    84,
                ),
                (
                    2,
                    "Sunrise Palm Meadows",
                    "Sarjapur Road, Bangalore",
                    "1200–3000 sq.ft",
                    "₹45 Lakhs",
                    "BMRDA & RERA Approved",
                    "40 ft Concrete Wide Roads",
                    "Clubhouse, Swimming Pool, Jogging Track, Sewage Treatment Plant, Solar Street Lights",
                    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
                    "https://www.w3schools.com/html/mov_bbb.mp4",
                    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                    "https://realestate-demo.example.com/book/sunrise-palm",
                    90,
                    52,
                ),
            ]
            cursor.executemany("""
                INSERT INTO projects (id, name, location, plot_sizes, starting_price, approval_status,
                road_specs, amenities, hero_image_url, walkthrough_video_url, brochure_pdf_url, booking_url,
                total_plots, available_plots)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, projects)

        # Seed Leads (illustrating opt-in vs opted-out compliance separation)
        cursor.execute("SELECT COUNT(*) FROM leads")
        if cursor.fetchone()[0] == 0:
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            sample_leads = [
                # Opted-in leads (Eligible for WhatsApp marketing)
                ("Aravind Kumar", "919876543210", "aravind.k@example.com", "Chennai", "Green Valley Emerald", 1, now_iso, None, "Website Form", "OPTED_IN", "Looking for 1200 sq.ft east-facing plot"),
                ("Priya Sundaram", "919812345678", "priya.s@example.com", "Chennai", "Green Valley Emerald", 1, now_iso, None, "Facebook Lead Ad", "OPTED_IN", "Interested in 2400 sq.ft corner plot"),
                ("Rajesh Sharma", "919845012345", "rajesh.sharma@example.com", "Bangalore", "Sunrise Palm Meadows", 1, now_iso, None, "Google Ads", "OPTED_IN", "Wants walkthrough video and layout map"),
                ("Kavita Menon", "919731234567", "kavita.m@example.com", "Chennai", "Green Valley Emerald", 1, now_iso, None, "Walk-in Inquiry", "OPTED_IN", "Wants sales call regarding bank loan approval"),
                ("Deepak Patel", "919920123456", "deepak.p@example.com", "Bangalore", "Sunrise Palm Meadows", 1, now_iso, None, "Property Portal", "OPTED_IN", "Ready to book 1500 sq.ft plot"),
                ("Suresh Raina", "919444123456", "suresh.r@example.com", "Chennai", "Green Valley Emerald", 1, now_iso, None, "Website Form", "OPTED_IN", "Requested pricing sheet"),

                # Opted-out leads (Strictly blocked from marketing templates)
                ("Vikram Rathore", "919898989898", "vikram.r@example.com", "Chennai", "Green Valley Emerald", 0, "2026-08-01T10:00:00", now_iso, "Website Form", "OPTED_OUT", "Replied STOP on 2026-08-15"),
                ("Ananya Roy", "919777777777", "ananya.roy@example.com", "Bangalore", "Sunrise Palm Meadows", 0, "2026-07-20T12:00:00", now_iso, "Facebook Lead Ad", "OPTED_OUT", "User opted out via unsubscribe keyword"),

                # Unverified leads (Did not check WhatsApp consent box - Ineligible)
                ("Manoj Verma", "919666666666", "manoj.v@example.com", "Chennai", "Green Valley Emerald", 0, None, None, "Cold Lead Import", "UNVERIFIED", "Did not provide WhatsApp opt-in consent"),
            ]
            cursor.executemany("""
                INSERT INTO leads (name, phone, email, city, project_interest, whatsapp_opt_in,
                opt_in_timestamp, opt_out_timestamp, source, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_leads)

        # Seed Demonstrative Campaign (Matching the real-estate analytics funnel)
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO campaigns (
                    name, project_id, template_name, language_code, audience_city,
                    status, total_leads, eligible, sent, delivered, read, replied,
                    interested, booked, failed, launched_at
                )
                VALUES (
                    'Green Valley Emerald - Mega Launch Campaign',
                    1,
                    'real_estate_launch_v1',
                    'en_US',
                    'Chennai',
                    'COMPLETED',
                    2500,
                    2100,
                    2050,
                    1980,
                    1720,
                    340,
                    125,
                    18,
                    50,
                    '2026-09-05T09:00:00'
                )
            """)

        conn.commit()


# ---------------- CRUD & Queries ---------------- #

def get_leads(opt_in_only: Optional[bool] = None, city: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        query = "SELECT * FROM leads WHERE 1=1"
        params = []
        if opt_in_only is True:
            query += " AND whatsapp_opt_in = 1 AND opt_out_timestamp IS NULL"
        elif opt_in_only is False:
            query += " AND (whatsapp_opt_in = 0 OR opt_out_timestamp IS NOT NULL)"
        if city and city.lower() != "all":
            query += " AND LOWER(city) = LOWER(?)"
            params.append(city)
        if search:
            query += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)"
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard])
        query += " ORDER BY id DESC"
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_lead_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    # Clean phone digits for matching
    cleaned = "".join(filter(str.isdigit, str(phone)))
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE phone = ? OR phone = ?", (cleaned, phone))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_or_update_lead(
    name: str,
    phone: str,
    email: Optional[str] = None,
    city: str = "Chennai",
    project_interest: str = "Green Valley Emerald",
    whatsapp_opt_in: bool = True,
    source: str = "Website Lead Form",
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    cleaned_phone = "".join(filter(str.isdigit, str(phone)))
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    opt_in_time = now_iso if whatsapp_opt_in else None
    status = "OPTED_IN" if whatsapp_opt_in else "UNVERIFIED"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO leads (name, phone, email, city, project_interest, whatsapp_opt_in,
                               opt_in_timestamp, opt_out_timestamp, source, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?)
            ON CONFLICT(phone) DO UPDATE SET
                name = excluded.name,
                email = coalesce(excluded.email, leads.email),
                city = excluded.city,
                project_interest = excluded.project_interest,
                whatsapp_opt_in = excluded.whatsapp_opt_in,
                opt_in_timestamp = coalesce(excluded.opt_in_timestamp, leads.opt_in_timestamp),
                status = excluded.status,
                notes = coalesce(excluded.notes, leads.notes)
        """, (name, cleaned_phone, email, city, project_interest, 1 if whatsapp_opt_in else 0,
              opt_in_time, source, status, notes))
        conn.commit()
    return get_lead_by_phone(cleaned_phone) or {}


def set_lead_opt_out(phone: str, reason: str = "User replied STOP") -> bool:
    cleaned = "".join(filter(str.isdigit, str(phone)))
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE leads
            SET whatsapp_opt_in = 0,
                opt_out_timestamp = ?,
                status = 'OPTED_OUT',
                notes = coalesce(notes || ' | ', '') || ?
            WHERE phone = ? OR phone = ?
        """, (now_iso, reason, cleaned, phone))
        conn.commit()
        return cursor.rowcount > 0


def set_lead_opt_in(phone: str, source: str = "User replied START") -> bool:
    cleaned = "".join(filter(str.isdigit, str(phone)))
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE leads
            SET whatsapp_opt_in = 1,
                opt_in_timestamp = ?,
                opt_out_timestamp = NULL,
                status = 'OPTED_IN',
                notes = coalesce(notes || ' | ', '') || ?
            WHERE phone = ? OR phone = ?
        """, (now_iso, source, cleaned, phone))
        conn.commit()
        return cursor.rowcount > 0


def get_projects() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_campaigns() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, p.name AS project_name, p.location AS project_location
            FROM campaigns c
            LEFT JOIN projects p ON c.project_id = p.id
            ORDER BY c.id DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_campaign(campaign_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, p.name AS project_name, p.location AS project_location
            FROM campaigns c
            LEFT JOIN projects p ON c.project_id = p.id
            WHERE c.id = ?
        """, (campaign_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_campaign(
    name: str,
    project_id: int,
    template_name: str = "real_estate_launch_v1",
    language_code: str = "en_US",
    audience_city: str = "All",
    status: str = "DRAFT",
    total_leads: int = 0,
    eligible: int = 0,
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO campaigns (name, project_id, template_name, language_code, audience_city,
                                   status, total_leads, eligible)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, project_id, template_name, language_code, audience_city, status, total_leads, eligible))
        conn.commit()
        return cursor.lastrowid


def update_campaign_metrics(campaign_id: int, **kwargs):
    valid_keys = {"total_leads", "eligible", "sent", "delivered", "read", "replied",
                  "interested", "booked", "failed", "status", "launched_at"}
    updates = []
    params = []
    for k, v in kwargs.items():
        if k in valid_keys:
            updates.append(f"{k} = ?")
            params.append(v)
    if not updates:
        return
    params.append(campaign_id)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE campaigns SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()


def increment_campaign_counter(campaign_id: int, counter_name: str, count: int = 1):
    allowed_counters = {"sent", "delivered", "read", "replied", "interested", "booked", "failed"}
    if counter_name not in allowed_counters:
        return
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE campaigns SET {counter_name} = {counter_name} + ? WHERE id = ?", (count, campaign_id))
        conn.commit()


def log_message(
    phone: str,
    campaign_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    whatsapp_message_id: Optional[str] = None,
    template_name: Optional[str] = None,
    status: str = "SENT",
    media_type: str = "IMAGE",
    media_url: Optional[str] = None,
    error_message: Optional[str] = None,
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO message_logs (
                campaign_id, lead_id, phone, whatsapp_message_id, template_name,
                status, media_type, media_url, error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (campaign_id, lead_id, phone, whatsapp_message_id, template_name,
              status, media_type, media_url, error_message))
        conn.commit()
        return cursor.lastrowid


def update_message_log_status(whatsapp_message_id: str, new_status: str):
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    timestamp_col = None
    if new_status.upper() == "DELIVERED":
        timestamp_col = "delivered_at"
    elif new_status.upper() == "READ":
        timestamp_col = "read_at"
    elif new_status.upper() == "REPLIED":
        timestamp_col = "replied_at"

    with get_connection() as conn:
        cursor = conn.cursor()
        if timestamp_col:
            cursor.execute(f"""
                UPDATE message_logs
                SET status = ?, {timestamp_col} = ?
                WHERE whatsapp_message_id = ?
            """, (new_status.upper(), now_iso, whatsapp_message_id))
        else:
            cursor.execute("""
                UPDATE message_logs
                SET status = ?
                WHERE whatsapp_message_id = ?
            """, (new_status.upper(), whatsapp_message_id))
        conn.commit()


def get_message_logs(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM message_logs ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]


def get_overall_stats() -> Dict[str, Any]:
    """Computes global funnel statistics across all campaigns and leads."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leads")
        total_leads = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM leads WHERE whatsapp_opt_in = 1 AND opt_out_timestamp IS NULL")
        eligible_leads = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM leads WHERE opt_out_timestamp IS NOT NULL")
        opted_out_leads = cursor.fetchone()[0]

        cursor.execute("""
            SELECT
                coalesce(SUM(sent), 0) AS total_sent,
                coalesce(SUM(delivered), 0) AS total_delivered,
                coalesce(SUM(read), 0) AS total_read,
                coalesce(SUM(replied), 0) AS total_replied,
                coalesce(SUM(interested), 0) AS total_interested,
                coalesce(SUM(booked), 0) AS total_booked
            FROM campaigns
        """)
        campaign_metrics = dict(cursor.fetchone())

        return {
            "total_leads": total_leads,
            "eligible_leads": eligible_leads,
            "opted_out_leads": opted_out_leads,
            "sent": campaign_metrics["total_sent"],
            "delivered": campaign_metrics["total_delivered"],
            "read": campaign_metrics["total_read"],
            "replied": campaign_metrics["total_replied"],
            "interested": campaign_metrics["total_interested"],
            "booked": campaign_metrics["total_booked"],
        }
