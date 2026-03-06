from fastapi import FastAPI

from app.routes.auth_routes import router as auth_router
from app.routes.attendance_routes import router as attendance_router
from app.routes.timetable_routes import router as timetable_router
from app.routes.faculty_routes import router as faculty_router
from app.routes.absentee_routes import router as absentee_router
from app.routes.holiday_routes import router as holiday_router
from app.routes.next_class_routes import router as next_class_router
from app.routes.chat_routes import router as chat_router


app = FastAPI(title="UniMate API")


@app.get("/")
def home():
    return {"message": "UniMate backend running"}


# Auth
app.include_router(auth_router)

# Attendance (overall)
app.include_router(attendance_router)

# Today's classes / next class
app.include_router(timetable_router)

# Faculty location / cabin
app.include_router(faculty_router)

# Absentee alerts
app.include_router(absentee_router)

# Holidays
app.include_router(holiday_router)

#next class
app.include_router(next_class_router)

#chat
app.include_router(chat_router)


