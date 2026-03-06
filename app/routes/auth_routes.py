from fastapi import APIRouter
from pydantic import BaseModel
from app.db import get_db_connection
from app.automation import trigger_otp
import uuid
from datetime import date

router = APIRouter()

class LoginRequest(BaseModel):
    system_id: str


class OTPRequest(BaseModel):
    otp: str


# ---------------- LOGIN ----------------
@router.post("/login")
def login_student(data: LoginRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT student_name, system_id, section
            FROM students
            WHERE system_id = %s
        """, (data.system_id,))

        student = cur.fetchone()

        if not student:
            cur.close()
            conn.close()
            return {"status": "error", "message": "Student not found"}

        session_token = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO user_sessions (system_id, session_token)
            VALUES (%s, %s)
        """, (student[1], session_token))

        conn.commit()
        cur.close()
        conn.close()

        return {
            "status": "success",
            "student_name": student[0],
            "system_id": student[1],
            "section": student[2],
            "session_token": session_token
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------------- CHECK LOGIN ----------------
@router.get("/check-login/{session_token}")
def check_login(session_token: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

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

        cur.execute("""
            SELECT otp FROM ezone_logins
            WHERE system_id = %s AND login_date = %s
        """, (system_id, today))

        login = cur.fetchone()

        cur.close()
        conn.close()

        if login:
            return {"status": "logged_in"}
        else:
            return {"status": "otp_required"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------------- REQUEST OTP ----------------
@router.post("/request-otp/{session_token}")
def request_otp(session_token: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

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

        cur.close()
        conn.close()

        trigger_otp(system_id)

        return {"status": "otp_sent"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------------- VERIFY OTP ----------------
@router.post("/verify-otp/{session_token}")
def verify_otp(session_token: str, data: OTPRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

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

        cur.execute("""
            DELETE FROM ezone_logins
            WHERE system_id = %s AND login_date = %s
        """, (system_id, today))

        cur.execute("""
            INSERT INTO ezone_logins (system_id, otp, login_date)
            VALUES (%s, %s, %s)
        """, (system_id, data.otp, today))

        conn.commit()
        cur.close()
        conn.close()

        return {"status": "otp_saved"}

    except Exception as e:
        return {"status": "error", "message": str(e)}