from fastapi import APIRouter
from app.db import get_connection
from app.automation import fetch_subject_attendance
from app.redis_client import r

router = APIRouter()


@router.get("/attendance-subject/{session_token}")
def get_subject_attendance(session_token: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # 🔐 GET SYSTEM ID
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

        # 🔑 GET OTP FROM REDIS
        otp = r.get(f"otp:{system_id}")

        if not otp:
            return {
                "status": "error",
                "message": "OTP required"
            }

        if isinstance(otp, bytes):
            otp = otp.decode()

        # 🚀 FETCH DATA
        result = fetch_subject_attendance(system_id, otp)

        return result

    except Exception as e:
        return {"status": "error", "message": str(e)}