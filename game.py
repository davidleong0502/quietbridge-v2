import time
import random
import streamlit as st

from wallet import get_user_wallet, save_wallets

ROWS, COLS = 6, 7
AFK_SECONDS = 60
AUTO_RERUN_EVERY = 2  # seconds

EMPTY, P1, P2 = 0, 1, 2

# Visuals
TOK = {EMPTY: "⚪", P1: "🔴", P2: "🟡"}

def _ensure_game_keys(SHARED: dict):
    SHARED.setdefault("lobby", [])
    SHARED.setdefault("matches", [])        # {id,a,b,time}
    SHARED.setdefault("match_of", {})       # user -> match_id
    SHARED.setdefault("games", {})          # match_id -> game_state

def _new_match_id() -> str:
    return f"m_{int(time.time()*1000)}_{random.randint(1000,9999)}"

def _get_match(SHARED: dict, match_id: str):
    for m in reversed(SHARED["matches"]):
        if m["id"] == match_id:
            return m
    return None

def _other(match: dict, me: str) -> str:
    return match["b"] if match["a"] == me else match["a"]

def _in_lobby(SHARED: dict, user: str) -> bool:
    return user in SHARED["lobby"]

def _join_lobby(SHARED: dict, user: str):
    if user not in SHARED["lobby"]:
        SHARED["lobby"].append(user)

def _leave_lobby(SHARED: dict, user: str):
    if user in SHARED["lobby"]:
        SHARED["lobby"].remove(user)
    SHARED["match_of"].pop(user, None)

def _init_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def _make_match(SHARED: dict, a: str, b: str) -> str:
    match_id = _new_match_id()
    SHARED["matches"].append({"id": match_id, "a": a, "b": b, "time": time.time()})
    SHARED["match_of"][a] = match_id
    SHARED["match_of"][b] = match_id

    # Connect 4 game state
    SHARED["games"][match_id] = {
        "board": _init_board(),
        "turn": a,            # a starts
        "winner": None,       # username or "draw"
        "scored": False,      # prevent double-awards
        "moves": 0,
        "created": time.time()
    }
    return match_id

def _try_matchmake(SHARED: dict):
    free = [u for u in SHARED["lobby"] if u not in SHARED["match_of"]]
    random.shuffle(free)
    while len(free) >= 2:
        a = free.pop()
        b = free.pop()
        _make_match(SHARED, a, b)

def _cleanup_stale(SHARED: dict):
    lobby_set = set(SHARED["lobby"])
    stale_users = [u for u in list(SHARED["match_of"].keys()) if u not in lobby_set]
    for u in stale_users:
        SHARED["match_of"].pop(u, None)

def _render_lamps(n: int):
    max_icons = 30
    lit = min(n, max_icons)
    extra = max(0, n - max_icons)
    icons = "💡" * lit + (f" +{extra}" if extra else "")
    st.markdown(
        f"<div style='font-size:34px; line-height:1.6; text-align:center;'>{icons}</div>",
        unsafe_allow_html=True,
    )

def _drop_piece(board, col, token):
    # return (row, col) placed, or None if column full
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = token
            return (r, col)
    return None

def _in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS

def _check_winner(board, last_r, last_c):
    token = board[last_r][last_c]
    if token == EMPTY:
        return False

    directions = [(0,1), (1,0), (1,1), (1,-1)]
    for dr, dc in directions:
        count = 1
        # forward
        r, c = last_r + dr, last_c + dc
        while _in_bounds(r, c) and board[r][c] == token:
            count += 1
            r, c = r + dr, c + dc
        # backward
        r, c = last_r - dr, last_c - dc
        while _in_bounds(r, c) and board[r][c] == token:
            count += 1
            r, c = r - dr, c - dc

        if count >= 4:
            return True
    return False

def _board_full(moves: int):
    return moves >= ROWS * COLS

def _render_board(board):
    # Simple clean board render
    lines = []
    for r in range(ROWS):
        lines.append(" ".join(TOK[board[r][c]] for c in range(COLS)))
    st.markdown(
        "<div style='font-size:28px; line-height:1.35; text-align:center;'>"
        + "<br>".join(lines)
        + "</div>",
        unsafe_allow_html=True,
    )
    st.caption("Columns: 1  2  3  4  5  6  7")

def _award_trophies(wallets, winner: str, loser: str):
    # +10 winner, -4 loser (clamp at 0)
    w_win = get_user_wallet(wallets, winner)
    w_lose = get_user_wallet(wallets, loser)

    w_win["trophies"] = int(w_win.get("trophies", 0)) + 10
    w_lose["trophies"] = max(0, int(w_lose.get("trophies", 0)) - 4)

    save_wallets(wallets)

def _render_score(wallets, a: str, b: str, display_name_fn):
    wa = get_user_wallet(wallets, a)
    wb = get_user_wallet(wallets, b)
    ta = int(wa.get("trophies", 0))
    tb = int(wb.get("trophies", 0))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{display_name_fn(a)}**")
        st.write(f"🏆 Trophies: **{ta}**")
        st.write("🔴 Token")
    with c2:
        st.markdown(f"**{display_name_fn(b)}**")
        st.write(f"🏆 Trophies: **{tb}**")
        st.write("🟡 Token")
        
def _auto_rerun_every(seconds: int):
    """
    Streamlit has no real background timer; this forces periodic reruns
    so AFK can be detected while users are sitting on the page.
    """
    if seconds <= 0:
        return
    st.markdown(
        f"""
        <script>
        setTimeout(function() {{
          window.parent.postMessage({{type: 'streamlit:rerun'}}, '*');
        }}, {seconds * 1000});
        </script>
        """,
        unsafe_allow_html=True,
    )

