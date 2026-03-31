const path = require("path");
const express = require("express");
const session = require("express-session");
const multer = require("multer");
const { customerApi, staffApi, catalogApi } = require("./apiClients");

const app = express();
const upload = multer();
const port = Number(process.env.PORT || 3000);

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "..", "template"));

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(
  session({
    secret: process.env.SESSION_SECRET || "keyboard-cat",
    resave: false,
    saveUninitialized: false
  })
);

app.use(express.static(path.join(__dirname, "..", "public")));

app.use(async (req, res, next) => {
  res.locals.user = req.session.customer || null;
  res.locals.staff = req.session.staff || null;
  res.locals.cartCount = 0;
  
  if (req.session.customer) {
    try {
      const resp = await customerApi.get(`/cart/${req.session.customer.id}`);
      const items = resp.data.items || [];
      res.locals.cartCount = items.reduce((acc, i) => acc + i.quantity, 0);
    } catch (e) {
      console.error("Failed to fetch cart count");
    }
  }
  next();
});

function requireCustomer(req, res, next) {
  if (!req.session.customer) {
    return res.redirect("/user/login");
  }
  return next();
}

function requireStaff(req, res, next) {
  if (!req.session.staff) {
    return res.redirect("/admin/login");
  }
  return next();
}

function toOldTemplateProduct(product) {
  return {
    id: product.id,
    type: product.type,
    name: product.name,
    price: product.price,
    detailDesc: product.detailDesc,
    shortDesc: product.shortDesc,
    quantity: product.quantity,
    sold: product.sold,
    factory: product.factory,
    target: product.target,
    image: product.image
  };
}

app.get("/", async (req, res, next) => {
  try {
    const q = (req.query.q || "").toString();
    const type = (req.query.type || "").toString();

    const response = await customerApi.get("/search", {
      params: {
        q,
        type
      }
    });

    return res.render("client/home/show", {
      products: (response.data.items || []).map(toOldTemplateProduct)
    });
  } catch (error) {
    return next(error);
  }
});

app.get("/product/:id", async (req, res, next) => {
  try {
    const response = await catalogApi.get(`/items/${req.params.id}`);
    return res.render("client/product/show", {
      product: toOldTemplateProduct(response.data.item)
    });
  } catch (error) {
    if (error.response?.status === 404) {
      return res.status(404).render("status/404");
    }
    return next(error);
  }
});

app.post("/add-product-to-cart/:id", requireCustomer, async (req, res, next) => {
  try {
    await customerApi.post("/cart/items", {
      customerId: req.session.customer.id,
      itemId: Number(req.params.id),
      quantity: 1
    });

    return res.redirect("/");
  } catch (error) {
  }
});

app.get("/cart", requireCustomer, async (req, res, next) => {
  try {
    const resp = await customerApi.get(`/cart/${req.session.customer.id}`);
    const items = resp.data.items || [];
    
    const cartItemsWithDetails = [];
    for (const item of items) {
      try {
        const prodResp = await catalogApi.get(`/items/${item.itemId}`);
        const productData = toOldTemplateProduct(prodResp.data.item);
        cartItemsWithDetails.push({ ...productData, cartQuantity: item.quantity });
      } catch (e) {
        console.error("Failed to fetch product catalog", e.message);
      }
    }

    return res.render("client/cart/show", {
      cartItems: cartItemsWithDetails
    });
  } catch (error) {
    return next(error);
  }
});

app.post("/cart/remove/:itemId", requireCustomer, async (req, res, next) => {
  try {
    await customerApi.delete(`/cart/${req.session.customer.id}/items/${req.params.itemId}`);
    return res.redirect("/cart");
  } catch (error) {
    return next(error);
  }
});

app.get("/checkout", requireCustomer, async (req, res, next) => {
  try {
    const resp = await customerApi.get(`/cart/${req.session.customer.id}`);
    const items = resp.data.items || [];

    if (items.length === 0) {
      return res.redirect("/cart");
    }

    const cartItemsWithDetails = [];
    for (const item of items) {
      try {
        const prodResp = await catalogApi.get(`/items/${item.itemId}`);
        const productData = toOldTemplateProduct(prodResp.data.item);
        cartItemsWithDetails.push({ ...productData, cartQuantity: item.quantity, itemId: item.itemId });
      } catch (e) {
        console.error("Failed to fetch product", e.message);
      }
    }

    const total = cartItemsWithDetails.reduce((sum, i) => sum + i.price * i.cartQuantity, 0);

    return res.render("client/checkout/show", {
      cartItems: cartItemsWithDetails,
      total,
      customer: req.session.customer,
      errors: [],
      oldData: {}
    });
  } catch (error) {
    return next(error);
  }
});

