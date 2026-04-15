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

        # 🎯 ATTENDANCE
        if "attendance" in message:
            from app.routes.attendance_routes import get_attendance

            result = get_attendance(token)

            if result["status"] == "success":
                att = result["attendance"]

                return {
                    "response": f"Your attendance:\nTotal: {att['total']}\nPresent: {att['present']}\nAbsent: {att['absent']}"
                }
            else:
                return {"response": result["message"]}

        # 🎯 ABSENTEE
        if "absent" in message:
            from app.routes.absentee_routes import get_absentee

            result = get_absentee(token)

            if result["status"] == "success":
                return {
                    "response": f"Your absentee details:\n{result['absentee']}"
                }
            else:
                return {"response": result["message"]}

        
       
        # 🎯 HOLIDAYS
        if "holiday" in message:
            from app.routes.holiday_routes import get_holidays

            result = get_holidays(token)

            if result["status"] == "success":
                 return {
            "response": f"Upcoming holidays:\n{result['holidays']}"
             }
            else:
                return {"response": result["message"]}
        

        # 🎯 FREE CLASSROOM
        if "free" in message:
            from app.routes.free_class_routes import get_free_class_now

            result = get_free_class_now()

            if result["status"] == "success":
                return {
                 "response": f"Free classrooms:\n{result['free_classes']}"
                }
            else:
                return{
                    "response": result["message"]
                }
        
        # 🎯 FACULTY LIVE
        # 🎯 FACULTY LIVE
        if any(k in message for k in ["faculty", "where is", "dr."]):
            from app.routes.faculty_live_routes import get_faculty_live

                # 🔥 CLEAN EXTRACTION (IMPORTANT)
            faculty_name = message.replace("where is", "")
            faculty_name = faculty_name.strip()
            faculty_name = " ".join(faculty_name.split())  # removes extra spaces

            # 🧪 DEBUG (remove later if you want)
            print(f"Extracted faculty: {faculty_name}")

            result = get_faculty_live(faculty_name)

            if result["status"] == "success":
                return {
            "response": f"{faculty_name} is at {result['location']}"
                }
            else:
                return {
            "response": result.get("message", "Faculty not found")
        }
    
        # ❌ DEFAULT (ALWAYS LAST)
        return {"response": "Ask me about your attendance or absentee"}

    except Exception as e:
        return {"response": str(e)}