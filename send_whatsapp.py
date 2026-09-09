#!/usr/bin/env python3
"""
Real Estate WhatsApp Marketing & Template Sending CLI Tool
Integrated with Meta WhatsApp Business Cloud API.
Supports:
- Credential verification
- Real Estate Layout Template generation & preview
- Single lead marketing dispatch (with strict opt-in compliance)
- Multi-lead campaign execution
- Lead consent management & opt-out tracking
"""

import argparse
import sys
import json

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from whatsapp.client import WhatsAppClient
import database
from marketing.template_generator import RealEstateTemplateGenerator
from marketing.compliance import ComplianceEngine
from marketing.campaign_engine import CampaignEngine


def print_banner():
    print("=" * 65)
    print("   🏡 Real Estate WhatsApp Marketing & Template Sending System")
    print("   Powered by Meta WhatsApp Business Cloud API")
    print("=" * 65)


def main(args=None):
    if args is None:
        parser = argparse.ArgumentParser(
            description="Real Estate WhatsApp Marketing CLI for Meta Cloud API."
        )
        parser.add_argument(
            "--verify",
            action="store_true",
            help="Check health and status of your Meta WhatsApp credentials.",
        )
        parser.add_argument(
            "--preview",
            action="store_true",
            help="Display rendered marketing template text and Meta JSON payload.",
        )
        parser.add_argument(
            "--to",
            type=str,
            help="Recipient phone number with country code (e.g. 919876543210).",
        )
        parser.add_argument(
            "--project-id",
            type=int,
            default=1,
            help="Real estate project ID (default: 1).",
        )
        parser.add_argument(
            "--media",
            type=str,
            choices=["IMAGE", "VIDEO", "DOCUMENT"],
            default="IMAGE",
            help="Header media type (default: IMAGE).",
        )
        parser.add_argument(
            "--campaign",
            action="store_true",
            help="Launch a marketing campaign to all opted-in leads.",
        )
        parser.add_argument(
            "--city",
            type=str,
            default="All",
            help="Audience city filter for campaign (e.g. Chennai, Bangalore, All).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the send or campaign without contacting Meta API.",
        )
        parser.add_argument(
            "--leads",
            action="store_true",
            help="List all leads and their WhatsApp opt-in compliance status.",
        )
        parser.add_argument(
            "--opt-out",
            type=str,
            help="Record an opt-out (STOP) for a phone number.",
        )
        parser.add_argument(
            "--direct",
            action="store_true",
            help="Send directly as a rich real estate layout media message (hero image + specs + booking links).",
        )
        parser.add_argument(
            "--template",
            type=str,
            default=None,
            help="Specify an approved Meta template name (e.g. jaspers_market_image_cta_v1, hello_world).",
        )
        parser.add_argument(
            "--interactive",
            "-i",
            action="store_true",
            help="Run in interactive guided menu mode.",
        )

        args = parser.parse_args()

    # Ensure database is ready
    database.init_db(seed_sample_data=True)

    # 1. Credential Verification Mode
    if args.verify:
        print("\n--- Verifying Meta WhatsApp Cloud API Credentials ---")
        try:
            client = WhatsAppClient()
            res = client.verify_credentials()
            if res.get("success"):
                data = res.get("data", {})
                print("✅ [SUCCESS] Connected to WhatsApp Business Cloud API!")
                print(f" • Display Number: {data.get('display_phone_number')}")
                print(f" • Verified Name:  {data.get('verified_name')}")
                print(f" • Status:         {data.get('code_verification_status')}")
                print(f" • Quality Rating: {data.get('quality_rating')}")
                print(f" • Phone Number ID:{data.get('id')}")
            else:
                print("❌ [FAILED] Verification failed:")
                print(f" • Error: {res.get('message')}")
                if res.get("diagnostic_hint"):
                    print(f" • Diagnostic Hint:\n   -> {res.get('diagnostic_hint')}")
        except Exception as e:
            print(f"❌ [ERROR] Could not initialize WhatsApp client: {e}")
        return

    # 2. Template Preview Mode
    if args.preview:
        project = database.get_project(args.project_id)
        if not project:
            print(f"[ERROR] Project ID {args.project_id} not found.")
            return

        print_banner()
        print(f"\n--- Rendered WhatsApp Text Preview for: {project['name']} ---")
        preview_text = RealEstateTemplateGenerator.format_rendered_message_text("Aravind Kumar", project)
        print(preview_text)
        print("\n--- Interactive Action Buttons ---")
        print(" [ 🗺️ View Layout ]   [ 📍 Book a Plot ]   [ 📞 Talk to Sales ]")

        meta_payload = RealEstateTemplateGenerator.build_meta_template_payload(
            to_phone="919876543210",
            lead_name="Aravind Kumar",
            project=project,
            media_type=args.media,
        )
        print("\n--- Meta WhatsApp Cloud API JSON Payload ---")
        print(json.dumps(meta_payload, indent=2))
        return

    # 3. Lead Listing Mode
    if args.leads:
        print_banner()
        leads = database.get_leads()
        stats = database.get_overall_stats()
        print(f"\nTotal Leads: {stats['total_leads']} | Eligible (Opted-in): {stats['eligible_leads']} | Opted-Out: {stats['opted_out_leads']}\n")
        print(f"{'NAME':<20} {'PHONE':<15} {'CITY':<12} {'CONSENT':<14} {'PROJECT INTEREST'}")
        print("-" * 80)
        for l in leads:
            if l['whatsapp_opt_in'] == 1 and not l['opt_out_timestamp']:
                consent = "✔ OPTED_IN"
            elif l['opt_out_timestamp']:
                consent = "✖ OPTED_OUT"
            else:
                consent = "⚠ UNVERIFIED"
            print(f"{l['name']:<20} {l['phone']:<15} {l['city']:<12} {consent:<14} {l['project_interest']}")
        return

    # 4. Opt-Out Mode
    if args.opt_out:
        success = database.set_lead_opt_out(args.opt_out, reason="CLI manual opt-out")
        if success:
            print(f"✅ Lead {args.opt_out} has been opted out. Future marketing sends will be blocked.")
        else:
            print(f"❌ Lead {args.opt_out} not found.")
        return

    # 5. Campaign Dispatch Mode
    if args.campaign:
        print_banner()
        engine = CampaignEngine()
        print(f"\nInitiating Campaign for Project ID {args.project_id} (City: {args.city})...")
        campaign_id = database.create_campaign(
            name=f"CLI Campaign - Project {args.project_id}",
            project_id=args.project_id,
            audience_city=args.city,
        )
        res = engine.run_campaign(
            campaign_id=campaign_id,
            dry_run=args.dry_run,
            media_type=args.media,
        )
        print("\n--- Campaign Execution Summary ---")
        print(f" • Campaign ID:       {res['campaign_id']}")
        print(f" • Project:           {res['project']}")
        print(f" • Total Lead Pool:   {res['total_leads']}")
        print(f" • Eligible Opted-In: {res['eligible_leads']}")
        print(f" • Sent Count:        {res['sent']}")
        print(f" • Ineligible Skipped:{res['ineligible_skipped']}")
        print(f" • Failed Count:      {res['failed']}")
        return

    # 6. Single Lead Template Dispatch Mode
    if args.to:
        print_banner()
        engine = CampaignEngine()
        print(f"\nChecking opt-in compliance for recipient {args.to}...")
        lead = database.get_lead_by_phone(args.to)
        if lead:
            eligible, reason = ComplianceEngine.can_send_marketing_message(lead)
            if not eligible:
                print(f"🚫 [BLOCKED BY COMPLIANCE] Cannot send to {args.to}:")
                print(f"   Reason: {reason}")
                return
            print(f"✔ Recipient verified: {lead['name']} ({lead['status']})")
        else:
            print(f"ℹ️ New recipient {args.to}. Verifying formatting...")

        res = engine.send_single_project_template(
            phone=args.to,
            project_id=args.project_id,
            media_type=args.media,
            dry_run=args.dry_run,
            direct=args.direct,
            template_name=args.template,
        )
        if res.get("success"):
            print("✅ [SUCCESS] Real estate message dispatched successfully!")
            if res.get("note"):
                print(f"ℹ️ {res.get('note')}")
            if args.dry_run:
                print("\nRendered Template Preview:")
                print(res.get("rendered_text"))
            else:
                wa_data = res.get("data", {})
                msgs = wa_data.get("messages", [])
                if msgs:
                    print(f" • WhatsApp Message ID: {msgs[0].get('id')}")
        else:
            print(f"❌ [FAILED] Error: {res.get('message')}")
            if res.get("error_code") == 132001:
                print("\n💡 Tip: Custom template 'real_estate_layout_launch' has not been registered in Meta WhatsApp Manager yet.")
                print("   👉 Use direct layout dispatch instead:  python send_whatsapp.py --to " + str(args.to) + " --direct")
                print("   👉 Or send with an approved template: python send_whatsapp.py --to " + str(args.to) + " --template hello_world")
        return

    # 7. Guided Interactive Mode
    print_banner()
    print("\nSelect an action:")
    print(" 1. Verify Meta WhatsApp API Credentials")
    print(" 2. Preview Real Estate Template & Meta JSON Payload")
    print(" 3. Send Real Estate Template to a Lead (with Opt-In Check)")
    print(" 4. Launch WhatsApp Marketing Campaign to Opted-in Leads")
    print(" 5. View Leads & Opt-In Compliance Records")
    print(" 6. Exit")

    choice = input("\nEnter choice [1-6, default 2]: ").strip() or "2"

    if choice == "1":
        args.verify = True
        main(args)
    elif choice == "2":
        args.preview = True
        main(args)
    elif choice == "3":
        phone = input("Enter recipient phone number with country code (e.g. 919876543210): ").strip()
        if phone:
            dry = input("Run in Dry-Run mode? (y/n, default y): ").strip().lower() != "n"
            args.to = phone
            args.dry_run = dry
            main(args)
    elif choice == "4":
        city = input("Enter audience city filter (e.g. Chennai, Bangalore, All, default All): ").strip() or "All"
        dry = input("Run in Dry-Run mode? (y/n, default y): ").strip().lower() != "n"
        args.campaign = True
        args.city = city
        args.dry_run = dry
        main(args)
    elif choice == "5":
        args.leads = True
        main(args)
    else:
        print("Goodbye!")


if __name__ == "__main__":
    main()
