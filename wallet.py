# wallet.py
from __future__ import annotations
from pathlib import Path
import json
from datetime import date, timedelta

WALLET_PATH = Path("wallets.json")

def load_wallets() -> dict:
    if WALLET_PATH.exists():
        try:
            return json.loads(WALLET_PATH.read_text())
        except Exception:
            return {}
    return {}

def save_wallets(wallets: dict) -> None:
    WALLET_PATH.write_text(json.dumps(wallets, indent=2))

def get_user_wallet(wallets: dict, user: str) -> dict:
    w = wallets.setdefault(
        user,
        {
            "coins": 12,
            "reputation": 0,
            "last_award_date": None,
        },
    )

    # ---- MIGRATION SUPPORT ----
    # convert old helper_score -> reputation
    if "reputation" not in w:
        w["reputation"] = int(w.get("helper_score", 0))

    # ensure coins exists
    if "coins" not in w:
        w["coins"] = 12

    if "last_award_date" not in w:
        w["last_award_date"] = None

    return w



def coins_for_streak(streak_len: int) -> int:
    # 1 day -> 1 coin, 3+ -> 2 coins, 5+ -> 3 coins
    if streak_len >= 5:
        return 3
    if streak_len >= 3:
        return 2
    return 1

def streak_ending_today(checkins: list) -> int:
    """
    Compute streak length ending today based on checkins that contain a 'date' field 'YYYY-MM-DD'
    OR contain a 'timestamp' field (fallback).
    """
    # Prefer explicit 'date' keys if your daily.py uses them
    dates = set()
    for c in checkins or []:
        if isinstance(c, dict):
            if "date" in c and c["date"]:
                dates.add(c["date"])
            elif "timestamp" in c and c["timestamp"]:
                # fallback: convert timestamp -> date string
                from datetime import datetime
                d = datetime.fromtimestamp(c["timestamp"]).date().isoformat()
                dates.add(d)

    if not dates:
        return 0

    today = date.today()
    streak = 0
    cur = today
    while cur.isoformat() in dates:
        streak += 1
        cur = cur - timedelta(days=1)
    return streak

def maybe_award_daily_coins(wallets: dict, user: str, checkins: list) -> int:
    """
    Award coins once per day per user. Returns coins awarded (0 if none).
    Uses streak length after today's check-in exists.
    """
    w = get_user_wallet(wallets, user)
    today_str = date.today().isoformat()

    # prevent double-award in the same day
    if w.get("last_award_date") == today_str:
        return 0

    streak_len = streak_ending_today(checkins)
    if streak_len <= 0:
        return 0

    earned = coins_for_streak(streak_len)
    w["coins"] = int(w.get("coins", 0)) + earned
    w["last_award_date"] = today_str
    return earned

def can_spend(wallets: dict, user: str, cost: int) -> bool:
    w = get_user_wallet(wallets, user)
    return int(w.get("coins", 0)) >= cost

def spend(wallets: dict, user: str, cost: int) -> bool:
    w = get_user_wallet(wallets, user)
    coins = int(w.get("coins", 0))
    if coins < cost:
        return False
    w["coins"] = coins - cost
    return True

def add_reputation(wallets: dict, user: str, points: int) -> None:
    w = get_user_wallet(wallets, user)
    w["reputation"] = int(w.get("reputation", 0)) + int(points)
