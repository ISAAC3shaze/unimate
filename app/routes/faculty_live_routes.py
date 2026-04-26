from fastapi import APIRouter
from app.db import get_connection
from datetime import datetime
import re

router = APIRouter()


@router.get("/faculty-live/{faculty_name}")
def get_faculty_live(faculty_name: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # 🧠 CLEAN NAME (IMPROVED)
        clean_name = faculty_name.lower()

        # remove noise words (IMPORTANT FIX)
        clean_name = re.sub(
            r"(where is|where|locate|find|sir|maam|madam|dr\.?|prof\.?|mr\.?|ms\.?)",
            "",
            clean_name,
            flags=re.IGNORECASE
        )

        # remove extra spaces
        clean_name = " ".join(clean_name.split())

        print("🔍 Searching faculty:", clean_name)  # DEBUG

        # 🕒 CURRENT TIME + DAY
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%a")  # Mon, Tue
        # 🧪 TEST MODE (temporary)
        #now = datetime.now()

        # simulate time (e.g. 11:30 AM)
        #current_time = datetime.strptime("13:15:00", "%H:%M:%S").time()
        #current_day = "Wed"   # match your timetable day

        #print("🧪 Test Time:", current_time, "| Day:", current_day)

        # 🎯 CHECK IF TEACHING
        cur.execute("""
            SELECT location_block, location_room, faculty_name
            FROM faculty_timetable
            WHERE LOWER(faculty_name) LIKE %s
            AND day_of_week = %s
            AND start_time <= %s
            AND end_time >= %s
            LIMIT 1
        """, (f"%{clean_name}%", current_day, current_time, current_time))

        result = cur.fetchone()

        if result:
            block, room, actual_name = result

            cur.close()
            conn.close()

            return {
                "status": "teaching",
                "name": actual_name,
                "block": block,
                "room": room
            }

        # 🎯 ELSE → CHECK CABIN
        cur.execute("""
            SELECT block, room_no, cabin_no, faculty_name
            FROM faculty
            WHERE LOWER(faculty_name) LIKE %s
            LIMIT 1
        """, (f"%{clean_name}%",))

        faculty = cur.fetchone()

        cur.close()
        conn.close()

        if faculty:
            block, room, cabin, actual_name = faculty

            return {
                "status": "free",
                "name": actual_name,
                "block": block,
                "room": room,
                "cabin": cabin
            }

        return {"status": "not_found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}