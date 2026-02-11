import time
import random
import streamlit as st
from pathlib import Path
from mood_logic import (
    recsupport,
    support_options,
    guided_next_page,
    guided_prompt,
    word_to_mode,
)
from daily import (
    load_checkins,
    save_checkins,
    upsert_today_checkin,
    renderstreak_card,
)
from dashboard import render_dashboard
from wallet import (
    load_wallets, save_wallets, get_user_wallet,
    maybe_award_daily_coins, can_spend, spend, add_reputation
)
from game import render_connect4_page


# ==============================
# SHARED STATE (ALL USERS ON THIS SERVER)
# ==============================
@st.cache_resource
def shared_state():
    return {
        "chat": [],
        "study": [],
        "bulletins": [],
        "replies": {},

        # NEW: connect four
        "lobby": [],
        "matches": [],
        "match_of": {},
        "games": {},
    }

SHARED = shared_state()

CHECKINS_PATH = Path("checkins.json")




# ==============================
# PRIVATE SESSION (PER USER)
# ==============================
if "wallets" not in st.session_state:
    st.session_state.wallets = load_wallets()

if "pending_nav" not in st.session_state:
    st.session_state.pending_nav = None

if "guided_banner" not in st.session_state:
    st.session_state.guided_banner = ""

if "name" not in st.session_state:
    ADJ = ["Soft", "Calm", "Warm", "Gentle", "Quiet", "Happy", "Funny"]
    NOUN = ["Cloud", "River", "Fox", "Lantern", "Pine", "Forest", "Ocean", "Sheep"]
    st.session_state.name = random.choice(ADJ) + random.choice(NOUN)

if "moods" not in st.session_state:
    st.session_state.moods = []  # stores backend 4-category moods

if "checkins" not in st.session_state:
    st.session_state.checkins = load_checkins()


if "reflections" not in st.session_state:
    st.session_state.reflections = []

if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

# mood-meter UI selection state
if "selected_word" not in st.session_state:
    st.session_state.selected_word = None

if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = None

# (optional) keep raw mood words for analytics later
if "mood_words" not in st.session_state:
    st.session_state.mood_words = []

# save mood flow state
if "last_mood" not in st.session_state:
    st.session_state.last_mood = None
if "support_mode" not in st.session_state:
    st.session_state.support_mode = None

# ==============================
# UI CONFIG
# ==============================
st.set_page_config(page_title="QuietBridge", layout="centered")

