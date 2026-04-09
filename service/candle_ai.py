import os
import uuid
import yfinance as yf
import time
import smtplib
import threading
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from model.candle_ai import MonitorSession, Notification


#  Settings 

EMAIL_SENDER   = os.getenv("EMAIL_SENDER",   "imabhaytiwari1@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD",  "")
EMAIL_ENABLED  = os.getenv("EMAIL_ENABLED",  "true").lower() == "true"
EMAIL_MIN_CONF = int(os.getenv("EMAIL_MIN_CONF", "80"))

LOOKBACK_CANDLES  = 60
MONITOR_INTERVALS = ["5m", "15m", "60m"]
INTERVAL_MIN      = {"1m":1,"2m":2,"5m":5,"15m":15,"30m":30,"60m":60,"90m":90}

MARKET_HOURS = {
    ".NS":    (3, 45, 10, 0,  [0,1,2,3,4]),
    ".BO":    (3, 45, 10, 0,  [0,1,2,3,4]),
    "US":     (13, 30, 20, 0, [0,1,2,3,4]),
    "CRYPTO": (0,  0, 23, 59, [0,1,2,3,4,5,6]),
}

SYMBOL_MAP = {
    "NIFTY 50":"^NSEI","NIFTY50":"^NSEI","NIFTY":"^NSEI","NSE":"^NSEI",
    "SENSEX":"^BSESN","BSE":"^BSESN","BANKNIFTY":"^NSEBANK",
    "BANK NIFTY":"^NSEBANK","NIFTYBANK":"^NSEBANK","NIFTY BANK":"^NSEBANK",
    "S&P 500":"^GSPC","SP500":"^GSPC","DOW":"^DJI","NASDAQ":"^IXIC",
    "RELIANCE":"RELIANCE.NS","RELAINCE":"RELIANCE.NS",
    "TCS":"TCS.NS","INFOSYS":"INFY.NS","INFY":"INFY.NS",
    "HDFC":"HDFCBANK.NS","HDFCBANK":"HDFCBANK.NS","WIPRO":"WIPRO.NS",
    "ICICI":"ICICIBANK.NS","ICICIBANK":"ICICIBANK.NS",
    "SBI":"SBIN.NS","SBIN":"SBIN.NS","ONGC":"ONGC.NS","IOC":"IOC.NS",
    "BAJAJ":"BAJAJFINSV.NS","BHARTIARTL":"BHARTIARTL.NS","AIRTEL":"BHARTIARTL.NS",
    "MARUTI":"MARUTI.NS","TATAMOTORS":"TATAMOTORS.NS","TATA MOTORS":"TATAMOTORS.NS",
    "TATASTEEL":"TATASTEEL.NS","TATA STEEL":"TATASTEEL.NS",
    "ADANIENT":"ADANIENT.NS","ADANI":"ADANIENT.NS",
    "ITC":"ITC.NS","HINDALCO":"HINDALCO.NS","JSWSTEEL":"JSWSTEEL.NS",
    "LT":"LT.NS","LTIM":"LTIM.NS","POWERGRID":"POWERGRID.NS","NTPC":"NTPC.NS",
    "BAJFINANCE":"BAJFINANCE.NS","M&M":"M&M.NS","ULTRACEMCO":"ULTRACEMCO.NS",
    "KOTAKBANK":"KOTAKBANK.NS","KOTAK":"KOTAKBANK.NS",
    "AXISBANK":"AXISBANK.NS","AXIS":"AXISBANK.NS",
    "TITAN":"TITAN.NS","NESTLEIND":"NESTLEIND.NS","NESTLE":"NESTLEIND.NS",
    "ASIANPAINT":"ASIANPAINT.NS","ASIAN PAINT":"ASIANPAINT.NS",
    "SUNPHARMA":"SUNPHARMA.NS","DRREDDY":"DRREDDY.NS","CIPLA":"CIPLA.NS",
    "DIVISLAB":"DIVISLAB.NS","HCLTECH":"HCLTECH.NS","HCL":"HCLTECH.NS",
    "TECHM":"TECHM.NS","EICHERMOT":"EICHERMOT.NS","HEROMOTOCO":"HEROMOTOCO.NS",
    "BAJAJ AUTO":"BAJAJ-AUTO.NS","BAJAJAUTO":"BAJAJ-AUTO.NS",
    "COALINDIA":"COALINDIA.NS","COAL INDIA":"COALINDIA.NS",
    "HINDCOPPER":"HINDCOPPER.NS","HINDPETRO":"HINDPETRO.NS",
    "ATGL":"ATGL.NS","TMCV":"TATAMOTORS.NS",
    "BTC":"BTC-USD","ETH":"ETH-USD","SOL":"SOL-USD",
}

