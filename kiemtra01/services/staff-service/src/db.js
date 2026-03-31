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
    CREATE TABLE IF NOT EXISTS staffs (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(100) NOT NULL UNIQUE,
      password_hash VARCHAR(255) NOT NULL,
      full_name VARCHAR(150) NOT NULL,
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
  `);

  const existing = await query("SELECT id FROM staffs WHERE username = ? LIMIT 1", ["staffadmin"]);
  if (existing.length === 0) {
    const hash = await bcrypt.hash("staff123", 10);
    await query(
      "INSERT INTO staffs (username, password_hash, full_name) VALUES (?, ?, ?)",
      ["staffadmin", hash, "Staff Admin"]
    );
  }
}

module.exports = {
  query,
  initDatabase
};
