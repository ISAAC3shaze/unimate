import psycopg2
import pandas as pd

conn = psycopg2.connect("postgresql://postgres:JiYQPfttbblGtLQeNJDCHMCtcEadIxuV@maglev.proxy.rlwy.net:43060/railway")
cur = conn.cursor()

df = pd.read_csv("Free_class_final.csv")

data = [tuple(row) for row in df.values]

cur.execute("DELETE FROM free_class;")

cur.executemany("""
    INSERT INTO free_class (room, day, start_time, end_time, status)
    VALUES (%s,%s,%s,%s,%s)
""", data)

conn.commit()
cur.close()
conn.close()

print("✅ Free class data inserted")