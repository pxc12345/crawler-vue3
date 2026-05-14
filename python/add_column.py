import pymysql

conn = pymysql.connect(
    host='localhost',
    port=3308,
    user='root',
    password='Pxc7890.',
    database='school_db'
)
cursor = conn.cursor()

cursor.execute("DESCRIBE students")
columns = [row[0] for row in cursor.fetchall()]
print("当前表结构:", columns)

if 'avatar_url' not in columns:
    cursor.execute("ALTER TABLE students ADD COLUMN avatar_url VARCHAR(500)")
    conn.commit()
    print("avatar_url 列已添加")
else:
    print("avatar_url 列已存在")

cursor.execute("DESCRIBE students")
for row in cursor.fetchall():
    print(row)

conn.close()