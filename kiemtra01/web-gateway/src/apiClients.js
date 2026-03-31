const axios = require("axios");

const customerApi = axios.create({
  baseURL: process.env.CUSTOMER_SERVICE_URL || "http://localhost:4002",
  timeout: 10000
});

const staffApi = axios.create({
  baseURL: process.env.STAFF_SERVICE_URL || "http://localhost:4003",
  timeout: 10000
});

const catalogApi = axios.create({
  baseURL: process.env.CATALOG_SERVICE_URL || "http://localhost:4001",
  timeout: 10000
});

module.exports = {
  customerApi,
  staffApi,
  catalogApi
};
