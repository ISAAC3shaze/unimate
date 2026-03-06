from fastapi import APIRouter
import requests
from app.chat_router import detect_intent

router = APIRouter()

BASE_URL = "https://unimate-lg25.onrender.com"
user_sessions = {}


@router.post("/chat")
def chat(message: str, user_id: str = "default"):

    # LOGIN PHASE
    if user_id not in user_sessions:

        if message.isdigit():

            r = requests.post(
                f"{BASE_URL}/login",
                json={"system_id": message}
            )

            token = r.json()["session_token"]

            user_sessions[user_id] = token

            return {
                "reply": "Login successful. Ask me anything."
            }

        return {"reply": "Please enter your system ID."}


    # AFTER LOGIN
    session_token = user_sessions[user_id]

    intent = detect_intent(message)


    if intent == "attendance":

        r = requests.get(
            f"{BASE_URL}/attendance/{session_token}"
        )

        return r.json()


    if intent == "absentee_alert":

        r = requests.get(
            f"{BASE_URL}/absentee-alert/{session_token}"
        )

        return r.json()


    if intent == "today_classes":

        r = requests.get(
            f"{BASE_URL}/today-classes/{session_token}"
        )

        return r.json()


    if intent == "holidays":

        r = requests.get(
            f"{BASE_URL}/holidays/{session_token}"
        )

        return r.json()


    if intent.startswith("faculty_location"):

        name = intent.split(":")[1]

        r = requests.get(
            f"{BASE_URL}/faculty-location/{name}"
        )

        return r.json()


    return {"reply": "Sorry, I couldn't understand that."}