BIAS = {
    "Morning Star"             :("BULLISH",85,"3C: bearish > small star > bullish above midpoint"),
    "Three White Soldiers"     :("BULLISH",85,"3 rising bullish bodies — sustained buying"),
    "Three Inside Up"          :("BULLISH",80,"Bullish harami confirmed by 3rd rising candle"),
    "W Pattern (Double Bottom)":("BULLISH",78,"Double low defended — buyers absorbing sellers"),
    "Bullish Engulfing"        :("BULLISH",78,"Bulls swallowed entire prior bearish body"),
    "Hammer"                   :("BULLISH",72,"Sellers pushed down, buyers fully recovered"),
    "Piercing Line"            :("BULLISH",68,"Bulls crossed bearish candle midpoint"),
    "Dragonfly Doji"           :("BULLISH",65,"Long lower wick — buyers took full control"),
    "Tweezer Bottom"           :("BULLISH",65,"Same low hit twice — buyers active at that price"),
    "Bullish Harami"           :("BULLISH",58,"Small inside candle — selling pressure slowing"),
    "Inverted Hammer"          :("BULLISH",52,"Buyers probed higher — needs confirm candle"),
    "Bullish Marubozu"         :("BULLISH",82,"No wicks — pure uninterrupted buying pressure"),
    "Strong Bullish Candle"    :("BULLISH",65,"Large body — buyers clearly in control"),
    "Bullish Candle"           :("BULLISH",52,"Mild bullish momentum"),
    "Evening Star"             :("BEARISH",85,"3C: bullish > small star > bearish below midpoint"),
    "Three Black Crows"        :("BEARISH",85,"3 falling bearish bodies — sustained selling"),
    "Three Inside Down"        :("BEARISH",80,"Bearish harami confirmed by 3rd falling candle"),
    "M Pattern (Double Top)"   :("BEARISH",78,"Double high defended — sellers absorbing buyers"),
    "Bearish Engulfing"        :("BEARISH",78,"Bears swallowed entire prior bullish body"),
    "Shooting Star"            :("BEARISH",72,"Buyers pushed up, sellers fully recovered"),
    "Dark Cloud Cover"         :("BEARISH",68,"Bears crossed bullish candle midpoint"),
    "Gravestone Doji"          :("BEARISH",65,"Long upper wick — sellers took full control"),
    "Tweezer Top"              :("BEARISH",65,"Same high hit twice — sellers active at that price"),
    "Hanging Man"              :("BEARISH",60,"Long lower wick at highs — buyers weakening"),
    "Bearish Harami"           :("BEARISH",58,"Small inside candle — buying pressure slowing"),
    "Bearish Marubozu"         :("BEARISH",82,"No wicks — pure uninterrupted selling pressure"),
    "Strong Bearish Candle"    :("BEARISH",65,"Large body — sellers clearly in control"),
    "Bearish Candle"           :("BEARISH",52,"Mild bearish momentum"),
    "Doji"                     :("NEUTRAL",40,"Open ≈ Close — perfect indecision"),
    "Doji Flat"                :("NEUTRAL",25,"No movement at all"),
    "Long-Legged Doji"         :("NEUTRAL",35,"Both sides fought equally — no winner"),
    "Spinning Top"             :("NEUTRAL",42,"Both wicks visible — neither side dominated"),
    "High Wave Candle"         :("NEUTRAL",35,"Extreme wicks — high uncertainty"),
    "Narrow Range Candle"      :("NEUTRAL",30,"Very small range — consolidation"),
}


