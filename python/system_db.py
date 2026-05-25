import pymysql
import os
import json
from datetime import datetime


class SystemDB:
    """
    系统监控数据库操作层
    使用 PyMySQL 连接 MySQL，管理系统日志、设置和用户偏好
    """

    def __init__(self):
        self._config = {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": int(os.environ.get("DB_PORT", 3308)),
            "user": os.environ.get("DB_USER", "root"),
            "password": os.environ.get("DB_PASSWORD", "Pxc7890."),
            "database": os.environ.get("DB_NAME", "crawler_manager"),
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
        }
        self._ensure_database()

    def _get_connection(self):
        config = dict(self._config)
        config.pop("database", None)
        config["charset"] = "utf8mb4"
        config["cursorclass"] = pymysql.cursors.DictCursor
        return pymysql.connect(**config)

    def _ensure_database(self):
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "CREATE DATABASE IF NOT EXISTS `{}` "
                    "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(
                        self._config["database"]
                    )
                )
            conn.commit()
            conn.close()
        except pymysql.Error as e:
            print(f"数据库创建警告: {e}")

    def _ensure_table(self):
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `system_logs` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `level` VARCHAR(10) NOT NULL DEFAULT 'INFO' COMMENT '日志级别: INFO/WARNING/ERROR',
                        `source` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '日志来源',
                        `message` TEXT COMMENT '日志消息',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX `idx_level` (`level`),
                        INDEX `idx_source` (`source`),
                        INDEX `idx_created_at` (`created_at`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='系统日志表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `system_settings` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `key` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '设置键名',
                        `value` TEXT COMMENT '设置值',
                        `description` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '设置描述',
                        UNIQUE INDEX `idx_key` (`key`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='系统设置表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `user_preferences` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `user_id` INT NOT NULL DEFAULT 0 COMMENT '用户ID',
                        `theme` VARCHAR(20) NOT NULL DEFAULT 'light' COMMENT '主题: light/dark',
                        `notification_config` JSON COMMENT '通知配置JSON',
                        `export_path` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '导出路径',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        UNIQUE INDEX `idx_user_id` (`user_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='用户偏好设置表'
                """)

            conn.commit()
            conn.close()
            return True
        except pymysql.Error as e:
            print(f"数据表创建失败: {e}")
            return False

    def connect(self):
        return self._ensure_table()

    def add_log(self, level="INFO", source="", message="", task_id=None):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO `system_logs`
                    (`level`, `source`, `message`, `task_id`)
                    VALUES (%(level)s, %(source)s, %(message)s, %(task_id)s)
                """
                cursor.execute(sql, {
                    "level": level,
                    "source": source,
                    "message": message,
                    "task_id": task_id,
                })
                log_id = cursor.lastrowid
            conn.commit()
            return log_id, None
        except pymysql.Error as e:
            return None, str(e)
        finally:
            if conn:
                conn.close()

    def get_logs(self, level="", source="", task_id=None, page=1, page_size=50, user_id=None):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                conditions = []
                params = {}

                if level:
                    conditions.append("`level` = %(level)s")
                    params["level"] = level

                if source:
                    conditions.append("`source` = %(source)s")
                    params["source"] = source

                if task_id:
                    conditions.append("`task_id` = %(task_id)s")
                    params["task_id"] = task_id

                where = ""
                if conditions:
                    where = "WHERE " + " AND ".join(conditions)

                count_sql = "SELECT COUNT(*) AS total FROM `system_logs` {}".format(where)
                cursor.execute(count_sql, params)
                total = cursor.fetchone()["total"]

                offset = (page - 1) * page_size
                list_sql = (
                    "SELECT * FROM `system_logs` {} "
                    "ORDER BY `created_at` DESC "
                    "LIMIT %(limit)s OFFSET %(offset)s"
                ).format(where)
                params["limit"] = page_size
                params["offset"] = offset
                cursor.execute(list_sql, params)
                rows = cursor.fetchall()

                for row in rows:
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")

                return rows, total
        except pymysql.Error as e:
            print(f"查询系统日志失败: {e}")
            return [], 0
        finally:
            if conn:
                conn.close()

    def clear_logs(self):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE `system_logs`")
            conn.commit()
            return True, "所有日志已清空"
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_setting(self, key):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `system_settings` WHERE `key` = %(key)s",
                    {"key": key}
                )
                return cursor.fetchone()
        except pymysql.Error as e:
            print(f"查询系统设置失败: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def set_setting(self, key, value, description=""):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT `id` FROM `system_settings` WHERE `key` = %(key)s",
                    {"key": key}
                )
                existing = cursor.fetchone()
                if existing:
                    sql = """
                        UPDATE `system_settings`
                        SET `value` = %(value)s, `description` = %(description)s
                        WHERE `id` = %(id)s
                    """
                    cursor.execute(sql, {
                        "value": value,
                        "description": description,
                        "id": existing["id"],
                    })
                else:
                    sql = """
                        INSERT INTO `system_settings`
                        (`key`, `value`, `description`)
                        VALUES (%(key)s, %(value)s, %(description)s)
                    """
                    cursor.execute(sql, {
                        "key": key,
                        "value": value,
                        "description": description,
                    })
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_all_settings(self):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM `system_settings` ORDER BY `key`")
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"查询所有设置失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_user_preferences(self, user_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `user_preferences` WHERE `user_id` = %(user_id)s",
                    {"user_id": user_id}
                )
                return cursor.fetchone()
        except pymysql.Error as e:
            print(f"查询用户偏好失败: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def save_user_preferences(self, user_id, theme="light", notification_config=None, export_path=""):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT `id` FROM `user_preferences` WHERE `user_id` = %(user_id)s",
                    {"user_id": user_id}
                )
                existing = cursor.fetchone()
                if existing:
                    sql = """
                        UPDATE `user_preferences`
                        SET `theme` = %(theme)s,
                            `notification_config` = %(notification_config)s,
                            `export_path` = %(export_path)s
                        WHERE `id` = %(id)s
                    """
                    cursor.execute(sql, {
                        "theme": theme,
                        "notification_config": json.dumps(notification_config) if notification_config else None,
                        "export_path": export_path,
                        "id": existing["id"],
                    })
                else:
                    sql = """
                        INSERT INTO `user_preferences`
                        (`user_id`, `theme`, `notification_config`, `export_path`)
                        VALUES (%(user_id)s, %(theme)s, %(notification_config)s, %(export_path)s)
                    """
                    cursor.execute(sql, {
                        "user_id": user_id,
                        "theme": theme,
                        "notification_config": json.dumps(notification_config) if notification_config else None,
                        "export_path": export_path,
                    })
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()


system_db = SystemDB()