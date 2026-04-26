from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.attendance_routes import router as attendance_router
from app.routes.today_class_routes import router as today_class_router

from app.routes.absentee_routes import router as absentee_router
from app.routes.holiday_routes import router as holiday_router

from app.routes.faculty_live_routes import router as faculty_live_router
from app.routes.free_class_routes import router as free_class_router
from app.routes.chat_routes import router as chat_router
from app.routes import results_routes
from app.routes import subject_attendance_routes

from app.db import get_connection

# ✅ CREATE APP ONLY ONCE
app = FastAPI(title="UniMate API")

# ✅ ADD CORS (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for now)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ HEALTH CHECK
@app.get("/health")
def health():
    return {"message": "server running"}

# ✅ ROOT
@app.get("/")
def home():
    return {"message": "UniMate backend running"}


# ================= ROUTES =================

app.include_router(auth_router)


app.include_router(attendance_router)


app.include_router(today_class_router)







app.include_router(absentee_router)


app.include_router(holiday_router)


app.include_router(faculty_live_router)


app.include_router(free_class_router)

app.include_router(chat_router)
app.include_router(results_routes.router)
app.include_router(subject_attendance_routes.router)






# ================= DB SETUP =================

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


# ✅ STARTUP EVENT
@app.on_event("startup")
def startup():
    create_tables()
    #redeploy fix