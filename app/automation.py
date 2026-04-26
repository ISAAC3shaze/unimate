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
        try:
            if "Total" in lines[i]:
                attendance["total"] = int(lines[i + 1])
            if "Present" in lines[i]:
                attendance["present"] = int(lines[i + 1])
            if "Absent" in lines[i]:
                attendance["absent"] = int(lines[i + 1])
        except:
            continue

    context.close()

    return attendance


# ---------------- TODAY CLASSES ----------------
def fetch_today_classes(system_id: str, otp: str):

    browser = get_browser()
    context = browser.new_context()
    page = context.new_page()

    login(page, system_id, otp)

    page.wait_for_selector("text=Today's Class")

    class_cards = page.locator("text=Block").locator("..").all()

    if page.locator("text=Holiday").count() > 0 and len(class_cards) == 0:
        context.close()
        return {"status": "holiday"}

    

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


#absentee alert function 
def fetch_absentee_alert(system_id: str, otp: str):

    browser = get_browser()
    context = browser.new_context()
    page = context.new_page()

    login(page, system_id, otp)

    page.wait_for_selector("text=Absentee Alert")

    alert_block = page.locator("text=Absentee Alert").locator("..")

    text = alert_block.inner_text()

    context.close()

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    if len(lines) <= 1:
        return {"status": "no_absence"}

    if len(lines) >= 3:
        return {
            "status": "absent",
            "subject": lines[1],
            "date": lines[2]
        }

    return {"status": "no_absence"}

#HOLIDAYS FUNCTION 
def fetch_holidays(system_id: str, otp: str):

    browser = get_browser()
    context = browser.new_context()
    page = context.new_page()

    login(page, system_id, otp)

    try:
        page.wait_for_timeout(4000)

        # 👉 get full page text (debug approach)
        text = page.inner_text("body")

        context.close()

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        holidays = []

        for i in range(len(lines) - 1):
            if any(day in lines[i+1] for day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]):
                holidays.append({
                    "name": lines[i],
                    "date": lines[i+1]
                })


        return {
            "status": "success",
            "holidays": holidays
        }

    except Exception as e:
        context.close()
        return {"status": "error", "message": str(e)}

    

#FOR RESULT
from app.automation import login
from datetime import datetime

def fetch_results(system_id: str, otp: str):
    browser = get_browser()
    context = browser.new_context()
    page = context.new_page()

    try:
        # 🔐 LOGIN
        login(page, system_id, otp)
        page.wait_for_load_state("networkidle")

        # 🚨 LOGIN FAIL CHECK
        if page.locator("text=Invalid System ID OR OTP!").count() > 0:
            context.close()
            return {
                "status": "error",
                "message": "Login failed - invalid or expired OTP"
            }

        # 🔽 SCROLL (important for loading CA section)
        for _ in range(6):
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(500)

        page.wait_for_timeout(2000)

        # 🔍 FIND ALL TABLES
        tables = page.locator("table").all()

        results = []

        # 🎯 LOOP THROUGH TABLES TO FIND CORRECT ONE
        for table in tables:
            text = table.inner_text()

            # identify CA table using headers
            if "Assignment 1" in text and "Assessment 1" in text:

                rows = table.locator("tbody tr").all()

                for row in rows:
                    cols = row.locator("td").all()

                    if len(cols) < 6:
                        continue

                    subject = cols[0].inner_text().strip()
                    a1 = cols[1].inner_text().strip()
                    ass1 = cols[2].inner_text().strip()
                    a2 = cols[3].inner_text().strip()
                    ass2 = cols[4].inner_text().strip()
                    total = cols[5].inner_text().strip()

                    results.append({
                        "subject": subject,
                        "assignment1": a1,
                        "assessment1": ass1,
                        "assignment2": a2,
                        "assessment2": ass2,
                        "total": total
                    })

                break  # ✅ stop after finding correct table

        context.close()

        # 🚨 NO DATA FOUND
        if not results:
            return {
                "status": "error",
                "message": "Results table not found"
            }

        return {
            "status": "success",
            "results": results
        }

    except Exception as e:
        context.close()
        return {"status": "error", "message": str(e)}
    
#subject attendance
def fetch_subject_attendance(system_id: str, otp: str):
    browser = get_browser()
    context = browser.new_context()
    page = context.new_page()

    try:
        # 🔐 LOGIN
        login(page, system_id, otp)
        page.wait_for_load_state("networkidle")

        # 🚨 LOGIN FAIL CHECK
        if page.locator("text=Invalid System ID OR OTP!").count() > 0:
            context.close()
            return {
                "status": "error",
                "message": "Login failed - invalid or expired OTP"
            }

        # 🧭 CORRECT PAGE
        page.goto("https://student.sharda.ac.in/admin/courses")
        page.wait_for_load_state("networkidle")
        # 🎯 SELECT CURRENT TERM (2502)
        try:
            tabs = page.locator("text=2502")

            if tabs.count() > 0:
                tabs.first.click()
                page.wait_for_timeout(2000)
        except:
            pass

        page.wait_for_selector("table")

        rows = page.locator("table tbody tr").all()

        data = []

        for row in rows:
            cols = row.locator("td").all()

            if len(cols) < 11:
                continue

            try:
                data.append({
                    "subject": cols[1].inner_text().strip(),
                    "code": cols[2].inner_text().strip(),
                    "faculty": cols[4].inner_text().strip(),
                    "delivered": cols[6].inner_text().strip(),
                    "attended": cols[7].inner_text().strip(),
                    "percentage": cols[10].inner_text().strip(),
                })
            except:
                continue

        context.close()

        if not data:
            return {
                "status": "error",
                "message": "No subject attendance data found"
            }

        return {
            "status": "success",
            "data": data
        }

    except Exception as e:
        context.close()
        return {"status": "error", "message": str(e)}
    