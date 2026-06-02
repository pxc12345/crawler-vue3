import pymysql

from db_settings import PYMYSQL_CONFIG


class BlessingDB:
    def __init__(self):
        self.config = dict(PYMYSQL_CONFIG)
        self.connection = None

    def _connect(self):
        if self.connection is None or not self.connection.open:
            self.connection = pymysql.connect(**self.config)
        return self.connection

    def _execute(self, sql, params=None, fetch_one=False, fetch_all=False, commit=False):
        conn = self._connect()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, params)
            if commit:
                conn.commit()
                return cursor.lastrowid
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
        return None

    def _table_exists(self, table_name):
        conn = self._connect()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s AND table_name = %s",
                (self.config["database"], table_name),
            )
            return cursor.fetchone()[0] > 0

    def _column_exists(self, table_name, column_name):
        conn = self._connect()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = %s AND table_name = %s AND column_name = %s",
                (self.config["database"], table_name, column_name),
            )
            return cursor.fetchone()[0] > 0

    def get_setting(self):
        return self._execute("SELECT * FROM system_settings WHERE id = 1", fetch_one=True)

    def update_setting(self, global_mode, birthday_text, festival_text, festival_name):
        sql = """
            UPDATE system_settings
            SET global_mode = %s,
                birthday_default_text = %s,
                festival_default_text = %s,
                current_nearest_festival = %s,
                update_time = NOW()
            WHERE id = 1
        """
        self._execute(sql, (global_mode, birthday_text, festival_text, festival_name), commit=True)

    def update_festival_name(self, festival_name):
        sql = "UPDATE system_settings SET current_nearest_festival = %s, update_time = NOW() WHERE id = 1"
        self._execute(sql, (festival_name,), commit=True)

    def get_all_festivals(self):
        return self._execute("SELECT * FROM festival_list ORDER BY sort ASC", fetch_all=True)

    def get_user_by_username(self, username):
        sql = """
            SELECT
              u.*,
              t.name AS theme_name,
              t.category AS theme_category,
              t.background_color,
              t.title_color,
              t.body_color,
              t.button_color,
              t.card_color,
              e.name AS effect_profile_name,
              e.welcome_effects,
              e.intro_effects,
              e.main_effects,
              e.closing_effects,
              e.particle_density,
              e.motion_level,
              e.glow_intensity
            FROM user_accounts u
            LEFT JOIN theme_template t ON u.theme_id = t.id
            LEFT JOIN effect_profile e ON u.effect_profile_id = e.id
            WHERE u.username = %s
        """
        return self._execute(sql, (username,), fetch_one=True)

    def get_all_users(self):
        sql = """
            SELECT
              u.id,
              u.username,
              u.bg_color,
              u.text_color,
              u.theme_id,
              u.effect_profile_id,
              u.create_time,
              t.name AS theme_name,
              t.category AS theme_category,
              t.background_color,
              t.title_color,
              t.body_color,
              t.button_color,
              t.card_color,
              e.name AS effect_profile_name,
              e.welcome_effects,
              e.intro_effects,
              e.main_effects,
              e.closing_effects,
              e.particle_density,
              e.motion_level,
              e.glow_intensity
            FROM user_accounts u
            LEFT JOIN theme_template t ON u.theme_id = t.id
            LEFT JOIN effect_profile e ON u.effect_profile_id = e.id
            ORDER BY u.create_time DESC
        """
        return self._execute(sql, fetch_all=True)

    def create_user(self, username, bg_color, text_color, theme_id=None, effect_profile_id=None):
        sql = """
            INSERT INTO user_accounts (username, bg_color, text_color, theme_id, effect_profile_id, create_time, update_time)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """
        return self._execute(sql, (username, bg_color, text_color, theme_id, effect_profile_id), commit=True)

    def update_user(self, user_id, bg_color, text_color, theme_id=None, effect_profile_id=None):
        sql = """
            UPDATE user_accounts
            SET bg_color = %s,
                text_color = %s,
                theme_id = %s,
                effect_profile_id = %s,
                update_time = NOW()
            WHERE id = %s
        """
        self._execute(sql, (bg_color, text_color, theme_id, effect_profile_id, user_id), commit=True)

    def delete_user(self, user_id):
        self._execute("DELETE FROM user_accounts WHERE id = %s", (user_id,), commit=True)

    def get_theme_by_id(self, theme_id):
        return self._execute("SELECT * FROM theme_template WHERE id = %s", (theme_id,), fetch_one=True)

    def get_all_themes(self):
        return self._execute("SELECT * FROM theme_template ORDER BY category ASC, sort ASC, id ASC", fetch_all=True)

    def create_theme(self, data):
        sql = """
            INSERT INTO theme_template
              (name, category, background_color, title_color, body_color, button_color, card_color, sort)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self._execute(
            sql,
            (
                data["name"],
                data["category"],
                data["background_color"],
                data["title_color"],
                data["body_color"],
                data["button_color"],
                data["card_color"],
                data.get("sort", 0),
            ),
            commit=True,
        )

    def update_theme(self, theme_id, data):
        sql = """
            UPDATE theme_template
            SET name = %s,
                category = %s,
                background_color = %s,
                title_color = %s,
                body_color = %s,
                button_color = %s,
                card_color = %s,
                sort = %s,
                update_time = NOW()
            WHERE id = %s
        """
        self._execute(
            sql,
            (
                data["name"],
                data["category"],
                data["background_color"],
                data["title_color"],
                data["body_color"],
                data["button_color"],
                data["card_color"],
                data.get("sort", 0),
                theme_id,
            ),
            commit=True,
        )

    def delete_theme(self, theme_id):
        self._execute("UPDATE user_accounts SET theme_id = NULL WHERE theme_id = %s", (theme_id,), commit=True)
        self._execute("DELETE FROM theme_template WHERE id = %s", (theme_id,), commit=True)

    def get_effect_profile_by_id(self, profile_id):
        return self._execute("SELECT * FROM effect_profile WHERE id = %s", (profile_id,), fetch_one=True)

    def get_all_effect_profiles(self):
        return self._execute("SELECT * FROM effect_profile ORDER BY sort ASC, id ASC", fetch_all=True)

    def create_effect_profile(self, data):
        sql = """
            INSERT INTO effect_profile
              (name, welcome_effects, intro_effects, main_effects, closing_effects,
               particle_density, motion_level, glow_intensity, sort)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self._execute(
            sql,
            (
                data["name"],
                data["welcome_effects"],
                data["intro_effects"],
                data["main_effects"],
                data["closing_effects"],
                data["particle_density"],
                data["motion_level"],
                data["glow_intensity"],
                data.get("sort", 0),
            ),
            commit=True,
        )

    def update_effect_profile(self, profile_id, data):
        sql = """
            UPDATE effect_profile
            SET name = %s,
                welcome_effects = %s,
                intro_effects = %s,
                main_effects = %s,
                closing_effects = %s,
                particle_density = %s,
                motion_level = %s,
                glow_intensity = %s,
                sort = %s,
                update_time = NOW()
            WHERE id = %s
        """
        self._execute(
            sql,
            (
                data["name"],
                data["welcome_effects"],
                data["intro_effects"],
                data["main_effects"],
                data["closing_effects"],
                data["particle_density"],
                data["motion_level"],
                data["glow_intensity"],
                data.get("sort", 0),
                profile_id,
            ),
            commit=True,
        )

    def delete_effect_profile(self, profile_id):
        self._execute("UPDATE user_accounts SET effect_profile_id = NULL WHERE effect_profile_id = %s", (profile_id,), commit=True)
        self._execute("DELETE FROM effect_profile WHERE id = %s", (profile_id,), commit=True)

    def get_content_configs(self, mode=None):
        if mode:
            return self._execute("SELECT * FROM content_config WHERE mode = %s ORDER BY step_order ASC", (mode,), fetch_all=True)
        return self._execute("SELECT * FROM content_config ORDER BY mode ASC, step_order ASC", fetch_all=True)

    def upsert_content_configs(self, mode, items):
        conn = self._connect()
        with conn.cursor() as cursor:
            for item in items:
                cursor.execute(
                    """
                    INSERT INTO content_config (mode, step_key, step_order, title, body, update_time)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE
                      title = VALUES(title),
                      body = VALUES(body),
                      step_order = VALUES(step_order),
                      update_time = NOW()
                    """,
                    (mode, item["step_key"], item["step_order"], item["title"], item["body"]),
                )
        conn.commit()

    def seed_themes(self, items):
        conn = self._connect()
        with conn.cursor() as cursor:
            for item in items:
                cursor.execute(
                    """
                    INSERT INTO theme_template
                      (name, category, background_color, title_color, body_color, button_color, card_color, sort)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                      category = VALUES(category),
                      background_color = VALUES(background_color),
                      title_color = VALUES(title_color),
                      body_color = VALUES(body_color),
                      button_color = VALUES(button_color),
                      card_color = VALUES(card_color),
                      sort = VALUES(sort),
                      update_time = NOW()
                    """,
                    (
                        item["name"],
                        item["category"],
                        item["background_color"],
                        item["title_color"],
                        item["body_color"],
                        item["button_color"],
                        item["card_color"],
                        item["sort"],
                    ),
                )
        conn.commit()

    def seed_effect_profiles(self, items):
        conn = self._connect()
        with conn.cursor() as cursor:
            for item in items:
                cursor.execute(
                    """
                    INSERT INTO effect_profile
                      (name, welcome_effects, intro_effects, main_effects, closing_effects,
                       particle_density, motion_level, glow_intensity, sort)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                      welcome_effects = VALUES(welcome_effects),
                      intro_effects = VALUES(intro_effects),
                      main_effects = VALUES(main_effects),
                      closing_effects = VALUES(closing_effects),
                      particle_density = VALUES(particle_density),
                      motion_level = VALUES(motion_level),
                      glow_intensity = VALUES(glow_intensity),
                      sort = VALUES(sort),
                      update_time = NOW()
                    """,
                    (
                        item["name"],
                        item["welcome_effects"],
                        item["intro_effects"],
                        item["main_effects"],
                        item["closing_effects"],
                        item["particle_density"],
                        item["motion_level"],
                        item["glow_intensity"],
                        item["sort"],
                    ),
                )
        conn.commit()

    def init_tables(self):
        theme_seeds = [
            {"name": "绯绒玫瑰", "category": "高级粉色系", "background_color": "#fff1ee", "title_color": "#8a2d3b", "body_color": "#473334", "button_color": "#cf6f5d", "card_color": "#fffaf7", "sort": 1},
            {"name": "珊瑚暮光", "category": "高级粉色系", "background_color": "#ffe2d6", "title_color": "#a63d4b", "body_color": "#51353a", "button_color": "#ef7d57", "card_color": "#fff8f3", "sort": 2},
            {"name": "裸杏香槟", "category": "高级粉色系", "background_color": "#f7e6db", "title_color": "#9e5f52", "body_color": "#4c3e39", "button_color": "#d69a67", "card_color": "#fff9f4", "sort": 3},
            {"name": "紫藤书房", "category": "高级紫色系", "background_color": "#f2ecff", "title_color": "#5b3c8a", "body_color": "#332d46", "button_color": "#8062d6", "card_color": "#fcfbff", "sort": 11},
            {"name": "梅子夜幕", "category": "高级紫色系", "background_color": "#ead7e8", "title_color": "#7a2d5d", "body_color": "#3f2d3a", "button_color": "#b04f82", "card_color": "#fff7fb", "sort": 12},
            {"name": "烟紫石墨", "category": "高级紫色系", "background_color": "#ebe7f2", "title_color": "#5e5778", "body_color": "#2f3342", "button_color": "#7f88a6", "card_color": "#ffffff", "sort": 13},
            {"name": "海盐蓝调", "category": "高级蓝色系", "background_color": "#e9f7ff", "title_color": "#176087", "body_color": "#233b4d", "button_color": "#2a94c9", "card_color": "#fbfeff", "sort": 21},
            {"name": "群青航线", "category": "高级蓝色系", "background_color": "#dfeaf7", "title_color": "#244a7c", "body_color": "#233248", "button_color": "#4571d8", "card_color": "#f8fbff", "sort": 22},
            {"name": "青瓷晨雾", "category": "高级蓝色系", "background_color": "#e1f3ef", "title_color": "#2a6c6a", "body_color": "#294440", "button_color": "#3ea88f", "card_color": "#fbfffd", "sort": 23},
            {"name": "琥珀花园", "category": "多色系混搭主题", "background_color": "#fff3dd", "title_color": "#8e5a1f", "body_color": "#4a4036", "button_color": "#d98632", "card_color": "#fffaf0", "sort": 31},
            {"name": "绿野假日", "category": "多色系混搭主题", "background_color": "#edf6e4", "title_color": "#456a34", "body_color": "#3b4633", "button_color": "#89b04a", "card_color": "#fbfff8", "sort": 32},
            {"name": "晴橙假信", "category": "多色系混搭主题", "background_color": "#ffe9d2", "title_color": "#9f4b14", "body_color": "#4f392f", "button_color": "#ff8f3d", "card_color": "#fff8f1", "sort": 33},
        ]
        effect_seeds = [
            {"name": "默认高级流光", "welcome_effects": "mist-glow,light-particles", "intro_effects": "silk-flow,letter-unfold", "main_effects": "stardust,festival-bokeh,card-highlight", "closing_effects": "signature-draw,seal-fade,afterglow", "particle_density": 0.65, "motion_level": 0.55, "glow_intensity": 0.72, "sort": 1},
            {"name": "庆典星幕", "welcome_effects": "light-particles,mist-glow", "intro_effects": "letter-unfold", "main_effects": "stardust,festival-bokeh", "closing_effects": "signature-draw,afterglow", "particle_density": 0.82, "motion_level": 0.7, "glow_intensity": 0.82, "sort": 2},
            {"name": "书信薄纱", "welcome_effects": "mist-glow", "intro_effects": "silk-flow,letter-unfold", "main_effects": "card-highlight", "closing_effects": "signature-draw,seal-fade", "particle_density": 0.35, "motion_level": 0.42, "glow_intensity": 0.6, "sort": 3},
        ]

        conn = self._connect()
        with conn.cursor() as cursor:
            if not self._table_exists("system_settings"):
                cursor.execute(
                    """
                    CREATE TABLE `system_settings` (
                      `id` INT NOT NULL AUTO_INCREMENT,
                      `global_mode` VARCHAR(20) NOT NULL DEFAULT 'birthday',
                      `current_nearest_festival` VARCHAR(50) NOT NULL DEFAULT '',
                      `birthday_default_text` TEXT NOT NULL,
                      `festival_default_text` TEXT NOT NULL,
                      `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
            else:
                if not self._column_exists("system_settings", "global_mode"):
                    cursor.execute("ALTER TABLE system_settings ADD COLUMN global_mode VARCHAR(20) NOT NULL DEFAULT 'birthday'")
                if not self._column_exists("system_settings", "current_nearest_festival"):
                    cursor.execute("ALTER TABLE system_settings ADD COLUMN current_nearest_festival VARCHAR(50) NOT NULL DEFAULT ''")
                if not self._column_exists("system_settings", "birthday_default_text"):
                    cursor.execute("ALTER TABLE system_settings ADD COLUMN birthday_default_text TEXT NOT NULL")
                if not self._column_exists("system_settings", "festival_default_text"):
                    cursor.execute("ALTER TABLE system_settings ADD COLUMN festival_default_text TEXT NOT NULL")
                if not self._column_exists("system_settings", "update_time"):
                    cursor.execute("ALTER TABLE system_settings ADD COLUMN update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")

            if not self._table_exists("user_accounts"):
                cursor.execute(
                    """
                    CREATE TABLE `user_accounts` (
                      `id` INT NOT NULL AUTO_INCREMENT,
                      `username` VARCHAR(30) NOT NULL,
                      `bg_color` VARCHAR(20) NOT NULL DEFAULT '#fef5f8',
                      `text_color` VARCHAR(20) NOT NULL DEFAULT '#333333',
                      `theme_id` INT NULL,
                      `effect_profile_id` INT NULL,
                      `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`),
                      UNIQUE KEY `uk_username` (`username`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
            else:
                if not self._column_exists("user_accounts", "bg_color"):
                    cursor.execute("ALTER TABLE user_accounts ADD COLUMN bg_color VARCHAR(20) NOT NULL DEFAULT '#fef5f8'")
                if not self._column_exists("user_accounts", "text_color"):
                    cursor.execute("ALTER TABLE user_accounts ADD COLUMN text_color VARCHAR(20) NOT NULL DEFAULT '#333333'")
                if not self._column_exists("user_accounts", "theme_id"):
                    cursor.execute("ALTER TABLE user_accounts ADD COLUMN theme_id INT NULL")
                if not self._column_exists("user_accounts", "effect_profile_id"):
                    cursor.execute("ALTER TABLE user_accounts ADD COLUMN effect_profile_id INT NULL")

            if not self._table_exists("festival_list"):
                cursor.execute(
                    """
                    CREATE TABLE `festival_list` (
                      `id` INT NOT NULL AUTO_INCREMENT,
                      `festival_name` VARCHAR(50) NOT NULL,
                      `month` INT NOT NULL,
                      `day` INT NOT NULL,
                      `is_lunar` TINYINT(1) NOT NULL DEFAULT 0,
                      `sort` INT NOT NULL DEFAULT 0,
                      PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )

            if not self._table_exists("theme_template"):
                cursor.execute(
                    """
                    CREATE TABLE `theme_template` (
                      `id` INT NOT NULL AUTO_INCREMENT,
                      `name` VARCHAR(60) NOT NULL,
                      `category` VARCHAR(30) NOT NULL,
                      `background_color` VARCHAR(20) NOT NULL,
                      `title_color` VARCHAR(20) NOT NULL,
                      `body_color` VARCHAR(20) NOT NULL,
                      `button_color` VARCHAR(20) NOT NULL,
                      `card_color` VARCHAR(20) NOT NULL,
                      `sort` INT NOT NULL DEFAULT 0,
                      `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`),
                      UNIQUE KEY `uk_theme_name` (`name`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )

            if not self._table_exists("effect_profile"):
                cursor.execute(
                    """
                    CREATE TABLE `effect_profile` (
                      `id` INT NOT NULL AUTO_INCREMENT,
                      `name` VARCHAR(80) NOT NULL,
                      `welcome_effects` VARCHAR(200) NOT NULL,
                      `intro_effects` VARCHAR(200) NOT NULL,
                      `main_effects` VARCHAR(200) NOT NULL,
                      `closing_effects` VARCHAR(200) NOT NULL,
                      `particle_density` DECIMAL(4,2) NOT NULL DEFAULT 0.65,
                      `motion_level` DECIMAL(4,2) NOT NULL DEFAULT 0.55,
                      `glow_intensity` DECIMAL(4,2) NOT NULL DEFAULT 0.72,
                      `sort` INT NOT NULL DEFAULT 0,
                      `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`),
                      UNIQUE KEY `uk_effect_profile_name` (`name`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )

            if not self._table_exists("content_config"):
                cursor.execute(
                    """
                    CREATE TABLE `content_config` (
                      `id` INT NOT NULL AUTO_INCREMENT,
                      `mode` VARCHAR(20) NOT NULL,
                      `step_key` VARCHAR(30) NOT NULL,
                      `step_order` INT NOT NULL,
                      `title` VARCHAR(120) NOT NULL,
                      `body` TEXT NOT NULL,
                      `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      PRIMARY KEY (`id`),
                      UNIQUE KEY `uk_mode_step` (`mode`, `step_key`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )

            conn.commit()

            cursor.execute("SELECT COUNT(*) as cnt FROM system_settings")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """
                    INSERT INTO system_settings (id, global_mode, birthday_default_text, festival_default_text)
                    VALUES (1, 'birthday',
                    '愿你的每一天都充满阳光与欢笑，愿所有美好如期而至。生日快乐！',
                    '祝你节日快乐，阖家幸福，万事如意！')
                    """
                )
                conn.commit()

            cursor.execute("SELECT COUNT(*) as cnt FROM festival_list")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """
                    INSERT INTO festival_list (festival_name, month, day, is_lunar, sort) VALUES
                    ('元旦', 1, 1, 0, 1),
                    ('春节', 1, 1, 1, 2),
                    ('情人节', 2, 14, 0, 3),
                    ('母亲节', 5, 12, 0, 4),
                    ('中秋节', 8, 15, 1, 5),
                    ('圣诞节', 12, 25, 0, 6)
                    """
                )
                conn.commit()

        self.seed_themes(theme_seeds)
        self.seed_effect_profiles(effect_seeds)


blessing_db = BlessingDB()
