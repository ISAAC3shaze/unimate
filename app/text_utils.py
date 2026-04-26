from rapidfuzz import fuzz

# keywords your bot understands
KEYWORDS = [
    "attendance",
    "subject",
    "result",
    "faculty",
    "holiday",
    "free",
    "class",
    "absent"
]

def correct_word(word: str):
    best_match = word
    highest_score = 0

    for key in KEYWORDS:
        score = fuzz.ratio(word, key)

        if score > highest_score and score > 75:
            highest_score = score
            best_match = key

    return best_match


def normalize_message(message: str):
    words = message.lower().split()

    corrected_words = [correct_word(w) for w in words]

    return " ".join(corrected_words)

def match_faculty_name(input_name: str, faculty_list: list):
    from rapidfuzz import fuzz

    best_match = None
    highest = 0

    for name in faculty_list:
        score = fuzz.ratio(input_name.lower(), name.lower())

        if score > highest and score > 70:
            highest = score
            best_match = name

    return best_match