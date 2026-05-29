import json
import pymysql
import os
from datetime import datetime

from db_settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET, DB_CA_PATH
from src.datetime_utils import (
    format_api_datetime,
    format_row_datetimes,
    get_local_day_bounds_for_query,
    get_request_timezone,
    get_effective_timezone,
    get_mysql_tz_offset,
    get_db_time_storage,
    get_timezone_offset_hours,
    bucket_datetimes_by_local_hour,
    API_DATETIME_FORMAT,
)


class CrawlerDB:
    """
    爬虫数据数据库操作层
    使用 PyMySQL 连接 MySQL，管理爬虫数据表
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
        """获取数据库连接"""
        config = dict(self._config)
        config.pop("database", None)
        config["charset"] = "utf8mb4"
        config["cursorclass"] = pymysql.cursors.DictCursor
        return pymysql.connect(**config)

    def _ensure_database(self):
        """自动创建数据库（如果不存在）"""
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
        """自动创建爬虫数据表（如果不存在），并添加缺失的列"""
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                # 创建表（如果不存在）
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `crawler_data` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                        `title` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '标题',
                        `link` VARCHAR(1000) NOT NULL DEFAULT '' COMMENT '链接地址',
                        `image_url` VARCHAR(1000) NOT NULL DEFAULT '' COMMENT '图片URL地址',
                        `content` TEXT COMMENT '正文内容摘要',
                        `source_url` VARCHAR(500) NOT NULL DEFAULT '' COMMENT '来源网址',
                        `page_number` INT DEFAULT 1 COMMENT '爬取页码',
                        `type` VARCHAR(20) NOT NULL DEFAULT 'link' COMMENT '数据类型: link/image/mixed',
                        `collected_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '采集时间',
                        INDEX `idx_source_url` (`source_url`(255)),
                        INDEX `idx_collected_at` (`collected_at`),
                        INDEX `idx_page_number` (`page_number`),
                        INDEX `idx_type` (`type`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    COMMENT='爬虫采集数据表'
                """)
                
                # 检查并添加缺失的列（兼容旧表）
                cursor.execute("SHOW COLUMNS FROM `crawler_data` LIKE 'image_url'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `crawler_data` ADD COLUMN `image_url` VARCHAR(1000) NOT NULL DEFAULT '' COMMENT '图片URL地址' AFTER `link`")
                
                cursor.execute("SHOW COLUMNS FROM `crawler_data` LIKE 'type'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `crawler_data` ADD COLUMN `type` VARCHAR(20) NOT NULL DEFAULT 'link' COMMENT '数据类型: link/image/mixed' AFTER `page_number`")

                cursor.execute("SHOW COLUMNS FROM `crawler_data` LIKE 'task_id'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `crawler_data` ADD COLUMN `task_id` INT DEFAULT NULL COMMENT '关联任务ID' AFTER `type`")

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `data_auto_write_config` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY,
                        `user_id` INT NOT NULL,
                        `target_type` VARCHAR(32) NOT NULL DEFAULT 'mysql',
                        `target_config` JSON,
                        `enabled` TINYINT(1) NOT NULL DEFAULT 0,
                        `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE KEY `uk_user` (`user_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `data_push_config` (
                        `id` INT AUTO_INCREMENT PRIMARY KEY,
                        `user_id` INT NOT NULL,
                        `push_type` VARCHAR(32) NOT NULL DEFAULT 'mixed',
                        `push_config` JSON,
                        `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE KEY `uk_user` (`user_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
            
            conn.commit()
            conn.close()
            return True
        except pymysql.Error as e:
            print(f"数据表创建失败: {e}")
            return False

    def connect(self):
        """
        初始化数据库连接并检查表结构
        在应用启动时调用
        """
        return self._ensure_table()

    def save_batch(self, items, task_id=None):
        """
        批量保存爬取结果
        :param items: 爬取结果列表，每项包含 title, link, image_url, content, source_url, page_number, type
        :param task_id: 任务ID（可选）
        :return: 实际保存的记录数
        """
        conn = None
        saved = 0
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO `crawler_data`
                    (`title`, `link`, `image_url`, `content`, `source_url`, `page_number`, `type`, `task_id`)
                    VALUES (%(title)s, %(link)s, %(image_url)s, %(content)s, %(source_url)s, %(page_number)s, %(type)s, %(task_id)s)
                """
                for item in items:
                    try:
                        item_type = item.get("type", "link")
                        img_url = item.get("image_url", "")
                        # 如果是图片类型且没有image_url，使用link作为备用
                        if item_type == "image" and not img_url:
                            img_url = item.get("link", "")
                        
                        cursor.execute(sql, {
                            "title": item.get("title", ""),
                            "link": item.get("link", ""),
                            "image_url": img_url,
                            "content": item.get("content", ""),
                            "source_url": item.get("source_url", ""),
                            "page_number": item.get("page_number", 1),
                            "type": item_type,
                            "task_id": task_id,
                        })
                        saved += 1
                    except pymysql.Error as e:
                        print(f"保存单条数据失败: {e}")
                        continue
            conn.commit()
        except pymysql.Error as e:
            print(f"批量保存数据失败: {e}")
        finally:
            if conn:
                conn.close()
        return saved

    def get_list(self, page=1, page_size=20, keyword="", task_id=None,
                 data_type=None, date_from=None, date_to=None,
                 sort_field=None, sort_order="desc", since=None):
        """
        分页查询爬取数据
        """
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                conditions = []
                params = {}

                if keyword:
                    conditions.append(
                        "(`title` LIKE %(keyword)s OR `content` LIKE %(keyword)s "
                        "OR `link` LIKE %(keyword)s OR `image_url` LIKE %(keyword)s)"
                    )
                    params["keyword"] = "%{}%".format(keyword)

                if task_id:
                    conditions.append("`task_id` = %(task_id)s")
                    params["task_id"] = task_id

                if data_type and data_type != "all":
                    conditions.append("`type` = %(data_type)s")
                    params["data_type"] = data_type

                if date_from:
                    conditions.append("DATE(`collected_at`) >= %(date_from)s")
                    params["date_from"] = date_from

                if date_to:
                    conditions.append("DATE(`collected_at`) <= %(date_to)s")
                    params["date_to"] = date_to

                if since:
                    conditions.append("`collected_at` >= %(since)s")
                    params["since"] = since

                where = ""
                if conditions:
                    where = "WHERE " + " AND ".join(conditions)

                allowed_sort = {
                    "title": "title",
                    "link": "link",
                    "content": "content",
                    "source_url": "source_url",
                    "type": "type",
                    "collected_at": "collected_at",
                    "image_url": "image_url",
                }
                order_col = allowed_sort.get(sort_field, "collected_at")
                order_dir = "ASC" if str(sort_order).lower() == "asc" else "DESC"

                count_sql = "SELECT COUNT(*) AS total FROM `crawler_data` {}".format(where)
                cursor.execute(count_sql, params)
                total = cursor.fetchone()["total"]

                offset = (page - 1) * page_size
                list_sql = (
                    "SELECT * FROM `crawler_data` {} "
                    "ORDER BY `{}` {} "
                    "LIMIT %(limit)s OFFSET %(offset)s"
                ).format(where, order_col, order_dir)
                params["limit"] = page_size
                params["offset"] = offset
                cursor.execute(list_sql, params)
                rows = cursor.fetchall()

                for row in rows:
                    format_row_datetimes(row, "collected_at")

                return rows, total
        except pymysql.Error as e:
            print(f"查询数据失败: {e}")
            return [], 0
        finally:
            if conn:
                conn.close()

    def get_task_data_stats(self, task_id, since=None):
        """任务数据概览（可选仅统计某次执行之后的数据）"""
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                conditions = ["`task_id` = %(task_id)s"]
                params = {"task_id": task_id}
                if since:
                    conditions.append("`collected_at` >= %(since)s")
                    params["since"] = since
                where = "WHERE " + " AND ".join(conditions)

                cursor.execute(
                    "SELECT COUNT(*) AS total FROM `crawler_data` {}".format(where),
                    params,
                )
                total_count = cursor.fetchone()["total"]

                cursor.execute(
                    "SELECT `type`, COUNT(*) AS cnt FROM `crawler_data` {} GROUP BY `type`".format(
                        where
                    ),
                    params,
                )
                type_distribution = {row["type"]: row["cnt"] for row in cursor.fetchall()}

                cursor.execute(
                    "SELECT MAX(`collected_at`) AS last_time FROM `crawler_data` {}".format(
                        where
                    ),
                    params,
                )
                last_time = cursor.fetchone()["last_time"]
                if last_time:
                    last_time = format_api_datetime(last_time)

                return {
                    "total_count": total_count,
                    "type_distribution": type_distribution,
                    "last_collected_at": last_time,
                }
        except pymysql.Error as e:
            print(f"任务数据统计失败: {e}")
            return {
                "total_count": 0,
                "type_distribution": {},
                "last_collected_at": None,
            }
        finally:
            if conn:
                conn.close()

    def delete_by_id(self, record_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM `crawler_data` WHERE `id` = %(id)s",
                    {"id": record_id}
                )
                if cursor.rowcount == 0:
                    return False, "数据不存在"
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def delete_by_ids(self, ids):
        if not ids:
            return 0, "未选择数据"
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                placeholders = ",".join(["%s"] * len(ids))
                sql = "DELETE FROM `crawler_data` WHERE `id` IN ({})".format(placeholders)
                cursor.execute(sql, ids)
                deleted = cursor.rowcount
            conn.commit()
            return deleted, None
        except pymysql.Error as e:
            return 0, str(e)
        finally:
            if conn:
                conn.close()

    def clear_all(self):
        """清空所有爬取数据"""
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE `crawler_data`")
            conn.commit()
            return True, "所有数据已清空"
        except pymysql.Error as e:
            return False, f"清空数据失败: {str(e)}"
        finally:
            if conn:
                conn.close()

    def get_all(self):
        """获取全部数据，用于导出"""
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `crawler_data` ORDER BY `collected_at` DESC"
                )
                rows = cursor.fetchall()
                for row in rows:
                    format_row_datetimes(row, "collected_at")
                return rows
        except pymysql.Error as e:
            print(f"获取全部数据失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def replace_all(self, items):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE `crawler_data`")
                sql = """
                    INSERT INTO `crawler_data`
                    (`title`, `link`, `image_url`, `content`, `source_url`, `page_number`, `type`, `task_id`)
                    VALUES (%(title)s, %(link)s, %(image_url)s, %(content)s, %(source_url)s, %(page_number)s, %(type)s, %(task_id)s)
                """
                for item in items:
                    cursor.execute(sql, self._item_params(item))
            conn.commit()
            return True
        except pymysql.Error as e:
            print(f"批量替换数据失败: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def _item_params(self, item):
        return {
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "image_url": item.get("image_url", ""),
            "content": item.get("content", ""),
            "source_url": item.get("source_url", ""),
            "page_number": item.get("page_number", 1),
            "type": item.get("type", "link"),
            "task_id": item.get("task_id"),
        }

    def bulk_upsert(self, items):
        """按 id 更新或插入，避免 TRUNCATE 误删未加载数据"""
        if not items:
            return True, 0
        conn = None
        updated = 0
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                insert_sql = """
                    INSERT INTO `crawler_data`
                    (`title`, `link`, `image_url`, `content`, `source_url`, `page_number`, `type`, `task_id`)
                    VALUES (%(title)s, %(link)s, %(image_url)s, %(content)s, %(source_url)s, %(page_number)s, %(type)s, %(task_id)s)
                """
                update_sql = """
                    UPDATE `crawler_data` SET
                    `title`=%(title)s, `link`=%(link)s, `image_url`=%(image_url)s,
                    `content`=%(content)s, `source_url`=%(source_url)s, `page_number`=%(page_number)s,
                    `type`=%(type)s, `task_id`=%(task_id)s
                    WHERE `id`=%(id)s
                """
                for item in items:
                    params = self._item_params(item)
                    rid = item.get("id")
                    if rid:
                        params["id"] = int(rid)
                        cursor.execute(update_sql, params)
                        if cursor.rowcount:
                            updated += 1
                        else:
                            cursor.execute(insert_sql, params)
                            updated += 1
                    else:
                        cursor.execute(insert_sql, params)
                        updated += 1
            conn.commit()
            return True, updated
        except pymysql.Error as e:
            print(f"批量 upsert 失败: {e}")
            return False, 0
        finally:
            if conn:
                conn.close()

    def get_export_list(self, task_id=None, date_from=None, date_to=None):
        rows, _ = self.get_list(
            page=1, page_size=100000, keyword="",
            task_id=task_id, date_from=date_from, date_to=date_to
        )
        return rows

    def save_auto_write_config(self, user_id, target_type, target_config, enabled=None):
        conn = None
        try:
            cfg = target_config if isinstance(target_config, dict) else {}
            if enabled is None:
                enabled = cfg.get("auto_write", cfg.get("enabled", False))
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO `data_auto_write_config`
                    (`user_id`, `target_type`, `target_config`, `enabled`)
                    VALUES (%(user_id)s, %(target_type)s, %(config)s, %(enabled)s)
                    ON DUPLICATE KEY UPDATE
                    `target_type`=VALUES(`target_type`),
                    `target_config`=VALUES(`target_config`),
                    `enabled`=VALUES(`enabled`)
                """, {
                    "user_id": user_id,
                    "target_type": target_type or "mysql",
                    "config": json.dumps(cfg, ensure_ascii=False),
                    "enabled": 1 if enabled else 0,
                })
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_auto_write_config(self, user_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `data_auto_write_config` WHERE `user_id`=%(uid)s",
                    {"uid": user_id},
                )
                row = cursor.fetchone()
                if not row:
                    return None
                cfg = row.get("target_config")
                if isinstance(cfg, str):
                    cfg = json.loads(cfg) if cfg else {}
                row["target_config"] = cfg or {}
                return row
        except pymysql.Error:
            return None
        finally:
            if conn:
                conn.close()

    def save_push_config(self, user_id, push_type, push_config):
        conn = None
        try:
            cfg = push_config if isinstance(push_config, dict) else {}
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO `data_push_config`
                    (`user_id`, `push_type`, `push_config`)
                    VALUES (%(user_id)s, %(push_type)s, %(config)s)
                    ON DUPLICATE KEY UPDATE
                    `push_type`=VALUES(`push_type`),
                    `push_config`=VALUES(`push_config`)
                """, {
                    "user_id": user_id,
                    "push_type": push_type or "mixed",
                    "config": json.dumps(cfg, ensure_ascii=False),
                })
            conn.commit()
            return True, None
        except pymysql.Error as e:
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def get_push_config(self, user_id):
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM `data_push_config` WHERE `user_id`=%(uid)s",
                    {"uid": user_id},
                )
                row = cursor.fetchone()
                if not row:
                    return None
                cfg = row.get("push_config")
                if isinstance(cfg, str):
                    cfg = json.loads(cfg) if cfg else {}
                row["push_config"] = cfg or {}
                return row
        except pymysql.Error:
            return None
        finally:
            if conn:
                conn.close()

    def test_external_db_connection(self, config):
        """测试外部数据库连接"""
        cfg = config or {}
        db_type = (cfg.get("db_type") or cfg.get("target_type") or "mysql").lower()
        if db_type not in ("mysql", "postgresql"):
            return False, "仅支持 MySQL / PostgreSQL"
        try:
            if db_type == "postgresql":
                import psycopg2
                conn = psycopg2.connect(
                    host=cfg.get("host", "localhost"),
                    port=int(cfg.get("port", 5432)),
                    user=cfg.get("user", ""),
                    password=cfg.get("password", ""),
                    dbname=cfg.get("database", cfg.get("dbname", "")),
                    connect_timeout=5,
                )
                conn.close()
            else:
                conn = pymysql.connect(
                    host=cfg.get("host", "localhost"),
                    port=int(cfg.get("port", 3306)),
                    user=cfg.get("user", ""),
                    password=cfg.get("password", ""),
                    database=cfg.get("database", ""),
                    charset="utf8mb4",
                    connect_timeout=5,
                )
                conn.close()
            return True, None
        except Exception as e:
            return False, str(e)

    def sync_auto_write_for_user(self, user_id, items):
        """爬虫入库后同步到用户配置的外部库"""
        cfg_row = self.get_auto_write_config(user_id)
        if not cfg_row or not cfg_row.get("enabled"):
            return
        cfg = cfg_row.get("target_config") or {}
        if not cfg.get("host") and not cfg.get("database"):
            return
        table = cfg.get("table", "collected_data")
        try:
            conn = pymysql.connect(
                host=cfg.get("host", "localhost"),
                port=int(cfg.get("port", 3306)),
                user=cfg.get("user", ""),
                password=cfg.get("password", ""),
                database=cfg.get("database", ""),
                charset="utf8mb4",
            )
            with conn.cursor() as cursor:
                for item in items:
                    cursor.execute(
                        f"INSERT INTO `{table}` (`title`, `link`, `content`, `source_url`) "
                        "VALUES (%(title)s, %(link)s, %(content)s, %(source_url)s)",
                        {
                            "title": item.get("title", ""),
                            "link": item.get("link", ""),
                            "content": item.get("content", ""),
                            "source_url": item.get("source_url", ""),
                        },
                    )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"自动入库同步失败: {e}")

    def get_count(self):
        """获取数据总条数"""
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM `crawler_data`")
                return cursor.fetchone()["total"]
        except pymysql.Error:
            return 0
        finally:
            if conn:
                conn.close()

    def get_stats(self):
        """获取统计信息：总数据条数"""
        return {
            "total_count": self.get_count()
        }

    def get_today_stats(self, tz_name=None):
        """获取用户本地「今日」统计：hourly_breakdown[本地小时]=条数。"""
        conn = None
        tz_name = get_effective_timezone(tz_name or get_request_timezone())
        offset_hours = get_timezone_offset_hours(tz_name)
        storage = get_db_time_storage()
        try:
            start_bound, end_bound = get_local_day_bounds_for_query(tz_name)
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                start_str = start_bound.strftime(API_DATETIME_FORMAT)
                end_str = end_bound.strftime(API_DATETIME_FORMAT)
                hourly = [0] * 24
                sql_bucketed = False

                # UTC 存储：SQL 层 DATE_ADD +8 再 HOUR，UTC 01:00 → 索引 9
                if storage == "utc" and offset_hours:
                    try:
                        cursor.execute(
                            "SELECT "
                            "HOUR(DATE_ADD(`collected_at`, INTERVAL %(offset)s HOUR)) AS local_h, "
                            "COUNT(*) AS cnt "
                            "FROM `crawler_data` "
                            "WHERE `collected_at` >= %(start)s AND `collected_at` < %(end)s "
                            "GROUP BY local_h",
                            {
                                "start": start_str,
                                "end": end_str,
                                "offset": int(offset_hours),
                            },
                        )
                        for row in cursor.fetchall():
                            h = row.get("local_h")
                            if h is not None and 0 <= int(h) < 24:
                                hourly[int(h)] = int(row.get("cnt") or 0)
                        sql_bucketed = True
                    except pymysql.Error as sql_err:
                        print(f"今日统计 SQL 分桶回退: {sql_err}")

                if not sql_bucketed:
                    cursor.execute(
                        "SELECT `collected_at` FROM `crawler_data` "
                        "WHERE `collected_at` >= %(start)s AND `collected_at` < %(end)s",
                        {"start": start_str, "end": end_str},
                    )
                    rows = cursor.fetchall()
                    hourly = bucket_datetimes_by_local_hour(rows, tz_name)

                today_total = sum(hourly)

                return {
                    "today_total": today_total,
                    "hourly_breakdown": hourly,
                    "timezone": tz_name,
                    "timezone_offset": get_mysql_tz_offset(tz_name),
                    "db_time_storage": storage,
                    "offset_hours": offset_hours,
                }
        except pymysql.Error as e:
            print(f"查询今日统计失败: {e}")
            return {
                "today_total": 0,
                "hourly_breakdown": [0] * 24,
                "timezone": tz_name,
                "timezone_offset": get_mysql_tz_offset(tz_name),
                "db_time_storage": storage,
                "offset_hours": offset_hours,
            }
        finally:
            if conn:
                conn.close()


crawler_db = CrawlerDB()