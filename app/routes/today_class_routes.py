from fastapi import APIRouter
from app.db import get_connection
from app.automation import fetch_today_classes

router = APIRouter()


@router.get("/today-classes/{session_token}")
def get_today_classes(session_token: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT system_id, otp FROM sessions
            WHERE session_token = %s
        """, (session_token,))

        session = cur.fetchone()

        cur.close()
        conn.close()

        if not session:
            return {"status": "error", "message": "Invalid session"}

        system_id, otp = session

        if not otp:
            return {"status": "error", "message": "OTP required"}

        data = fetch_today_classes(system_id, otp)

        return {
            "status": "success",
            "data": data
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}