#  In-memory notification store 
# Stores all alerts where confidence > 80%.
# Frontend reads these via GET /api/candle/notifications.
# Max 500 notifications kept to avoid memory growing forever.

_notifications: List[Notification] = []
_notif_lock    = threading.Lock()
MAX_NOTIFICATIONS = 500


def _store_notification(candle, pattern, direction, confidence,
                        trend, support, resistance, symbol, interval):
    """Store one notification in memory."""
    notif = Notification(
        id=f"{symbol}:{interval}:{candle['time']}:{uuid.uuid4().hex[:6]}",
        symbol=symbol,
        interval=interval,
        time=candle["time"],
        pattern=pattern,
        direction=direction,
        confidence=confidence,
        signal=("BUY Signal"  if direction=="BULLISH" else
                "SELL Signal" if direction=="BEARISH" else "WAIT"),
        trend=trend,
        support=support,
        resistance=resistance,
        candle_open=round(candle["open"],  2),
        candle_high=round(candle["high"],  2),
        candle_low=round(candle["low"],    2),
        candle_close=round(candle["close"],2),
    )
    with _notif_lock:
        _notifications.append(notif)
        # Keep only the latest MAX_NOTIFICATIONS
        if len(_notifications) > MAX_NOTIFICATIONS:
            del _notifications[:-MAX_NOTIFICATIONS]


def get_notifications(unread_only: bool = False) -> List[Notification]:
    with _notif_lock:
        if unread_only:
            return [n for n in _notifications if not n.is_read]
        return list(_notifications)


def mark_notifications_read(ids: List[str]):
    with _notif_lock:
        id_set = set(ids)
        for n in _notifications:
            if n.id in id_set:
                n.is_read = True


def clear_notifications():
    with _notif_lock:
        _notifications.clear()


# Helpers (unchanged from candle_ai.py) 

def fix_symbol(raw: str) -> str:
    s = raw.strip().upper()
    return SYMBOL_MAP.get(s, s)


def is_market_open(symbol: str):
    now_utc = datetime.now(timezone.utc)
    weekday = now_utc.weekday()
    if symbol.endswith("-USD") or symbol.endswith("-USDT"):
        return True, "Crypto — 24/7 live"
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        suffix, label = ".NS", "NSE/BSE"
    elif symbol.startswith("^"):
        suffix = ".NS" if ("NSE" in symbol or "BSE" in symbol) else "US"
        label  = "Index"
    else:
        suffix, label = "US", "US Market"
    h = MARKET_HOURS[suffix]
    if weekday not in h[4]:
        return False, f"{label} CLOSED (weekend)"
    open_t  = now_utc.replace(hour=h[0], minute=h[1], second=0, microsecond=0)
    close_t = now_utc.replace(hour=h[2], minute=h[3], second=0, microsecond=0)
    if open_t <= now_utc <= close_t:
        return True, f"{label} OPEN — {int((close_t-now_utc).total_seconds()//60)} min until close"
    elif now_utc < open_t:
        return False, f"{label} opens in {int((open_t-now_utc).total_seconds()//60)} min"
    else:
        return False, f"{label} CLOSED for today"


def _secs_to_next_candle(interval: str) -> int:
    mins = INTERVAL_MIN.get(interval, 5)
    now  = datetime.now()
    secs_left = (mins*60) - ((now.minute*60 + now.second) % (mins*60))
    return max(5, secs_left + 5)


def metrics(o, h, l, c):
    rng=h-l; body=abs(c-o); bull=c>=o
    uw=h-max(o,c); lw=min(o,c)-l
    bp=body/rng if rng>1e-10 else 0
    up=uw/rng   if rng>1e-10 else 0
    lp=lw/rng   if rng>1e-10 else 0
    return body,rng,bull,uw,lw,bp,up,lp


# Pattern detection (unchanged from candle_ai.py) 

