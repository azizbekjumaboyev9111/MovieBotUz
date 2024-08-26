import pymysql


DB_NAME="kino"
DB_PASSWORD="parol"
DB_USERNAME="kino"
DB_port = 3306
DB_SERVER = "localhost"


# Ma'lumotlar bazasiga ulanish uchun bog'lanishni o'rnatish
conn = pymysql.connect(host=DB_SERVER, user=DB_USERNAME, password=DB_PASSWORD, database=DB_NAME, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

cursor = conn.cursor()


# SQL jadvalini yaratish so'rovlari

create_mailing_table = """
CREATE TABLE `mailing` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status` varchar(50) NOT NULL,
  `chat_id` bigint NOT NULL,
  `message_id` bigint NOT NULL,
  `reply_markup` text NOT NULL,
  `mail_type` text NOT NULL,
  `offset` bigint NOT NULL,
  `send` bigint NOT NULL,
  `not_send` bigint NOT NULL,
  `type` text NOT NULL,
  `location` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

create_users_table = """
CREATE TABLE `users` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` varchar(100) NOT NULL,
    `status` TEXT,
PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

create_admins_table = """
CREATE TABLE `admins` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` varchar(100) NOT NULL,
    `name` TEXT,
PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

create_groups_table = """
CREATE TABLE `groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `status` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2092 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""


create_ads_table = """
CREATE TABLE `ads` (
    `id` int NOT NULL AUTO_INCREMENT,
    `text` varchar(500) NOT NULL,
    `url` TEXT,
PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""


create_channels_table = """
CREATE TABLE `channels` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `channel_id` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `channel_id` (`channel_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

create_settings_table = """
CREATE TABLE `settings` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL  DEFAULT 'channels',
  `value` varchar(255) NOT NULL DEFAULT 'True',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""



create_movie_table = """
CREATE TABLE `movies` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` TEXT,
    `quality` TEXT,
    `file_id` TEXT,
    `file_size` TEXT,
    `views` TEXT,
PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

create_saved_table = """
CREATE TABLE `saved` (
    `id` int NOT NULL AUTO_INCREMENT,
    `user_id` TEXT,
    `kino_id` TEXT,
PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

# cursor.execute(create_ads_table)
# cursor.execute(create_admins_table)
# cursor.execute(create_mailing_table)
# cursor.execute(create_users_table)
# cursor.execute(create_channels_table)
# cursor.execute(create_settings_table)
# cursor.execute(create_movie_table)
# cursor.execute(create_saved_table)
cursor.execute(create_groups_table)
# O'zgarishlarni saqlash va ulanishni yopish
conn.commit()
cursor.close()
conn.close()

print("Jadvallar muvaffaqiyatli yaratildi.")
