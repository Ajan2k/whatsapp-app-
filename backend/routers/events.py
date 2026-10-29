"""
SSE Event Router for Real-Time Dashboard Synchronization
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from backend import events

router = APIRouter(tags=["Events"])


class BroadcastEventRequest(BaseModel):
    event_type: str
    data: Optional[Dict[str, Any]] = None


@router.get("/api/events")
async def sse_events():
    """Server-Sent Events endpoint for real-time dashboard synchronization."""
    return StreamingResponse(
        events.subscribe(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/api/events/broadcast")
def broadcast_external_event(req: BroadcastEventRequest):
    """Allows CLI scripts and external workers to push real-time updates to connected dashboards."""
    events.broadcast(req.event_type, req.data or {})
    return {"success": True, "broadcasted": req.event_type}