# Global theme: pastel blue bg + centered headings/text + softened sidebar/buttons
st.markdown(
    """
<style>
/* Pastel blue background for the whole app */
.stApp {
    background: #EAF4FF;   /* pastel blue */
}

/* Make content feel less stretched on big screens */
.block-container {
    max-width: 720px;
    padding-top: 2rem;
}

/* Center the main page title ("QuietBridge") */
h1 {
    text-align: center;
    margin-bottom: 0.25rem;
}

/* Center common headings */
h2, h3 {
    text-align: center;
}

/* Center captions + normal text blocks you write with st.caption/st.write */
[data-testid="stCaptionContainer"],
[data-testid="stMarkdownContainer"] p {
    text-align: center;
}

/* Sidebar: slightly translucent to feel softer */
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(8px);
}

/* Buttons: rounded, soft */
div.stButton > button {
    border-radius: 14px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("QuietBridge")
def display_name(user: str) -> str:
    w = get_user_wallet(st.session_state.wallets, user)

    rep = int(w.get("reputation", 0))
    trophies = int(w.get("trophies", 0))

    return f"{user} (Rep {rep} · 🏆 {trophies})"




st.caption(f"You are: **{st.session_state.name}**")

PAGES = [
    "🏠 Home",
    "📋 Dashboard",
    "💬 Chatroom",
    "📌 Community Query",
    "🎮 Connect Four",
    "🫧 Reflection",
]



# 1) Ensure nav exists (so radio can store selection)
if "nav" not in st.session_state:
    st.session_state.nav = "Home"

# 2) If guided match asked to jump, set nav BEFORE the widget is created
if st.session_state.pending_nav in PAGES:
    st.session_state.nav = st.session_state.pending_nav
    st.session_state.pending_nav = None

# 3) Keyed widget remembers selection across reruns
page = st.sidebar.radio("Navigate", PAGES, key="nav")
w = get_user_wallet(st.session_state.wallets, st.session_state.name)
w = get_user_wallet(st.session_state.wallets, st.session_state.name)
st.sidebar.markdown("---")
st.sidebar.write(f"🪙 Coins: **{w['coins']}**")
today_iso = time.strftime("%Y-%m-%d")
checked_today = any(c.get("date") == today_iso for c in st.session_state.checkins)
st.sidebar.caption("🔥 1-day streak → +1 coin")
st.sidebar.caption("🔥🔥 3-day streak → +2 coins")
st.sidebar.caption("🔥🔥🔥 5-day streak → +3 coins")

if checked_today:
    st.sidebar.caption("✅ You’ve checked in today — come back tomorrow to extend your streak.")
else:
    st.sidebar.caption("👉 Save a mood check-in today to start or continue your streak.")

st.sidebar.write(f"⭐ Reputation: **{w.get('reputation', 0)}**")
st.sidebar.write(f"🏆 Trophies: **{w.get('trophies', 0)}**")




# clear pending nav after it's applied
st.session_state.pending_nav = None

# ==============================
# HOME
# ==============================
if page == "🏠 Home":

    st.subheader("How are you feeling right now?")
    st.caption("Tap a word. First instinct is fine.")



    def pick_word(word: str):
        st.session_state.selected_word = word
        st.session_state.selected_mode = word_to_mode(word)

    mood_grid = [
        ["Excited", "Joyful", "Motivated", "Inspired"],
        ["Tense",   "Alert",  "Engaged",   "Proud"],
        ["Sad",     "Calm",   "Content",   "Peaceful"],
        ["Drained", "Tired",  "Restful",   "Serene"],
    ]

    st.markdown("#### Mood meter")

    # axis hints to preserve the "meter" vibe
    top = st.columns([1, 8, 1])
    with top[1]:
        st.caption("⬆️ Higher energy")

    mid = st.columns([1, 8, 1])

    with mid[0]:
        st.markdown(
            """
            <div style="height: 100%; display:flex; align-items:center; justify-content:center;">
                <span style="writing-mode: vertical-rl; transform: rotate(180deg); opacity:0.75;">
                    Unpleasant ⟵ Pleasant
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Option 1: Streamlit-native buttons + strong selection indicator
    with mid[1]:
        # 4x4 mood grid using Streamlit buttons (same look/feel as before)
        for row in mood_grid:
            cols = st.columns(4, gap="small")
            for i, word in enumerate(row):
                selected = (st.session_state.selected_word == word)
                label = f"✅ {word}" if selected else word
                cols[i].button(
                    label,
                    key=f"mood_{word}",
                    use_container_width=True,
                    on_click=pick_word,
                    args=(word,),
                )

        # Selected indicator + clear (keeps your features)
        cA, cB = st.columns([3, 1])
        with cA:
            if st.session_state.selected_word:
                st.success(f"Selected: **{st.session_state.selected_word}**")
            else:
                st.info("Select a word above.")
        with cB:
            if st.button("Clear", use_container_width=True):
                st.session_state.selected_word = None
                st.session_state.selected_mode = None
                st.rerun()



    with mid[2]:
        st.markdown(
            """
            <div style="height: 100%; display:flex; align-items:center; justify-content:center;">
                <span style="writing-mode: vertical-rl; opacity:0.75;">
                    Pleasant ⟶ Unpleasant
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    bottom = st.columns([1, 8, 1])
    with bottom[1]:
        st.caption("⬇️ Lower energy")

    st.divider()


    if st.button("Save mood", use_container_width=True):
        if not st.session_state.selected_mode:
            st.warning("Pick a mood word first.")
        else:
            # !!!!!!!!
            # keep your existing behavior
            st.session_state.moods.append({
    "mood": st.session_state.selected_mode,  # backend category
    "timestamp": time.time()
})

            st.session_state.last_mood = st.session_state.selected_mode
            st.session_state.mood_words.append(st.session_state.selected_word)

            # NEW: streak check-in record (one per day, persisted)
            st.session_state.checkins = upsert_today_checkin(
                st.session_state.checkins,
                word=st.session_state.selected_word,
                mode=st.session_state.selected_mode,
            )
            save_checkins(st.session_state.checkins)
            st.toast("Check-in saved. Proud of you.", icon="✅")
            st.session_state.checkins = upsert_today_checkin(
                st.session_state.checkins,
                word=st.session_state.selected_word,
                mode=st.session_state.selected_mode,
            )
            save_checkins(st.session_state.checkins)

            earned = maybe_award_daily_coins(
                st.session_state.wallets,
                st.session_state.name,
                st.session_state.checkins,
            )
            save_wallets(st.session_state.wallets)

            if earned > 0:
                st.toast(f"+{earned} coin(s) earned from your streak.", icon="🪙")

            
            st.success("Saved.")
            
 



    # ---- Guided Match ----
    # ---- Guided Support Hub ----
    if st.session_state.last_mood is not None:
        st.divider()
        st.subheader("What support do you want right now?")
        st.caption("There’s no wrong choice — pick what feels most helpful in this moment.")

        # Pull streak context
        today_iso = time.strftime("%Y-%m-%d")
        checked_today = any(
            c.get("date") == today_iso for c in st.session_state.checkins
        )

        if checked_today:
            st.success("You’ve already checked in today — nice consistency 🥹")
        else:
            st.info("A check-in today can help keep your streak alive.")

        # Recommender logic
        rec = recsupport(st.session_state.last_mood)
        opts = support_options()

        cols = st.columns(2)
        clicked = None

        for i, (key, title, desc) in enumerate(opts):
            with cols[i % 2]:

                # Soft highlight recommended option
                label = f"⭐ {title}" if key == rec else title

                if st.button(label, use_container_width=True):
                    clicked = key

                st.caption(desc)

        if clicked:
            st.session_state.support_mode = clicked
            st.session_state.guided_banner = guided_prompt(
                clicked,
                st.session_state.last_mood,
            )

            st.session_state.pending_nav = guided_next_page(clicked)
            st.rerun()

        # ------------------
        # Streak card
        # ------------------
        renderstreak_card(st.session_state.checkins)

        # ------------------
        # Streak settings
        # ------------------
        with st.expander("⚙️ Streak settings"):
            if st.button("Reset streak data (demo)", type="secondary"):
                st.session_state.checkins = []
                save_checkins([])
                st.success("Streak data cleared.")
                st.rerun()

    # !!!!!!!!


# ==============================
# QUIET CHAT
# ==============================
elif page == "💬 Chatroom":

    st.subheader("A gentle shared space to talk")

    if st.session_state.get("guided_banner"):
        st.info(st.session_state.guided_banner)

    st.caption("Short, low-pressure messages.")

    for m in SHARED["chat"][-20:]:
        st.write(f"**{display_name(m['u'])}**: {m['t']}")


    msg = st.text_input("Message", placeholder="Type something gentle")

    if st.button("Send"):
        if msg.strip():
            SHARED["chat"].append({
                "u": st.session_state.name,
                "t": msg.strip(),
                "time": time.time()
            })
            st.session_state.chat_count += 1
            st.rerun()
        else:
            st.warning("Type something first.")

# ==============================
# SILENT CO-STUDY
# ==============================
elif page == "🎮 Connect Four":

    render_connect4_page(SHARED, st.session_state.name, display_name)

# ==============================
# REFLECTION
# ==============================
elif page == "🫧 Reflection":
    st.subheader("Prompt of the day")
    st.write("What is one small thing you survived today?")

    text = st.text_area(
        "Reflection",
        height=150,
        label_visibility="collapsed"
    )

    if st.button("Save reflection"):
        if text.strip():
            st.session_state.reflections.append(text.strip())
            st.success("Saved.")
        else:
            st.warning("Write something first.")

    if st.session_state.reflections:
        st.divider()
        st.write("Recent reflections:")
        for r in reversed(st.session_state.reflections[-3:]):
            st.write(f"- {r}")

# ==============================
# BULLETIN BOARD
# ==============================
elif page == "📌 Community Query":

    st.subheader("Community Query")
    st.caption("Post a worry or question. Others can reply anonymously with gentle advice.")

    st.markdown(
        """
        <div style="text-align:center; opacity:0.85; font-size: 0.95rem;">
            <b>Costs & rewards</b><br>
            Posting a question: <b>10 coins</b> · Replying: <b>2 coins</b> · Each reply earns <b>+1 reputation</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------
    # POSTING (COSTS COINS)
    # --------------------------
    with st.expander("✍️ Post something (anonymous to others)", expanded=True):
        title = st.text_input("Title", placeholder="e.g., Feeling behind in school")
        body = st.text_area(
            "What’s going on?",
            placeholder="Share as much as you want.",
            height=120,
        )

        col1, col2 = st.columns([1, 2])
        with col1:
            post_anon = st.checkbox("Post anonymously", value=True)
        with col2:
            st.caption("If anonymous: your username won’t be shown on the board.")

        POST_COST = 10

        if st.button("Post to board", use_container_width=True):
            if not title.strip() or not body.strip():
                st.warning("Please fill in both title and details.")

            elif not can_spend(
                st.session_state.wallets,
                st.session_state.name,
                POST_COST,
            ):
                w = get_user_wallet(
                    st.session_state.wallets,
                    st.session_state.name,
                )
                st.error(
                    f"Not enough coins. Posting costs {POST_COST}, you have {w['coins']}."
                )

            else:
                spend(
                    st.session_state.wallets,
                    st.session_state.name,
                    POST_COST,
                )
                save_wallets(st.session_state.wallets)

                post_id = f"p_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

                SHARED["bulletins"].append(
                    {
                        "id": post_id,
                        "title": title.strip(),
                        "body": body.strip(),
                        "author": None if post_anon else st.session_state.name,
                        "time": time.time(),
                    }
                )

                SHARED["replies"].setdefault(post_id, [])

                st.success("Posted.")
                st.rerun()

    st.divider()

    # --------------------------
    # VIEW POSTS + REPLIES
    # --------------------------
    posts = list(reversed(SHARED["bulletins"]))  # newest first
    if not posts:
        st.info("No posts yet. Be the first to start the board.")
    else:
        q = st.text_input("Search posts", placeholder="Type keywords…")
        if q.strip():
            ql = q.strip().lower()
            posts = [
                p
                for p in posts
                if ql in p["title"].lower() or ql in p["body"].lower()
            ]

        for p in posts[:30]:
                author_label = "Anonymous" if p["author"] is None else display_name(p["author"])
                st.caption(f"Posted by **{author_label}**")

                st.write(p["body"])

                replies = SHARED["replies"].get(p["id"], [])

# sort by reputation (descending)
                replies = sorted(
                    replies,
                    key=lambda r: get_user_wallet(
                        st.session_state.wallets,
                        r.get("author"),
                    ).get("reputation", 0)
                    if r.get("author")
                    else 0,
                    reverse=True,
                )          

                if replies:
                    st.write("**Replies:**")
                    for r in replies[-10:]:
                        reply_author = r.get("author")
                        tag = display_name(reply_author) if reply_author else "Anonymous"
                        st.write(f"• **{tag}**: {r['text']}")

                else:
                    st.caption("No replies yet.")

                with st.form(
                    key=f"reply_form_{p['id']}",
                    clear_on_submit=True,
                ):
                    reply_text = st.text_area(
                        "Reply (anonymous)",
                        key=f"reply_{p['id']}",
                        placeholder="Write something helpful and kind…",
                        height=90,
                    )
                    submitted = st.form_submit_button("Send reply")

                # --------------------------
                # REPLY COST + HELPER SCORE
                # --------------------------
                REPLY_COST = 2
                REPUTATION_PER_REPLY = 1


                if submitted:
                    if not reply_text.strip():
                        st.warning("Write a reply first.")

                    elif not can_spend(
                        st.session_state.wallets,
                        st.session_state.name,
                        REPLY_COST,
                    ):
                        w = get_user_wallet(
                            st.session_state.wallets,
                            st.session_state.name,
                        )
                        st.error(
                            f"Not enough coins. Replying costs {REPLY_COST}, you have {w['coins']}."
                        )

                    else:
                        spend(
                            st.session_state.wallets,
                            st.session_state.name,
                            REPLY_COST,
                        )

                        add_reputation(
                            st.session_state.wallets,
                            st.session_state.name,
                            REPUTATION_PER_REPLY,
                        )

                        

                        save_wallets(st.session_state.wallets)

                        rep_id = f"r_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

                        SHARED["replies"].setdefault(p["id"], []).append(
                            {
                                "id": rep_id,
                                "text": reply_text.strip(),
                                "author": st.session_state.name,
                                "time": time.time(),
                            }
                        )

                        st.toast(
                            f"Reply sent. +{REPUTATION_PER_REPLY} reputation.",

                            icon="🫶",
                        )

                        st.rerun()

                st.divider()


# ==============================
# DASHBOARD
# ==============================
elif page == "📋 Dashboard":

    render_dashboard(st.session_state.moods, st.session_state.chat_count, st.session_state.checkins)

