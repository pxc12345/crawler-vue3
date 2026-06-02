-- ========================================
-- 专属祝福网站 - 完整建表SQL
-- 数据库: MySQL 8.0+
-- ========================================

-- 全局配置表
CREATE TABLE IF NOT EXISTS `system_settings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `global_mode` VARCHAR(20) NOT NULL DEFAULT 'birthday' COMMENT '全局模式：birthday生日/festival节日',
  `current_nearest_festival` VARCHAR(50) NOT NULL DEFAULT '' COMMENT '当前自动匹配的最近节日名称',
  `birthday_default_text` TEXT NOT NULL COMMENT '生日模式全局默认祝福文案',
  `festival_default_text` TEXT NOT NULL COMMENT '节日模式全局默认祝福文案',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '配置更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='全局配置表';

-- 初始化默认配置
INSERT INTO `system_settings` (`id`, `global_mode`, `birthday_default_text`, `festival_default_text`)
VALUES (1, 'birthday',
  '愿你的每一天都充满阳光与欢笑，愿所有美好都如期而至。生日快乐！',
  '祝你节日快乐，阖家幸福，万事如意！')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- 普通用户账号表
CREATE TABLE IF NOT EXISTS `user_accounts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(30) NOT NULL COMMENT '登录账号名',
  `bg_color` VARCHAR(20) NOT NULL DEFAULT '#fef5f8' COMMENT '专属页面背景色',
  `text_color` VARCHAR(20) NOT NULL DEFAULT '#333333' COMMENT '专属页面文字色',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '账号创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '账号更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='普通用户账号表';

-- 节日数据表
CREATE TABLE IF NOT EXISTS `festival_list` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `festival_name` VARCHAR(50) NOT NULL COMMENT '节日名称',
  `month` INT NOT NULL COMMENT '月份',
  `day` INT NOT NULL COMMENT '日期',
  `is_lunar` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0=公历 1=农历',
  `sort` INT NOT NULL DEFAULT 0 COMMENT '排序权重',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='节日数据表';

-- 初始化6个默认节日数据
INSERT INTO `festival_list` (`festival_name`, `month`, `day`, `is_lunar`, `sort`) VALUES
('元旦', 1, 1, 0, 1),
('春节', 1, 1, 1, 2),
('情人节', 2, 14, 0, 3),
('母亲节', 5, 12, 0, 4),
('中秋节', 8, 15, 1, 5),
('圣诞节', 12, 25, 0, 6)
ON DUPLICATE KEY UPDATE `id`=`id`;