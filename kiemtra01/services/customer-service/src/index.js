const express = require("express");
const axios = require("axios");
const bcrypt = require("bcryptjs");
const { initDatabase, query } = require("./db");

const app = express();
const port = Number(process.env.PORT || 4002);
const catalogServiceUrl = process.env.CATALOG_SERVICE_URL || "http://localhost:4001";

app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ ok: true, service: "customer-service" });
});

app.post("/auth/register", async (req, res) => {
  const { username, password, fullName, address, phone } = req.body;

  if (!username || !password || !fullName) {
    return res.status(400).json({ message: "username, password, fullName are required" });
  }

  const existing = await query("SELECT id FROM customers WHERE username = ? LIMIT 1", [username]);
  if (existing.length > 0) {
    return res.status(409).json({ message: "Username already exists" });
  }

  const passwordHash = await bcrypt.hash(password, 10);
  const result = await query(
    `
    INSERT INTO customers (username, password_hash, full_name, address, phone)
    VALUES (?, ?, ?, ?, ?)
    `,
    [username, passwordHash, fullName, address || "", phone || ""]
  );

  return res.status(201).json({
    customer: {
      id: result.insertId,
      username,
      fullName,
      address: address || "",
      phone: phone || ""
    }
  });
});

app.post("/auth/login", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ message: "username and password are required" });
  }

  const users = await query(
    "SELECT id, username, password_hash, full_name, address, phone FROM customers WHERE username = ? LIMIT 1",
    [username]
  );

  if (users.length === 0) {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  const user = users[0];
  const matched = await bcrypt.compare(password, user.password_hash);
  if (!matched) {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  return res.json({
    customer: {
      id: user.id,
      username: user.username,
      fullName: user.full_name,
      address: user.address,
      phone: user.phone
    }
  });
});

app.post("/cart", async (req, res) => {
  const { customerId } = req.body;
  if (!customerId || Number(customerId) <= 0) {
    return res.status(400).json({ message: "customerId is required" });
  }

  const exists = await query("SELECT id FROM customers WHERE id = ? LIMIT 1", [Number(customerId)]);
  if (exists.length === 0) {
    return res.status(404).json({ message: "Customer not found" });
  }

  const result = await query(
    "INSERT INTO carts (customer_id, status) VALUES (?, 'active')",
    [Number(customerId)]
  );

  return res.status(201).json({ cart: { id: result.insertId, customerId: Number(customerId), status: "active" } });
});

app.post("/cart/items", async (req, res) => {
  const { customerId, itemId, quantity } = req.body;

  if (!customerId || !itemId) {
    return res.status(400).json({ message: "customerId and itemId are required" });
  }

  const cartRows = await query(
    "SELECT id FROM carts WHERE customer_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1",
    [Number(customerId)]
  );

  let cartId;
  if (cartRows.length === 0) {
    const cartResult = await query(
      "INSERT INTO carts (customer_id, status) VALUES (?, 'active')",
      [Number(customerId)]
    );
    cartId = cartResult.insertId;
  } else {
    cartId = cartRows[0].id;
  }

  await query(
    "INSERT INTO cart_items (cart_id, item_id, quantity) VALUES (?, ?, ?)",
    [cartId, Number(itemId), Number(quantity || 1)]
  );

  return res.status(201).json({ message: "Item added to cart", cartId });
});

app.get("/cart/:customerId", async (req, res) => {
  const { customerId } = req.params;
  const cartRows = await query(
    "SELECT id FROM carts WHERE customer_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1",
    [Number(customerId)]
  );
  if (cartRows.length === 0) {
    return res.json({ items: [] });
  }
  const items = await query(
    "SELECT id, item_id as itemId, quantity FROM cart_items WHERE cart_id = ?",
    [cartRows[0].id]
  );
  
  // Aggregate items by itemId
  const aggregated = {};
  for(const item of items) {
    if(!aggregated[item.itemId]) {
        aggregated[item.itemId] = { ...item };
    } else {
        aggregated[item.itemId].quantity += item.quantity;
    }
  }
  return res.json({ items: Object.values(aggregated) });
});

app.delete("/cart/:customerId/items/:itemId", async (req, res) => {
  const { customerId, itemId } = req.params;
  const cartRows = await query(
    "SELECT id FROM carts WHERE customer_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1",
    [Number(customerId)]
  );
  if (cartRows.length > 0) {
    await query("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?", [cartRows[0].id, Number(itemId)]);
  }
  return res.json({ success: true });
});

