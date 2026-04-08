import threading
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class MonitorSession:
    """
    Live state for one (symbol + interval) monitor.
    email_receivers — set per user when they call /start
    """
    symbol:           str
    interval:         str
    email_receivers:  List[str]        = field(default_factory=list)
    today_candles:    List[dict]       = field(default_factory=list)
    last_ts:          Optional[str]    = None
    validated:        bool             = False
    start_time:       datetime         = field(default_factory=datetime.utcnow)
    first_run_done:   bool             = False
    stop_event:       threading.Event  = field(default_factory=threading.Event)
    last_pattern:     Optional[str]    = None
    last_confidence:  Optional[int]    = None
    last_direction:   Optional[str]    = None
    last_candle_time: Optional[str]    = None
    last_signal:      Optional[str]    = None