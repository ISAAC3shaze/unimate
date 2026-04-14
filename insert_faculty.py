import pandas as pd
import psycopg2

conn = psycopg2.connect("postgresql://postgres:JiYQPfttbblGtLQeNJDCHMCtcEadIxuV@maglev.proxy.rlwy.net:43060/railway")
cur = conn.cursor()

df = pd.read_csv("student_detail.csv")

for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO students (
            system_id, name, roll_no, course, section, email, specialization
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (system_id) DO NOTHING;
    """, (
        row["Student System ID"],
        row["Student Name"],
        row["Student Roll No."],
        row["Course"],
        row["Section"],
        row["Student Email ID"],
        row["Specialization"]
    ))

conn.commit()
cur.close()
conn.close()