def render_connect4_page(SHARED: dict, me: str, display_name_fn):
    _ensure_game_keys(SHARED)
    _cleanup_stale(SHARED)

    st.subheader("Connect Four")
    st.caption("Join the lobby to be matched. Winner +10 🏆, loser −4 🏆.")

    # Join/Leave
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if _in_lobby(SHARED, me):
            if st.button("Leave lobby", use_container_width=True):
                _leave_lobby(SHARED, me)
                st.rerun()
        else:
            if st.button("Join lobby", use_container_width=True):
                _join_lobby(SHARED, me)
                st.rerun()

    st.divider()

    # Lobby display
    n = len(SHARED["lobby"])
    st.markdown("### Players online")
    st.markdown(f"## **{n}** in lobby")
    _render_lamps(n)

    if SHARED["lobby"]:
        with st.expander("See who’s in the lobby", expanded=False):
            for u in SHARED["lobby"]:
                st.write(f"• {display_name_fn(u)}")

    st.divider()

    # Matchmake each render
    _try_matchmake(SHARED)

    match_id = SHARED["match_of"].get(me)
    if not match_id:
        if _in_lobby(SHARED, me):
            st.info("Waiting for an opponent…")
            if st.button("Re-roll matchmaking", use_container_width=True):
                SHARED["match_of"].pop(me, None)
                _try_matchmake(SHARED)
                st.rerun()
        else:
            st.caption("Join the lobby to start.")
        return

    match = _get_match(SHARED, match_id)
    if not match:
        st.warning("Match not found (state reset). Rejoin lobby.")
        SHARED["match_of"].pop(me, None)
        return

    a, b = match["a"], match["b"]
    other = _other(match, me)

    st.success(f"Matched! You ↔ **{display_name_fn(other)}**")

    # Need wallets from app session_state
    wallets = st.session_state.get("wallets")
    if wallets is None:
        st.error("Wallets not loaded in session_state. Make sure app.py sets st.session_state.wallets.")
        return

    _render_score(wallets, a, b, display_name_fn)
    st.divider()

    # Game state
    game = SHARED["games"].get(match_id)
    if not game:
        # recreate safely
      SHARED["games"][match_id] = {
          "board": _init_board(),
          "turn": a,
          "winner": None,
          "scored": False,
          "moves": 0,
          "created": time.time(),
          "last_action": time.time(),   # NEW
      }

    game = SHARED["games"][match_id]

    board = game["board"]
        # -------------------------
    # AFK TIMER (turn-based)
    # -------------------------
    now = time.time()

    # periodically rerun for AFK detection while game is active
    if game["winner"] is None:
        _auto_rerun_every(AUTO_RERUN_EVERY)

    if game["winner"] is None:
        elapsed = now - float(game.get("last_action", now))
        turn_user = game["turn"]

        # Forfeit if AFK too long
        if elapsed >= AFK_SECONDS:
            afk_loser = turn_user
            afk_winner = b if afk_loser == a else a
            game["winner"] = afk_winner
            st.toast(
                f"⏳ {display_name_fn(afk_loser)} was AFK. Forfeit!",
                icon="⏳",
            )
            st.rerun()

        # Countdown display
        remaining = max(0, int(AFK_SECONDS - elapsed))
        if game["winner"] is None:
            st.caption(
                f"AFK timer: **{remaining}s** left for "
                f"{display_name_fn(turn_user)} to move."
            )


    # Winner / awards (once)
    if game["winner"] and not game["scored"]:
        if game["winner"] != "draw":
            winner = game["winner"]
            loser = b if winner == a else a
            _award_trophies(wallets, winner, loser)
            game["scored"] = True
            st.toast(f"🏆 {display_name_fn(winner)} wins! +10 trophies", icon="🏆")
            st.toast(f"{display_name_fn(loser)} loses −4 trophies", icon="⚠️")
        else:
            game["scored"] = True

    # Status
    if game["winner"] == "draw":
        st.warning("It’s a draw.")
    elif game["winner"]:
        st.success(f"Winner: **{display_name_fn(game['winner'])}**")
    else:
        turn_user = game["turn"]
        token = "🔴" if turn_user == a else "🟡"
        if turn_user == me:
            st.info(f"Your turn ({token})")
        else:
            st.caption(f"Waiting for **{display_name_fn(turn_user)}** to play ({token})")

    # Render board
    _render_board(board)
    st.divider()

    # Column buttons
    disabled = (game["winner"] is not None) or (game["turn"] != me)

    cols = st.columns(COLS)
    for c in range(COLS):
        with cols[c]:
            if st.button(f"{c+1}", key=f"c4_{match_id}_{c}", use_container_width=True, disabled=disabled):
                # Apply move
                token = P1 if me == a else P2
                placed = _drop_piece(board, c, token)
                if placed is None:
                    st.warning("That column is full. Pick another.")
                    st.rerun()

                game["moves"] += 1
                r, cc = placed
                game["last_action"] = time.time()


                # Win check
                if _check_winner(board, r, cc):
                    game["winner"] = me
                elif _board_full(game["moves"]):
                    game["winner"] = "draw"
                else:
                    # swap turn
                    game["turn"] = other

                st.rerun()

    # Controls after game ends
    if game["winner"] is not None:
        cA, cB = st.columns(2)
        with cA:
            if st.button("Play again (same opponent)", use_container_width=True):
                SHARED["games"][match_id] = {
                    "board": _init_board(),
                    "turn": a,
                    "winner": None,
                    "scored": False,
                    "moves": 0,
                    "created": time.time(),
                    "last_action": time.time(),
                }
                st.rerun()

        with cB:
            if st.button("Rematch (leave + rejoin)", use_container_width=True):
                _leave_lobby(SHARED, me)
                _join_lobby(SHARED, me)
                st.rerun()