app.post("/orders", async (req, res) => {
  const { customerId, receiverName, receiverPhone, receiverAddress, paymentMethod, note, items } = req.body;

  if (!customerId || !receiverName || !receiverPhone || !receiverAddress || !items || items.length === 0) {
    return res.status(400).json({ message: "Thiếu thông tin đặt hàng" });
  }

  const totalAmount = items.reduce((sum, i) => sum + i.price * i.quantity, 0);

  const orderResult = await query(
    `INSERT INTO orders (customer_id, receiver_name, receiver_phone, receiver_address, payment_method, total_amount, note)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
    [Number(customerId), receiverName, receiverPhone, receiverAddress, paymentMethod || "cod", totalAmount, note || ""]
  );
  const orderId = orderResult.insertId;

  for (const item of items) {
    await query(
      "INSERT INTO order_items (order_id, item_id, item_name, item_price, quantity) VALUES (?, ?, ?, ?, ?)",
      [orderId, Number(item.itemId), item.name, Number(item.price), Number(item.quantity)]
    );
  }

  // Clear the active cart
  const cartRows = await query(
    "SELECT id FROM carts WHERE customer_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1",
    [Number(customerId)]
  );
  if (cartRows.length > 0) {
    await query("DELETE FROM cart_items WHERE cart_id = ?", [cartRows[0].id]);
    await query("UPDATE carts SET status = 'completed' WHERE id = ?", [cartRows[0].id]);
  }

  return res.status(201).json({ order: { id: orderId, totalAmount, status: "pending" } });
});

app.get("/orders/all", async (_req, res) => {
  const orders = await query(
    `SELECT o.*, c.username, c.full_name 
     FROM orders o 
     JOIN customers c ON o.customer_id = c.id 
     ORDER BY o.created_at DESC`
  );

  const result = [];
  for (const order of orders) {
    const items = await query("SELECT * FROM order_items WHERE order_id = ?", [order.id]);
    result.push({
      id: order.id,
      customerId: order.customer_id,
      username: order.username,
      fullName: order.full_name,
      receiverName: order.receiver_name,
      receiverPhone: order.receiver_phone,
      receiverAddress: order.receiver_address,
      paymentMethod: order.payment_method,
      totalAmount: order.total_amount,
      status: order.status,
      note: order.note,
      createdAt: order.created_at,
      items
    });
  }

  return res.json({ orders: result });
});

app.patch("/orders/:id/status", async (req, res) => {
  const { id } = req.params;
  const { status } = req.body;

  const allowed = ["pending", "processing", "shipping", "completed", "cancelled"];
  if (!allowed.includes(status)) {
    return res.status(400).json({ message: "Trạng thái không hợp lệ" });
  }

  await query("UPDATE orders SET status = ? WHERE id = ?", [status, Number(id)]);
  return res.json({ success: true });
});

app.get("/orders/:customerId", async (req, res) => {
  const { customerId } = req.params;
  const orders = await query(
    "SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC",
    [Number(customerId)]
  );

  const result = [];
  for (const order of orders) {
    const items = await query(
      "SELECT * FROM order_items WHERE order_id = ?",
      [order.id]
    );
    result.push({ ...order, items });
  }

  return res.json({ orders: result });
});

app.get("/search", async (req, res) => {
  const q = (req.query.q || "").toString();
  const type = (req.query.type || "").toString();

  const response = await axios.get(`${catalogServiceUrl}/items`, {
    params: {
      q,
      type
    }
  });

  return res.json({ items: response.data.items || [] });
});

app.get("/customers", async (_req, res) => {
  const rows = await query(
    "SELECT id, username, full_name, address, phone FROM customers ORDER BY id DESC"
  );

  return res.json({
    customers: rows.map((r) => ({
      id: r.id,
      username: r.username,
      fullName: r.full_name,
      address: r.address,
      phone: r.phone,
      accountType: "CUSTOMER"
    }))
  });
});

app.use((err, _req, res, _next) => {
  console.error("customer-service error", err);
  res.status(500).json({ message: "Internal server error" });
});

initDatabase()
  .then(() => {
    app.listen(port, () => {
      console.log(`customer-service running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Failed to initialize customer database", error);
    process.exit(1);
  });
