from fastapi import APIRouter
from app.db import get_connection
from app.automation import fetch_absentee
from app.redis_client import r   # ✅ ADD THIS

router = APIRouter()


@router.get("/absentee/{session_token}")
def get_absentee(session_token: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # 🔐 GET SYSTEM ID ONLY
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

        # 🔥 GET OTP FROM REDIS
        otp = r.get(f"otp:{system_id}")

        if not otp:
            return {
                "status": "error",
                "message": "OTP required"
            }

        # 🚀 FETCH ABSENTEE
        absentee = fetch_absentee(system_id, otp)

        return {
            "status": "success",
            "absentee": absentee
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}