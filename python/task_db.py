import pymysql
import os
import json
from datetime import datetime

from db_settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET, DB_CA_PATH
from src.datetime_utils import now_utc_str


class TaskDB:
    """
    任务管理数据库操作层
    使用 PyMySQL 连接 MySQL，管理爬虫任务、模板、版本、收藏和调度配置
    """

    def __init__(self):
        self._config = {
            "host": os.environ.get("DB_HOST", DB_HOST),
            "port": int(os.environ.get("DB_PORT", DB_PORT)),
            "user": os.environ.get("DB_USER", DB_USER),
            "password": os.environ.get("DB_PASSWORD", DB_PASSWORD),
            "database": os.environ.get("DB_NAME", DB_NAME),
            "charset": DB_CHARSET,
            "ssl_ca": DB_CA_PATH,
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
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
                    CREATE TABLE IF NOT EXISTS `crawler_tasks` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `name` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '任务名称',
                        `target_url` VARCHAR(1000) NOT NULL DEFAULT '' COMMENT '目标URL',
                        `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '任务状态: RUNNING/PENDING/COMPLETED/FAILED',
                        `cron_expr` VARCHAR(100) NOT NULL DEFAULT '' COMMENT 'Cron表达式',
                        `concurrency` INT DEFAULT 1 COMMENT '并发数',
                        `interval_seconds` INT DEFAULT 0 COMMENT '任务间隔秒数',
                        `retry_count` INT DEFAULT 0 COMMENT '重试次数',
                        `retry_interval` INT DEFAULT 60 COMMENT '重试间隔秒数',
                        `proxy_group` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '代理组',
                        `alert_rules` JSON COMMENT '告警规则配置JSON',
                        `config` JSON COMMENT '任务配置JSON',
                        `user_id` INT DEFAULT 0 COMMENT '用户ID',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                        INDEX `idx_status` (`status`),
                        INDEX `idx_user_id` (`user_id`),
                        INDEX `idx_name` (`name`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='爬虫任务表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `task_templates` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `name` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '模板名称',
                        `description` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '模板描述',
                        `config` JSON COMMENT '模板配置JSON',
                        `user_id` INT DEFAULT 0 COMMENT '用户ID',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX `idx_user_id` (`user_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='任务模板表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `task_versions` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `task_id` INT NOT NULL DEFAULT 0 COMMENT '任务ID',
                        `version_index` INT NOT NULL DEFAULT 1 COMMENT '版本序号',
                        `config` JSON COMMENT '任务配置JSON',
                        `change_log` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '变更日志',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX `idx_task_id` (`task_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='任务版本表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `task_favorites` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `user_id` INT NOT NULL DEFAULT 0 COMMENT '用户ID',
                        `task_id` INT NOT NULL DEFAULT 0 COMMENT '任务ID',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX `idx_user_id` (`user_id`),
                        INDEX `idx_task_id` (`task_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='任务收藏表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `user_recent_tasks` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY,
                        `user_id` INT NOT NULL,
                        `task_id` INT NOT NULL,
                        `action` VARCHAR(50) NOT NULL DEFAULT 'view',
                        `used_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE KEY `uk_user_task` (`user_id`, `task_id`),
                        INDEX `idx_user_used` (`user_id`, `used_at`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                for col_def in [
                    ("execution_time", "DECIMAL(10,2) DEFAULT NULL COMMENT '执行耗时(秒)'"),
                    ("data_count", "INT DEFAULT 0 COMMENT '采集数据条数'"),
                    ("success_rate", "DECIMAL(5,2) DEFAULT NULL COMMENT '成功率(%)'"),
                    ("error_message", "TEXT COMMENT '错误信息'"),
                ]:
                    col_name = col_def[0]
                    cursor.execute("SHOW COLUMNS FROM `crawler_tasks` LIKE %(col)s", {"col": col_name})
                    if not cursor.fetchone():
                        cursor.execute(
                            "ALTER TABLE `crawler_tasks` ADD COLUMN `{}` {}".format(col_name, col_def[1])
                        )

                for col_def in [
                    ("category", "VARCHAR(50) NOT NULL DEFAULT 'general' COMMENT '模板分类'"),
                    ("is_favorite", "TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否常用模板'"),
                    ("use_count", "INT NOT NULL DEFAULT 0 COMMENT '使用次数'"),
                    ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'"),
                ]:
                    col_name = col_def[0]
                    cursor.execute("SHOW COLUMNS FROM `task_templates` LIKE %(col)s", {"col": col_name})
                    if not cursor.fetchone():
                        cursor.execute(
                            "ALTER TABLE `task_templates` ADD COLUMN `{}` {}".format(col_name, col_def[1])
                        )

            conn.commit()
            conn.close()
            return True
        except pymysql.Error as e:
            print(f"数据表创建失败: {e}")
            return False

    def connect(self):
        return self._ensure_table()

    def _normalize_task_row(self, row):
        """解析 config JSON 并统一状态字段"""
        if not row:
            return row
        config = row.get("config")
        if isinstance(config, str) and config.strip():
            try:
                row["config"] = json.loads(config)
            except (json.JSONDecodeError, TypeError):
                row["config"] = {}
        elif not isinstance(config, dict):
            row["config"] = {}
        status = (row.get("status") or "PENDING").upper()
        if status == "ERROR":
            status = "FAILED"
        row["status"] = status
        return row

    def get_task_list(self, page=1, page_size=20, keyword="", status=""):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                conditions = []
                params = {}

                if keyword:
                    conditions.append("`name` LIKE %(keyword)s")
                    params["keyword"] = "%{}%".format(keyword)

                if status:
                    conditions.append("`status` = %(status)s")
                    params["status"] = status

                where = ""
                if conditions:
                    where = "WHERE " + " AND ".join(conditions)

                count_sql = "SELECT COUNT(*) AS total FROM `crawler_tasks` t {}".format(where)
                cursor.execute(count_sql, params)
                total = cursor.fetchone()["total"]

                offset = (page - 1) * page_size
                list_sql = (
                    "SELECT t.* FROM `crawler_tasks` t {} "
                    "ORDER BY t.`updated_at` DESC "
                    "LIMIT %(limit)s OFFSET %(offset)s"
                ).format(where)
                params["limit"] = page_size
                params["offset"] = offset
                cursor.execute(list_sql, params)
                rows = cursor.fetchall()

                for row in rows:
                    self._normalize_task_row(row)

                return rows, total
        except pymysql.Error as e:
            print(f"查询任务列表失败: {e}")
            return [], 0
        finally:
            if conn:
                conn.close()

    def create_task(self, name, target_url, status="PENDING", cron_expr="", concurrency=1,
                    interval_seconds=0, retry_count=0, retry_interval=60, proxy_group="",
                    alert_rules=None, config=None, user_id=0):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO `crawler_tasks`
                    (`name`, `target_url`, `status`, `cron_expr`, `concurrency`,
                     `interval_seconds`, `retry_count`, `retry_interval`, `proxy_group`,
                     `alert_rules`, `config`, `user_id`)
                    VALUES (%(name)s, %(target_url)s, %(status)s, %(cron_expr)s, %(concurrency)s,
                            %(interval_seconds)s, %(retry_count)s, %(retry_interval)s, %(proxy_group)s,
                            %(alert_rules)s, %(config)s, %(user_id)s)
                """
                cursor.execute(sql, {
                    "name": name,
                    "target_url": target_url,
                    "status": status,
                    "cron_expr": cron_expr,
                    "concurrency": concurrency,
                    "interval_seconds": interval_seconds,
                    "retry_count": retry_count,
                    "retry_interval": retry_interval,
                    "proxy_group": proxy_group,
                    "alert_rules": json.dumps(alert_rules) if alert_rules else None,
                    "config": json.dumps(config) if config else None,
                    "user_id": user_id,
                })
                task_id = cursor.lastrowid
            conn.commit()
            return task_id, None
        except pymysql.Error as e:
            return None, str(e)
        finally:
            if conn:
                conn.close()

    def update_task(self, task_id, **kwargs):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                allowed_fields = [
                    "name", "target_url", "status", "cron_expr", "concurrency",
                    "interval_seconds", "retry_count", "retry_interval", "proxy_group",
                    "alert_rules", "config"
                ]
                updates = []
                params = {"task_id": task_id}

                for field in allowed_fields:
                    if field in kwargs:
                        if field in ("alert_rules", "config"):
                            params[field] = json.dumps(kwargs[field]) if kwargs[field] is not None else None
                        else:
                            params[field] = kwargs[field]
                        updates.append("`{}` = %({})s".format(field, field))

                if not updates:
                    return False, "没有可更新的字段"

                sql = "UPDATE `crawler_tasks` SET {} WHERE `id` = %(task_id)s".format(
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

    def delete_task(self, task_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM `crawler_tasks` WHERE `id` = %(task_id)s", {"task_id": task_id})
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_task_by_id(self, task_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `crawler_tasks` WHERE `id` = %(task_id)s",
                    {"task_id": task_id}
                )
                row = cursor.fetchone()
                if row:
                    self._normalize_task_row(row)
                return row
        except pymysql.Error as e:
            print(f"查询任务失败: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def _normalize_template_row(self, row):
        if not row:
            return row
        config = row.get("config")
        if isinstance(config, str) and config.strip():
            try:
                row["config"] = json.loads(config)
            except (json.JSONDecodeError, TypeError):
                row["config"] = {}
        elif not isinstance(config, dict):
            row["config"] = {}
        row["is_favorite"] = 1 if row.get("is_favorite") else 0
        row["use_count"] = int(row.get("use_count") or 0)
        row["category"] = row.get("category") or "general"
        return row

    def get_templates(self, user_id=0, category="", favorite_only=False):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                conditions = ["`user_id` = %(user_id)s"]
                params = {"user_id": user_id}
                if category:
                    conditions.append("`category` = %(category)s")
                    params["category"] = category
                if favorite_only:
                    conditions.append("`is_favorite` = 1")
                where = "WHERE " + " AND ".join(conditions)
                cursor.execute(
                    "SELECT * FROM `task_templates` {} "
                    "ORDER BY `is_favorite` DESC, `updated_at` DESC, `created_at` DESC".format(where),
                    params
                )
                rows = cursor.fetchall()
                for row in rows:
                    self._normalize_template_row(row)
                return rows
        except pymysql.Error as e:
            print(f"查询模板列表失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def create_template(self, name, description="", config=None, user_id=0, category="general", is_favorite=0):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO `task_templates`
                    (`name`, `description`, `config`, `user_id`, `category`, `is_favorite`)
                    VALUES (%(name)s, %(description)s, %(config)s, %(user_id)s, %(category)s, %(is_favorite)s)
                """
                cursor.execute(sql, {
                    "name": name,
                    "description": description,
                    "config": json.dumps(config, ensure_ascii=False) if config else None,
                    "user_id": user_id,
                    "category": category or "general",
                    "is_favorite": 1 if is_favorite else 0,
                })
                template_id = cursor.lastrowid
            conn.commit()
            return template_id, None
        except pymysql.Error as e:
            return None, str(e)
        finally:
            if conn:
                conn.close()

    def update_template(self, template_id, user_id=0, **kwargs):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT `id` FROM `task_templates` WHERE `id` = %(template_id)s AND `user_id` = %(user_id)s",
                    {"template_id": template_id, "user_id": user_id}
                )
                if not cursor.fetchone():
                    return False, "模板不存在"

                allowed_fields = ["name", "description", "config", "category", "is_favorite"]
                updates = []
                params = {"template_id": template_id, "user_id": user_id}
                for field in allowed_fields:
                    if field in kwargs:
                        value = kwargs[field]
                        if field == "config":
                            params[field] = json.dumps(value, ensure_ascii=False) if value is not None else None
                        elif field == "is_favorite":
                            params[field] = 1 if value else 0
                        else:
                            params[field] = value
                        updates.append("`{}` = %({})s".format(field, field))

                if not updates:
                    return False, "没有可更新的字段"

                sql = (
                    "UPDATE `task_templates` SET {} "
                    "WHERE `id` = %(template_id)s AND `user_id` = %(user_id)s"
                ).format(", ".join(updates))
                cursor.execute(sql, params)
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def delete_template(self, template_id, user_id=0):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM `task_templates` WHERE `id` = %(template_id)s AND `user_id` = %(user_id)s",
                    {"template_id": template_id, "user_id": user_id}
                )
                if cursor.rowcount == 0:
                    return False, "模板不存在"
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_template_by_id(self, template_id, user_id=0):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                if user_id:
                    cursor.execute(
                        "SELECT * FROM `task_templates` WHERE `id` = %(template_id)s AND `user_id` = %(user_id)s",
                        {"template_id": template_id, "user_id": user_id}
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM `task_templates` WHERE `id` = %(template_id)s",
                        {"template_id": template_id}
                    )
                row = cursor.fetchone()
                if row:
                    self._normalize_template_row(row)
                return row
        except pymysql.Error as e:
            print(f"查询模板失败: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def increment_template_use_count(self, template_id, user_id=0):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE `task_templates` SET `use_count` = `use_count` + 1 "
                    "WHERE `id` = %(template_id)s AND `user_id` = %(user_id)s",
                    {"template_id": template_id, "user_id": user_id}
                )
                if cursor.rowcount == 0:
                    return False, "模板不存在"
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    EXECUTION_LOG_PREFIX = "执行结果:"

    def save_task_version(self, task_id, config, change_log=""):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COALESCE(MAX(`version_index`), 0) AS max_index FROM `task_versions` WHERE `task_id` = %(task_id)s",
                    {"task_id": task_id}
                )
                row = cursor.fetchone()
                version_index = row["max_index"] + 1

                sql = """
                    INSERT INTO `task_versions`
                    (`task_id`, `version_index`, `config`, `change_log`)
                    VALUES (%(task_id)s, %(version_index)s, %(config)s, %(change_log)s)
                """
                cursor.execute(sql, {
                    "task_id": task_id,
                    "version_index": version_index,
                    "config": json.dumps(config) if config else None,
                    "change_log": change_log,
                })
                version_id = cursor.lastrowid
            conn.commit()
            return version_id, version_index, None
        except pymysql.Error as e:
            return None, None, str(e)
        finally:
            if conn:
                conn.close()

    def save_execution_record(self, task_id, config, status, data_count):
        """仅任务启动并跑完后写入，与编辑配置无关"""
        change_log = "{}{}, 数据: {}条".format(
            self.EXECUTION_LOG_PREFIX, status, data_count
        )
        return self.save_task_version(task_id, config, change_log)

    def _normalize_version_rows(self, rows):
        for row in rows:
            cfg = row.get("config")
            if isinstance(cfg, str) and cfg.strip():
                try:
                    row["config"] = json.loads(cfg)
                except (json.JSONDecodeError, TypeError):
                    row["config"] = {}
            elif not isinstance(cfg, dict):
                row["config"] = {}
            row["record_type"] = (
                "execution"
                if (row.get("change_log") or "").strip().startswith(self.EXECUTION_LOG_PREFIX)
                else "config"
            )
        return rows

    def get_task_executions(self, task_id):
        """只返回「点击启动」产生的执行记录，不含编辑配置产生的版本"""
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `task_versions` WHERE `task_id` = %(task_id)s "
                    "AND `change_log` LIKE %(prefix)s "
                    "ORDER BY `version_index` DESC",
                    {"task_id": task_id, "prefix": self.EXECUTION_LOG_PREFIX + "%"},
                )
                rows = cursor.fetchall()
                return self._normalize_version_rows(rows)
        except pymysql.Error as e:
            print(f"查询任务执行记录失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_task_versions(self, task_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `task_versions` WHERE `task_id` = %(task_id)s ORDER BY `version_index` DESC",
                    {"task_id": task_id}
                )
                rows = cursor.fetchall()
                return self._normalize_version_rows(rows)
        except pymysql.Error as e:
            print(f"查询任务版本列表失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def rollback_version(self, task_id, version_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `task_versions` WHERE `id` = %(version_id)s AND `task_id` = %(task_id)s",
                    {"version_id": version_id, "task_id": task_id}
                )
                version = cursor.fetchone()
                if not version:
                    return False, "版本不存在"

                config = version.get("config")
                cursor.execute(
                    "UPDATE `crawler_tasks` SET `config` = %(config)s WHERE `id` = %(task_id)s",
                    {"config": json.dumps(config) if isinstance(config, dict) else config, "task_id": task_id}
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def add_favorite(self, user_id, task_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT `id` FROM `task_favorites` WHERE `user_id` = %(user_id)s AND `task_id` = %(task_id)s",
                    {"user_id": user_id, "task_id": task_id}
                )
                if cursor.fetchone():
                    return True, None

                sql = """
                    INSERT INTO `task_favorites`
                    (`user_id`, `task_id`)
                    VALUES (%(user_id)s, %(task_id)s)
                """
                cursor.execute(sql, {"user_id": user_id, "task_id": task_id})
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def remove_favorite(self, user_id, task_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM `task_favorites` WHERE `user_id` = %(user_id)s AND `task_id` = %(task_id)s",
                    {"user_id": user_id, "task_id": task_id}
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_favorites(self, user_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                sql = """
                    SELECT t.* FROM `crawler_tasks` t
                    INNER JOIN `task_favorites` f ON t.`id` = f.`task_id`
                    WHERE f.`user_id` = %(user_id)s
                    ORDER BY f.`created_at` DESC
                """
                cursor.execute(sql, {"user_id": user_id})
                rows = cursor.fetchall()
                return rows
        except pymysql.Error as e:
            print(f"查询收藏任务失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def count_by_user(self, user_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) AS total FROM `crawler_tasks` WHERE `user_id`=%(uid)s OR `user_id`=0",
                    {"uid": user_id},
                )
                return cursor.fetchone()["total"]
        except pymysql.Error:
            return 0
        finally:
            if conn:
                conn.close()

    def touch_recent_task(self, user_id, task_id, action="view"):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO `user_recent_tasks` (`user_id`, `task_id`, `action`)
                    VALUES (%(user_id)s, %(task_id)s, %(action)s)
                    ON DUPLICATE KEY UPDATE `used_at`=NOW(), `action`=VALUES(`action`)
                    """,
                    {"user_id": user_id, "task_id": task_id, "action": action},
                )
            conn.commit()
            return True
        except pymysql.Error as e:
            print(f"记录最近任务失败: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_recent_tasks(self, user_id, limit=10):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT t.*, r.`used_at`, r.`action` AS last_action
                    FROM `user_recent_tasks` r
                    INNER JOIN `crawler_tasks` t ON t.`id` = r.`task_id`
                    WHERE r.`user_id` = %(user_id)s
                    ORDER BY r.`used_at` DESC
                    LIMIT %(limit)s
                    """,
                    {"user_id": user_id, "limit": limit},
                )
                rows = cursor.fetchall()
                for row in rows:
                    format_row_datetimes(row, "used_at", "updated_at", "created_at")
                return rows
        except pymysql.Error as e:
            print(f"查询最近任务失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_task_status(self, task_id, status):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE `crawler_tasks` SET `status` = %(status)s WHERE `id` = %(task_id)s",
                    {"status": status, "task_id": task_id}
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def update_task_stats(self, task_id, execution_time, data_count, success_rate, error_message=''):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE `crawler_tasks` SET `execution_time` = %(execution_time)s, "
                    "`data_count` = %(data_count)s, `success_rate` = %(success_rate)s, "
                    "`error_message` = %(error_message)s WHERE `id` = %(task_id)s",
                    {"execution_time": execution_time, "data_count": data_count, "success_rate": success_rate, "error_message": error_message, "task_id": task_id}
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_count_by_status(self, status):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) AS total FROM `crawler_tasks` WHERE `status` = %(status)s",
                    {"status": status}
                )
                return cursor.fetchone()["total"]
        except pymysql.Error:
            return 0
        finally:
            if conn:
                conn.close()

    def set_all_failed_to_pending(self):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE `crawler_tasks` SET `status` = 'pending' WHERE `status` = 'failed'"
                )
                affected = cursor.rowcount
            conn.commit()
            return affected, None
        except pymysql.Error as e:
            return 0, str(e)
        finally:
            if conn:
                conn.close()

    def get_task_list_with_favorites(self, user_id, status="", keyword="", page=1, page_size=20):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                conditions = []
                params = {"user_id": user_id}

                conditions.append("(t.`user_id` = %(user_id)s OR t.`user_id` = 0)")

                if keyword:
                    conditions.append("(`name` LIKE %(keyword)s OR `target_url` LIKE %(keyword)s)")
                    params["keyword"] = "%{}%".format(keyword)

                if status:
                    conditions.append("`status` = %(status)s")
                    params["status"] = status.upper()

                where = ""
                if conditions:
                    where = "WHERE " + " AND ".join(conditions)

                count_sql = "SELECT COUNT(*) AS total FROM `crawler_tasks` t {}".format(where)
                cursor.execute(count_sql, params)
                total = cursor.fetchone()["total"]

                offset = (page - 1) * page_size
                list_sql = (
                    "SELECT t.*, "
                    "CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END AS is_favorite "
                    "FROM `crawler_tasks` t "
                    "LEFT JOIN `task_favorites` f ON t.`id` = f.`task_id` AND f.`user_id` = %(user_id)s "
                    "{} "
                    "ORDER BY t.`updated_at` DESC "
                    "LIMIT %(limit)s OFFSET %(offset)s"
                ).format(where)
                params["limit"] = page_size
                params["offset"] = offset
                cursor.execute(list_sql, params)
                rows = cursor.fetchall()

                for row in rows:
                    self._normalize_task_row(row)

                return rows, total
        except pymysql.Error as e:
            print(f"查询任务列表失败: {e}")
            return [], 0
        finally:
            if conn:
                conn.close()

    def get_list(self, user_id=0, status="", keyword="", page=1, page_size=20):
        return self.get_task_list_with_favorites(
            user_id=user_id, status=status, keyword=keyword,
            page=page, page_size=page_size
        )

    def clone_task_for_run(self, task_id, user_id=0, run_label=None):
        """基于已有任务克隆一条新的运行记录（每次点击运行创建新任务）。"""
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `crawler_tasks` WHERE `id` = %(task_id)s",
                    {"task_id": task_id},
                )
                source = cursor.fetchone()
            if not source:
                return None, "任务不存在"

            source_uid = int(source.get("user_id") or 0)
            req_uid = int(user_id or 0)
            if req_uid and source_uid not in (0, req_uid):
                return None, "无权操作此任务"

            config = source.get("config")
            if isinstance(config, str) and config.strip():
                try:
                    config = json.loads(config)
                except (json.JSONDecodeError, TypeError):
                    config = {}
            elif not isinstance(config, dict):
                config = {}
            config = dict(config)
            config.pop("_last_execution", None)
            config["last_run_started_at"] = now_utc_str()
            config["source_task_id"] = int(task_id)

            base_name = (source.get("name") or "任务").strip()
            if " · " in base_name:
                base_name = base_name.rsplit(" · ", 1)[0]
            label = run_label or now_utc_str()
            new_name = "{} · {}".format(base_name, label)

            alert_rules = source.get("alert_rules")
            if isinstance(alert_rules, str) and alert_rules.strip():
                try:
                    alert_rules = json.loads(alert_rules)
                except (json.JSONDecodeError, TypeError):
                    alert_rules = None

            owner_id = req_uid if req_uid else source_uid
            return self.create_task(
                name=new_name,
                target_url=source.get("target_url", ""),
                status="PENDING",
                cron_expr=source.get("cron_expr", ""),
                concurrency=source.get("concurrency", 1) or 1,
                interval_seconds=source.get("interval_seconds", 0) or 0,
                retry_count=source.get("retry_count", 0) or 0,
                retry_interval=source.get("retry_interval", 60) or 60,
                proxy_group=source.get("proxy_group", ""),
                alert_rules=alert_rules,
                config=config,
                user_id=owner_id,
            )
        except pymysql.Error as e:
            return None, str(e)
        finally:
            if conn:
                conn.close()

    def get_by_id(self, task_id, user_id=0):
        return self.get_task_by_id(task_id)

    def start_task(self, task_id, user_id=0):
        task = self.get_task_by_id(task_id)
        if not task:
            return False, "任务不存在"
        if task.get("status", "").upper() == "RUNNING":
            return True, "任务已在运行中"
        return self.update_task_status(task_id, "RUNNING")

    def stop_task(self, task_id, user_id=0):
        task = self.get_task_by_id(task_id)
        if not task:
            return False, "任务不存在"
        if task.get("status", "").upper() != "RUNNING":
            return True, "任务未在运行"
        return self.update_task_status(task_id, "PENDING")

    def create(self, user_id=0, name="", task_type="", config=None, description="", template_id=None):
        target_url = ""
        if isinstance(config, dict):
            target_url = config.get("target_url", "")
        task_id, err = self.create_task(
            name=name,
            target_url=target_url,
            config=config,
            user_id=user_id
        )
        if err:
            return None
        return task_id

    def update(self, task_id, user_id=0, **kwargs):
        return self.update_task(task_id, **kwargs)

    def delete(self, task_id, user_id=0):
        return self.delete_task(task_id)

    def get_versions(self, task_id, user_id=0):
        return self.get_task_versions(task_id)

    def rollback_version(self, task_id, version_id, user_id=0):
        return self.rollback_version(task_id, version_id)


task_db = TaskDB()