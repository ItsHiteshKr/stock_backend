from fastapi import APIRouter, HTTPException
from typing import Optional

from schema.candle_ai import (
    StartMonitorRequest, StartMonitorResponse,
    StopMonitorRequest, StopMonitorResponse,
    StatusResponse, MonitorStatusItem,
    SymbolsResponse, MarketStatusResponse,
    NotificationOut, NotificationsResponse, MarkReadRequest,
)
from service.candle_ai import (
    start_monitoring, stop_monitoring, get_status,
    fix_symbol, is_market_open, SYMBOL_MAP,
    get_notifications, mark_notifications_read, clear_notifications,
)

router = APIRouter(prefix="/api/candle", tags=["Candle AI"])


# Monitor endpoints 

@router.post("/start", response_model=StartMonitorResponse)
async def start(req: StartMonitorRequest):
    """
    Start live monitoring for a list of stocks.
    - Each stock monitors 5m, 15m, 60m automatically.
    - Notifications stored when confidence > 80%.
    - email_receivers is optional — leave empty [] for API-only notifications.
    """
    try:
        started = start_monitoring(req.symbols, req.email_receivers)
        msg = f"{len(started)} monitors started."
        if req.email_receivers:
            msg += f" Email alerts → {req.email_receivers}"
        else:
            msg += " API notifications only (no email)."
        return StartMonitorResponse(success=True, started=started, message=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=StopMonitorResponse)
async def stop(req: StopMonitorRequest):
    """Stop monitoring a stock (all intervals or one specific interval)."""
    try:
        stopped = stop_monitoring(req.symbol, req.interval)
        if not stopped:
            raise HTTPException(status_code=404,
                detail=f"No active monitor for {req.symbol}"
                       +(f" [{req.interval}]" if req.interval else ""))
        return StopMonitorResponse(success=True, stopped=stopped,
                                   message=f"{len(stopped)} monitor(s) stopped.")
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=StatusResponse)
async def status():
    """Get current status of all active monitors."""
    items = [MonitorStatusItem(**m) for m in get_status()]
    return StatusResponse(total_monitors=len(items), monitors=items)


# Notification endpoints 

@router.get("/notifications", response_model=NotificationsResponse)
async def get_all_notifications():
    """
    Get all notifications where confidence > 80%.
    Frontend polls this endpoint every few seconds to show alerts.
    Returns both read and unread notifications.
    """
    notifs = get_notifications(unread_only=False)
    unread = sum(1 for n in notifs if not n.is_read)
    return NotificationsResponse(
        total=len(notifs),
        unread_count=unread,
        notifications=[NotificationOut(**n.__dict__) for n in notifs]
    )


@router.get("/notifications/unread", response_model=NotificationsResponse)
async def get_unread_notifications():
    """
    Get only unread notifications.
    Frontend uses this to show badge count or popup.
    """
    notifs = get_notifications(unread_only=True)
    return NotificationsResponse(
        total=len(notifs),
        unread_count=len(notifs),
        notifications=[NotificationOut(**n.__dict__) for n in notifs]
    )


@router.post("/notifications/mark-read")
async def mark_read(req: MarkReadRequest):
    """
    Mark notifications as read after frontend has shown them.
    Pass list of notification IDs to mark.
    """
    mark_notifications_read(req.ids)
    return {"success": True, "marked": len(req.ids)}

