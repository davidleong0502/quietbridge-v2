import datetime
import streamlit as st
import pandas as pd

from mood_logic import mood_to_num
from daily import calendar_heatmap


def _normalize_moods(moods: list):
    """
    Supports both:
      - list[str] like ["Good", "Okay", ...]
      - list[dict] like [{"mood":"Good","timestamp":...}, ...]
    Returns list[dict] with keys mood + timestamp (timestamp may be None).
    """
    out = []
    for entry in moods or []:
        if isinstance(entry, dict):
            m = entry.get("mood")
            ts = entry.get("timestamp")
            if m is not None:
                out.append({"mood": m, "timestamp": ts})
        elif isinstance(entry, str):
            out.append({"mood": entry, "timestamp": None})
    return out


def render_dashboard(moods: list, chat_count: int, checkins: list[dict]):
    st.subheader("Here is your wellbeing overview!")

    # --- REPLACEMENT: heatmap instead of timeline graph ---
    st.write("### Your Check-in Map")
    st.caption("A simple view of your consistency over time (darker = higher mood level).")
    calendar_heatmap(checkins, weeks=16)

    st.divider()

    # --- Keep your existing dashboard features ---
    entries = _normalize_moods(moods)
    mood_strings = [e["mood"] for e in entries if e.get("mood") is not None]

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Summary of your Moods")
        if mood_strings:
            mood_counts = pd.Series(mood_strings).value_counts()
            st.write("**Your most frequent moods:**")
            for mood, count in mood_counts.head(3).items():
                times_word = "time" if count == 1 else "times"
                st.write(f"- {mood}: {count} {times_word}")

            avg_mood_score = sum(mood_to_num(m) for m in mood_strings) / len(mood_strings)
            st.write(f"**Average mood score:** {avg_mood_score:.2f} (1=lowest, 4=highest)")
        else:
            avg_mood_score = None
            st.info("No mood history yet — log a few check-ins on the Home page.")

    with col2:
        st.write("### An Insight for You")
        if not mood_strings:
            st.info("Log a few moods first, then I can generate a trend insight.")
        elif avg_mood_score > 3:
            st.success("It looks like you've been experiencing predominantly positive moods lately! Keep it up 💛")
        elif avg_mood_score > 2:
            st.info("Your moods are generally balanced. Remember to take moments for self-care.")
        else:
            st.warning("It seems you've been facing some challenges. Consider reaching out or trying a reflection.")

    st.divider()

    st.write("### Mood Log")
    st.caption("All moods you've recorded, with timestamps (newest first).")

    # show mood log (with timestamps when available)
    for e in reversed(entries):
        m = e.get("mood")
        ts = e.get("timestamp")
        if m is None:
            continue
        if ts is not None:
            t = datetime.datetime.fromtimestamp(ts).strftime("%B %d, %Y at %I:%M %p")
            st.write(f"**{m}** — {t}")
        else:
            st.write(f"**{m}**")

    st.divider()

    if chat_count >= 2:
        st.write("You tend to reach out when you check in.")
    elif len(entries) >= 3:
        st.write("You have been checking in consistently. Keep up the good work!")
    elif len(entries) > 0:
        st.write("You have started tracking your mood.")
    else:
        st.write("Start with one check-in. That is enough for today.")
