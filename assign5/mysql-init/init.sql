-- MySQL initialization: tạo tất cả databases cho các microservices
CREATE DATABASE IF NOT EXISTS db_staff CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_customer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_catalog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_book CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_cart CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_order CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_ship CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_pay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_comment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_recommender CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Cấp quyền cho root từ mọi host
GRANT ALL PRIVILEGES ON db_staff.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_manager.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_customer.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_catalog.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_book.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_cart.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_order.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_ship.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_pay.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_comment.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_recommender.* TO 'root'@'%';
FLUSH PRIVILEGES;
