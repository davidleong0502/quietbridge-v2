
import json
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
import altair as alt
import streamlit as st

from mood_logic import mood_to_num
# !!!!!!!!
# ==============================
# DAILY CHECK-IN STREAK (ADVANCED)
# ==============================

CHECKINS_PATH = Path("checkins.json")

def load_checkins() -> list[dict]:
    if not CHECKINS_PATH.exists():
        return []
    try:
        return json.loads(CHECKINS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_checkins(checkins: list[dict]) -> None:
    CHECKINS_PATH.write_text(json.dumps(checkins, ensure_ascii=False, indent=2), encoding="utf-8")

def upsert_today_checkin(checkins: list[dict], word: str, mode: str) -> list[dict]:
    """
    One check-in per day: saving again overwrites today's entry.
    Stores both the selected Mood Meter word and the backend mode.
    """
    today = date.today().isoformat()
    level = mood_to_num(mode)
    rec = {"date": today, "word": word, "mode": mode, "level": level}

    out = [c for c in checkins if c.get("date") != today]
    out.append(rec)
    out.sort(key=lambda x: x.get("date", ""))
    return out

def unique_dates(checkins: list[dict]) -> set[date]:
    out = set()
    for c in checkins:
        d = c.get("date")
        if d:
            out.add(date.fromisoformat(d))
    return out

def compute_streaks(checkins: list[dict], grace_days: int = 0) -> dict:
    """
    grace_days=0 strict streak
    grace_days=1 gentle streak: allows 1 missed day while counting
    """
    days = unique_dates(checkins)
    if not days:
        return {"current": 0, "best": 0}

    # current streak (strictly from today backwards; gentle allows misses)
    cur = 0
    misses = 0
    cursor = date.today()
    while True:
        if cursor in days:
            cur += 1
        else:
            misses += 1
            if misses > grace_days:
                break
        cursor -= timedelta(days=1)

    # best streak (scan day-by-day across history)
    sorted_days = sorted(days)
    best = 0
    for start in sorted_days:
        streak = 0
        misses = 0
        cursor = start
        while True:
            if cursor in days:
                streak += 1
            else:
                misses += 1
                if misses > grace_days:
                    break
            cursor += timedelta(days=1)
        best = max(best, streak)

    return {"current": cur, "best": best}

def week_progress(checkins: list[dict], goal: int = 5) -> tuple[int, int]:
    today = date.today()
    y, w, _ = today.isocalendar()
    days = unique_dates(checkins)
    cnt = sum(1 for d in days if d.isocalendar()[:2] == (y, w))
    return cnt, goal

def mood_stats_7d(checkins: list[dict]) -> dict:
    if not checkins:
        return {"avg_level": None, "top_word": None}

    today = date.today()
    cutoff = today - timedelta(days=6)

    last7 = [c for c in checkins if c.get("date") and date.fromisoformat(c["date"]) >= cutoff]
    if not last7:
        return {"avg_level": None, "top_word": None}

    avg = sum(int(c.get("level", 3)) for c in last7) / len(last7)

    freq = {}
    for c in last7:
        w = c.get("word")
        if w:
            freq[w] = freq.get(w, 0) + 1
    top_word = max(freq, key=freq.get) if freq else None

    return {"avg_level": avg, "top_word": top_word}

def calendar_heatmap(checkins: list[dict], weeks: int = 16):
    """
    GitHub-style heatmap for the last N weeks.
    level: 0 (no check-in) to 4
    """
    if not checkins:
        st.info("No check-ins yet.")
        return

    # latest level per day
    day_level = {}
    for c in checkins:
        if c.get("date"):
            day_level[date.fromisoformat(c["date"])] = int(c.get("level", 3))

    end = date.today()
    start = end - timedelta(days=weeks * 7 - 1)

    rows = []
    d = start
    while d <= end:
        lvl = day_level.get(d, 0)
        week_idx = (d - start).days // 7
        dow = d.weekday()  # Mon=0..Sun=6
        rows.append({"date": d.isoformat(), "week": week_idx, "dow": dow, "level": lvl})
        d += timedelta(days=1)

    df = pd.DataFrame(rows)

    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X("week:O", title=None, axis=alt.Axis(labels=False, ticks=False)),
            y=alt.Y(
    "dow:O",
    title=None,
    sort=[0, 1, 2, 3, 4, 5, 6],
    axis=alt.Axis(
        values=[0, 1, 2, 3, 4, 5, 6],  # force all days to show
        labelExpr="['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][datum.value]",
        ticks=True,
        labelPadding=6,
    ),
),
            color=alt.Color("level:Q", scale=alt.Scale(domain=[0, 1, 2, 3, 4]), legend=None),
            tooltip=["date:N", "level:Q"],
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)

