import pymysql
from datetime import datetime


class NotificationDB:
    def __init__(self):
        self.connection = pymysql.connect(
            host='localhost',
            port=3308,
            user='root',
            password='Pxc7890.',
            database='school_db',
            charset='utf8mb4'
        )
        self._init_db()

    def _init_db(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    email VARCHAR(255) UNIQUE,
                    phone VARCHAR(20) UNIQUE,
                    password_hash VARCHAR(255),
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verification_codes (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    code VARCHAR(10) NOT NULL,
                    code_type VARCHAR(20) NOT NULL,
                    target VARCHAR(255) NOT NULL,
                    expires_at DATETIME NOT NULL,
                    used TINYINT(1) DEFAULT 0,
                    created_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            self.connection.commit()

    def create_user(self, email=None, phone=None, password_hash=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (email, phone, password_hash, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                (email, phone, password_hash, now, now)
            )
            self.connection.commit()
            return cursor.lastrowid

    def get_user_by_email(self, email):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, email, phone, password_hash, created_at FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "phone": row[2],
                    "password_hash": row[3],
                    "created_at": row[4]
                }
            return None

    def get_user_by_phone(self, phone):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, email, phone, password_hash, created_at FROM users WHERE phone = %s", (phone,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "phone": row[2],
                    "password_hash": row[3],
                    "created_at": row[4]
                }
            return None

    def save_verification_code(self, user_id, code, code_type, target, expires_at):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO verification_codes (user_id, code, code_type, target, expires_at, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, code, code_type, target, expires_at, now)
            )
            self.connection.commit()
            return cursor.lastrowid

    def get_valid_code(self, user_id, code, code_type, target):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, code, code_type, target, expires_at, used
                FROM verification_codes
                WHERE user_id = %s AND code = %s AND code_type = %s AND target = %s AND used = 0
            """, (user_id, code, code_type, target))
            row = cursor.fetchone()
            if row:
                expires_at = row[5]
                if expires_at > datetime.now():
                    return {
                        "id": row[0],
                        "user_id": row[1],
                        "code": row[2],
                        "code_type": row[3],
                        "target": row[4],
                        "expires_at": row[5],
                        "used": row[6]
                    }
            return None

    def mark_code_used(self, code_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE verification_codes SET used = 1 WHERE id = %s",
                (code_id,)
            )
            self.connection.commit()

    def get_user_by_id(self, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, email, phone, password_hash, created_at FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "phone": row[2],
                    "password_hash": row[3],
                    "created_at": row[4]
                }
            return None


notification_db = NotificationDB()
