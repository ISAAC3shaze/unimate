import psycopg2

# 🔴 Paste your FULL Railway connection URL here
conn = psycopg2.connect(
    "postgresql://postgres:JiYQPfttbblGtLQeNJDCHMCtcEadIxuV@maglev.proxy.rlwy.net:43060/railway"
)

cur = conn.cursor()

data = [
    (1, 'Dr. Subrata Sahana', 'Mon', '11:35:00', '12:25:00', '3', '108A'),
    (2, 'Dr. Subrata Sahana', 'Mon', '15:00:00', '15:50:00', '3', '308B'),
    (3, 'Dr. Subrata Sahana', 'Mon', '15:50:00', '16:40:00', '3', '308B'),
    (4, 'Dr. Subrata Sahana', 'Tue', '09:00:00', '09:50:00', '3', '311A'),
    (5, 'Dr. Subrata Sahana', 'Tue', '11:35:00', '12:25:00', '3', '308B')
]

cur.executemany("""
    INSERT INTO faculty_timetable
    (id, faculty_name, day_of_week, start_time, end_time, location_block, location_room)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
""", data)

conn.commit()
cur.close()
conn.close()

print("✅ Timetable inserted successfully")