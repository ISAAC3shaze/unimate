from fastapi import APIRouter
from app.db import get_db_connection
from datetime import datetime

router = APIRouter()

#for faculty timetable or of she/he in cabin 
@router.get("/faculty-location/{faculty_name}")
def faculty_location(faculty_name: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%a")  # Mon Tue Wed Thu Fri

        # check if teaching right now
        cur.execute("""
            SELECT location_block, location_room
            FROM faculty_timetable
            WHERE faculty_name ILIKE %s
            AND day_of_week = %s
            AND start_time <= %s
            AND end_time >= %s
        """, (f"%{faculty_name}%", current_day, current_time, current_time))

        teaching = cur.fetchone()

        if teaching:
            block, room = teaching
            cur.close()
            conn.close()

            return {
                "status": "teaching",
                "message": f"{faculty_name} is currently teaching in Block {block} Room {room}"
            }

        # if not teaching → get cabin
        cur.execute("""
            SELECT block, floor, room_no, cabin_no
            FROM faculty_cabin
            WHERE faculty_name ILIKE %s
        """, (f"%{faculty_name}%",))

        cabin = cur.fetchone()

        cur.close()
        conn.close()

        if cabin:
            block, floor, room_no, cabin_no = cabin

            return {
                "status": "not_teaching",
                "message": f"{faculty_name} is not teaching right now. Cabin: Block {block}, Floor {floor}, Room {room_no}, Cabin {cabin_no}"
            }

        return {
            "status": "error",
            "message": "Faculty not found"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    

##for the information of faculty next class    
@router.get("/faculty-next-class/{faculty_name}")
def faculty_next_class(faculty_name: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%a")

        cur.execute("""
            SELECT start_time, location_block, location_room
            FROM faculty_timetable
            WHERE faculty_name ILIKE %s
            AND day_of_week = %s
            AND start_time > %s
            ORDER BY start_time ASC
            LIMIT 1
        """, (f"%{faculty_name}%", current_day, current_time))

        next_class = cur.fetchone()

        cur.close()
        conn.close()

        if next_class:
            start_time, block, room = next_class

            return {
                "status": "next_class",
                "message": f"Next class is at {start_time.strftime('%H:%M')} in Block {block} Room {room}"
            }

        return {
            "status": "no_class",
            "message": "No more classes scheduled today"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    

#for the faculty contact details     
@router.get("/faculty-contact/{faculty_name}")
def faculty_contact(faculty_name: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT designation, department, mobile, email
            FROM faculty_cabin
            WHERE faculty_name ILIKE %s
        """, (f"%{faculty_name}%",))

        faculty = cur.fetchone()

        cur.close()
        conn.close()

        if not faculty:
            return {
                "status": "error",
                "message": "Faculty not found"
            }

        designation, department, mobile, email = faculty

        return {
            "status": "success",
            "designation": designation,
            "department": department,
            "mobile": mobile,
            "email": email
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    

