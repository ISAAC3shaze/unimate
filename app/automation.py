from playwright.sync_api import sync_playwright
from datetime import datetime

EZONE_URL = "https://student.sharda.ac.in/admin"


# ---------------- OTP TRIGGER ----------------
def trigger_otp(system_id: str):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            slow_mo=50
        )

        context = browser.new_context()
        page = context.new_page()

        page.goto(EZONE_URL)
        page.wait_for_load_state("networkidle")

        page.fill("#system_id", system_id)

        page.click("#send_stu_otp_email")

        browser.close()

        return True


# ---------------- ATTENDANCE ----------------
def fetch_attendance(system_id: str, otp: str):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            slow_mo=50
        )

        context = browser.new_context()
        page = context.new_page()

        page.goto(EZONE_URL)
        page.wait_for_load_state("networkidle")

        page.fill("#system_id", system_id)
        page.fill("#otp", otp)

        page.click("button:has-text('Login')")
        page.wait_for_load_state("networkidle")

        page.wait_for_selector("text=Total Attendance")

        attendance_card = page.locator("text=Total Attendance").locator("..").locator("..")

        summary_column = attendance_card.locator("div", has_text="Present").filter(
            has_text="Absent"
        ).first

        raw_text = summary_column.inner_text()

        lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

        attendance = {}

        for i in range(len(lines)):
            if "Total" in lines[i]:
                attendance["total"] = int(lines[i + 1])
            if "Present" in lines[i]:
                attendance["present"] = int(lines[i + 1])
            if "Absent" in lines[i]:
                attendance["absent"] = int(lines[i + 1])

        browser.close()

        return attendance


# ---------------- TODAY CLASSES ----------------
def fetch_today_classes(system_id: str, otp: str):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            slow_mo=50
        )

        context = browser.new_context()
        page = context.new_page()

        page.goto(EZONE_URL)
        page.wait_for_load_state("networkidle")

        page.fill("#system_id", system_id)
        page.fill("#otp", otp)

        page.click("button:has-text('Login')")
        page.wait_for_load_state("networkidle")

        page.wait_for_selector("text=Today's Class")
        
        if page.locator("text=Holiday").count() > 0:
            browser.close()
            return {"status": "holiday"}

        class_cards = page.locator("text=Block").locator("..")

        cards = class_cards.all()

        classes = []

        for card in cards:

            text = card.inner_text()

            lines = [l.strip() for l in text.split("\n") if l.strip()]

            if len(lines) < 3:
                continue

            time_range = lines[0]
            subject = lines[1]
            location = lines[2]
            faculty = lines[3] if len(lines) > 3 else ""

            start, end = time_range.split("-")

            classes.append({
                "start": start.strip(),
                "end": end.strip(),
                "subject": subject,
                "location": location,
                "faculty": faculty
            })

        browser.close()

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


# ---------------- ABSENTEE ALERT ----------------
def fetch_absentee_alert(system_id: str, otp: str):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            slow_mo=50
        )

        context = browser.new_context()
        page = context.new_page()

        page.goto(EZONE_URL)
        page.wait_for_load_state("networkidle")

        page.fill("#system_id", system_id)
        page.fill("#otp", otp)

        page.click("button:has-text('Login')")
        page.wait_for_load_state("networkidle")

        page.wait_for_selector("text=Absentee Alert")

        alert_block = page.locator("text=Absentee Alert").locator("..")

        text = alert_block.inner_text()

        browser.close()

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


# ---------------- HOLIDAYS ----------------
def fetch_holidays(system_id: str, otp: str):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            slow_mo=50
        )

        context = browser.new_context()
        page = context.new_page()

        page.goto(EZONE_URL)
        page.wait_for_load_state("networkidle")

        page.fill("#system_id", system_id)
        page.fill("#otp", otp)

        page.click("button:has-text('Login')")
        page.wait_for_load_state("networkidle")

        holiday_widget = page.locator(".studentbg").filter(has_text="Holiday").nth(2)

        text = holiday_widget.inner_text()

        browser.close()

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        holidays = []

        i = 1
        while i < len(lines):
            holidays.append({
                "name": lines[i],
                "date": lines[i + 1] if i + 1 < len(lines) else ""
            })
            i += 2

        return {
            "status": "success",
            "holidays": holidays
        }

