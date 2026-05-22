import pymysql
import os
from datetime import datetime


class AlertDB:
    """
    告警管理数据库操作层
    使用 PyMySQL 连接 MySQL，管理告警规则和告警记录
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
                    CREATE TABLE IF NOT EXISTS `alert_rules` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `name` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '规则名称',
                        `task_id` INT NOT NULL DEFAULT 0 COMMENT '关联任务ID, 0表示全局规则',
                        `type` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '告警类型: FAILED/TIMEOUT/DATA_ANOMALY/IP_BLOCKED',
                        `threshold` INT NOT NULL DEFAULT 0 COMMENT '触发阈值',
                        `enabled` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用: 1-启用, 0-禁用',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX `idx_task_id` (`task_id`),
                        INDEX `idx_type` (`type`),
                        INDEX `idx_enabled` (`enabled`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='告警规则表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `alert_records` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `task_id` INT NOT NULL DEFAULT 0 COMMENT '关联任务ID',
                        `rule_id` INT NOT NULL DEFAULT 0 COMMENT '关联规则ID',
                        `type` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '告警类型',
                        `message` VARCHAR(1000) NOT NULL DEFAULT '' COMMENT '告警消息',
                        `is_read` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已读: 1-已读, 0-未读',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX `idx_task_id` (`task_id`),
                        INDEX `idx_rule_id` (`rule_id`),
                        INDEX `idx_is_read` (`is_read`),
                        INDEX `idx_created_at` (`created_at`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='告警记录表'
                """)

            conn.commit()
            conn.close()
            return True
        except pymysql.Error as e:
            print(f"数据表创建失败: {e}")
            return False

    def connect(self):
        return self._ensure_table()

    def add_alert_rule(self, name, task_id=0, rule_type="", threshold=0, enabled=1):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO `alert_rules`
                    (`name`, `task_id`, `type`, `threshold`, `enabled`)
                    VALUES (%(name)s, %(task_id)s, %(type)s, %(threshold)s, %(enabled)s)
                """
                cursor.execute(sql, {
                    "name": name,
                    "task_id": task_id,
                    "type": rule_type,
                    "threshold": threshold,
                    "enabled": enabled,
                })
                rule_id = cursor.lastrowid
            conn.commit()
            return rule_id, None
        except pymysql.Error as e:
            return None, str(e)
        finally:
            if conn:
                conn.close()

    def get_alert_rules(self, task_id=None, enabled=None):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                conditions = []
                params = {}

                if task_id is not None:
                    conditions.append("`task_id` = %(task_id)s")
                    params["task_id"] = task_id

                if enabled is not None:
                    conditions.append("`enabled` = %(enabled)s")
                    params["enabled"] = enabled

                where = ""
                if conditions:
                    where = "WHERE " + " AND ".join(conditions)

                sql = "SELECT * FROM `alert_rules` {} ORDER BY `created_at` DESC".format(where)
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                for row in rows:
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                return rows
        except pymysql.Error as e:
            print(f"查询告警规则失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_alert_rule(self, rule_id, **kwargs):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                allowed_fields = ["name", "task_id", "type", "threshold", "enabled"]
                updates = []
                params = {"rule_id": rule_id}

                for field in allowed_fields:
                    if field in kwargs:
                        params[field] = kwargs[field]
                        updates.append("`{}` = %({})s".format(field, field))

                if not updates:
                    return False, "没有可更新的字段"

                sql = "UPDATE `alert_rules` SET {} WHERE `id` = %(rule_id)s".format(
                    ", ".join(updates)
                )
                cursor.execute(sql, params)
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def delete_alert_rule(self, rule_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM `alert_rules` WHERE `id` = %(rule_id)s",
                    {"rule_id": rule_id}
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def add_alert_record(self, task_id, rule_id, record_type, message):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO `alert_records`
                    (`task_id`, `rule_id`, `type`, `message`)
                    VALUES (%(task_id)s, %(rule_id)s, %(type)s, %(message)s)
                """
                cursor.execute(sql, {
                    "task_id": task_id,
                    "rule_id": rule_id,
                    "type": record_type,
                    "message": message,
                })
                record_id = cursor.lastrowid
            conn.commit()
            return record_id, None
        except pymysql.Error as e:
            return None, str(e)
        finally:
            if conn:
                conn.close()

    def get_alert_records(self, task_id=None, rule_id=None, record_type="", is_read=None,
                          page=1, page_size=20):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                conditions = []
                params = {}

                if task_id is not None:
                    conditions.append("`task_id` = %(task_id)s")
                    params["task_id"] = task_id

                if rule_id is not None:
                    conditions.append("`rule_id` = %(rule_id)s")
                    params["rule_id"] = rule_id

                if record_type:
                    conditions.append("`type` = %(type)s")
                    params["type"] = record_type

                if is_read is not None:
                    conditions.append("`is_read` = %(is_read)s")
                    params["is_read"] = is_read

                where = ""
                if conditions:
                    where = "WHERE " + " AND ".join(conditions)

                count_sql = "SELECT COUNT(*) AS total FROM `alert_records` {}".format(where)
                cursor.execute(count_sql, params)
                total = cursor.fetchone()["total"]

                offset = (page - 1) * page_size
                list_sql = (
                    "SELECT * FROM `alert_records` {} "
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
            print(f"查询告警记录失败: {e}")
            return [], 0
        finally:
            if conn:
                conn.close()

    def mark_as_read(self, record_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE `alert_records` SET `is_read` = 1 WHERE `id` = %(record_id)s",
                    {"record_id": record_id}
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_unread_count(self):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) AS total FROM `alert_records` WHERE `is_read` = 0"
                )
                return cursor.fetchone()["total"]
        except pymysql.Error as e:
            print(f"查询未读告警数失败: {e}")
            return 0
        finally:
            if conn:
                conn.close()


alert_db = AlertDB()