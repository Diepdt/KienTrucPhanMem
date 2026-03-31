const express = require("express");
const { initDatabase, query } = require("./db");

const app = express();
const port = Number(process.env.PORT || 4001);

app.use(express.json());

function normalizeProductRow(row) {
  return {
    id: row.id,
    type: row.type,
    name: row.name,
    price: Number(row.price),
    detailDesc: row.detail_desc || "",
    shortDesc: row.short_desc || "",
    quantity: row.quantity,
    sold: row.sold,
    factory: row.factory || "",
    target: row.target || "",
    image: row.image || ""
  };
}

app.get("/health", async (_req, res) => {
  res.json({ ok: true, service: "catalog-service" });
});

app.get("/items", async (req, res) => {
  const q = (req.query.q || "").toString().trim();
  const type = (req.query.type || "").toString().trim().toLowerCase();

  const where = [];
  const params = [];

  if (q) {
    params.push(`%${q}%`);
    where.push(`(name ILIKE $${params.length} OR short_desc ILIKE $${params.length})`);
  }

  if (type === "laptop" || type === "mobile") {
    params.push(type);
    where.push(`type = $${params.length}`);
  }

  const whereSql = where.length > 0 ? `WHERE ${where.join(" AND ")}` : "";
  const result = await query(
    `SELECT * FROM products ${whereSql} ORDER BY id DESC;`,
    params
  );

  res.json({
    items: result.rows.map(normalizeProductRow)
  });
});

app.get("/items/:id", async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ message: "Invalid product id" });
  }

  const result = await query("SELECT * FROM products WHERE id = $1;", [id]);
  if (result.rows.length === 0) {
    return res.status(404).json({ message: "Product not found" });
  }

  return res.json({ item: normalizeProductRow(result.rows[0]) });
});

app.post("/items", async (req, res) => {
  const {
    type,
    name,
    price,
    detailDesc,
    shortDesc,
    quantity,
    sold,
    factory,
    target,
    image
  } = req.body;

  const normalizedType = (type || "").toLowerCase();
  if (!["laptop", "mobile"].includes(normalizedType)) {
    return res.status(400).json({ message: "type must be laptop or mobile" });
  }

  if (!name || Number(price) <= 0) {
    return res.status(400).json({ message: "name and price are required" });
  }

  const result = await query(
    `
    INSERT INTO products
      (type, name, price, detail_desc, short_desc, quantity, sold, factory, target, image, updated_at)
    VALUES
      ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
    RETURNING *;
    `,
    [
      normalizedType,
      name,
      Number(price),
      detailDesc || "",
      shortDesc || "",
      Number(quantity || 0),
      Number(sold || 0),
      factory || "",
      target || "",
      image || ""
    ]
  );

  return res.status(201).json({ item: normalizeProductRow(result.rows[0]) });
});

app.put("/items/:id", async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ message: "Invalid product id" });
  }

  const {
    type,
    name,
    price,
    detailDesc,
    shortDesc,
    quantity,
    sold,
    factory,
    target,
    image
  } = req.body;

  const existing = await query("SELECT * FROM products WHERE id = $1;", [id]);
  if (existing.rows.length === 0) {
    return res.status(404).json({ message: "Product not found" });
  }

  const current = existing.rows[0];
  const normalizedType = (type || current.type).toLowerCase();

  const updated = await query(
    `
    UPDATE products
    SET type = $1,
        name = $2,
        price = $3,
        detail_desc = $4,
        short_desc = $5,
        quantity = $6,
        sold = $7,
        factory = $8,
        target = $9,
        image = $10,
        updated_at = NOW()
    WHERE id = $11
    RETURNING *;
    `,
    [
      normalizedType,
      name || current.name,
      Number(price ?? current.price),
      detailDesc ?? current.detail_desc,
      shortDesc ?? current.short_desc,
      Number(quantity ?? current.quantity),
      Number(sold ?? current.sold),
      factory ?? current.factory,
      target ?? current.target,
      image ?? current.image,
      id
    ]
  );

  return res.json({ item: normalizeProductRow(updated.rows[0]) });
});

app.delete("/items/:id", async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ message: "Invalid product id" });
  }

  const result = await query("DELETE FROM products WHERE id = $1 RETURNING id;", [id]);
  if (result.rows.length === 0) {
    return res.status(404).json({ message: "Product not found" });
  }

  return res.json({ deleted: true, id });
});

app.use((err, _req, res, _next) => {
  console.error("catalog-service error", err);
  res.status(500).json({ message: "Internal server error" });
});

initDatabase()
  .then(() => {
    app.listen(port, () => {
      console.log(`catalog-service running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Failed to initialize catalog database", error);
    process.exit(1);
  });
