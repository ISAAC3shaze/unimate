from fastapi import APIRouter
from app.db import get_db_connection
from app.automation import fetch_today_classes
from datetime import date

router = APIRouter()


@router.get("/today-classes/{session_token}")
def today_classes(session_token: str):

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # get system_id from session
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

        # get today's OTP
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

        # scrape classes
        classes = fetch_today_classes(system_id, otp)

        return classes

    except Exception as e:
        return {"status": "error", "message": str(e)}