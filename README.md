# Real Estate WhatsApp Marketing & Template Sending System

An enterprise-grade Python solution integrated with the **Meta WhatsApp Business Cloud API** for real estate layout and block-booking platforms.

Transform your marketing pipeline into a compliant, automated **Lead → Opt-In → Marketing Template → Interaction → Plot Booking** funnel.

---

## Key Architecture & Features

```
REAL ESTATE CRM
      │
      ▼
Lead Management (Opt-In Consent)
      ├── whatsapp_opt_in = True  ──► Eligible ──► Throttled Marketing Dispatch ──► Meta WhatsApp Cloud API ──► Lead
      └── whatsapp_opt_in = False ──► Ineligible ──► STOP (Blocked)
```

### 1. Strict Meta Opt-In Compliance & Consent Tracking
- Complies with [Meta's Business Messaging Policy](https://developers.facebook.com/documentation/business-messaging/whatsapp/getting-opt-in).
- Database models record `whatsapp_opt_in`, `opt_in_timestamp`, `source`, and `opt_out_timestamp`.
- **Automatic STOP Opt-Out**: When a lead replies with `STOP`, `UNSUBSCRIBE`, or `CANCEL`, the system instantly marks them as `OPTED_OUT`, logs the timestamp, confirms the unsubscription via WhatsApp, and permanently blocks future promotional templates until reactivated with `START`.

### 2. Marketing Template Generation (Images, Videos, Buttons, Booking Links)
- Constructs valid Meta Cloud API payloads (`type: "template"`) for real estate launches:
  - **Media Headers**: Hero layout images, walkthrough videos (MP4), or layout plan PDFs.
  - **Dynamic Parameters**: Lead name `{{1}}`, Project name `{{2}}`, Location `{{3}}`, Plot sizes `{{4}}`, Starting price `{{5}}`, Approvals `{{6}}`, Roads & Amenities `{{7}}`.
  - **Interactive Action Buttons**: `[🗺️ View Layout]`, `[📍 Book a Plot]`, `[📞 Talk to Sales]`.
  - **Compliance Footer**: `Reply STOP to unsubscribe • ABC Properties`.

### 3. Campaign Funnel Analytics
Tracks real-time conversion through every stage of your real-estate marketing pipeline:
```
Total Leads (2,500) ──► Eligible Opted-In (2,100) ──► Sent (2,050) ──► Delivered (1,980) 
   ──► Read (1,720) ──► Replied (340) ──► Interested (125) ──► Booked (18)
```

### 4. Interactive WhatsApp Smartphone Simulator & Admin Dashboard
- **Web Dashboard**: High-aesthetic dark mode with emerald accents.
- **Live Smartphone Simulator**: Previews layout templates, media headers, and clickable action buttons.
- **Lead Manager**: View leads, toggle opt-in state, and register new leads with explicit consent checkboxes.
- **Campaign Launchpad**: Dispatch campaigns to opted-in leads with 1-click execution or simulated dry-run.

---

## Quick Start

### 1. Installation
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration (`.env`)
Create or edit your `.env` file with your Meta credentials:
```ini
# Meta WhatsApp Business Cloud API Credentials
WHATSAPP_API_KEY=your_meta_system_user_or_access_token_here
PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_BUSSINESS_ACCOUNT_ID=your_whatsapp_business_account_id_here

# Webhook Verification Token (custom secret string)
WEBHOOK_VERIFY_TOKEN=whatsapp_realestate_verify_token_123

PORT=8000
```

---

## 1. Using the Command-Line Tool (`send_whatsapp.py`)

### Verify WhatsApp Cloud API Credentials
```bash
python send_whatsapp.py --verify
```

### Preview Real Estate Marketing Template & Meta JSON Payload
```bash
python send_whatsapp.py --preview
```

### View Registered Leads & Opt-In Compliance Badges
```bash
python send_whatsapp.py --leads
```

### Send Real Estate Template to a Single Phone (with Opt-In Check)
```bash
python send_whatsapp.py --to 918825781789
```
*(Add `--dry-run` to simulate without calling the Meta API)*

### Launch a Throttled Marketing Campaign
```bash
python send_whatsapp.py --campaign --project-id 1 --city Chennai
```

### Interactive Guided CLI Mode
```bash
python send_whatsapp.py --interactive
```

---

## 2. Running the Webhook Server & Admin Dashboard (`webhook_server.py`)

Start the FastAPI application:
```bash
python webhook_server.py
```
Open **`http://127.0.0.1:8000/`** in your browser to access the Admin Dashboard and Live Smartphone Simulator.

### Connecting with Meta Developer Dashboard
1. Expose port 8000 using `ngrok` or Cloudflare Tunnel:
   ```bash
   ngrok http 8000
   ```
2. In Meta App Dashboard -> **WhatsApp > Configuration > Webhook**:
   - **Callback URL**: `https://your-domain.ngrok-free.app/webhook`
   - **Verify Token**: `whatsapp_realestate_verify_token_123`
3. Subscribe to the `messages` webhook field.
4. The server will now automatically process delivery receipts (`sent`, `delivered`, `read`), opt-outs (`STOP`), and inbound buyer booking requests!

---

## 3. Automated Test Suite

Run the comprehensive test suite verifying client normalization, template generation, opt-in compliance, STOP keyword handling, campaign audience filtering, and webhook endpoints:
```bash
python test_suite.py
```

All 16 unit and integration tests pass out-of-the-box.
