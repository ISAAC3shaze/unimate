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
                return {"response": "OTP verified successfully! You can now ask for attendance."}
            else:
                return {"response": "Invalid OTP. Please try again."}

        # 🎯 ATTENDANCE
        if "attendance" in message:
            from app.routes.attendance_routes import get_attendance

            result = get_attendance(token)

            if result["status"] == "success":
                att = result["attendance"]

                total = att["total"]
                present = att["present"]
                absent = att["absent"]

                percentage = (present / total) * 100 if total > 0 else 0
                percentage = round(percentage, 1)

                if percentage >= 75:
                    status_msg = "✅ You’re in a safe zone. Keep it up!"
                elif percentage >= 60:
                    status_msg = "⚠️ You’re getting close to the risk zone."
                else:
                    status_msg = "🚨 You’re below 75%. Risk of being debarred!"

                return {
                    "response": (
                        f"You’ve attended {present} out of {total} classes.\n\n"
                        f"Your attendance is {percentage}%.\n\n"
                        f"{status_msg}"
                    )
                }

            if "otp" in result["message"].lower():
                from app.routes.auth_routes import request_otp
                request_otp(token)

                return {"response": "OTP required. I’ve sent an OTP to your email. Please enter it."}

            return {"response": result["message"]}

        # 🎯 ABSENTEE
        if "absent" in message:
            from app.routes.absentee_routes import get_absentee

            result = get_absentee(token)

            if result["status"] == "success":
                abs_data = result["absentee"]

                if abs_data.get("status") == "no_absence":
                    return {"response": "You have no absences today ✅"}
                else:
                    return {"response": f"You were absent in:\n{abs_data}"}

            if "otp" in result["message"].lower():
                from app.routes.auth_routes import request_otp
                request_otp(token)

                return {"response": "OTP required. I’ve sent an OTP to your email. Please enter it."}

            return {"response": result["message"]}

        # 🎯 HOLIDAYS
        # 🎯 HOLIDAYS (HARDCODED - FINAL DEMO VERSION)
        if "holiday" in message:

            from datetime import datetime

            holidays = [
        {"name": "New Year", "date": "01 Jan 2026"},
        {"name": "Makar Sankranti", "date": "14 Jan 2026"},
        {"name": "Holiday", "date": "24 Jan 2026"},
        {"name": "Republic Day", "date": "26 Jan 2026"},
        {"name": "Holiday", "date": "14 Feb 2026"},
        {"name": "Maha Shivaratri", "date": "15 Feb 2026"},
        {"name": "Holiday", "date": "28 Feb 2026"},
        {"name": "Holi", "date": "04 Mar 2026"},
        {"name": "Holiday", "date": "05 Mar 2026"},
        {"name": "Eid-ul-Fitr", "date": "21 Mar 2026"},
        {"name": "Ram Navami", "date": "26 Mar 2026"},
        {"name": "Holiday", "date": "28 Mar 2026"},
        {"name": "Mahavir Jayanti", "date": "31 Mar 2026"},
        {"name": "Good Friday", "date": "03 Apr 2026"},
        {"name": "Holiday", "date": "11 Apr 2026"},
        {"name": "Dr. Ambedkar Jayanti", "date": "14 Apr 2026"},
        {"name": "Remedial Classes", "date": "21 Apr 2026"},
        {"name": "Buddha Purnima", "date": "01 May 2026"},
        {"name": "Eid", "date": "27 May 2026"},
            ]

        # 🔥 Today fixed for demo
            today = datetime.strptime("17 May 2026", "%d %b %Y")

            # 🔥 sort ALL holidays
            holidays_sorted = sorted(
                holidays,
                key=lambda x: datetime.strptime(x["date"], "%d %b %Y")
            )

        # 🔥 upcoming filter
            upcoming = []
            for h in holidays_sorted:
                h_date = datetime.strptime(h["date"], "%d %b %Y")
                if h_date >= today:
                    upcoming.append(h)

        # 🧠 detect number
            count = 1
            for word in message.split():
                if word.isdigit():
                    count = int(word)

    # 🧠 choose list
            if "all" in message or "full" in message:
                selected = holidays_sorted
            else:
                selected = upcoming[:count]

            if not selected:
                return {"response": "No upcoming holidays found."}

    # 💬 single
            if len(selected) == 1 and "all" not in message:
                h = selected[0]
                return {
                "response": f"Your next holiday is {h['name']} on {h['date']} 🎉"
                }

    # 💬 multiple
            response = "Here are your holidays:\n\n"
            for h in selected:
                response += f"• {h['name']} — {h['date']}\n"

            return {"response": response}

        # 🎯 FREE CLASSROOM
        if "free" in message:
            from app.routes.free_class_routes import get_free_class_now

            result = get_free_class_now()

            if result["status"] == "success":
                return {"response": f"Free classrooms:\n{result['free_classes']}"}

            return {"response": result["message"]}

        # 🎯 FACULTY
        if any(k in message for k in ["faculty", "where", "dr."]):
            from app.routes.faculty_live_routes import get_faculty_live

            faculty_name = message.replace("where is", "").replace("where", "").strip()
            faculty_name = " ".join(faculty_name.split())

            result = get_faculty_live(faculty_name)

            if result["status"] == "teaching":
                return {"response": f"{faculty_name} is teaching in Block {result['block']} Room {result['room']}"}

            elif result["status"] == "free":
                return {"response": f"{faculty_name} is free in Block {result['block']} Room {result['room']} Cabin {result['cabin']}"}

            elif result["status"] == "not_found":
                return {"response": "Faculty not found"}

            return {"response": result.get("message", "Error fetching faculty location")}

        return {"response": "Ask me about your attendance, holidays, or absentee"}

    except Exception as e:
        return {"response": str(e)}