def detect_pattern(window, session=None, interval='5m'):
    if not window: return "No Data",1
    c=window[-1]; o,h,l,close=c["open"],c["high"],c["low"],c["close"]
    body,rng,bull,uw,lw,bp,up,lp=metrics(o,h,l,close)
    min_range_ok=(rng/(close+1e-10))>=0.0015
    _iv=interval if interval else "5m"
    if _iv=="60m": _n,_mc=3,2
    elif _iv=="15m": _n,_mc=4,2
    else: _n,_mc=6,3
    hist=session if(session and len(session)>=_mc) else None
    def _tw(offset=0,n=_n):
        if hist is None: return None
        lb=hist[-n:] if offset==0 else hist[-(n+offset):-offset]
        return lb if lb and len(lb)>=2 else None
    def is_down(offset=0):
        lb=_tw(offset)
        if lb is None: return False
        b=sum(1 for x in lb if x["close"]<x["open"])
        return b>=len(lb)*0.67 and lb[-1]["close"]<lb[0]["open"]
    def is_up(offset=0):
        lb=_tw(offset)
        if lb is None: return False
        b=sum(1 for x in lb if x["close"]>=x["open"])
        return b>=len(lb)*0.67 and lb[-1]["close"]>lb[0]["open"]
    if len(window)>=3:
        p1=window[-3]; p2=window[-2]
        o1,h1,l1,c1=p1["open"],p1["high"],p1["low"],p1["close"]
        o2,h2,l2,c2=p2["open"],p2["high"],p2["low"],p2["close"]
        b1=abs(c1-o1); b2=abs(c2-o2); bl1=c1>=o1; bl2=c2>=o2; r1=h1-l1; r2=h2-l2
        if(not bl1 and r1>1e-10 and b1/r1>0.30 and b1>b2*2 and r2>1e-10 and b2/r2<0.35
               and bull and bp>0.30 and close>(o1+c1)/2 and is_down(offset=2)):
            return "Morning Star",3
        if(bl1 and r1>1e-10 and b1/r1>0.30 and b1>b2*2 and r2>1e-10 and b2/r2<0.35
               and not bull and bp>0.30 and close<(o1+c1)/2 and is_up(offset=2)):
            return "Evening Star",3
        if(bl1 and bl2 and bull and c2>c1 and close>c2 and o2>c1 and o2<h1
               and o>c2 and o<h2 and r1>1e-10 and b1/r1>0.50 and r2>1e-10 and b2/r2>0.50 and bp>0.50):
            return "Three White Soldiers",3
        if(not bl1 and not bl2 and not bull and c2<c1 and close<c2 and o2<c1 and o2>l1
               and o<c2 and o>l2 and r1>1e-10 and b1/r1>0.50 and r2>1e-10 and b2/r2>0.50 and bp>0.50):
            return "Three Black Crows",3
        bh=(not bl1 and r1>1e-10 and b1/r1>=0.30 and bl2 and o2>c1 and c2<o1 and abs(c2-o2)<b1*0.6)
        if bh and bull and close>c2 and is_down(offset=2): return "Three Inside Up",3
        bd=(bl1 and r1>1e-10 and b1/r1>=0.30 and not bl2 and o2<c1 and c2>o1 and abs(c2-o2)<b1*0.6)
        if bd and not bull and close<c2 and is_up(offset=2): return "Three Inside Down",3
    src=session if session and len(session)>=8 else None
    if src:
        lw_s=[x["low"] for x in src[-12:]]; hw_s=[x["high"] for x in src[-12:]]
        mn=min(lw_s); mi=lw_s.index(mn)
        if 2<=mi<=len(lw_s)-3:
            sl=min(lw_s[mi+2:mi+6]); si=lw_s.index(sl,mi+2)
            pk=max(hw_s[mi:si+1]) if mi<si else mn
            if abs(sl-mn)<=mn*0.0025 and pk>=mn*1.008 and close>mn*1.005:
                return "W Pattern (Double Bottom)",1
        hm_s=[x["high"] for x in src[-12:]]; lm_s=[x["low"] for x in src[-12:]]
        mx=max(hm_s); mxi=hm_s.index(mx)
        if 2<=mxi<=len(hm_s)-3:
            ei=min(mxi+6,len(hm_s)); sh=max(hm_s[mxi+2:ei]); shi=hm_s.index(sh,mxi+2)
            dip=min(lm_s[mxi:shi+1]) if mxi<shi else mx
            if abs(sh-mx)<=mx*0.0025 and dip<=mx*0.992 and close<mx*0.995:
                return "M Pattern (Double Top)",1
    if len(window)>=2:
        pv=window[-2]; po,ph,pl,pc_p=pv["open"],pv["high"],pv["low"],pv["close"]
        pb,pr,pbl,*_=metrics(po,ph,pl,pc_p); mid=(po+pc_p)/2.0
        pmn=min(po,pc_p); pmx=max(po,pc_p); cmn=min(o,close); cmx=max(o,close)
        if not pbl and bull and pb/(pr+1e-10)>0.10 and cmn<pmn and cmx>pmx and body>pb and is_down(1):
            return "Bullish Engulfing",2
        if pbl and not bull and pb/(pr+1e-10)>0.10 and cmn<pmn and cmx>pmx and body>pb and is_up(1):
            return "Bearish Engulfing",2
        if not pbl and bull and bp>=0.25 and o<pc_p and close>mid and close<po and is_down(1):
            return "Piercing Line",2
        if pbl and not bull and bp>=0.25 and o>pc_p and close<mid and close>po and is_up(1):
            return "Dark Cloud Cover",2
        if not pbl and bull and pb/(pr+1e-10)>=0.15 and o>pc_p and close<po and body<pb*0.6 and is_down(1):
            return "Bullish Harami",2
        if pbl and not bull and pb/(pr+1e-10)>=0.15 and o<pc_p and close>po and body<pb*0.6 and is_up(1):
            return "Bearish Harami",2
        if pbl and not bull and abs(h-ph)<=0.2 and up>0.25 and pb/(pr+1e-10)>0.10 and is_up(1):
            return "Tweezer Top",2
        if not pbl and bull and abs(l-pl)<=0.2 and lp>0.25 and pb/(pr+1e-10)>0.10 and is_down(1):
            return "Tweezer Bottom",2
    if rng<1e-10: return "Doji Flat",1
    if bp<=0.08 and lp>=0.65 and up<=0.12 and min_range_ok and is_down(): return "Dragonfly Doji",1
    if bp<=0.08 and up>=0.65 and lp<=0.12 and min_range_ok and is_up():   return "Gravestone Doji",1
    if bp<=0.10 and up>=0.30 and lp>=0.30 and min_range_ok: return "Long-Legged Doji",1
    if bp<=0.08: return "Doji",1
    if not bull and up>=0.55 and bp<=0.25 and lp<=0.15 and min_range_ok and is_up():  return "Shooting Star",1
    if bull  and up>=0.55 and bp<=0.25 and lp<=0.15 and min_range_ok and is_down():   return "Inverted Hammer",1
    if bull  and lp>=0.55 and bp<=0.25 and up<=0.15 and min_range_ok and is_down():   return "Hammer",1
    if not bull and lp>=0.55 and bp<=0.25 and up<=0.15 and min_range_ok and is_up():  return "Hanging Man",1
    if bp<=0.20 and up>=0.35 and lp>=0.35 and min_range_ok: return "High Wave Candle",1
    if 0.10<=bp<=0.35 and up>=0.15 and lp>=0.15 and min_range_ok: return "Spinning Top",1
    if bull  and bp>=0.90 and uw<=0.05 and lw<=0.05: return "Bullish Marubozu",1
    if not bull and bp>=0.90 and uw<=0.05 and lw<=0.05: return "Bearish Marubozu",1
    if bull  and bp>=0.60 and min_range_ok: return "Strong Bullish Candle",1
    if not bull and bp>=0.60 and min_range_ok: return "Strong Bearish Candle",1
    if rng/(close+1e-10)<0.002: return "Narrow Range Candle",1
    return ("Bullish Candle" if bull else "Bearish Candle"),1


