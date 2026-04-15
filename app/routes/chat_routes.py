from fastapi import APIRouter
from pydantic import BaseModel
from app.db import get_connection


router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_token: str


@router.post("/chat")
def chat(data: ChatRequest):
    try:
        message = data.message.lower()
        token = data.session_token

        # 🔐 GET SYSTEM ID
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT system_id FROM sessions
            WHERE session_token = %s
        """, (token,))

        session = cur.fetchone()

        cur.close()
        conn.close()

        if not session:
            return {"response": "Invalid session"}

        system_id = session[0]

        # 🎯 ATTENDANCE
        if "attendance" in message:
            from app.routes.attendance_routes import get_attendance

            result = get_attendance(token)

            if result["status"] == "success":
                att = result["attendance"]

                return {
                    "response": f"Your attendance:\nTotal: {att['total']}\nPresent: {att['present']}\nAbsent: {att['absent']}"
                }
            else:
                return {"response": result["message"]}

        # ❌ DEFAULT
        return {"response": "Ask me about your attendance"}

    except Exception as e:
        return {"response": str(e)}