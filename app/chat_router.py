import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an intent classifier for a university assistant called UniMate.

Your job is to map a student's message to ONE of these intents:

attendance
absentee_alert
today_classes
holidays
faculty_location

Rules:
- Return ONLY the intent.
- No explanation.
- If asking about teacher location return:
faculty_location:Faculty Name

Examples:

User: What is my attendance?
Output: attendance

User: Am I absent today?
Output: absentee_alert

User: When is my next class?
Output: today_classes

User: Show holidays
Output: holidays

User: Where is Kanika ma'am?
Output: faculty_location:Kanika Singla
"""

def detect_intent(message):

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
    )

    return completion.choices[0].message.content.strip()