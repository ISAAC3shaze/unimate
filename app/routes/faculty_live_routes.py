from fastapi import APIRouter
from app.db import get_connection
from datetime import datetime

router = APIRouter()


@router.get("/faculty-live/{faculty_name}")
def get_faculty_live(faculty_name: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # current time + day
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%a")  # Mon, Tue

        # check timetable
        cur.execute("""
            SELECT location_block, location_room
            FROM faculty_timetable
            WHERE LOWER(faculty_name) = LOWER(%s)
            AND day_of_week = %s
            AND start_time <= %s
            AND end_time >= %s
        """, (faculty_name, current_day, current_time, current_time))

        result = cur.fetchone()

        if result:
            cur.close()
            conn.close()
            return {
                "status": "teaching",
                "block": result[0],
                "room": result[1]
            }

        # else → get cabin
        cur.execute("""
            SELECT block, room_no, cabin_no
            FROM faculty
            WHERE LOWER(faculty_name) = LOWER(%s)
        """, (faculty_name,))

        faculty = cur.fetchone()

        cur.close()
        conn.close()

        if faculty:
            return {
                "status": "free",
                "block": faculty[0],
                "room": faculty[1],
                "cabin": faculty[2]
            }

        return {"status": "not_found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}