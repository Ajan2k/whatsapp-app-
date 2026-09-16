# Real Estate WhatsApp Marketing & Webhook Automation Platform

[![Tests](https://img.shields.io/badge/tests-16%20passed-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)]()
[![Meta WhatsApp Cloud API](https://img.shields.io/badge/Meta%20Cloud%20API-v21.0-25D366.svg)]()
[![Case Study PDF](https://img.shields.io/badge/Case%20Study-PDF%20Available-blue.svg)](./WhatsApp_RealEstate_Platform_Case_Study.pdf)

An enterprise-grade **Real Estate WhatsApp Marketing, Template Generation, Webhook Handshake, and Opt-In Compliance Platform** built with Python 3.11, FastAPI, and Meta's official WhatsApp Business Cloud API (Graph API v21.0).

---

## 📄 Case Study Deliverable

* **Publication-Grade PDF Report:** [`WhatsApp_RealEstate_Platform_Case_Study.pdf`](./WhatsApp_RealEstate_Platform_Case_Study.pdf) (8 pages, high-res visual assets, executive charts, and before/after metrics)
* **Markdown Case Study Document:** [`CASE_STUDY.md`](./CASE_STUDY.md) (Complete text version with architecture diagram, KPI breakdown, and client testimonials)

---

## 🌟 Key Architecture Capabilities

1. **Meta WhatsApp Business Cloud API Integration (`whatsapp/client.py`)**
   - Direct Graph API v21.0 endpoint integration
   - Pre-approved marketing template dispatch with media headers (4K drone photos, videos, PDF brochures)
   - Dynamic interactive CTA action buttons (`[View Layout]`, `[Book a Plot]`, `[Talk to Sales]`)
   - E.164 phone number sanitization and bearer token authentication

2. **Automated Opt-in Compliance & STOP Interception (`marketing/compliance.py`)**
   - Sub-10ms keyword parser matching `STOP`, `UNSUBSCRIBE`, `CANCEL`, `START`
   - Instant consent revocation in SQLite database to prevent carrier spam penalties
   - Compliant with Meta Business Messaging Policy and Indian DPDP Act 2023

3. **Real-Time Layout Inventory & Template Hydration (`marketing/template_generator.py`)**
   - Dynamically injects layout details (project name, location, plot size ranges, starting prices, RERA/DTCP approvals)
   - Live synchronization of available vs. total inventory

4. **Throttled Campaign Funnel Engine (`marketing/campaign_engine.py`)**
   - Segmented broadcast dispatching by city and project
   - Token-bucket rate limiting (default 20 msgs/sec) to prevent HTTP 429 throttling
   - Full funnel analytics tracking: `Total Leads` → `Opted-In` → `Sent` → `Delivered` → `Read` → `Replied` → `Interested` → `Booked`

5. **Bidirectional Webhook Server & Interactive Simulator (`webhook_server.py`)**
   - `GET /webhook`: Meta verification handshake (`hub.challenge`, `hub.verify_token`)
   - `POST /webhook`: Inbound delivery receipts (`sent`, `delivered`, `read`) and user interactive replies
   - Interactive Admin Console & browser-based smartphone simulator for campaign pre-flight testing

---

## 🚀 Quick Start Guide

### 1. Installation

```bash
git clone https://github.com/Ajan2k/whatsapp-app-.git
cd whatsapp-app-

# Install required dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure your Meta WhatsApp credentials:

```bash
cp .env.example .env
```

```ini
WHATSAPP_API_KEY=your_meta_system_user_access_token
PHONE_NUMBER_ID=your_meta_phone_number_id
WHATSAPP_BUSSINESS_ACCOUNT_ID=your_waba_id
WEBHOOK_VERIFY_TOKEN=whatsapp_realestate_verify_token_123
PORT=8000
```

### 3. Running the Server

Start the FastAPI application:

```bash
python3 webhook_server.py
```

The server binds to `http://0.0.0.0:8000`:
- **Admin Dashboard & Phone Simulator:** `http://localhost:8000/dashboard`
- **Interactive OpenAPI Docs:** `http://localhost:8000/docs`
- **Meta Webhook Endpoint:** `http://localhost:8000/webhook`

---

## 🧪 Running Automated Tests

Run the complete 16-test suite covering phone sanitization, template hydration, opt-in compliance, campaign funnel throttling, and webhook handshakes:

```bash
python3 test_suite.py
```

---

## 📊 Generating the Case Study PDF

To re-render the high-resolution architecture diagrams and publication-grade PDF:

```bash
# 1. Generate high-resolution asset charts and architecture diagrams
python3 generate_assets.py

# 2. Build the 8-page publication PDF
python3 build_case_study_pdf.py
```

Output: `WhatsApp_RealEstate_Platform_Case_Study.pdf` (letter format, print-ready, numbered canvas with running headers/footers).
