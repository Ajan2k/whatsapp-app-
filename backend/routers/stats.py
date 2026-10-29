"""
Stats & Funnel Analytics Router
"""

from fastapi import APIRouter
import database

router = APIRouter(tags=["Stats"])


@router.get("/api/stats")
def get_dashboard_stats():
    """Returns top-level unified campaign and message log funnel statistics."""
    return database.get_overall_stats()
