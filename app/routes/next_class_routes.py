from fastapi import APIRouter
from app.db import get_db_connection
from app.automation import fetch_today_classes
from datetime import date

router = APIRouter()


@router.get("/next-class/{session_token}")
def next_class(session_token: str):

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get system ID
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

        # Get OTP for today
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

        result = fetch_today_classes(system_id, otp)

        return result

    except Exception as e:
        return {"status": "error", "message": str(e)}