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
        if "holiday" in message:
            from app.routes.holiday_routes import get_holidays
            from datetime import datetime
            import re

            result = get_holidays(token)

            if result["status"] == "success":
                holidays = result["holidays"]

                # 🔥 FIX: remove time
                today = datetime.now().date()

                all_holidays = []
                upcoming_holidays = []

                for h in holidays:
                    try:
                        raw_date = h["date"].split(":")[-1].strip()

                        # remove st/nd/rd/th
                        clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', raw_date)

                        date_obj = datetime.strptime(clean_date, "%d %b %Y").date()

                        holiday_obj = {
                            "name": h["name"],
                            "date": date_obj
                        }

                        all_holidays.append(holiday_obj)

                        if date_obj >= today:
                            upcoming_holidays.append(holiday_obj)

                    except Exception as e:
                        print("Holiday parse error:", e)
                        continue

                # sort
                all_holidays.sort(key=lambda x: x["date"])
                upcoming_holidays.sort(key=lambda x: x["date"])

                # detect number
                count = 1
                for word in message.split():
                    if word.isdigit():
                        count = int(word)

                # full vs upcoming
                if "all" in message or "full" in message:
                    selected = all_holidays
                else:
                    selected = upcoming_holidays[:count]

                if not selected:
                    return {"response": "No upcoming holidays found."}

                # single holiday
                if len(selected) == 1 and "all" not in message:
                    h = selected[0]
                    formatted_date = h["date"].strftime("%d %b %Y")

                    return {
                        "response": f"Your next holiday is {h['name']} on {formatted_date} 🎉"
                    }

                # multiple holidays
                response = "Here are your holidays:\n\n"

                for h in selected:
                    formatted_date = h["date"].strftime("%d %b %Y")
                    response += f"• {h['name']} — {formatted_date}\n"

                return {"response": response}

            return {"response": result["message"]}

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