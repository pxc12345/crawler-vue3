import pymysql
import os
import json
from datetime import datetime


class TaskDB:
    """
    任务管理数据库操作层
    使用 PyMySQL 连接 MySQL，管理爬虫任务、模板、版本、收藏和调度配置
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

            conn.commit()
            conn.close()
            return True
        except pymysql.Error as e:
            print(f"数据表创建失败: {e}")
            return False

    def connect(self):
        return self._ensure_table()

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
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                    if row.get("updated_at"):
                        row["updated_at"] = row["updated_at"].strftime("%Y-%m-%d %H:%M:%S")

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
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                    if row.get("updated_at"):
                        row["updated_at"] = row["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
                return row
        except pymysql.Error as e:
            print(f"查询任务失败: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_templates(self, user_id=0):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `task_templates` WHERE `user_id` = %(user_id)s ORDER BY `created_at` DESC",
                    {"user_id": user_id}
                )
                rows = cursor.fetchall()
                for row in rows:
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                return rows
        except pymysql.Error as e:
            print(f"查询模板列表失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def create_template(self, name, description="", config=None, user_id=0):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO `task_templates`
                    (`name`, `description`, `config`, `user_id`)
                    VALUES (%(name)s, %(description)s, %(config)s, %(user_id)s)
                """
                cursor.execute(sql, {
                    "name": name,
                    "description": description,
                    "config": json.dumps(config) if config else None,
                    "user_id": user_id,
                })
                template_id = cursor.lastrowid
            conn.commit()
            return template_id, None
        except pymysql.Error as e:
            return None, str(e)
        finally:
            if conn:
                conn.close()

    def delete_template(self, template_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM `task_templates` WHERE `id` = %(template_id)s",
                    {"template_id": template_id}
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_template_by_id(self, template_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `task_templates` WHERE `id` = %(template_id)s",
                    {"template_id": template_id}
                )
                row = cursor.fetchone()
                if row and row.get("created_at"):
                    row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                return row
        except pymysql.Error as e:
            print(f"查询模板失败: {e}")
            return None
        finally:
            if conn:
                conn.close()

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
                for row in rows:
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                return rows
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
                for row in rows:
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                    if row.get("updated_at"):
                        row["updated_at"] = row["updated_at"].strftime("%Y-%m-%d %H:%M:%S")
                return rows
        except pymysql.Error as e:
            print(f"查询收藏任务失败: {e}")
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

                conditions.append("t.`user_id` = %(user_id)s")

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
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                    if row.get("updated_at"):
                        row["updated_at"] = row["updated_at"].strftime("%Y-%m-%d %H:%M:%S")

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