import pymysql
import os
from datetime import datetime


class CrawlerDB:
    """
    爬虫数据数据库操作层
    使用 PyMySQL 连接 MySQL，管理爬虫数据表
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

    def save_batch(self, items):
        """
        批量保存爬取结果
        :param items: 爬取结果列表，每项包含 title, link, image_url, content, source_url, page_number, type
        :return: 实际保存的记录数
        """
        conn = None
        saved = 0
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO `crawler_data`
                    (`title`, `link`, `image_url`, `content`, `source_url`, `page_number`, `type`)
                    VALUES (%(title)s, %(link)s, %(image_url)s, %(content)s, %(source_url)s, %(page_number)s, %(type)s)
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

    def get_list(self, page=1, page_size=20, keyword=""):
        """
        分页查询爬取数据
        :param page: 页码
        :param page_size: 每页条数
        :param keyword: 搜索关键词（模糊匹配标题和内容）
        :return: (数据列表, 总条数)
        """
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                if keyword:
                    where = "WHERE `title` LIKE %(keyword)s OR `content` LIKE %(keyword)s"
                    params = {"keyword": "%{}%".format(keyword)}
                else:
                    where = ""
                    params = {}

                count_sql = "SELECT COUNT(*) AS total FROM `crawler_data` {}".format(where)
                cursor.execute(count_sql, params)
                total = cursor.fetchone()["total"]

                offset = (page - 1) * page_size
                list_sql = (
                    "SELECT * FROM `crawler_data` {} "
                    "ORDER BY `collected_at` DESC "
                    "LIMIT %(limit)s OFFSET %(offset)s"
                ).format(where)
                params["limit"] = page_size
                params["offset"] = offset
                cursor.execute(list_sql, params)
                rows = cursor.fetchall()

                for row in rows:
                    if row.get("collected_at"):
                        row["collected_at"] = row["collected_at"].strftime("%Y-%m-%d %H:%M:%S")

                return rows, total
        except pymysql.Error as e:
            print(f"查询数据失败: {e}")
            return [], 0
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
                    if row.get("collected_at"):
                        row["collected_at"] = row["collected_at"].strftime("%Y-%m-%d %H:%M:%S")
                return rows
        except pymysql.Error as e:
            print(f"获取全部数据失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

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

    def get_today_stats(self):
        """获取今日统计数据：今日总数和每小时分组统计"""
        conn = None
        try:
            conn = pymysql.connect(**self._config)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) AS total FROM `crawler_data` "
                    "WHERE DATE(`collected_at`) = CURDATE()"
                )
                total = cursor.fetchone()["total"]

                hourly = [0] * 24
                cursor.execute(
                    "SELECT HOUR(`collected_at`) AS h, COUNT(*) AS cnt "
                    "FROM `crawler_data` "
                    "WHERE DATE(`collected_at`) = CURDATE() "
                    "GROUP BY HOUR(`collected_at`) "
                    "ORDER BY h"
                )
                for row in cursor.fetchall():
                    h = row["h"]
                    if 0 <= h < 24:
                        hourly[h] = row["cnt"]

                return {
                    "today_total": total,
                    "hourly_breakdown": hourly
                }
        except pymysql.Error as e:
            print(f"查询今日统计失败: {e}")
            return {"today_total": 0, "hourly_breakdown": [0] * 24}
        finally:
            if conn:
                conn.close()


crawler_db = CrawlerDB()