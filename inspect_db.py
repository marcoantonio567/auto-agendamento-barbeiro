import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
try:
    cursor.execute("PRAGMA table_info(tb_usuarios)")
    columns = cursor.fetchall()
    print("Columns in tb_usuarios:")
    for col in columns:
        print(col)
except Exception as e:
    print(e)
finally:
    conn.close()
