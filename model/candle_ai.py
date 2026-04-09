import threading
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Notification:
    """
    One alert stored in memory when confidence > 80%.
    Frontend reads these via GET /api/candle/notifications.
    """
    id:          str       # unique id e.g. "RELIANCE.NS:5m:10:15"
    symbol:      str
    interval:    str
    time:        str       # candle close time e.g. "10:15"
    pattern:     str
    direction:   str       # BULLISH / BEARISH
    confidence:  int
    signal:      str       # BUY Signal / SELL Signal
    trend:       str
    support:     Optional[float]
    resistance:  Optional[float]
    candle_open:   float
    candle_high:   float
    candle_low:    float
    candle_close:  float
    created_at:  datetime  = field(default_factory=datetime.utcnow)
    is_read:     bool      = False


@dataclass
class MonitorSession:
    """
    Live state for one (symbol + interval) monitor.
    email_receivers — set per user when they call /start
    """
    symbol:           str
    interval:         str
    email_receivers:  List[str]       = field(default_factory=list)
    today_candles:    List[dict]      = field(default_factory=list)
    last_ts:          Optional[str]   = None
    validated:        bool            = False
    start_time:       datetime        = field(default_factory=datetime.utcnow)
    first_run_done:   bool            = False
    stop_event:       threading.Event = field(default_factory=threading.Event)
    last_pattern:     Optional[str]   = None
    last_confidence:  Optional[int]   = None
    last_direction:   Optional[str]   = None
    last_candle_time: Optional[str]   = None
    last_signal:      Optional[str]   = None