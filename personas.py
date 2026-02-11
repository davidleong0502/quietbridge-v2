import random

ADJ = ["Soft", "Calm", "Warm", "Gentle", "Quiet"]
NOUN = ["Cloud", "River", "Fox", "Lantern", "Pine"]

def generate_name() -> str:
    return f"{random.choice(ADJ)}{random.choice(NOUN)}"