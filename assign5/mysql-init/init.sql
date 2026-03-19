-- MySQL initialization: tạo tất cả databases cho các microservices
CREATE DATABASE IF NOT EXISTS assign5_staff CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_customer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_catalog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_book CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_cart CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_order CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_ship CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_pay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_comment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_recommender CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS assign5_cloth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Cấp quyền cho root từ mọi host
GRANT ALL PRIVILEGES ON assign5_staff.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_manager.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_customer.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_catalog.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_book.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_cart.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_order.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_ship.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_pay.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_comment.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_recommender.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_agent.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON assign5_cloth.* TO 'root'@'%';
FLUSH PRIVILEGES;
