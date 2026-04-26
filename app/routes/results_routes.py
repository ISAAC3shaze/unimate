from fastapi import APIRouter
from app.db import get_connection
from app.automation import fetch_results
from app.redis_client import r

router = APIRouter()


@router.get("/results/{session_token}")
def get_results(session_token: str):
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

        # 🔥 GET OTP FROM REDIS (SAME AS ATTENDANCE)
        otp = r.get(f"otp:{system_id}")

        if not otp:
            return {
                "status": "error",
                "message": "OTP required"
            }

        # ⚠️ IMPORTANT (same fix you missed earlier)
        if isinstance(otp, bytes):
            otp = otp.decode()

        # 🚀 FETCH RESULTS
        results = fetch_results(system_id, otp)

        return {
            "status": "success",
            "results": results
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}