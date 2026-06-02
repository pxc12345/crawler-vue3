-- 祝福系统升级 SQL：主题模板 + 特效方案 + 分步文案

CREATE TABLE IF NOT EXISTS `theme_template` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `effect_profile` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `content_config` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET @theme_id_col_exists = (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'user_accounts'
    AND column_name = 'theme_id'
);
SET @theme_id_sql = IF(
  @theme_id_col_exists = 0,
  'ALTER TABLE `user_accounts` ADD COLUMN `theme_id` INT NULL',
  'SELECT 1'
);
PREPARE theme_id_stmt FROM @theme_id_sql;
EXECUTE theme_id_stmt;
DEALLOCATE PREPARE theme_id_stmt;

SET @effect_id_col_exists = (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'user_accounts'
    AND column_name = 'effect_profile_id'
);
SET @effect_id_sql = IF(
  @effect_id_col_exists = 0,
  'ALTER TABLE `user_accounts` ADD COLUMN `effect_profile_id` INT NULL',
  'SELECT 1'
);
PREPARE effect_id_stmt FROM @effect_id_sql;
EXECUTE effect_id_stmt;
DEALLOCATE PREPARE effect_id_stmt;

INSERT INTO `theme_template`
(`name`, `category`, `background_color`, `title_color`, `body_color`, `button_color`, `card_color`, `sort`)
VALUES
('绯绒玫瑰', '高级粉色系', '#fff1ee', '#8a2d3b', '#473334', '#cf6f5d', '#fffaf7', 1),
('珊瑚暮光', '高级粉色系', '#ffe2d6', '#a63d4b', '#51353a', '#ef7d57', '#fff8f3', 2),
('裸杏香槟', '高级粉色系', '#f7e6db', '#9e5f52', '#4c3e39', '#d69a67', '#fff9f4', 3),
('紫藤书房', '高级紫色系', '#f2ecff', '#5b3c8a', '#332d46', '#8062d6', '#fcfbff', 11),
('梅子夜幕', '高级紫色系', '#ead7e8', '#7a2d5d', '#3f2d3a', '#b04f82', '#fff7fb', 12),
('烟紫石墨', '高级紫色系', '#ebe7f2', '#5e5778', '#2f3342', '#7f88a6', '#ffffff', 13),
('海盐蓝调', '高级蓝色系', '#e9f7ff', '#176087', '#233b4d', '#2a94c9', '#fbfeff', 21),
('群青航线', '高级蓝色系', '#dfeaf7', '#244a7c', '#233248', '#4571d8', '#f8fbff', 22),
('青瓷晨雾', '高级蓝色系', '#e1f3ef', '#2a6c6a', '#294440', '#3ea88f', '#fbfffd', 23),
('琥珀花园', '多色系混搭主题', '#fff3dd', '#8e5a1f', '#4a4036', '#d98632', '#fffaf0', 31),
('绿野假日', '多色系混搭主题', '#edf6e4', '#456a34', '#3b4633', '#89b04a', '#fbfff8', 32),
('晴橙假信', '多色系混搭主题', '#ffe9d2', '#9f4b14', '#4f392f', '#ff8f3d', '#fff8f1', 33)
ON DUPLICATE KEY UPDATE
  `category` = VALUES(`category`),
  `background_color` = VALUES(`background_color`),
  `title_color` = VALUES(`title_color`),
  `body_color` = VALUES(`body_color`),
  `button_color` = VALUES(`button_color`),
  `card_color` = VALUES(`card_color`),
  `sort` = VALUES(`sort`);

INSERT INTO `effect_profile`
(`name`, `welcome_effects`, `intro_effects`, `main_effects`, `closing_effects`, `particle_density`, `motion_level`, `glow_intensity`, `sort`)
VALUES
('默认高级流光', 'mist-glow,light-particles', 'silk-flow,letter-unfold', 'stardust,festival-bokeh,card-highlight', 'signature-draw,seal-fade,afterglow', 0.65, 0.55, 0.72, 1),
('庆典星幕', 'light-particles,mist-glow', 'letter-unfold', 'stardust,festival-bokeh', 'signature-draw,afterglow', 0.82, 0.70, 0.82, 2),
('书信薄纱', 'mist-glow', 'silk-flow,letter-unfold', 'card-highlight', 'signature-draw,seal-fade', 0.35, 0.42, 0.60, 3)
ON DUPLICATE KEY UPDATE
  `welcome_effects` = VALUES(`welcome_effects`),
  `intro_effects` = VALUES(`intro_effects`),
  `main_effects` = VALUES(`main_effects`),
  `closing_effects` = VALUES(`closing_effects`),
  `particle_density` = VALUES(`particle_density`),
  `motion_level` = VALUES(`motion_level`),
  `glow_intensity` = VALUES(`glow_intensity`),
  `sort` = VALUES(`sort`);

INSERT INTO `content_config` (`mode`, `step_key`, `step_order`, `title`, `body`)
VALUES
('birthday', 'welcome', 1, '今夜为你亮灯', '把日历翻到今天，连风都像替你轻声报喜。愿你推开这一页时，先被温柔接住，再被喜悦慢慢包围。'),
('birthday', 'intro', 2, '把好时光留给你', '愿你走过的每一步都算数，认真喜欢过的事情都能开花，努力熬过的夜晚都能在未来变成星光。'),
('birthday', 'main', 3, '愿望开始靠近', '愿你新一岁的生活有热烈也有安稳，有奔赴远方的勇气，也有回到日常的松弛。愿欢喜有回应，期待有着落，生日快乐。'),
('birthday', 'closing', 4, '把祝福珍藏', '把这一份偏爱好好收下吧。愿它陪你度过明亮的时刻，也陪你穿过普通的日子，提醒你一直值得被认真祝福。'),
('festival', 'welcome', 1, '节日已至', '节日像一封刚拆开的信，先把热闹送到门前，再把惦念慢慢放进心里。今天这一份祝福，也专门为你而来。'),
('festival', 'intro', 2, '愿此刻被照亮', '愿你无论身在何处，都能在这个节点里感受到陪伴、松弛和被惦记的安心，让生活暂时停下来，对你多一点温柔。'),
('festival', 'main', 3, '平安喜乐常在', '愿这个节日替你带来轻松和好消息，愿平安常在，喜乐常在，心之所向都有回音。'),
('festival', 'closing', 4, '心意缓缓落下', '把这份节日心意留在今天，也带进之后的日子里。愿你接下来遇见的人和事，都能继续把温暖递给你。')
ON DUPLICATE KEY UPDATE
  `step_order` = VALUES(`step_order`),
  `title` = VALUES(`title`),
  `body` = VALUES(`body`);
