from fastapi import APIRouter
from app.db import get_connection
from app.automation import fetch_attendance

router = APIRouter()


@router.get("/attendance/{session_token}")
def get_attendance(session_token: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # get system_id and otp from sessions table
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

        attendance = fetch_attendance(system_id, otp)

        return {
            "status": "success",
            "attendance": attendance
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}