app.post("/checkout", requireCustomer, async (req, res, next) => {
  try {
    const { receiverName, receiverPhone, receiverAddress, paymentMethod, note } = req.body;
    const errors = [];

    if (!receiverName) errors.push("Vui lòng nhập họ tên người nhận");
    if (!receiverPhone) errors.push("Vui lòng nhập số điện thoại");
    if (!receiverAddress) errors.push("Vui lòng nhập địa chỉ nhận hàng");

    // Re-fetch cart items to include in order
    const resp = await customerApi.get(`/cart/${req.session.customer.id}`);
    const items = resp.data.items || [];

    if (items.length === 0) {
      return res.redirect("/cart");
    }

    const cartItemsWithDetails = [];
    for (const item of items) {
      try {
        const prodResp = await catalogApi.get(`/items/${item.itemId}`);
        const productData = toOldTemplateProduct(prodResp.data.item);
        cartItemsWithDetails.push({ ...productData, cartQuantity: item.quantity, itemId: item.itemId });
      } catch (e) {
        console.error("Failed to fetch product", e.message);
      }
    }

    if (errors.length > 0) {
      const total = cartItemsWithDetails.reduce((sum, i) => sum + i.price * i.cartQuantity, 0);
      return res.status(400).render("client/checkout/show", {
        cartItems: cartItemsWithDetails,
        total,
        customer: req.session.customer,
        errors,
        oldData: req.body
      });
    }

    const orderItems = cartItemsWithDetails.map(i => ({
      itemId: i.itemId,
      name: i.name,
      price: i.price,
      quantity: i.cartQuantity
    }));

    const orderResp = await customerApi.post("/orders", {
      customerId: req.session.customer.id,
      receiverName,
      receiverPhone,
      receiverAddress,
      paymentMethod: paymentMethod || "cod",
      note,
      items: orderItems
    });

    const orderId = orderResp.data.order.id;
    const totalAmount = orderResp.data.order.totalAmount;

    return res.redirect(`/order-success?orderId=${orderId}&total=${totalAmount}`);
  } catch (error) {
    return next(error);
  }
});

app.get("/order-success", requireCustomer, (req, res) => {
  return res.render("client/checkout/success", {
    orderId: req.query.orderId,
    total: Number(req.query.total || 0)
  });
});

app.get("/order-history", requireCustomer, async (req, res, next) => {
  try {
    const resp = await customerApi.get(`/orders/${req.session.customer.id}`);
    return res.render("client/checkout/history", {
      orders: resp.data.orders || []
    });
  } catch (error) {
    return next(error);
  }
});

app.get("/user/login", (_req, res) => {
  return res.render("user/login", { messages: [], action: "/user/login" });
});

app.post("/user/login", async (req, res) => {
  try {
    const response = await customerApi.post("/auth/login", req.body);
    req.session.customer = response.data.customer;
    return res.redirect("/");
  } catch (_error) {
    return res.status(401).render("user/login", {
      messages: ["Dang nhap that bai. Vui long thu lai."],
      action: "/user/login"
    });
  }
});

app.get("/user/register", (_req, res) => {
  return res.render("user/register", {
    errors: [],
    oldData: {
      username: "",
      password: "",
      confirmPassword: "",
      fullName: "",
      phone: "",
      address: ""
    }
  });
});

app.post("/user/register", async (req, res) => {
  const { username, password, confirmPassword, fullName, address, phone } = req.body;
  const errors = [];

  if (!username || !password || !fullName) {
    errors.push("Vui long nhap day du username, password, fullName");
  }

  if (password !== confirmPassword) {
    errors.push("Xac nhan mat khau khong khop");
  }

  if (errors.length > 0) {
    return res.status(400).render("user/register", {
      errors,
      oldData: req.body
    });
  }

  try {
    await customerApi.post("/auth/register", {
      username,
      password,
      fullName,
      address,
      phone
    });

    return res.redirect("/user/login");
  } catch (error) {
    return res.status(400).render("user/register", {
      errors: [error.response?.data?.message || "Dang ky that bai"],
      oldData: req.body
    });
  }
});

app.post("/user/logout", (req, res) => {
  req.session.destroy(() => {
    res.redirect("/");
  });
});

app.get("/admin/login", (_req, res) => {
  return res.render("user/login", { messages: [], action: "/admin/login" });
});

app.post("/admin/login", async (req, res) => {
  try {
    const response = await staffApi.post("/auth/login", req.body);
    req.session.staff = response.data.staff;
    return res.redirect("/admin");
  } catch (_error) {
    return res.status(401).render("user/login", {
      messages: ["Staff dang nhap that bai."],
      action: "/admin/login"
    });
  }
});

