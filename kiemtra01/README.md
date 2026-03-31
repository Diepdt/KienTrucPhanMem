# Laptop + Mobile Microservices (Docker)

Project microservices cho bai kiem tra voi 2 DB:
- MySQL: customer + staff
- PostgreSQL: laptop + mobile catalog
- Khong su dung SQLite

## Services
- `catalog-service` (PostgreSQL): quan ly laptop/mobile item
- `customer-service` (MySQL): dang ky, dang nhap, tao gio hang, tim kiem
- `staff-service` (MySQL): staff login, nhap item, cap nhat item
- `web-gateway` (Express + EJS): UI staff va customer, ket noi den cac service

## Chay project
```bash
docker compose up --build
```

Sau khi chay:
- Customer UI: http://localhost:3200
- Staff UI: http://localhost:3200/admin

Cong DB publish ra host (neu can debug):
- MySQL: localhost:33406
- PostgreSQL: localhost:35432

## Tai khoan mau
- Staff:
  - username: `staffadmin`
  - password: `staff123`

## API chinh
- Customer service:
  - `POST /auth/register`
  - `POST /auth/login`
  - `POST /cart` (tao gio hang)
  - `POST /cart/items`
  - `GET /search?q=...&type=laptop|mobile`
- Staff service:
  - `POST /auth/login`
  - `POST /items` (nhap item)
  - `PUT /items/:id` (cap nhat)
- Catalog service:
  - `GET /items`
  - `GET /items/:id`
  - `POST /items`
  - `PUT /items/:id`
  - `DELETE /items/:id`

## Ghi chu
- Cac form staff va customer UI da duoc noi vao backend.
- Template frontend duoc giu nguyen tu thu muc `template`.
