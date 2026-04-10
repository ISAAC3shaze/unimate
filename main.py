from fastapi import FastAPI

from app.routes.auth_routes import router as auth_router
from app.routes.attendance_routes import router as attendance_router
from app.routes.today_class_routes import router as today_class_router
# from app.routes.timetable_routes import router as timetable_router
# from app.routes.faculty_routes import router as faculty_router
from app.routes.absentee_routes import router as absentee_router
# from app.routes.holiday_routes import router as holiday_router
# from app.routes.next_class_routes import router as next_class_router
# from app.routes.chat_routes import router as chat_router

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"message": "server running"}

app = FastAPI(title="UniMate API")


@app.get("/")
def home():
    return {"message": "UniMate backend running"}


# Auth
app.include_router(auth_router)

# Attendance (overall)
app.include_router(attendance_router)

#today class
app.include_router(today_class_router)

# # Today's classes / next class
# app.include_router(timetable_router)

# #Facultylocation / cabin
# app.include_router(faculty_router)

# # Absentee alerts
app.include_router(absentee_router)

# # Holidays
# app.include_router(holiday_router)

# #next class
# app.include_router(next_class_router)

# #chat
# app.include_router(chat_router)

from app.db import get_connection

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        system_id VARCHAR(50) UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id SERIAL PRIMARY KEY,
        session_token VARCHAR(255),
        system_id VARCHAR(50),
        otp VARCHAR(10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.on_event("startup")
def startup():
    create_tables()