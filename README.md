# UniMate 🚀

AI-powered University Assistant Chatbot

---

## 📌 Overview

UniMate is a smart chatbot designed to help students access university-related information in real time. It integrates with the university portal (eZone) to fetch live data like attendance, results, faculty location, and more.

The system is built with a scalable backend and is designed to support future AI-based intent understanding.

---

## ⚙️ Tech Stack

### Backend

- FastAPI (API framework)
- PostgreSQL (Database)
- Redis (OTP/session handling)
- Playwright (Web scraping automation)

### Frontend

- Next.js / React (Chat UI)

---

## 🚀 Features

- ✅ **Attendance Tracking (OTP-based)**
- ✅ **Subject-wise Attendance**
- ✅ **Results Fetching**
- ✅ **Free Classroom Detection**
- ✅ **Faculty Live Location**
- ✅ **Holiday Listing**
- ✅ **Session-based Chat System**

---

## 🧠 System Architecture

User → Frontend (Chat UI) → FastAPI Backend →
→ Database (PostgreSQL)
→ Redis (OTP/session)
→ Playwright (eZone scraping)

---

## 🛠️ Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/ISAAC3shaze/unimate.git
cd unimate
```

---

### 2. Backend Setup

#### Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Install Playwright Browsers

```bash
playwright install
```

---

### 3. Environment Variables

Create a `.env` file in the root:

```env
DATABASE_URL=your_postgresql_connection_string
REDIS_URL=your_redis_connection_string
```

---

### 4. Run Backend

```bash
uvicorn main:app --reload
```

---

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 📂 Project Structure

```
unimate/
│
├── app/                # Backend logic
├── routes/             # API routes
├── automation.py       # Playwright scraping
├── db.py               # Database connection
├── redis_client.py     # Redis integration
├── main.py             # FastAPI entry point
│
├── frontend/           # Frontend (Next.js)
│
├── requirements.txt
└── README.md
```

---

## ⚠️ Important Notes

- Redis must be running for OTP functionality
- Playwright is required for scraping (run `playwright install`)
- Database must be properly configured
- This project currently uses rule-based intent handling (LLM integration planned)

---

## 🚀 Future Improvements

- 🤖 LLM-based intent understanding
- 🎯 Better conversational UI
- 📊 Analytics dashboard
- 📱 Mobile optimization

---

## 👨‍💻 Author

**Isaac**

---

## ⭐ If you found this useful, consider giving it a star!
