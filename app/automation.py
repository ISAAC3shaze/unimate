from playwright.sync_api import sync_playwright
from datetime import datetime

EZONE_URL = "https://student.sharda.ac.in/admin"

_playwright = None
_browser = None


# ---------------- SHARED BROWSER ----------------
def get_browser():
    global _playwright, _browser

    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=True)

    return _browser


# ---------------- LOGIN ----------------
def login(page, system_id, otp):
    page.goto(EZONE_URL)
    page.wait_for_load_state("networkidle")

    page.fill("#system_id", system_id)
    page.fill("#otp", otp)

    page.click("button:has-text('Login')")
    page.wait_for_load_state("networkidle")


# ---------------- OTP TRIGGER ----------------
def trigger_otp(system_id: str):

    browser = get_browser()
    context = browser.new_context()
    page = context.new_page()

    page.goto(EZONE_URL)
    page.wait_for_load_state("networkidle")

    page.fill("#system_id", system_id)
    page.click("#send_stu_otp_email")

    context.close()

    return True


# ---------------- ATTENDANCE ----------------
def fetch_attendance(system_id: str, otp: str):

    browser = get_browser()
    context = browser.new_context()
    page = context.new_page()

    login(page, system_id, otp)

    page.wait_for_selector("text=Total Attendance")

    attendance_card = page.locator("text=Total Attendance").locator("..").locator("..")

    raw_text = attendance_card.inner_text()

    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

    attendance = {}

    for i in range(len(lines)):
        if "Total" in lines[i]:
            attendance["total"] = int(lines[i + 1])
        if "Present" in lines[i]:
            attendance["present"] = int(lines[i + 1])
        if "Absent" in lines[i]:
            attendance["absent"] = int(lines[i + 1])

    context.close()

    return attendance


# ---------------- TODAY CLASSES ----------------
def fetch_today_classes(system_id: str, otp: str):

    browser = get_browser()
    context = browser.new_context()
    page = context.new_page()

    login(page, system_id, otp)

    page.wait_for_selector("text=Today's Class")

    if page.locator("text=Holiday").count() > 0:
        context.close()
        return {"status": "holiday"}

    class_cards = page.locator("text=Block").locator("..").all()

    classes = []

    for card in class_cards:
        text = card.inner_text()
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        if len(lines) < 3:
            continue

        start, end = lines[0].split("-")

        classes.append({
            "start": start.strip(),
            "end": end.strip(),
            "subject": lines[1],
            "location": lines[2],
            "faculty": lines[3] if len(lines) > 3 else ""
        })

    context.close()

    now = datetime.now().time()

    for c in classes:
        start = datetime.strptime(c["start"], "%H:%M:%S").time()
        end = datetime.strptime(c["end"], "%H:%M:%S").time()

        if start <= now <= end:
            return {"status": "current_class", **c}

    for c in classes:
        start = datetime.strptime(c["start"], "%H:%M:%S").time()

        if start > now:
            return {"status": "next_class", **c}

    return {"status": "college_over"}