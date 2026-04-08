from fastapi import APIRouter, HTTPException
from typing import Optional

from schema.candle_ai import (
    StartMonitorRequest, StartMonitorResponse,
    StopMonitorRequest, StopMonitorResponse,
    StatusResponse, MonitorStatusItem,
    SymbolsResponse, MarketStatusResponse,
)
from service.candle_ai import (
    start_monitoring, stop_monitoring, get_status,
    fix_symbol, is_market_open, SYMBOL_MAP,
)

router = APIRouter(prefix="/api/candle", tags=["Candle AI"])


@router.post("/start", response_model=StartMonitorResponse)
async def start(req: StartMonitorRequest):
    try:
        started = start_monitoring(req.symbols, req.email_receivers)
        return StartMonitorResponse(
            success=True,
            started=started,
            message=f"{len(started)} monitors started. Alerts → {req.email_receivers}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=StopMonitorResponse)
async def stop(req: StopMonitorRequest):
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
    items = [MonitorStatusItem(**m) for m in get_status()]
    return StatusResponse(total_monitors=len(items), monitors=items)


