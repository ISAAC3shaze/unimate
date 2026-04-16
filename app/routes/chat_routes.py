from fastapi import APIRouter
from pydantic import BaseModel
from app.db import get_connection

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_token: str


@router.post("/chat")
def chat(data: ChatRequest):
    try:
        message = data.message.lower()
        token = data.session_token

        # 🔐 GET SYSTEM ID FROM SESSION
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT system_id FROM sessions
            WHERE session_token = %s
        """, (token,))

        session = cur.fetchone()

        cur.close()
        conn.close()

        if not session:
            return {"response": "Invalid session"}

        system_id = session[0]

        # 🔥 OTP VERIFY HANDLER
        if message.isdigit() and len(message) == 6:
            from app.routes.auth_routes import verify_otp, OTPRequest

            otp_data = OTPRequest(otp=message)
            result = verify_otp(token, otp_data)

            if result["status"] == "otp_saved":
                return {
                    "response": "OTP verified successfully! You can now ask for attendance."
                }
            else:
                return {
                    "response": "Invalid OTP. Please try again."
                }

        # 🎯 ATTENDANCE
        if "attendance" in message:
            from app.routes.attendance_routes import get_attendance

            result = get_attendance(token)

            if result["status"] == "success":
                att = result["attendance"]
                return {
                    "response": f"Your attendance:\nTotal: {att['total']}\nPresent: {att['present']}\nAbsent: {att['absent']}"
                }

            # 🔥 OTP TRIGGER
            if "otp" in result["message"].lower():
                from app.routes.auth_routes import request_otp
                request_otp(token)

                return {
                    "response": "OTP required. I’ve sent an OTP to your email. Please enter it."
                }

            return {"response": result["message"]}

        # 🎯 ABSENTEE
        if "absent" in message:
            from app.routes.absentee_routes import get_absentee

            result = get_absentee(token)

            if result["status"] == "success":
                return {
                    "response": f"Your absentee details:\n{result['absentee']}"
                }

            if "otp" in result["message"].lower():
                from app.routes.auth_routes import request_otp
                request_otp(token)

                return {
                    "response": "OTP required. I’ve sent an OTP to your email. Please enter it."
                }

            return {"response": result["message"]}

        # 🎯 HOLIDAYS
        if "holiday" in message:
            from app.routes.holiday_routes import get_holidays

            result = get_holidays(token)

            if result["status"] == "success":
                return {
                    "response": f"Upcoming holidays:\n{result['holidays']}"
                }

            return {"response": result["message"]}

        # 🎯 FREE CLASSROOM
        if "free" in message:
            from app.routes.free_class_routes import get_free_class_now

            result = get_free_class_now()

            if result["status"] == "success":
                return {
                    "response": f"Free classrooms:\n{result['free_classes']}"
                }

            return {"response": result["message"]}

        # 🎯 FACULTY LIVE
        if any(k in message for k in ["faculty", "where", "dr."]):
            from app.routes.faculty_live_routes import get_faculty_live

            faculty_name = message.replace("where is", "").replace("where", "").strip()
            faculty_name = " ".join(faculty_name.split())

            result = get_faculty_live(faculty_name)

            if result["status"] == "teaching":
                return {
                    "response": f"{faculty_name} is teaching in Block {result['block']} Room {result['room']}"
                }

            elif result["status"] == "free":
                return {
                    "response": f"{faculty_name} is free in Block {result['block']} Room {result['room']} Cabin {result['cabin']}"
                }

            elif result["status"] == "not_found":
                return {"response": "Faculty not found"}

            return {"response": result.get("message", "Error fetching faculty location")}

        return {"response": "Ask me about your attendance or absentee"}

    except Exception as e:
        return {"response": str(e)}