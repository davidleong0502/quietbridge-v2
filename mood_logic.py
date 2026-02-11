def mood_to_num(mood: str) -> int:
    mapping = {"Good": 4, "Okay": 3, "Lonely": 2, "Overwhelmed": 1}
    return mapping.get(mood, 3)


def simple_insight(moods_count: int, chats_count: int) -> str:
    if chats_count >= 2:
        return "You tend to use the chatroom when you check in."
    if moods_count >= 3:
        return "You have been checking in consistently."
    return "Small check-ins still matter."


WORD_TO_MODE = {
    "Tense": "Overwhelmed",
    "Alert": "Overwhelmed",

    "Excited": "Good",
    "Joyful": "Good",
    "Motivated": "Good",
    "Inspired": "Good",
    "Engaged": "Good",
    "Proud": "Good",


    "Calm": "Okay",
    "Content": "Okay",
    "Peaceful": "Okay",
    "Restful": "Okay",
    "Serene": "Okay",


    "Sad": "Lonely",
    "Drained": "Lonely",
    "Tired": "Lonely",
}


def word_to_mode(word: str) -> str:
    return WORD_TO_MODE.get((word or "").strip(), "Okay")


def recsupport(mood: str) -> str:
    """
    mood here is one of: "Good", "Okay", "Lonely", "Overwhelmed"
    Return one of: "talk", "study", "community", "reflect"
    """
    mood = (mood or "").strip()

    if mood == "Lonely":
        return "talk"
    if mood == "Overwhelmed":
        return "study"
    if mood == "Okay":
        return "community"
   
    return "talk"


def support_options():
    return [
        ("talk", "💬 Chatroom", "Talk in a gentle, low-pressure shared space."),
        ("study", "🎮 Connect Four", "Play a quick match. Winner +10 🏆, loser −4 🏆."),
        ("community", "📌 Community Query", "Post a worry or question; others can reply anonymously."),
        ("reflect", "🫧 Reflection", "Reset privately, then rejoin when ready."),
    ]



def guided_next_page(mode: str) -> str:
    mapping = {
        "talk": "💬 Chatroom",
        "study": "🎮 Connect Four",
        "community": "📌 Community Query",
        "reflect": "🫧 Reflection",
    }
    return mapping.get(mode, "🏠 Home")


def guided_prompt(mode: str, mood: str) -> str:
    if mode == "community":
        return "Share a worry or question — the community can respond with gentle, anonymous replies."
    if mode == "talk":
        return f"You’re not alone — others may feel {mood.lower()} too. Say something gentle."
    if mode == "study":
        return "No talking needed. Just show up and focus together."
    return "Take a breath. Write one small truth."
