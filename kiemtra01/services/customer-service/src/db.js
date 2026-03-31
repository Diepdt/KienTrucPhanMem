const mysql = require("mysql2/promise");
const bcrypt = require("bcryptjs");

const pool = mysql.createPool({
  host: process.env.MYSQL_HOST || "localhost",
  port: Number(process.env.MYSQL_PORT || 3306),
  user: process.env.MYSQL_USER || "root",
  password: process.env.MYSQL_PASSWORD || "root123",
  database: process.env.MYSQL_DATABASE || "identity_db",
  waitForConnections: true,
  connectionLimit: 10
});

async function query(sql, params = []) {
  const [rows] = await pool.execute(sql, params);
  return rows;
}

async function initDatabase() {
  await query(`
    CREATE TABLE IF NOT EXISTS customers (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(100) NOT NULL UNIQUE,
      password_hash VARCHAR(255) NOT NULL,
      full_name VARCHAR(150) NOT NULL,
      address VARCHAR(255),
      phone VARCHAR(30),
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
  `);

  await query(`
    CREATE TABLE IF NOT EXISTS carts (
      id INT AUTO_INCREMENT PRIMARY KEY,
      customer_id INT NOT NULL,
      status VARCHAR(30) NOT NULL DEFAULT 'active',
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      CONSTRAINT fk_cart_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
  `);

  await query(`
    CREATE TABLE IF NOT EXISTS cart_items (
      id INT AUTO_INCREMENT PRIMARY KEY,
      cart_id INT NOT NULL,
      item_id INT NOT NULL,
      quantity INT NOT NULL DEFAULT 1,
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      CONSTRAINT fk_item_cart FOREIGN KEY (cart_id) REFERENCES carts(id)
    );
  `);

  await query(`
    CREATE TABLE IF NOT EXISTS orders (
      id INT AUTO_INCREMENT PRIMARY KEY,
      customer_id INT NOT NULL,
      receiver_name VARCHAR(150) NOT NULL,
      receiver_phone VARCHAR(30) NOT NULL,
      receiver_address VARCHAR(255) NOT NULL,
      payment_method VARCHAR(50) NOT NULL DEFAULT 'cod',
      total_amount BIGINT NOT NULL DEFAULT 0,
      status VARCHAR(30) NOT NULL DEFAULT 'pending',
      note TEXT,
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
  `);

  await query(`
    CREATE TABLE IF NOT EXISTS order_items (
      id INT AUTO_INCREMENT PRIMARY KEY,
      order_id INT NOT NULL,
      item_id INT NOT NULL,
      item_name VARCHAR(255) NOT NULL,
      item_price BIGINT NOT NULL,
      quantity INT NOT NULL DEFAULT 1,
      CONSTRAINT fk_order_item FOREIGN KEY (order_id) REFERENCES orders(id)
    );
  `);

  const existing = await query("SELECT id FROM customers WHERE username = ? LIMIT 1", ["customer01"]);
  if (existing.length === 0) {
    const hash = await bcrypt.hash("customer123", 10);
    await query(
      `
      INSERT INTO customers (username, password_hash, full_name, address, phone)
      VALUES (?, ?, ?, ?, ?)
      `,
      ["customer01", hash, "Default Customer", "HCM City", "0900000000"]
    );
  }
}

module.exports = {
  query,
  initDatabase
};
