import pymysql
import os
import requests
from datetime import datetime
from urllib.parse import urlparse

from db_settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET, DB_CA_PATH
from src.datetime_utils import format_row_datetimes


def _format_alive_seconds(seconds):
    if not seconds:
        return '-'
    seconds = int(seconds)
    if seconds < 60:
        return f'{seconds}秒'
    if seconds < 3600:
        return f'{seconds // 60}分钟'
    if seconds < 86400:
        return f'{seconds // 3600}小时'
    return f'{round(seconds / 86400, 1)}天'


def _normalize_proxy_status(status):
    """仅探测成功的代理为 online，其余均为 offline。"""
    s = (status or '').lower()
    if s == 'online':
        return 'online'
    return 'offline'


def _format_proxy_row(row):
    if not row:
        return row
    row['status'] = _normalize_proxy_status(row.get('status'))
    row['success_rate'] = float(row.get('success_rate') or 0)
    row['alive_time'] = _format_alive_seconds(row.get('alive_seconds'))
    row['aliveTime'] = row['alive_time']
    row['last_check'] = row.get('last_check_at')
    row['lastCheck'] = row.get('last_check_at')
    row['successRate'] = row['success_rate']
    return row


class ProxyDB:
    """
    代理池数据库操作层
    使用 PyMySQL 连接 MySQL，管理代理IP、分组、黑白名单和速率限制
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
                    CREATE TABLE IF NOT EXISTS `proxy_pool` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `ip` VARCHAR(45) NOT NULL DEFAULT '' COMMENT '代理IP地址',
                        `port` INT NOT NULL DEFAULT 0 COMMENT '代理端口',
                        `protocol` VARCHAR(10) NOT NULL DEFAULT 'http' COMMENT '代理协议',
                        `status` VARCHAR(20) NOT NULL DEFAULT 'offline' COMMENT '代理状态: online/offline',
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

                for col_sql in (
                    ("rate_limit_config", "retry_count", "INT NOT NULL DEFAULT 3 COMMENT '重试次数'"),
                    ("site_blacklist", "enabled", "TINYINT(1) NOT NULL DEFAULT 1"),
                    ("site_whitelist", "enabled", "TINYINT(1) NOT NULL DEFAULT 1"),
                ):
                    table, col, definition = col_sql
                    cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE '{col}'")
                    if not cursor.fetchone():
                        cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN `{col}` {definition}")

                # 从未探测过的代理不应显示为在线（兼容旧默认 ONLINE/active）
                cursor.execute("""
                    UPDATE `proxy_pool`
                    SET `status` = 'offline'
                    WHERE `last_check_at` IS NULL
                      AND LOWER(`status`) IN ('online', 'active', 'ok')
                """)
                # 历史数据：active/ok 且探测成功率>0 的视为 online，其余归为 offline
                cursor.execute("""
                    UPDATE `proxy_pool`
                    SET `status` = 'online'
                    WHERE LOWER(`status`) IN ('active', 'ok')
                      AND `last_check_at` IS NOT NULL
                      AND `success_rate` > 0
                """)
                cursor.execute("""
                    UPDATE `proxy_pool`
                    SET `status` = 'offline'
                    WHERE LOWER(`status`) IN ('active', 'ok')
                      AND (`last_check_at` IS NULL OR `success_rate` <= 0)
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
                    format_row_datetimes(row, "last_check_at", "created_at")
                    _format_proxy_row(row)
                return rows
        except pymysql.Error as e:
            print(f"查询代理失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_proxy_by_id(self, proxy_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM `proxy_pool` WHERE `id`=%(id)s", {"id": proxy_id})
                row = cursor.fetchone()
                if row:
                    format_row_datetimes(row, "last_check_at", "created_at")
                    return _format_proxy_row(row)
                return None
        except pymysql.Error:
            return None
        finally:
            if conn:
                conn.close()

    def probe_proxy(self, proxy_id):
        row = self.get_proxy_by_id(proxy_id)
        if not row:
            return False, "代理不存在", None
        ip, port = row.get("ip"), row.get("port")
        protocol = (row.get("protocol") or "http").lower()
        # 多数 HTTP/HTTPS 代理实际使用 http 协议握手，https 仅表示可转发 HTTPS 流量
        scheme = protocol if protocol in ("socks5", "socks4") else "http"
        proxy_url = f"{scheme}://{ip}:{port}"
        success = False
        try:
            resp = requests.get(
                "http://httpbin.org/ip",
                proxies={"http": proxy_url, "https": proxy_url},
                timeout=8,
            )
            success = resp.status_code == 200
        except Exception:
            success = False
        alive = int(row.get("alive_seconds") or 0)
        if success:
            alive = alive + 60 if alive else 60
        status = "online" if success else "offline"
        rate = 95.0 if success else max(0.0, float(row.get("success_rate") or 0) - 10)
        self.refresh_proxy(proxy_id, status=status, success_rate=rate, alive_seconds=alive)
        updated = self.get_proxy_by_id(proxy_id)
        return True, None, updated

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
                    (`ip`, `port`, `protocol`, `status`)
                    VALUES (%(ip)s, %(port)s, %(protocol)s, 'offline')
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

    def get_proxies_by_group_name(self, group_name):
        """按分组名称获取可用代理列表"""
        if not group_name or not str(group_name).strip():
            return []
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.* FROM `proxy_pool` p
                    INNER JOIN `proxy_group_mapping` m ON p.id = m.proxy_id
                    INNER JOIN `proxy_groups` g ON g.id = m.group_id
                    WHERE g.name = %(group_name)s
                      AND LOWER(p.status) = 'online'
                    ORDER BY p.success_rate DESC, p.created_at DESC
                    """,
                    {"group_name": str(group_name).strip()},
                )
                rows = cursor.fetchall()
                for row in rows:
                    format_row_datetimes(row, "last_check_at", "created_at")
                return rows
        except pymysql.Error as e:
            print(f"按分组查询代理失败: {e}")
            return []
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
                    format_row_datetimes(row, "created_at")
                    cursor.execute(
                        "SELECT `proxy_id` FROM `proxy_group_mapping` WHERE `group_id`=%(gid)s",
                        {"gid": row["id"]},
                    )
                    row["proxies"] = [r["proxy_id"] for r in cursor.fetchall()]
                return rows
        except pymysql.Error as e:
            print(f"查询代理分组失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def delete_proxy_group(self, group_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM `proxy_group_mapping` WHERE `group_id`=%(gid)s",
                    {"gid": group_id},
                )
                cursor.execute(
                    "DELETE FROM `proxy_groups` WHERE `id`=%(gid)s",
                    {"gid": group_id},
                )
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
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

    def sync_group_proxies(self, group_id, proxy_ids):
        """将分组内代理成员同步为指定列表（全量替换）。"""
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT `id` FROM `proxy_groups` WHERE `id` = %(group_id)s",
                    {"group_id": group_id},
                )
                if not cursor.fetchone():
                    return False, "分组不存在"

                normalized = []
                for pid in proxy_ids or []:
                    try:
                        normalized.append(int(pid))
                    except (TypeError, ValueError):
                        continue

                cursor.execute(
                    "DELETE FROM `proxy_group_mapping` WHERE `group_id` = %(group_id)s",
                    {"group_id": group_id},
                )
                for proxy_id in normalized:
                    cursor.execute(
                        "SELECT `id` FROM `proxy_pool` WHERE `id` = %(proxy_id)s",
                        {"proxy_id": proxy_id},
                    )
                    if not cursor.fetchone():
                        continue
                    cursor.execute(
                        """
                        INSERT INTO `proxy_group_mapping` (`group_id`, `proxy_id`)
                        VALUES (%(group_id)s, %(proxy_id)s)
                        """,
                        {"group_id": group_id, "proxy_id": proxy_id},
                    )
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
                    format_row_datetimes(row, "created_at")
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
                    format_row_datetimes(row, "created_at")
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
                if row:
                    format_row_datetimes(row, "created_at")
                return row
        except pymysql.Error as e:
            print(f"查询速率限制失败: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def set_rate_limit(self, requests_per_minute=60, concurrent_max=10, task_id=None, retry_count=3):
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
                               SET `requests_per_minute` = %(rpm)s, `concurrent_max` = %(cm)s,
                                   `retry_count` = %(retry)s
                               WHERE `id` = %(id)s""",
                            {
                                "rpm": requests_per_minute, "cm": concurrent_max,
                                "retry": retry_count, "id": existing["id"],
                            },
                        )
                    else:
                        sql = """
                            INSERT INTO `rate_limit_config`
                            (`task_id`, `requests_per_minute`, `concurrent_max`, `retry_count`)
                            VALUES (%(task_id)s, %(rpm)s, %(cm)s, %(retry)s)
                        """
                        cursor.execute(sql, {
                            "task_id": task_id,
                            "rpm": requests_per_minute,
                            "cm": concurrent_max,
                            "retry": retry_count,
                        })
                else:
                    cursor.execute(
                        "SELECT `id` FROM `rate_limit_config` WHERE `task_id` IS NULL"
                    )
                    existing = cursor.fetchone()
                    if existing:
                        cursor.execute(
                            """UPDATE `rate_limit_config`
                               SET `requests_per_minute` = %(rpm)s, `concurrent_max` = %(cm)s,
                                   `retry_count` = %(retry)s
                               WHERE `id` = %(id)s""",
                            {
                                "rpm": requests_per_minute, "cm": concurrent_max,
                                "retry": retry_count, "id": existing["id"],
                            },
                        )
                    else:
                        sql = """
                            INSERT INTO `rate_limit_config`
                            (`requests_per_minute`, `concurrent_max`, `retry_count`)
                            VALUES (%(rpm)s, %(cm)s, %(retry)s)
                        """
                        cursor.execute(sql, {
                            "rpm": requests_per_minute,
                            "cm": concurrent_max,
                            "retry": retry_count,
                        })
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_rate_limits_bundle(self):
        global_cfg = self.get_rate_limit()
        conn = None
        tasks = []
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `rate_limit_config` WHERE `task_id` IS NOT NULL ORDER BY `created_at` DESC"
                )
                tasks = cursor.fetchall()
                for row in tasks:
                    format_row_datetimes(row, "created_at")
        except pymysql.Error:
            pass
        finally:
            if conn:
                conn.close()
        return {"global": global_cfg, "tasks": tasks}

    def get_effective_rate_limit(self, task_id=None):
        task_cfg = self.get_rate_limit(task_id) if task_id else None
        global_cfg = self.get_rate_limit()
        cfg = task_cfg or global_cfg or {}
        rpm = int(cfg.get("requests_per_minute") or 60)
        concurrent = int(cfg.get("concurrent_max") or 10)
        retry = int(cfg.get("retry_count") or 3)
        interval = 60.0 / max(rpm, 1)
        return {
            "requests_per_minute": rpm,
            "concurrent_max": concurrent,
            "retry_count": retry,
            "request_interval": interval,
        }

    def _match_site_pattern(self, url, pattern):
        if not pattern:
            return False
        try:
            host = urlparse(url if '://' in url else f'http://{url}').netloc or url
            pat = pattern.strip().lower()
            h = host.lower()
            if pat.startswith('*.'):
                return h.endswith(pat[2:]) or h == pat[2:]
            return pat in h or h.endswith(pat.lstrip('.'))
        except Exception:
            return pat in (url or '')

    def is_url_allowed(self, url):
        blacklist = [b for b in self.get_blacklist() if b.get("enabled", 1)]
        for item in blacklist:
            if self._match_site_pattern(url, item.get("url", "")):
                return False, "blacklist"
        whitelist = [w for w in self.get_whitelist() if w.get("enabled", 1)]
        if whitelist:
            for item in whitelist:
                if self._match_site_pattern(url, item.get("url", "")):
                    return True, None
            return False, "whitelist"
        return True, None


proxy_db = ProxyDB()