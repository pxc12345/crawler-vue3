import pymysql
import os
from datetime import datetime


class ProxyDB:
    """
    代理池数据库操作层
    使用 PyMySQL 连接 MySQL，管理代理IP、分组、黑白名单和速率限制
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
                    CREATE TABLE IF NOT EXISTS `proxy_pool` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `ip` VARCHAR(45) NOT NULL DEFAULT '' COMMENT '代理IP地址',
                        `port` INT NOT NULL DEFAULT 0 COMMENT '代理端口',
                        `protocol` VARCHAR(10) NOT NULL DEFAULT 'http' COMMENT '代理协议',
                        `status` VARCHAR(20) NOT NULL DEFAULT 'ONLINE' COMMENT '代理状态: ONLINE/OFFLINE',
                        `success_rate` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '成功率',
                        `alive_seconds` INT NOT NULL DEFAULT 0 COMMENT '存活时长(秒)',
                        `last_check_at` DATETIME COMMENT '最后检测时间',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX `idx_status` (`status`),
                        INDEX `idx_protocol` (`protocol`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='代理池表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `proxy_groups` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `name` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '分组名称',
                        `description` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '分组描述',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='代理分组表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `proxy_group_mapping` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `group_id` INT NOT NULL DEFAULT 0 COMMENT '分组ID',
                        `proxy_id` INT NOT NULL DEFAULT 0 COMMENT '代理ID',
                        INDEX `idx_group_id` (`group_id`),
                        INDEX `idx_proxy_id` (`proxy_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='代理分组映射表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `site_blacklist` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `url` VARCHAR(1000) NOT NULL DEFAULT '' COMMENT '黑名单URL',
                        `reason` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '拉黑原因',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX `idx_url` (`url`(255))
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='站点黑名单表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `site_whitelist` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `url` VARCHAR(1000) NOT NULL DEFAULT '' COMMENT '白名单URL',
                        `reason` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '加入原因',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX `idx_url` (`url`(255))
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='站点白名单表'
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `rate_limit_config` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `task_id` INT DEFAULT NULL COMMENT '关联任务ID, NULL表示全局配置',
                        `requests_per_minute` INT NOT NULL DEFAULT 60 COMMENT '每分钟请求数',
                        `concurrent_max` INT NOT NULL DEFAULT 10 COMMENT '最大并发数',
                        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX `idx_task_id` (`task_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='速率限制配置表'
                """)

            conn.commit()
            conn.close()
            return True
        except pymysql.Error as e:
            print(f"数据表创建失败: {e}")
            return False

    def connect(self):
        return self._ensure_table()

    def get_proxies(self, status=None, protocol=""):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                conditions = []
                params = {}

                if status:
                    conditions.append("`status` = %(status)s")
                    params["status"] = status

                if protocol:
                    conditions.append("`protocol` = %(protocol)s")
                    params["protocol"] = protocol

                where = ""
                if conditions:
                    where = "WHERE " + " AND ".join(conditions)

                sql = "SELECT * FROM `proxy_pool` {} ORDER BY `created_at` DESC".format(where)
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                for row in rows:
                    if row.get("last_check_at"):
                        row["last_check_at"] = row["last_check_at"].strftime("%Y-%m-%d %H:%M:%S")
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                return rows
        except pymysql.Error as e:
            print(f"查询代理失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def add_proxy(self, ip, port, protocol="http"):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT `id` FROM `proxy_pool` WHERE `ip` = %(ip)s AND `port` = %(port)s",
                    {"ip": ip, "port": port}
                )
                existing = cursor.fetchone()
                if existing:
                    return existing["id"], None

                sql = """
                    INSERT INTO `proxy_pool`
                    (`ip`, `port`, `protocol`)
                    VALUES (%(ip)s, %(port)s, %(protocol)s)
                """
                cursor.execute(sql, {
                    "ip": ip,
                    "port": port,
                    "protocol": protocol,
                })
                proxy_id = cursor.lastrowid
            conn.commit()
            return proxy_id, None
        except pymysql.Error as e:
            return None, str(e)
        finally:
            if conn:
                conn.close()

    def delete_proxy(self, proxy_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM `proxy_pool` WHERE `id` = %(proxy_id)s",
                    {"proxy_id": proxy_id}
                )
                cursor.execute(
                    "DELETE FROM `proxy_group_mapping` WHERE `proxy_id` = %(proxy_id)s",
                    {"proxy_id": proxy_id}
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def refresh_proxy(self, proxy_id, status, success_rate=0.0, alive_seconds=0):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE `proxy_pool`
                       SET `status` = %(status)s,
                           `success_rate` = %(success_rate)s,
                           `alive_seconds` = %(alive_seconds)s,
                           `last_check_at` = NOW()
                       WHERE `id` = %(proxy_id)s""",
                    {
                        "proxy_id": proxy_id,
                        "status": status,
                        "success_rate": success_rate,
                        "alive_seconds": alive_seconds,
                    }
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_proxy_groups(self):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `proxy_groups` ORDER BY `created_at` DESC"
                )
                rows = cursor.fetchall()
                for row in rows:
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                return rows
        except pymysql.Error as e:
            print(f"查询代理分组失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def create_proxy_group(self, name, description=""):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO `proxy_groups`
                    (`name`, `description`)
                    VALUES (%(name)s, %(description)s)
                """
                cursor.execute(sql, {
                    "name": name,
                    "description": description,
                })
                group_id = cursor.lastrowid
            conn.commit()
            return group_id, None
        except pymysql.Error as e:
            return None, str(e)
        finally:
            if conn:
                conn.close()

    def assign_proxy_to_group(self, group_id, proxy_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT `id` FROM `proxy_group_mapping` WHERE `group_id` = %(group_id)s AND `proxy_id` = %(proxy_id)s",
                    {"group_id": group_id, "proxy_id": proxy_id}
                )
                if cursor.fetchone():
                    return True, None

                sql = """
                    INSERT INTO `proxy_group_mapping`
                    (`group_id`, `proxy_id`)
                    VALUES (%(group_id)s, %(proxy_id)s)
                """
                cursor.execute(sql, {"group_id": group_id, "proxy_id": proxy_id})
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_blacklist(self):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `site_blacklist` ORDER BY `created_at` DESC"
                )
                rows = cursor.fetchall()
                for row in rows:
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                return rows
        except pymysql.Error as e:
            print(f"查询黑名单失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def add_blacklist(self, url, reason=""):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT `id` FROM `site_blacklist` WHERE `url` = %(url)s",
                    {"url": url}
                )
                if cursor.fetchone():
                    return True, None

                sql = """
                    INSERT INTO `site_blacklist`
                    (`url`, `reason`)
                    VALUES (%(url)s, %(reason)s)
                """
                cursor.execute(sql, {"url": url, "reason": reason})
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def remove_blacklist(self, blacklist_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM `site_blacklist` WHERE `id` = %(id)s",
                    {"id": blacklist_id}
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_whitelist(self):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `site_whitelist` ORDER BY `created_at` DESC"
                )
                rows = cursor.fetchall()
                for row in rows:
                    if row.get("created_at"):
                        row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                return rows
        except pymysql.Error as e:
            print(f"查询白名单失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def add_whitelist(self, url, reason=""):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT `id` FROM `site_whitelist` WHERE `url` = %(url)s",
                    {"url": url}
                )
                if cursor.fetchone():
                    return True, None

                sql = """
                    INSERT INTO `site_whitelist`
                    (`url`, `reason`)
                    VALUES (%(url)s, %(reason)s)
                """
                cursor.execute(sql, {"url": url, "reason": reason})
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def remove_whitelist(self, whitelist_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM `site_whitelist` WHERE `id` = %(id)s",
                    {"id": whitelist_id}
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_rate_limit(self, task_id=None):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                if task_id is not None:
                    cursor.execute(
                        "SELECT * FROM `rate_limit_config` WHERE `task_id` = %(task_id)s ORDER BY `created_at` DESC LIMIT 1",
                        {"task_id": task_id}
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM `rate_limit_config` WHERE `task_id` IS NULL ORDER BY `created_at` DESC LIMIT 1"
                    )
                row = cursor.fetchone()
                if row and row.get("created_at"):
                    row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                return row
        except pymysql.Error as e:
            print(f"查询速率限制失败: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def set_rate_limit(self, requests_per_minute=60, concurrent_max=10, task_id=None):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                if task_id is not None:
                    cursor.execute(
                        "SELECT `id` FROM `rate_limit_config` WHERE `task_id` = %(task_id)s",
                        {"task_id": task_id}
                    )
                    existing = cursor.fetchone()
                    if existing:
                        cursor.execute(
                            """UPDATE `rate_limit_config`
                               SET `requests_per_minute` = %(rpm)s, `concurrent_max` = %(cm)s
                               WHERE `id` = %(id)s""",
                            {"rpm": requests_per_minute, "cm": concurrent_max, "id": existing["id"]}
                        )
                    else:
                        sql = """
                            INSERT INTO `rate_limit_config`
                            (`task_id`, `requests_per_minute`, `concurrent_max`)
                            VALUES (%(task_id)s, %(rpm)s, %(cm)s)
                        """
                        cursor.execute(sql, {
                            "task_id": task_id,
                            "rpm": requests_per_minute,
                            "cm": concurrent_max,
                        })
                else:
                    cursor.execute(
                        "SELECT `id` FROM `rate_limit_config` WHERE `task_id` IS NULL"
                    )
                    existing = cursor.fetchone()
                    if existing:
                        cursor.execute(
                            """UPDATE `rate_limit_config`
                               SET `requests_per_minute` = %(rpm)s, `concurrent_max` = %(cm)s
                               WHERE `id` = %(id)s""",
                            {"rpm": requests_per_minute, "cm": concurrent_max, "id": existing["id"]}
                        )
                    else:
                        sql = """
                            INSERT INTO `rate_limit_config`
                            (`requests_per_minute`, `concurrent_max`)
                            VALUES (%(rpm)s, %(cm)s)
                        """
                        cursor.execute(sql, {
                            "rpm": requests_per_minute,
                            "cm": concurrent_max,
                        })
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()


proxy_db = ProxyDB()