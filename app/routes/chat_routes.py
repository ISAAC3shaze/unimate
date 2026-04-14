from fastapi import APIRouter
from pydantic import BaseModel
from app.db import get_connection

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_token: str


@router.post("/chat")
def chat(data: ChatRequest):
    message = data.message.lower()
    token = data.session_token

    conn = get_connection()
    cur = conn.cursor()

    # 🔐 Get system_id from session
    cur.execute("""
        SELECT system_id FROM sessions WHERE session_token = %s
    """, (token,))
    session = cur.fetchone()

    if not session:
        return {"response": "Invalid session. Please login again."}

    system_id = session[0]

    # 🧠 RULE-BASED INTENT DETECTION

    # 1️⃣ ATTENDANCE
    if "attendance" in message:
        return {"response": f"Fetching your attendance for {system_id}..."}

    # 2️⃣ FREE CLASS
    elif "free class" in message:
        return {"response": "Checking free classrooms..."}

    # 3️⃣ FACULTY
    elif "where is" in message or "faculty" in message:
        return {"response": "Checking faculty location..."}

    # 4️⃣ DEFAULT
    else:
        return {"response": "Sorry, I didn’t understand. Try asking about attendance, timetable, or free classes."}