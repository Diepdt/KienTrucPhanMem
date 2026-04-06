# 🌱 Seed Data Scripts

These scripts initialize the database with essential data to prevent data loss when adding new services.

## Accounts Created

| Service | Email | Password | Role |
|---------|-------|----------|------|
| staff-service | `staff@gmail.com` | `12345678` | Staff |
| manager-service | `manager@gmail.com` | `12345678` | Manager |
| customer-service | `customer@gmail.com` | `12345678` | Customer |

## Categories Created

### Book Categories
- Tâm linh (Spirituality)
- Tâm lý học (Psychology)
- Tài chính (Finance)
- Phát triển bản thân (Self-development)

### Cloth Categories
- Áo sơ mi (Shirts)
- Sweater (Sweaters)
- Quần âu (Trousers)

### Laptop Categories
- Gaming
- Văn phòng (Office)
- Thiết kế (Design)
- Ultrabook

### Mobile Categories
- Smartphone
- Flagship
- Mid-range
- Budget

## How to Run

### 1. Ensure Docker is Running
```bash
docker-compose up -d
```

### 2. Wait for Services to Start
All services need to be fully initialized with migrations. Check logs:
```bash
docker-compose logs -f
```

### 3. Run Seed Scripts

**Outside Docker (from host machine):**
```bash
# If your services are accessible via localhost:8000-8015

# For staff account
python seed-scripts/seed_staff.py

# For manager account
python seed-scripts/seed_manager.py

# For customer account
python seed-scripts/seed_customer.py

# For categories
python seed-scripts/seed_categories.py
```

**Inside Docker:**
```bash
# Connect to a service container
docker exec -it <service-name> bash

# Run seed script (example for staff-service)
cd /app
python ../seed-scripts/seed_staff.py
```

### 4. Verify Data Created
```bash
# Check staff account
curl -X GET http://localhost:8001/api/staff/?email=staff@gmail.com \
  -H "Authorization: Token YOUR_TOKEN"

# Check categories
curl -X GET http://localhost:8004/api/categories/?product_type=book
```

## Script Details

### `seed_staff.py`
- **Location**: staff-service database
- **Creates**: User account with `is_staff=True`
- **Email**: `staff@gmail.com`
- **Password**: `12345678`

### `seed_manager.py`
- **Location**: manager-service database
- **Creates**: User account with `is_staff=True`
- **Email**: `manager@gmail.com`
- **Password**: `12345678`

### `seed_customer.py`
- **Location**: customer-service database
- **Creates**: User account with `is_staff=False`
- **Email**: `customer@gmail.com`
- **Password**: `12345678`

### `seed_categories.py`
- **Location**: catalog-service database
- **Creates**: 15 categories across 4 product types
- **Idempotent**: Safe to run multiple times (won't duplicate)
- **Checks**: Uses `product_type` and `name` unique constraint to prevent duplicates

## Running All Seeds at Once

Create a shell script `run_all_seeds.sh`:

```bash
#!/bin/bash

echo "🌱 Running all seed scripts..."

cd staff-service
python ../seed-scripts/seed_staff.py

cd ../manager-service
python ../seed-scripts/seed_manager.py

cd ../customer-service
python ../seed-scripts/seed_customer.py

cd ../catalog-service
python ../seed-scripts/seed_categories.py

echo "✓ All seeds completed!"
```

Then run:
```bash
chmod +x run_all_seeds.sh
./run_all_seeds.sh
```

## Important Notes

1. **Idempotent**: All scripts check for existing records before creating, so running them multiple times is safe
2. **No Data Loss**: Scripts only add data, never delete or modify existing records
3. **Service Dependencies**: Ensure services are fully started before running seeds
4. **Timing**: Wait 30-60 seconds after `docker-compose up` before running seeds to ensure migrations complete

## Troubleshooting

**Error: "Can't connect to MySQL server"**
- Ensure MySQL container is running: `docker ps | grep mysql`
- Check MySQL logs: `docker-compose logs mysql`
- Wait longer for MySQL to fully initialize (can take 30+ seconds on first run)

**Error: "No such module"**
- Ensure you're running scripts from the workspace root: `cd /path/to/assign5`
- Check Python path is correctly set in the script

**Error: "Table doesn't exist"**
- Migrations may not have run yet
- Wait for service logs to show "Migrations applied successfully"
- Check service logs: `docker-compose logs <service-name>`

## Related Documentation
- See `REPORT.md` for full project documentation
- See `SERVICE_STATISTICS.md` for service overview
- See individual `requirements.txt` for each service's dependencies
