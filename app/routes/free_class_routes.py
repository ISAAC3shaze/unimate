from fastapi import APIRouter
from app.db import get_connection
from datetime import datetime

router = APIRouter()


@router.get("/free-class-now")
def get_free_class_now():
    try:
        conn = get_connection()
        cur = conn.cursor()

        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%a")

        cur.execute("""
            SELECT room
            FROM free_class
            WHERE day = %s
            AND start_time <= %s
            AND end_time >= %s
            AND LOWER(status) = 'available'
        """, (current_day, current_time, current_time))

        rooms = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "status": "success",
            "free_classes": [r[0] for r in rooms]
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}