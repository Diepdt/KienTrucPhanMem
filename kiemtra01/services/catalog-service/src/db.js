const { Pool } = require("pg");

const pool = new Pool({
  host: process.env.POSTGRES_HOST || "localhost",
  port: Number(process.env.POSTGRES_PORT || 5432),
  user: process.env.POSTGRES_USER || "postgres",
  password: process.env.POSTGRES_PASSWORD || "postgres123",
  database: process.env.POSTGRES_DB || "catalog_db"
});

async function query(text, params = []) {
  const result = await pool.query(text, params);
  return result;
}

async function initDatabase() {
  await query(`
    CREATE TABLE IF NOT EXISTS products (
      id SERIAL PRIMARY KEY,
      type VARCHAR(20) NOT NULL CHECK (type IN ('laptop', 'mobile')),
      name VARCHAR(255) NOT NULL,
      price NUMERIC(12, 2) NOT NULL,
      detail_desc TEXT,
      short_desc TEXT,
      quantity INTEGER NOT NULL DEFAULT 0,
      sold INTEGER NOT NULL DEFAULT 0,
      factory VARCHAR(100),
      target VARCHAR(100),
      image VARCHAR(500),
      created_at TIMESTAMP NOT NULL DEFAULT NOW(),
      updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
  `);

  await query(`
    CREATE INDEX IF NOT EXISTS idx_products_type ON products(type);
  `);

  await query(`
    CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
  `);

  const countResult = await query("SELECT COUNT(*)::int AS total FROM products;");
  if (countResult.rows[0].total === 0) {
    await query(
      `
      INSERT INTO products (type, name, price, detail_desc, short_desc, quantity, sold, factory, target, image)
      VALUES
        ('laptop', 'MacBook Air M3 13-inch', 28990000, 'Laptop Apple M3 cho cong viec va hoc tap.', 'Mong nhe, pin lau, chip M3.', 25, 3, 'APPLE', 'SINHVIEN-VANPHONG', 'https://images.unsplash.com/photo-1517336714739-489689fd1ca8?w=800'),
        ('laptop', 'ASUS ROG Strix G16', 35990000, 'Laptop gaming hieu nang cao RTX.', 'Man hinh 165Hz, phu hop game thu.', 12, 2, 'ASUS', 'GAMING', 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800'),
        ('mobile', 'iPhone 15 Pro', 26990000, 'Dien thoai cao cap chip A17 Pro.', 'Camera manh, hieu nang tot.', 40, 5, 'APPLE', 'DOANH-NHAN', 'https://images.unsplash.com/photo-1592286927505-1def25115558?w=800'),
        ('mobile', 'Samsung Galaxy S24', 21990000, 'Flagship Android man hinh dep.', 'Hieu nang can bang, camera tot.', 30, 4, 'SAMSUNG', 'MONG-NHE', 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800');
      `
    );
  }
}

module.exports = {
  query,
  initDatabase
};
