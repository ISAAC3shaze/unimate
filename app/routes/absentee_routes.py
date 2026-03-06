from fastapi import APIRouter
from app.db import get_db_connection
from app.automation import fetch_absentee_alert
from datetime import date

router = APIRouter()


@router.get("/absentee-alert/{session_token}")
def absentee_alert(session_token: str):

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # get system_id
        cur.execute("""
            SELECT system_id
            FROM user_sessions
            WHERE session_token = %s
        """, (session_token,))

        session = cur.fetchone()

        if not session:
            cur.close()
            conn.close()
            return {"status": "error", "message": "Invalid session"}

        system_id = session[0]

        # get OTP
        cur.execute("""
            SELECT otp
            FROM ezone_logins
            WHERE system_id = %s
            AND login_date = %s
        """, (system_id, date.today()))

        login = cur.fetchone()

        cur.close()
        conn.close()

        if not login:
            return {"status": "error", "message": "OTP required"}

        otp = login[0]

        alert = fetch_absentee_alert(system_id, otp)

        return alert

    except Exception as e:
        return {"status": "error", "message": str(e)}