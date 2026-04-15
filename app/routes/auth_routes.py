from fastapi import APIRouter
from pydantic import BaseModel
from app.db import get_connection
from app.automation import trigger_otp
import uuid
from datetime import datetime, timedelta
from app.redis_client import r

router = APIRouter()


class LoginRequest(BaseModel):
    system_id: str


class OTPRequest(BaseModel):
    otp: str


# ---------------- LOGIN ----------------
@router.post("/login")
def login_student(data: LoginRequest):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # 🔍 CHECK STUDENT IN DB
        cur.execute("""
            SELECT name, course, section 
            FROM students 
            WHERE system_id = %s
        """, (data.system_id,))

        student = cur.fetchone()

        if not student:
            cur.close()
            conn.close()
            return {"status": "error", "message": "Invalid Student ID"}

        name, course, section = student

        # 🔐 CREATE SESSION TOKEN
        session_token = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO sessions (system_id, session_token)
            VALUES (%s, %s)
        """, (data.system_id, session_token))

        conn.commit()
        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": "OTP required",
            "session_token": session_token,
            "name": name,
            "course": course,
            "section": section
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------------- CHECK LOGIN ----------------
@router.get("/check-login/{session_token}")
def check_login(session_token: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT system_id, otp, created_at FROM sessions
            WHERE session_token = %s
        """, (session_token,))

        session = cur.fetchone()

        if not session:
            cur.close()
            conn.close()
            return {"status": "error", "message": "Invalid session"}

        system_id, otp, created_at = session

        today = date.today()

        if otp and created_at.date() == today:
            cur.close()
            conn.close()
            return {"status": "logged_in"}
        else:
            cur.close()
            conn.close()
            return {"status": "otp_required"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------------- REQUEST OTP ----------------
@router.post("/request-otp/{session_token}")
def request_otp(session_token: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT system_id FROM sessions
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
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT system_id FROM sessions
            WHERE session_token = %s
        """, (session_token,))

        session = cur.fetchone()

        if not session:
            cur.close()
            conn.close()
            return {"status": "error", "message": "Invalid session"}

        # ✅ FIX: extract system_id
        system_id = session[0]

        

        now = datetime.now()
        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        seconds_until_midnight = int((midnight - now).total_seconds())

        # 🔐 store OTP till midnight (per user)
        
        r.setex(f"otp:{system_id}", seconds_until_midnight, data.otp)

        cur.close()
        conn.close()

        return {"status": "otp_saved"}

    except Exception as e:
        return {"status": "error", "message": str(e)}