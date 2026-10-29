"""
Real-Time Event Broadcaster for WhatsApp Marketing Platform
Powers Server-Sent Events (SSE) between backend, CLI script, Meta webhooks, and dashboard.
"""

import asyncio
import json
import logging
from typing import Set, Dict, Any, AsyncGenerator

logger = logging.getLogger("EventBus")

# In-memory subscriber queues for connected dashboard clients
_subscribers: Set[asyncio.Queue] = set()
_main_loop: asyncio.AbstractEventLoop = None


def register_event_loop(loop: asyncio.AbstractEventLoop):
    global _main_loop
    _main_loop = loop


async def subscribe() -> AsyncGenerator[str, None]:
    """Generates SSE stream for a connected client."""
    queue = asyncio.Queue(maxsize=100)
    _subscribers.add(queue)
    logger.info("New dashboard client subscribed to SSE stream. Total: %d", len(_subscribers))

    # Send initial welcome / ping event
    welcome_payload = json.dumps({"status": "connected", "subscribers": len(_subscribers)})
    yield f"event: ping\ndata: {welcome_payload}\n\n"

    try:
        while True:
            try:
                # Wait for next event or send heartbeat every 20 seconds
                event_data = await asyncio.wait_for(queue.get(), timeout=20.0)
                yield event_data
            except asyncio.TimeoutError:
                # Keep-alive heartbeat comment
                yield ": heartbeat\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        _subscribers.discard(queue)
        logger.info("Dashboard client disconnected from SSE stream. Remaining: %d", len(_subscribers))


def broadcast(event_type: str, data: Dict[str, Any] = None):
    """
    Broadcasts an event to all active dashboard subscribers.
    Thread-safe and works from both sync and async contexts.
    """
    if not _subscribers:
        return

    payload = json.dumps(data or {})
    sse_message = f"event: {event_type}\ndata: {payload}\n\n"

    for q in list(_subscribers):
        try:
            if q.full():
                try:
                    q.get_nowait()
                except Exception:
                    pass
            q.put_nowait(sse_message)
        except Exception as ex:
            logger.debug("Could not queue event for subscriber: %s", ex)
