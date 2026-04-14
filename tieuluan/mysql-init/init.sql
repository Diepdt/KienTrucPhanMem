-- MySQL initialization: tạo tất cả databases cho các microservices
CREATE DATABASE IF NOT EXISTS tieuluan_staff CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_customer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_catalog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_book CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_cart CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_order CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_ship CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_pay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_comment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_recommender CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_cloth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_laptop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_mobile CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tieuluan_gateway CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Cấp quyền cho root từ mọi host
GRANT ALL PRIVILEGES ON tieuluan_staff.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_manager.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_customer.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_catalog.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_book.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_cart.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_order.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_ship.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_pay.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_comment.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_recommender.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_agent.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_cloth.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_laptop.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_mobile.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON tieuluan_gateway.* TO 'root'@'%';
FLUSH PRIVILEGES;
