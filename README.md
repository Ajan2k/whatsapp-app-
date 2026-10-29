# Real Estate WhatsApp Marketing & Template Sending System

An enterprise-grade Python solution integrated with the **Meta WhatsApp Business Cloud API** for real estate layout and block-booking platforms.

Transform your marketing pipeline into a compliant, automated **Lead → Opt-In → Marketing Template → Interaction → Plot Booking** funnel.

> 📖 **Knowledge Transfer (KT) Document:** For an in-depth architecture breakdown, live demo script, and presenter guide, see [KT_DOCUMENTATION.md](KT_DOCUMENTATION.md).

---

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    docker-compose.yml                      │
│                                                           │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  frontend    │    │   backend    │    │     db       │ │
│  │  (Nginx)     │───►│  (FastAPI)   │───►│ (PostgreSQL) │ │
│  │  Port 80     │    │  Port 8000   │    │  Port 5432   │ │
│  │              │    │              │    │              │ │
│  │ Static files │    │ API routes   │    │ leads        │ │
│  │ Reverse proxy│    │ SSE events   │    │ projects     │ │
│  │              │    │ Webhooks     │    │ campaigns    │ │
│  └─────────────┘    └──────────────┘    │ message_logs │ │
│                                          └──────────────┘ │
└───────────────────────────────────────────────────────────┘
```

| Container | Technology | Purpose |
|-----------|-----------|---------|
| **frontend** | Nginx (Alpine) | Serves static HTML/CSS/JS, reverse-proxies API & SSE to backend |
| **backend** | Python 3.12 + FastAPI | REST API, SSE real-time events, Meta webhook receiver |
| **db** | PostgreSQL 16 (Alpine) | Persistent storage for leads, projects, campaigns, message logs |

---

## Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed

### 1. Environment Configuration

Copy the example env file and fill in your Meta WhatsApp credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:
```ini
# Meta WhatsApp Business Cloud API Credentials
WHATSAPP_API_KEY=your_meta_access_token
PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSSINESS_ACCOUNT_ID=your_waba_id

# Webhook Verification Token
WEBHOOK_VERIFY_TOKEN=whatsapp_realestate_verify_token_123

# PostgreSQL (defaults work out of the box)
POSTGRES_USER=whatsapp_user
POSTGRES_PASSWORD=whatsapp_pass
POSTGRES_DB=whatsapp_marketing
```

### 2. Build & Run

```bash
docker compose up --build -d
```

### 3. Access the Dashboard

Open **http://localhost** in your browser to access the Admin Dashboard and Live WhatsApp Simulator.

---

## Key Features

### Strict Meta Opt-In Compliance & Consent Tracking
- Complies with [Meta's Business Messaging Policy](https://developers.facebook.com/documentation/business-messaging/whatsapp/getting-opt-in)
- Database records `whatsapp_opt_in`, `opt_in_timestamp`, `source`, and `opt_out_timestamp`
- **Automatic STOP Opt-Out**: When a lead replies STOP, the system instantly marks them as opted out

### Marketing Template Generation
- Media Headers: Hero layout images, walkthrough videos, layout plan PDFs
- Dynamic Parameters: Lead name, Project name, Location, Plot sizes, Starting price, Approvals, Amenities
- Interactive Action Buttons: View Layout, Book a Plot, Talk to Sales

### Campaign Funnel Analytics
```
Total Leads → Eligible Opted-In → Sent → Delivered → Read → Replied → Interested → Booked
```

### Interactive Admin Dashboard
- Dark mode with emerald accents
- Live smartphone WhatsApp simulator
- Lead management with opt-in/opt-out controls
- Campaign launchpad with 1-click execution

---

## Connecting with Meta Developer Dashboard

1. Expose port 80 using `ngrok` or Cloudflare Tunnel:
   ```bash
   ngrok http 80
   ```
2. In Meta App Dashboard → **WhatsApp > Configuration > Webhook**:
   - **Callback URL**: `https://your-domain.ngrok-free.app/webhook`
   - **Verify Token**: `whatsapp_realestate_verify_token_123`
3. Subscribe to the `messages` webhook field.

---

## Useful Commands

```bash
# Start all services
docker compose up --build -d

# View logs
docker compose logs -f

# View backend logs only
docker compose logs -f backend

# Stop all services
docker compose down

# Stop and remove all data (including database)
docker compose down -v

# Access PostgreSQL directly
docker compose exec db psql -U whatsapp_user -d whatsapp_marketing

# Rebuild a single service
docker compose up --build backend -d
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Dashboard funnel statistics |
| GET | `/api/leads` | List leads with filters |
| POST | `/api/leads` | Create/update a lead |
| POST | `/api/leads/toggle-opt-in` | Toggle opt-in status |
| DELETE | `/api/leads/{id}` | Delete a lead |
| GET | `/api/projects` | List real estate projects |
| GET | `/api/templates/preview` | Preview template payload |
| GET | `/api/campaigns` | List campaigns |
| POST | `/api/campaigns` | Launch a campaign |
| GET | `/api/whatsapp/verify` | Verify Meta API credentials |
| POST | `/api/whatsapp/send` | Send template to a lead |
| GET | `/api/logs` | Message delivery logs |
| GET | `/api/events` | SSE real-time event stream |
| GET/POST | `/webhook` | Meta webhook endpoint |
| GET | `/health` | Backend health check |