# Analysis helpers 

def investigate(today_candles,pattern):
    w=today_candles[-LOOKBACK_CANDLES:] if len(today_candles)>LOOKBACK_CANDLES else today_candles
    up=down=flat=0
    for i in range(len(w)-1):
        if w[i]["pattern"]==pattern:
            a=w[i]["close"]; b=w[i+1]["close"]
            if b>a: up+=1
            elif b<a: down+=1
            else: flat+=1
    return up,down,flat,up+down+flat

def get_ema(today_candles,period=20):
    closes=[c["close"] for c in today_candles]
    if len(closes)<period: return None
    ema=sum(closes[:period])/period; k=2.0/(period+1)
    for p in closes[period:]: ema=p*k+ema*(1-k)
    return round(ema,2)

def get_trend(today_candles,n=6):
    if len(today_candles)<2: return "LOW DATA"
    n=min(n,len(today_candles)); seq=today_candles[-n:]
    ups=sum(1 for c in seq if c["close"]>=c["open"]); dns=n-ups
    ema=get_ema(today_candles,20); price=today_candles[-1]["close"]
    eb=ema is not None and price>ema; ed=ema is not None and price<ema
    if ups==n and eb: return "STRONG UPTREND"
    elif ups==n: return "UPTREND"
    elif ups>=n*0.67: return "UPTREND"
    elif dns==n and ed: return "STRONG DOWNTREND"
    elif dns==n: return "DOWNTREND"
    elif dns>=n*0.67: return "DOWNTREND"
    else: return "CHOPPY"

