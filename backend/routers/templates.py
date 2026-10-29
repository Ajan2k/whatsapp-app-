"""
Real Estate Templates & Project Catalog Router
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

import database
from marketing.template_generator import RealEstateTemplateGenerator

router = APIRouter(tags=["Templates & Projects"])


@router.get("/api/projects")
def list_projects():
    """Lists all real estate projects and layouts."""
    return database.get_projects()


@router.get("/api/projects/{project_id}")
def get_project_details(project_id: int):
    """Retrieves layout details, pricing, approvals, and media for a specific project."""
    project = database.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/api/templates/preview")
def preview_template(
    project_id: int = 1,
    lead_name: str = "Aravind Kumar",
    media_type: str = "IMAGE",
):
    """
    Returns rendered text preview, Meta Cloud API JSON payload,
    and WhatsApp Business Manager registration schema.
    """
    project = database.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    text_preview = RealEstateTemplateGenerator.format_rendered_message_text(lead_name, project)
    meta_payload = RealEstateTemplateGenerator.build_meta_template_payload(
        to_phone="919876543210",
        lead_name=lead_name,
        project=project,
        media_type=media_type,
    )
    interactive_payload = RealEstateTemplateGenerator.build_meta_interactive_message(
        to_phone="919876543210",
        lead_name=lead_name,
        project=project,
        media_type=media_type,
    )
    registration_schema = RealEstateTemplateGenerator.get_meta_registration_schema()

    return {
        "text_preview": text_preview,
        "meta_cloud_api_payload": meta_payload,
        "meta_interactive_payload": interactive_payload,
        "meta_registration_schema": registration_schema,
    }
