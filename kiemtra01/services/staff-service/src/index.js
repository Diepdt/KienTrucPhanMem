const express = require("express");
const axios = require("axios");
const bcrypt = require("bcryptjs");
const { initDatabase, query } = require("./db");

const app = express();
const port = Number(process.env.PORT || 4003);
const catalogServiceUrl = process.env.CATALOG_SERVICE_URL || "http://localhost:4001";

app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ ok: true, service: "staff-service" });
});

app.post("/auth/login", async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ message: "username and password are required" });
  }

  const rows = await query(
    "SELECT id, username, password_hash, full_name FROM staffs WHERE username = ? LIMIT 1",
    [username]
  );

  if (rows.length === 0) {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  const staff = rows[0];
  const matched = await bcrypt.compare(password, staff.password_hash);

  if (!matched) {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  return res.json({
    staff: {
      id: staff.id,
      username: staff.username,
      fullName: staff.full_name
    }
  });
});

function requireStaff(req, res, next) {
  const staffId = Number(req.header("x-staff-id"));
  if (!Number.isInteger(staffId) || staffId <= 0) {
    return res.status(401).json({ message: "Staff authentication required" });
  }

  req.staffId = staffId;
  return next();
}

app.post("/items", requireStaff, async (req, res) => {
  const response = await axios.post(`${catalogServiceUrl}/items`, req.body);
  return res.status(201).json(response.data);
});

app.put("/items/:id", requireStaff, async (req, res) => {
  const response = await axios.put(`${catalogServiceUrl}/items/${req.params.id}`, req.body);
  return res.json(response.data);
});

app.use((err, _req, res, _next) => {
  if (err.response) {
    return res.status(err.response.status).json(err.response.data);
  }

  console.error("staff-service error", err);
  return res.status(500).json({ message: "Internal server error" });
});

initDatabase()
  .then(() => {
    app.listen(port, () => {
      console.log(`staff-service running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Failed to initialize staff database", error);
    process.exit(1);
  });