def get_levels(today_candles):
    w=today_candles[-LOOKBACK_CANDLES:] if len(today_candles)>LOOKBACK_CANDLES else today_candles
    if len(w)<2: return None,None
    return round(min(c["low"] for c in w),2),round(max(c["high"] for c in w),2)

def vol_signal(today_candles,v):
    w=today_candles[-20:] if len(today_candles)>=20 else today_candles
    if not w: return "NO DATA",0.0
    avg=sum(c["volume"] for c in w)/len(w)
    if avg<1e-10 or v<1e-10: return "INDEX-NO VOL",0.0
    r=v/avg
    if r>=2.5: lbl="VERY HIGH"
    elif r>=1.5: lbl="HIGH"
    elif r<=0.40: lbl="VERY LOW"
    elif r<=0.70: lbl="LOW"
    else: lbl="NORMAL"
    return lbl,round(r,1)

def build_verdict(pattern,today_candles,v):
    bias_dir,base_conf,rule=BIAS.get(pattern,("NEUTRAL",40,"Unknown"))
    up,down,flat,samples=investigate(today_candles,pattern)
    total=max(1,up+down+flat)
    if samples==0:
        direction=bias_dir; confidence=base_conf; basis="Classic TA — first occurrence"
    elif samples==1:
        direction=bias_dir
        confidence=min(95,base_conf+5) if(up>=down)==(bias_dir=="BULLISH") else max(30,base_conf-5)
        basis=f"Pattern dominant | 1 sample: {up}U/{down}D"
    elif samples<=3:
        win=(up/total if bias_dir=="BULLISH" else down/total)*100
        s="BULLISH" if up>down else("BEARISH" if down>up else "NEUTRAL")
        confidence=(round(base_conf*0.70+win*0.30) if s==bias_dir else
                    round(base_conf*0.80) if s=="NEUTRAL" else max(35,round(base_conf*0.60)))
        direction=bias_dir; basis=f"Pattern bias | {samples} samples: {up}U/{down}D"
    elif samples<=6:
        s,win=(("BULLISH",round(up/total*100)) if up>down else
               ("BEARISH",round(down/total*100)) if down>up else ("NEUTRAL",50))
        confidence=(round(base_conf*0.50+win*0.50) if s==bias_dir else
                    round(base_conf*0.65) if s=="NEUTRAL" else max(40,round(win*0.60)))
        direction=bias_dir if s in(bias_dir,"NEUTRAL") else s
        basis=f"{samples} samples: {up}U/{down}D | TA: {bias_dir}"
    else:
        s,win=(("BULLISH",round(up/total*100)) if up>down else
               ("BEARISH",round(down/total*100)) if down>up else ("NEUTRAL",50))
        if s=="NEUTRAL": confidence=round(base_conf*0.40+50*0.60); direction=bias_dir
        elif s==bias_dir: confidence=round(win*0.70+base_conf*0.30); direction=bias_dir
        else: confidence=round(win*0.65); direction=s
        basis=f"Session ({samples} samples): {up}U/{down}D | TA: {bias_dir}"
    v_label,v_ratio=vol_signal(today_candles,v)
    if direction!="NEUTRAL":
        if v_ratio>=2.5: confidence=min(95,confidence+10)
        elif v_ratio>=1.5: confidence=min(95,confidence+5)
        elif v_ratio<=0.40: confidence=max(25,confidence-12)
        elif v_ratio<=0.70: confidence=max(25,confidence-5)
    confidence=max(25,min(95,confidence))
    return direction,confidence,rule,basis,up,down,flat,samples,v_label,v_ratio


