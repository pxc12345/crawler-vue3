import time
import pymysql
from datetime import datetime


class NotificationDB:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 3308,
            'user': 'root',
            'password': 'Pxc7890.',
            'database': 'school_db',
            'charset': 'utf8mb4'
        }
        self.connection = None
        self._connect()

    def _connect(self):
        try:
            if self.connection:
                self.connection.close()
            self.connection = pymysql.connect(**self.db_config)
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

    def _ensure_connection(self, retry_count=0, max_retries=3):
        try:
            if self.connection is None or not self.connection.open:
                self._connect()
            else:
                try:
                    self.connection.ping()
                except Exception:
                    self._connect()
        except Exception:
            if retry_count < max_retries:
                time.sleep(0.5 * (retry_count + 1))
                self._ensure_connection(retry_count + 1, max_retries)
            else:
                raise

    def _init_db(self):
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(100) UNIQUE,
                    email VARCHAR(255) UNIQUE,
                    phone VARCHAR(20) UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    login_attempts INT DEFAULT 0,
                    locked_until DATETIME,
                    last_login_at DATETIME,
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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS token_blacklist (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    token VARCHAR(500) NOT NULL UNIQUE,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_history (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    action VARCHAR(50) NOT NULL,
                    ip_address VARCHAR(50),
                    user_agent VARCHAR(255),
                    details TEXT,
                    created_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            self.connection.commit()

    def create_user(self, email=None, phone=None, password_hash=None):
        self._ensure_connection()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (email, phone, password_hash, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                (email, phone, password_hash, now, now)
            )
            self.connection.commit()
            return cursor.lastrowid

    def get_user_by_email(self, email):
        self._ensure_connection()
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
        self._ensure_connection()
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
        self._ensure_connection()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO verification_codes (user_id, code, code_type, target, expires_at, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, code, code_type, target, expires_at, now)
            )
            self.connection.commit()
            return cursor.lastrowid

    def get_valid_code(self, user_id, code, code_type, target):
        self._ensure_connection()
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
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE verification_codes SET used = 1 WHERE id = %s",
                (code_id,)
            )
            self.connection.commit()

    def get_user_by_id(self, user_id):
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email, phone, password_hash, login_attempts, locked_until, last_login_at, created_at FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "password_hash": row[4],
                    "login_attempts": row[5],
                    "locked_until": row[6],
                    "last_login_at": row[7],
                    "created_at": row[8]
                }
            return None

    def get_user_by_username(self, username):
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email, phone, password_hash, login_attempts, locked_until, last_login_at, created_at FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "password_hash": row[4],
                    "login_attempts": row[5],
                    "locked_until": row[6],
                    "last_login_at": row[7],
                    "created_at": row[8]
                }
            return None

    def get_user_by_email_or_username(self, identifier):
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, phone, password_hash, login_attempts, locked_until, last_login_at, created_at 
                FROM users 
                WHERE email = %s OR username = %s
            """, (identifier, identifier))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "password_hash": row[4],
                    "login_attempts": row[5],
                    "locked_until": row[6],
                    "last_login_at": row[7],
                    "created_at": row[8]
                }
            return None

    def update_user_password(self, user_id, password_hash):
        self._ensure_connection()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password_hash = %s, updated_at = %s WHERE id = %s",
                (password_hash, now, user_id)
            )
            self.connection.commit()

    def increment_login_attempts(self, user_id):
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET login_attempts = login_attempts + 1, updated_at = %s WHERE id = %s",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id)
            )
            self.connection.commit()

    def reset_login_attempts(self, user_id):
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET login_attempts = 0, locked_until = NULL, updated_at = %s WHERE id = %s",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id)
            )
            self.connection.commit()

    def lock_user(self, user_id, lock_until):
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET locked_until = %s, updated_at = %s WHERE id = %s",
                (lock_until.strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id)
            )
            self.connection.commit()

    def update_last_login(self, user_id):
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET last_login_at = %s, updated_at = %s WHERE id = %s",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id)
            )
            self.connection.commit()

    def add_token_to_blacklist(self, token, expires_at):
        self._ensure_connection()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO token_blacklist (token, expires_at, created_at) VALUES (%s, %s, %s)",
                (token, expires_at.strftime("%Y-%m-%d %H:%M:%S"), now)
            )
            self.connection.commit()

    def is_token_blacklisted(self, token):
        try:
            self._connect()  # 每次都创建新连接
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id FROM token_blacklist WHERE token = %s AND expires_at > %s", (token, datetime.now()))
                return cursor.fetchone() is not None
        except Exception:
            return False  # 出错时跳过检查，不阻止请求

    def add_password_history(self, user_id, password_hash):
        self._ensure_connection()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO password_history (user_id, password_hash, created_at) VALUES (%s, %s, %s)",
                (user_id, password_hash, now)
            )
            self.connection.commit()

    def get_password_history(self, user_id, limit=5):
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT password_hash FROM password_history 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (user_id, limit))
            return [row[0] for row in cursor.fetchall()]

    def add_audit_log(self, user_id, action, ip_address=None, user_agent=None, details=None):
        self._ensure_connection()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO audit_logs (user_id, action, ip_address, user_agent, details, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, action, ip_address, user_agent, details, now)
            )
            self.connection.commit()

    def create_user_with_username(self, username, email=None, phone=None, password_hash=None):
        self._ensure_connection()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, email, phone, password_hash, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (username, email, phone, password_hash, now, now)
            )
            self.connection.commit()
            return cursor.lastrowid


notification_db = NotificationDB()
