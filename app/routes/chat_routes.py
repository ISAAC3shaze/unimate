from fastapi import APIRouter
from pydantic import BaseModel
from app.db import get_connection
from app.routes.attendance_routes import get_attendance
import requests
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
     # make sure this is at top


    if "attendance" in message:
        try:
            res = requests.get(
            f"https://unimate-production.up.railway.app/attendance/{system_id}"
            )

            data = res.json()

            return {
                "response": f"Your attendance is {data}"
            }
    
        except Exception as e:
             print("ERROR:", e)
        return {
            "response": "Error fetching attendance."
        }

    # 2️⃣ FREE CLASS
    elif "free class" in message:
        return {"response": "Checking free classrooms..."}

    # 3️⃣ FACULTY
    elif "where is" in message or "faculty" in message:
        return {"response": "Checking faculty location..."}

    # 4️⃣ DEFAULT
    else:
        return {"response": "Sorry, I didn’t understand. Try asking about attendance, timetable, or free classes."}