# Email

def send_alert(candle,pattern,direction,confidence,rule,
               trend,support,resistance,v_label,v_ratio,
               symbol,interval,up,down,samples,
               email_receivers:List[str]):
    if not EMAIL_ENABLED or not email_receivers: return
    if confidence<=EMAIL_MIN_CONF: return
    if direction=="BULLISH": move,signal="PRICE WILL GO UP","BUY Signal"
    elif direction=="BEARISH": move,signal="PRICE WILL GO DOWN","SELL Signal"
    else: move,signal="NO CLEAR DIRECTION","WAIT — No Signal"
    if confidence>=75: cw="HIGH confidence"
    elif confidence>=60: cw="MEDIUM confidence"
    elif confidence>=45: cw="LOW confidence"
    else: cw="VERY LOW confidence — do not act"
    bull=candle["close"]>=candle["open"]
    subject=f"[CANDLE AI] {symbol} | {pattern} | {signal} | {candle['time']} | {confidence}% {cw.split()[0]}"
    body=f"""
CANDLE AI — Pattern Alert

  Symbol     :  {symbol}  [{interval}]
  Time       :  {candle['time']}  ({'BULLISH' if bull else 'BEARISH'} candle)
  Open: {round(candle['open'],2)}  High: {round(candle['high'],2)}  Low: {round(candle['low'],2)}  Close: {round(candle['close'],2)}

  Pattern    :  {pattern}
  Signal     :  {signal}
  Confidence :  {confidence}%  —  {cw}
  Trend      :  {trend}
  Support    :  {support}   Resistance: {resistance}
"""
    msg=MIMEMultipart()
    msg["From"]=EMAIL_SENDER; msg["To"]=", ".join(email_receivers); msg["Subject"]=subject
    msg.attach(MIMEText(body,"plain"))
    for attempt in range(1,4):
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com",465,timeout=15) as srv:
                srv.login(EMAIL_SENDER,EMAIL_PASSWORD)
                srv.sendmail(EMAIL_SENDER,email_receivers,msg.as_string())
            break
        except smtplib.SMTPAuthenticationError: break
        except Exception:
            if attempt<3: time.sleep(attempt*3)


# Data fetch 

def fetch_candles(symbol,interval):
    for attempt in range(1,4):
        try:
            df=yf.Ticker(symbol).history(period="1d",interval=interval)
            if df is None or df.empty: return None
            df.index=(df.index.tz_localize(None) if df.index.tzinfo is None
                      else df.index.tz_convert(None))
            df=df.rename(columns={"Open":"open","High":"high","Low":"low",
                                   "Close":"close","Volume":"volume"})
            return df[["open","high","low","close","volume"]]
        except Exception:
            if attempt<3: time.sleep(attempt*5)
    return None


# Session registry 

_sessions: Dict[str,MonitorSession] = {}
_lock = threading.Lock()


# Monitor thread 

def _run_monitor(state: MonitorSession):
    symbol=state.symbol; interval=state.interval
    while not state.stop_event.is_set():
        try:
            df=fetch_candles(symbol,interval)
            if df is not None and not df.empty:
                _process(df,state)
        except Exception as e:
            print(f"[MONITOR ERROR] {symbol} {interval}: {e}")
        state.stop_event.wait(timeout=_secs_to_next_candle(interval))