app.get("/admin", requireStaff, (_req, res) => {
  return res.render("admin/dashboard/show");
});

app.get("/admin/product", requireStaff, async (_req, res, next) => {
  try {
    const response = await catalogApi.get("/items");
    return res.render("admin/product/show", {
      products: (response.data.items || []).map(toOldTemplateProduct)
    });
  } catch (error) {
    return next(error);
  }
});

app.get("/admin/create-product", requireStaff, (_req, res) => {
  return res.render("admin/product/create", {
    errors: [],
    oldData: {
      type: "laptop",
      name: "",
      price: "",
      detailDesc: "",
      shortDesc: "",
      quantity: "",
      sold: "",
      image: "",
      factory: "APPLE",
      target: "GAMING"
    }
  });
});

app.post("/admin/create-product", requireStaff, upload.none(), async (req, res) => {
  try {
    const payload = {
      type: req.body.type || "laptop",
      name: req.body.name,
      price: Number(req.body.price || 0),
      detailDesc: req.body.detailDesc,
      shortDesc: req.body.shortDesc,
      quantity: Number(req.body.quantity || 0),
      sold: Number(req.body.sold || 0),
      factory: req.body.factory,
      target: req.body.target,
      image:
        req.body.image ||
        "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800"
    };

    await staffApi.post("/items", payload, {
      headers: {
        "x-staff-id": String(req.session.staff.id)
      }
    });

    return res.redirect("/admin/product");
  } catch (error) {
    return res.status(400).render("admin/product/create", {
      errors: [{ message: error.response?.data?.message || "Create product failed", path: "form" }],
      oldData: req.body
    });
  }
});

app.get("/admin/update-product/:id", requireStaff, async (req, res, next) => {
  try {
    const response = await catalogApi.get(`/items/${req.params.id}`);
    return res.render("admin/product/detail", {
      errors: {},
      data: toOldTemplateProduct(response.data.item)
    });
  } catch (error) {
    if (error.response?.status === 404) {
      return res.status(404).render("status/404");
    }
    return next(error);
  }
});

app.post("/admin/update-product/:id", requireStaff, upload.none(), async (req, res) => {
  try {
    const payload = {
      type: req.body.type || "laptop",
      name: req.body.name,
      price: Number(req.body.price || 0),
      detailDesc: req.body.detailDesc,
      shortDesc: req.body.shortDesc,
      quantity: Number(req.body.quantity || 0),
      sold: Number(req.body.sold || 0),
      factory: req.body.factory,
      target: req.body.target,
      image: req.body.image
    };

    await staffApi.put(`/items/${req.params.id}`, payload, {
      headers: {
        "x-staff-id": String(req.session.staff.id)
      }
    });

    return res.redirect("/admin/product");
  } catch (error) {
    return res.status(400).render("admin/product/detail", {
      errors: {
        form: error.response?.data?.message || "Update product failed"
      },
      data: { ...req.body, id: Number(req.params.id) }
    });
  }
});

app.post("/admin/delete-product/:id", requireStaff, async (req, res, next) => {
  try {
    await catalogApi.delete(`/items/${req.params.id}`);
    return res.redirect("/admin/product");
  } catch (error) {
    return next(error);
  }
});

app.get("/admin/user", requireStaff, async (_req, res, next) => {
  try {
    const response = await customerApi.get("/customers");
    return res.render("admin/user/show", {
      users: (response.data.customers || []).map((c) => ({
        id: c.id,
        fullName: c.fullName,
        username: c.username,
        address: c.address,
        phone: c.phone,
        accountType: c.accountType,
        roleId: 2
      })),
      roles: [
        { id: 1, name: "ADMIN" },
        { id: 2, name: "CUSTOMER" }
      ]
    });
  } catch (error) {
    return next(error);
  }
});

app.get("/admin/order", requireStaff, async (_req, res, next) => {
  try {
    const response = await customerApi.get("/orders/all");
    return res.render("admin/order/show", {
      orders: response.data.orders || []
    });
  } catch (error) {
    return next(error);
  }
});

app.post("/admin/order/:id/status", requireStaff, async (req, res, next) => {
  try {
    await customerApi.patch(`/orders/${req.params.id}/status`, { status: req.body.status });
    return res.redirect("/admin/order");
  } catch (error) {
    return next(error);
  }
});

app.get("/403", (_req, res) => {
  res.status(403).render("status/403");
});

app.use((_req, res) => {
  res.status(404).render("status/404");
});

app.use((err, _req, res, _next) => {
  console.error("web-gateway error", err);
  res.status(500).render("status/500");
});

app.listen(port, () => {
  console.log(`web-gateway running on port ${port}`);
});
