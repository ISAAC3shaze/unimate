import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres:JiYQPfttbblGtLQeNJDCHMCtcEadIxuV@maglev.proxy.rlwy.net:43060/railway"
)

cur = conn.cursor()

cur.execute("DROP TABLE faculty_timetable;")

conn.commit()
cur.close()
conn.close()

print("✅ Table dropped successfully")