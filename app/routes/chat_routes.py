from fastapi import APIRouter
from pydantic import BaseModel
from app.db import get_connection
from app.routes.attendance_routes import get_attendance

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_token: str


@router.post("/chat")
def chat(data: ChatRequest):
    try:
        message = data.message.lower()
        token = data.session_token

        # 🔐 GET SYSTEM ID FROM SESSION
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT system_id FROM sessions
            WHERE session_token = %s
        """, (token,))

        session = cur.fetchone()

        if not session:
            cur.close()
            conn.close()
            return {"response": "Invalid session. Please login again."}

        system_id = session[0]

        cur.close()
        conn.close()

        # 🎯 ATTENDANCE ONLY
    if "attendance" in message:
        try:
            from app.routes.attendance_routes import get_attendance

            result = get_attendance(token)

            if result["status"] == "success":
                att = result["attendance"]

                return {
                "response": f"Your attendance:\nTotal: {att['total']}\nPresent: {att['present']}\nAbsent: {att['absent']}"
            }
            else:
                return {
                "response": result["message"]
            }

        except Exception as e:
            return {
            "response": f"Error fetching attendance: {str(e)}"
        }