def renderstreak_card(checkins: list[dict]):

    # ==============================
    # STREAK CARD CSS (REQUIRED)
    # ==============================
    st.markdown("""
    <style>
    .qb-card{
      background: rgba(255,255,255,0.92);
      border-radius: 18px;
      padding: 18px 18px 14px 18px;
      box-shadow: 0 8px 24px rgba(15, 30, 60, 0.10);
      border: 1px solid rgba(10,30,60,0.08);
      margin: 14px 0 18px 0;
    }
    .qb-title{
      font-size: 1.05rem;
      font-weight: 700;
      margin-bottom: 10px;
      display:flex;
      align-items:center;
      gap:8px;
    }
    .qb-row{
      display:flex;
      flex-wrap:wrap;
      gap:10px;
      justify-content:space-between;
    }
    .qb-pill{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(234,244,255,0.9);
      border: 1px solid rgba(10,30,60,0.08);
      font-size: 0.9rem;
      white-space: nowrap;
    }
    .qb-pill .dot{
      width:10px;height:10px;border-radius:50%;
      display:inline-block;
    }

    .qb-badge{
      flex: 1 1 140px;
      min-width: 140px;
      background: rgba(255,255,255,0.95);
      border: 1px solid rgba(10,30,60,0.08);
      border-radius: 14px;
      padding: 12px;
    }
    .qb-badge .big{
      font-size: 1.1rem;
      font-weight: 800;
    }
    .qb-badge .label{
      font-size: 0.82rem;
      opacity: 0.75;
      margin-top: 2px;
    }

    .qb-progress-wrap{
      margin-top: 12px;
      background: rgba(234,244,255,0.7);
      border: 1px solid rgba(10,30,60,0.08);
      border-radius: 14px;
      padding: 12px;
    }
    .qb-mini{ font-size: 0.85rem; opacity: 0.85; }

    .qb-progress-bar{
      height: 10px;
      border-radius: 999px;
      background: rgba(10,30,60,0.12);
      overflow:hidden;
      margin: 8px 0;
    }
    .qb-progress-fill{
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg,#6aa9ff,#8fc5ff);
    }

    /* pulse highlight */
    .qb-pulse{
      position: relative;
    }
    .qb-pulse:after{
      content:"";
      position:absolute;
      inset:-2px;
      border-radius: 16px;
      border: 2px solid rgba(0,180,120,0.35);
      animation: qbPulse 1.6s ease-out infinite;
      pointer-events:none;
    }
    @keyframes qbPulse{
      0%{ transform: scale(0.97); opacity: 0.9; }
      100%{ transform: scale(1.05); opacity: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

    # ==============================
    # LOGIC
    # ==============================
    gentle = st.toggle("Gentle streak mode (1-day grace)", value=True)
    grace = 1 if gentle else 0

    streaks = compute_streaks(checkins, grace_days=grace)
    wk, goal = week_progress(checkins, goal=5)
    stats = mood_stats_7d(checkins)

    today_iso = date.today().isoformat()
    checked_today = any(c.get("date") == today_iso for c in checkins)

    if "last_seen_checkin_date" not in st.session_state:
        st.session_state.last_seen_checkin_date = None

    if checked_today and st.session_state.last_seen_checkin_date != today_iso:
        st.balloons()
        st.session_state.last_seen_checkin_date = today_iso

    pct = 0 if goal <= 0 else min(100, int((wk / goal) * 100))

    avg = "-" if stats["avg_level"] is None else f"{stats['avg_level']:.2f}"
    top_word = stats["top_word"]

    if streaks["current"] >= 7:
        vibe = "You’re on fire this week"
    elif streaks["current"] >= 3:
        vibe = "Nice momentum"
    elif streaks["current"] >= 1:
        vibe = "Great start"
    else:
        vibe = "Start a gentle streak today"

    status_text = "Checked in today" if checked_today else "Not checked in yet"
    status_dot = "rgba(0,180,120,0.85)" if checked_today else "rgba(255,140,0,0.85)"
    pulse_class = "qb-badge qb-pulse" if checked_today else "qb-badge"

    # ==============================
    # RENDER CARD
    # ==============================
    st.markdown(
        f"""
        <div class="qb-card">
          <div class="qb-title">🔥 Daily check-in streak</div>

          <div class="qb-row" style="margin-bottom:10px;">
            <span class="qb-pill">
              <span class="dot" style="background:{status_dot};"></span>
              <b>{status_text}</b>
            </span>
            <span class="qb-pill">💬 {vibe}</span>
            {"<span class='qb-pill'>🌟 Most common (7d): <b>"+top_word+"</b></span>" if top_word else ""}
          </div>

          <div class="qb-row">
            <div class="{pulse_class}">
              <div class="big">🔥 {streaks["current"]}</div>
              <div class="label">Current streak</div>
            </div>
            <div class="qb-badge">
              <div class="big">🏆 {streaks["best"]}</div>
              <div class="label">Best streak</div>
            </div>
            <div class="qb-badge">
              <div class="big">📈 {avg}</div>
              <div class="label">Avg level (7 days)</div>
            </div>
            <div class="qb-badge">
              <div class="big">📅 {wk}/{goal}</div>
              <div class="label">Weekly goal</div>
            </div>
          </div>

          <div class="qb-progress-wrap">
            <div style="display:flex; justify-content:space-between;">
              <div class="qb-mini"><b>Weekly progress</b> — aim for {goal} check-ins</div>
              <div class="qb-mini"><b>{pct}%</b></div>
            </div>
            <div class="qb-progress-bar">
              <div class="qb-progress-fill" style="width:{pct}%;"></div>
            </div>
            <div class="qb-mini">Tip: gentle consistency beats perfection</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_query_mood() -> str | None:
    # Works across Streamlit versions
    try:
        qp = st.query_params  # new API
        return qp.get("mood", None)
    except Exception:
        qp = st.experimental_get_query_params()
        v = qp.get("mood", [None])
        return v[0] if v else None

def set_query_mood(word: str | None):
    try:
        if word is None:
            st.query_params.clear()
        else:
            st.query_params["mood"] = word
    except Exception:
        if word is None:
            st.experimental_set_query_params()
        else:
            st.experimental_set_query_params(mood=word)

def render_mood_tiles(mood_grid: list[list[str]], selected_word: str | None):
    # Colors tuned to match your 4x4 mood meter vibe
    COLORS = {
        # Row 1 (high energy, pleasant-ish): warm
        "Excited":   ("#9F3B39", "#FFFFFF"),
        "Joyful":    ("#B76545", "#FFFFFF"),
        "Motivated": ("#D3A24A", "#1D1D1D"),
        "Inspired":  ("#E7CF5D", "#1D1D1D"),

        # Row 2 (high energy, mixed): muted warm/olive
        "Tense":     ("#7C4B5B", "#FFFFFF"),
        "Alert":     ("#8D6A5B", "#FFFFFF"),
        "Engaged":   ("#A79A56", "#1D1D1D"),
        "Proud":     ("#C7BE58", "#1D1D1D"),

        # Row 3 (low energy-ish, neutral pleasant): gray/green
        "Sad":       ("#6C6A88", "#FFFFFF"),
        "Calm":      ("#7B7E78", "#FFFFFF"),
        "Content":   ("#8F9966", "#1D1D1D"),
        "Peaceful":  ("#A6B26A", "#1D1D1D"),

        # Row 4 (low energy): blue/green
        "Drained":   ("#4E89B0", "#FFFFFF"),
        "Tired":     ("#5E97A2", "#FFFFFF"),
        "Restful":   ("#6E9F86", "#FFFFFF"),
        "Serene":    ("#86A96B", "#1D1D1D"),
    }

    # axis hints (optional but nice)
    st.markdown(
        """
        <div class="qb-axes">
          <div class="qb-axes-row"><span>⬆️ Higher energy</span><span>PLEASANT →</span></div>
          <div class="qb-axes-mid">
            <span class="v">UNPLEASANT ← PLEASANT</span>
            <span class="spacer"></span>
            <span class="v2">PLEASANT → UNPLEASANT</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # tiles grid
    html = ['<div class="qb-mood-grid">']
    for row in mood_grid:
        for word in row:
            bg, fg = COLORS.get(word, ("#FFFFFF", "#111111"))
            cls = "qb-tile selected" if word == selected_word else "qb-tile"
            # clicking sets query param -> rerun -> python picks it up
            html.append(
                f'<a class="{cls}" href="?mood={word}" style="background:{bg}; color:{fg};">{word}</a>'
            )
    html.append("</div>")
    st.markdown("\n".join(html), unsafe_allow_html=True)
