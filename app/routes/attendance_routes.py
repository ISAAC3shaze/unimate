from fastapi import APIRouter
from app.db import get_connection
from app.automation import fetch_attendance
from app.redis_client import r   # ✅ ADD THIS

router = APIRouter()


@router.get("/attendance/{session_token}")
def get_attendance(session_token: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # 🔐 GET SYSTEM ID FROM SESSION
        cur.execute("""
            SELECT system_id FROM sessions
            WHERE session_token = %s
        """, (session_token,))

        session = cur.fetchone()

        cur.close()
        conn.close()

        if not session:
            return {"status": "error", "message": "Invalid session"}

        system_id = session[0]

        # 🔥 GET OTP FROM REDIS (MAIN FIX)
        otp = r.get(f"otp:{system_id}")

        if not otp:
            return {
                "status": "error",
                "message": "OTP required"
            }

        # 🚀 FETCH ATTENDANCE USING STORED OTP
        attendance = fetch_attendance(system_id, otp)

        return {
            "status": "success",
            "attendance": attendance
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}