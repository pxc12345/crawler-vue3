import pymysql
from datetime import datetime


class StudentDB:
    def __init__(self):
        self.connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='Pxc7890.',
            database='school_db',
            charset='utf8mb4'
        )
        self._init_db()

    def _init_db(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    grade DOUBLE NOT NULL,
                    create_time DATETIME,
                    update_time DATETIME
                )
            """)
            self.connection.commit()

    def create(self, name, age, grade):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO students (name, age, grade, create_time, update_time) VALUES (%s, %s, %s, %s, %s)",
                (name, age, grade, now, now)
            )
            self.connection.commit()
            return cursor.lastrowid

    def get_all(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, name, age, grade FROM students")
            rows = cursor.fetchall()
            return [{
                "student_id": row[0],
                "name": row[1],
                "age": row[2],
                "grade": row[3]
            } for row in rows]

    def get_by_id(self, student_id):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, name, age, grade FROM students WHERE id = %s", (student_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "student_id": row[0],
                    "name": row[1],
                    "age": row[2],
                    "grade": row[3]
                }
            return None

    def get_by_name(self, name):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, name, age, grade FROM students WHERE name LIKE %s", (f"%{name}%",))
            rows = cursor.fetchall()
            return [{
                "student_id": row[0],
                "name": row[1],
                "age": row[2],
                "grade": row[3]
            } for row in rows]

    def update(self, student_id, name=None, age=None, grade=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if age is not None:
            updates.append("age = %s")
            params.append(age)
        if grade is not None:
            updates.append("grade = %s")
            params.append(grade)

        if updates:
            updates.append("update_time = %s")
            params.append(now)
            params.append(student_id)

            with self.connection.cursor() as cursor:
                sql = f"UPDATE students SET {', '.join(updates)} WHERE id = %s"
                cursor.execute(sql, params)
                self.connection.commit()
                return cursor.rowcount > 0
        return False

    def delete(self, student_id):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            self.connection.commit()
            return cursor.rowcount > 0

    def delete_batch(self, student_ids):
        with self.connection.cursor() as cursor:
            placeholders = ",".join("%s" * len(student_ids))
            cursor.execute(f"DELETE FROM students WHERE id IN ({placeholders})", student_ids)
            self.connection.commit()
            return cursor.rowcount

    def exists(self, student_id):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM students WHERE id = %s", (student_id,))
            return cursor.fetchone() is not None

    def count(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM students")
            return cursor.fetchone()[0]

    def close(self):
        self.connection.close()


class StudentModel:
    def __init__(self, student_id, name, age, grade):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "grade": self.grade
        }


class StudentService:
    def __init__(self):
        self.db = StudentDB()

    def create_student(self, name, age, grade):
        if not name or len(name.strip()) == 0:
            raise ValueError("姓名不能为空")
        if age < 1 or age > 150:
            raise ValueError("年龄必须在1-150之间")
        if grade < 0 or grade > 100:
            raise ValueError("成绩必须在0-100之间")

        student_id = self.db.create(name, age, grade)
        return StudentModel(student_id, name, age, grade)

    def get_all_students(self):
        rows = self.db.get_all()
        return [StudentModel(row["student_id"], row["name"], row["age"], row["grade"]) for row in rows]

    def get_student_by_id(self, student_id):
        row = self.db.get_by_id(student_id)
        if not row:
            raise ValueError(f"学生ID {student_id} 不存在")
        return StudentModel(row["student_id"], row["name"], row["age"], row["grade"])

    def search_by_name(self, name):
        rows = self.db.get_by_name(name)
        return [StudentModel(row["student_id"], row["name"], row["age"], row["grade"]) for row in rows]

    def update_student(self, student_id, name=None, age=None, grade=None):
        if name is not None and len(name.strip()) == 0:
            raise ValueError("姓名不能为空")
        if age is not None and (age < 1 or age > 150):
            raise ValueError("年龄必须在1-150之间")
        if grade is not None and (grade < 0 or grade > 100):
            raise ValueError("成绩必须在0-100之间")

        if not self.db.exists(student_id):
            raise ValueError(f"学生ID {student_id} 不存在")

        self.db.update(student_id, name, age, grade)
        return self.get_student_by_id(student_id)

    def delete_student(self, student_id):
        if not self.db.exists(student_id):
            raise ValueError(f"学生ID {student_id} 不存在")
        self.db.delete(student_id)
        return True

    def batch_delete_students(self, student_ids):
        existing = [sid for sid in student_ids if self.db.exists(sid)]
        if not existing:
            raise ValueError("没有找到要删除的学生")
        return self.db.delete_batch(existing)

    def get_statistics(self):
        students = self.get_all_students()
        if not students:
            return {
                "total": 0,
                "average_age": 0,
                "average_grade": 0,
                "highest_grade": None,
                "lowest_grade": None
            }

        ages = [s.age for s in students]
        grades = [s.grade for s in students]

        return {
            "total": len(students),
            "average_age": sum(ages) / len(ages),
            "average_grade": sum(grades) / len(grades),
            "highest_grade": max(grades),
            "lowest_grade": min(grades)
        }


student_service = StudentService()