def _process(df,state:MonitorSession):
    symbol=state.symbol; interval=state.interval
    closed=df.iloc[:-1]
    show_last_one=None
    if not state.first_run_done:
        last_ts=None
        for ts,row in closed.iterrows(): last_ts=str(ts)
        show_last_one=last_ts; state.first_run_done=True
    for ts,row in closed.iterrows():
        ts_str=str(ts)
        if state.last_ts and ts_str<=state.last_ts: continue
        if show_last_one and ts_str!=show_last_one:
            state.last_ts=ts_str; continue
        state.last_ts=ts_str
        o=float(row["open"]); h=float(row["high"])
        l=float(row["low"]);  c=float(row["close"]); v=float(row["volume"])
        try:
            im=INTERVAL_MIN.get(interval,5)
            t=datetime.fromtimestamp(ts.timestamp()+im*60).strftime("%H:%M")
        except: t=str(ts)[11:16]
        candle={"open":o,"high":h,"low":l,"close":c,"volume":v,"time":t,"pattern":""}
        today=state.today_candles
        if len(today)>=2: window=today[-2:]+[candle]
        elif len(today)==1: window=[today[-1],candle]
        else: window=[candle]
        result=detect_pattern(window,session=today,interval=interval)
        pattern,cn=result if isinstance(result,tuple) else (result,1)
        candle["pattern"]=pattern; today.append(candle)
        direction,conf,rule,basis,up,down,flat,samples,v_lbl,v_ratio=build_verdict(pattern,today,v)
        trend=get_trend(today); support,resist=get_levels(today)
        state.last_pattern=pattern; state.last_confidence=conf
        state.last_direction=direction; state.last_candle_time=t
        state.last_signal=("BUY Signal" if direction=="BULLISH" else
                           "SELL Signal" if direction=="BEARISH" else "WAIT")

        # ── When confidence > 80%: store notification + optional email ──
        if conf > EMAIL_MIN_CONF and direction != "NEUTRAL":
            # Always store in-memory notification (frontend reads this)
            _store_notification(candle, pattern, direction, conf,
                                trend, support, resist, symbol, interval)
            # Send email only if user provided email addresses
            if state.email_receivers:
                threading.Thread(
                    target=send_alert,
                    args=(candle,pattern,direction,conf,rule,trend,support,resist,
                          v_lbl,v_ratio,symbol,interval,up,down,samples,
                          state.email_receivers),
                    daemon=True
                ).start()


# Public functions called by router 

def start_monitoring(raw_symbols:List[str], email_receivers:List[str]) -> List[str]:
    started=[]
    for raw in raw_symbols:
        symbol=fix_symbol(raw)
        for interval in MONITOR_INTERVALS:
            key=f"{symbol}:{interval}"
            with _lock:
                if key in _sessions: continue
                state=MonitorSession(symbol=symbol,interval=interval,
                                     email_receivers=email_receivers)
                _sessions[key]=state
            threading.Thread(target=_run_monitor,args=(state,),
                             daemon=True,name=f"monitor-{key}").start()
            started.append(key)
    return started


def stop_monitoring(symbol:str, interval:Optional[str]=None) -> List[str]:
    stopped=[]
    with _lock:
        keys=[k for k in list(_sessions.keys())
              if k.startswith(symbol) and(interval is None or k.endswith(f":{interval}"))]
        for key in keys:
            _sessions[key].stop_event.set(); del _sessions[key]; stopped.append(key)
    return stopped


def get_status() -> List[dict]:
    result=[]
    with _lock:
        for key,state in _sessions.items():
            is_open,_=is_market_open(state.symbol)
            result.append({
                "symbol":state.symbol,"interval":state.interval,
                "candles_today":len(state.today_candles),"is_market_open":is_open,
                "email_receivers":state.email_receivers,
                "last_candle_time":state.last_candle_time,
                "last_pattern":state.last_pattern,"last_confidence":state.last_confidence,
                "last_direction":state.last_direction,"last_signal":state.last_signal,
            })
    return result