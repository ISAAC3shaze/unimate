from fastapi import APIRouter
import requests
import os
from app.chat_router import detect_intent

router = APIRouter()

# BASE URL for deployed server
BASE_URL = os.getenv("BASE_URL", "https://unimate-lg25.onrender.com")

# store sessions in memory
user_sessions = {}


@router.post("/chat")
def chat(message: str, user_id: str = "default"):

    # ---------- LOGIN PHASE ----------
    if user_id not in user_sessions:

        # user must send system id first
        if message.isdigit():

            try:
                r = requests.post(
                    f"{BASE_URL}/login",
                    json={"system_id": message}
                )

                data = r.json()

                # safe check
                if "session_token" not in data:
                    return {
                        "reply": "Login failed. Please check your system ID."
                    }

                token = data["session_token"]

                user_sessions[user_id] = token

                return {
                    "reply": "Login successful. Ask me anything."
                }

            except Exception:
                return {
                    "reply": "Login service unavailable. Try again."
                }

        return {"reply": "Please enter your system ID."}

    # ---------- AFTER LOGIN ----------
    session_token = user_sessions[user_id]

    intent = detect_intent(message)

    # ---------- ATTENDANCE ----------
    if intent == "attendance":

        r = requests.get(
            f"{BASE_URL}/attendance/{session_token}"
        )

        return r.json()

    # ---------- ABSENTEE ALERT ----------
    if intent == "absentee_alert":

        r = requests.get(
            f"{BASE_URL}/absentee-alert/{session_token}"
        )

        return r.json()

    # ---------- TODAY CLASSES ----------
    if intent == "today_classes":

        r = requests.get(
            f"{BASE_URL}/today-classes/{session_token}"
        )

        return r.json()

    # ---------- HOLIDAYS ----------
    if intent == "holidays":

        r = requests.get(
            f"{BASE_URL}/holidays/{session_token}"
        )

        return r.json()

    # ---------- FACULTY LOCATION ----------
    if intent.startswith("faculty_location"):

        name = intent.split(":")[1]

        r = requests.get(
            f"{BASE_URL}/faculty-location/{name}"
        )

        return r.json()
        
    return {"reply": "Sorry, I couldn't understand that."}
