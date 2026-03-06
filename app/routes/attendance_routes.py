from fastapi import APIRouter
from app.db import get_db_connection
from app.automation import fetch_attendance
from datetime import date

router = APIRouter()


@router.get("/attendance/{session_token}")
def get_attendance(session_token: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # get system_id from session
        cur.execute("""
            SELECT system_id FROM user_sessions
            WHERE session_token = %s
        """, (session_token,))
        session = cur.fetchone()

        if not session:
            cur.close()
            conn.close()
            return {"status": "error", "message": "Invalid session"}

        system_id = session[0]
        today = date.today()

        # get OTP for today
        cur.execute("""
            SELECT otp FROM ezone_logins
            WHERE system_id = %s AND login_date = %s
        """, (system_id, today))

        login = cur.fetchone()

        cur.close()
        conn.close()

        if not login:
            return {"status": "error", "message": "OTP required"}

        otp = login[0]

        print("SYSTEM ID:", system_id)
        print("OTP:", otp)

        attendance = fetch_attendance(system_id, otp)

        print("ATTENDANCE RESULT:", attendance)
        return {
            "status": "success",
            "attendance": attendance
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}