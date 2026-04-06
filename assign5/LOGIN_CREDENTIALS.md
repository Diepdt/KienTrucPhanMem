# 📋 Login Credentials - assign5 E-Commerce Platform

All accounts have been successfully created and tested. Use these credentials to login at http://localhost:8000/user/login/

## ✅ Available Accounts

### 1. Manager Account
```
Email:    manager@gmail.com
Password: 12345678
Role:     Manager
Token:    f77ccbf1abac400e7180052ba7d4bb431c979c04198c1059d919c8d0033e8e0d
```
- **Database**: assign5_manager
- **Model**: manager_manager
- **Endpoint**: POST /api/manager/login/
- **Access**: Admin panel at /admin-panel/

### 2. Staff Account
```
Email:    staff@gmail.com
Password: 12345678
Role:     Staff
Token:    29e19d5814b6f12b7cc8e2398f3d9ce3362d553a30c8b4246957a4e180ac44c9
```
- **Database**: assign5_staff
- **Model**: staff_staff
- **Endpoint**: POST /api/staff/login/
- **Access**: Admin panel at /admin-panel/

### 3. Customer Account
```
Email:    customer@gmail.com
Password: 12345678
Role:     Customer
Token:    713fc13fcd2bc83eb3651a5cb5a04d6efec4e2b7f338cc4a519e976e645702eb
```
- **Database**: assign5_customer
- **Model**: customer_customer
- **Endpoint**: POST /api/customers/login/
- **Access**: Customer portal at /customer/

## 🔑 Password Hash (SHA256)
```
Password: 12345678
SHA256:   ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f
```

All passwords use SHA256 hashing without salt (security note: in production, use bcrypt or PBKDF2).

## 🌐 Login Flow

1. Visit http://localhost:8000/user/login/
2. Enter email and password
3. The login page tries:
   - `/api/manager/login/` first
   - `/api/staff/login/` second  
   - `/api/customers/login/` last (different endpoint)
4. Token stored in localStorage
5. Redirected to `/admin-panel/` or `/customer/` depending on account type

## 📊 Account Creation Method

Accounts were created by **direct SQL insert** into MySQL with these table structures:

### manager_manager table
```sql
INSERT INTO manager_manager (name, email, password, is_active, created_at) 
VALUES ('Manager Account', 'manager@gmail.com', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', 1, NOW());
```

### staff_staff table
```sql
INSERT INTO staff_staff (name, email, password, role, is_active, created_at) 
VALUES ('Staff Account', 'staff@gmail.com', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', 'staff', 1, NOW());
```

### customer_customer table
```sql
INSERT INTO customer_customer (name, email, password, is_active, created_at) 
VALUES ('Customer Account', 'customer@gmail.com', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', 1, NOW());
```

## 🔧 Why Direct SQL Insertion?

The original seed scripts used Django's `create_user()` which works with Django's built-in User model. The manager, staff, and customer services have **custom password hashing** (SHA256), not Django's default PBKDF2. 

**Solution**: Direct SQL insertion with pre-hashed SHA256 password ensures compatibility.

## ✨ What's Working

- ✅ Manager login at http://localhost:8000/user/login/
- ✅ Staff login at http://localhost:8000/user/login/
- ✅ Customer login at http://localhost:8000/user/login/
- ✅ All three accounts have valid tokens
- ✅ Correct redirection to admin panel or customer portal

## 🎯 Testing

Test any account via API:
```bash
curl -X POST "http://localhost:8000/api/manager/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "manager@gmail.com", "password": "12345678"}'
```

Response:
```json
{
  "token": "f77ccbf1abac400e7180052ba7d4bb431c979c04198c1059d919c8d0033e8e0d",
  "manager": {
    "id": 1,
    "name": "Manager Account",
    "email": "manager@gmail.com",
    "is_active": true
  }
}
```

## 📝 Notes

- All accounts are active (`is_active=true`)
- Tokens are generated automatically on first login
- Tokens use SHA256 hashing (`hashlib.sha256(os.urandom(32)).hexdigest()`)
- Account creation date shows server timezone (Asia/Ho_Chi_Minh)
