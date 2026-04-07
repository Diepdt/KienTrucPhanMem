# 🚀 GUIDE DEPLOY & SỬ DỤNG AI CHAT TRÊN WEBSITE
## Deploy Chuẩn Bị - Từ A-Z (Tiếng Việt)

---

## 📍 **HIỆN TẠI - STATUS**

✅ **Đã Hoàn Thành:**
- Chat widget HTML/CSS/JS: ✓
- API routes (Backend): ✓  
- API Gateway routing: ✓
- Integration vào footer: ✓

❌ **Cần Làm Tiếp:**
- Build & start Docker
- Train mô hình AI
- Test chat

---

## 🔧 **BƯỚC 1: CẬP NHẬT DOCKER-COMPOSE**

Đảm bảo `docker-compose.yml` có service recommender-ai-service và biến môi trường:

```yaml
# docker-compose.yml

services:
  recommender-ai-service:
    build:
      context: ./recommender-ai-service
      dockerfile: Dockerfile
    container_name: recommender-ai-service
    ports:
      - "8011:8000"  # Port service
    environment:
      - DEBUG=True
      - GEMINI_API_KEY=${GEMINI_API_KEY}  # ⚠️ QUAN TRỌNG! (Free tier Google)
      - GEMINI_MODEL=gemini-2.0-flash
      - DB_NAME=db_recommender
      - DB_USER=root
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=mysql
      - DB_PORT=3306
      # Service dependencies
      - CUSTOMER_SERVICE_URL=http://customer-service:8003
      - ORDER_SERVICE_URL=http://order-service:8007
      - CART_SERVICE_URL=http://cart-service:8006
      - BOOK_SERVICE_URL=http://book-service:8005
      - LAPTOP_SERVICE_URL=http://laptop-service:8014
      - MOBILE_SERVICE_URL=http://mobile-service:8015
      - CLOTH_SERVICE_URL=http://cloth-service:8013
      - SHIP_SERVICE_URL=http://ship-service:8011
      - PAY_SERVICE_URL=http://pay-service:8012
    depends_on:
      - mysql
      - customer-service
      - order-service
      - cart-service
      - book-service
    networks:
      - ecommerce_network

  api-gateway:
    environment:
      - RECOMMENDER_SERVICE_URL=http://recommender-ai-service:8011
      # ... other services
```

---

## 🔑 **BƯỚC 2: SETUP GEMINI API KEY**

### **2a. Lấy API Key (Miễn Phí):**
1. Vào https://aistudio.google.com/app/apikey
2. Đăng nhập Google account (nếu chưa)
3. Click "Create API key"
4. Copy key: `AIza...xxxxxxxxxxxxx`

### **2b. Set vào Docker:**

**Cách 1: Tạo file `.env`**
```bash
# c:\django\assign5\.env
GEMINI_API_KEY=AIza...xxxxxxxxxxxxx
GEMINI_MODEL=gemini-2.0-flash
```

**Cách 2: Thêm trực tiếp vào docker-compose.yml**
```yaml
environment:
  - GEMINI_API_KEY=AIza...xxxxxxxxxxxxx
  - GEMINI_MODEL=gemini-2.0-flash
```

**Cách 3: Set biến môi trường (PowerShell)**
```powershell
$env:GEMINI_API_KEY = "AIza...xxxxxxxxxxxxx"
$env:GEMINI_MODEL = "gemini-2.0-flash"
```

---

## 🐳 **BƯỚC 3: BUILD & START DOCKER**

```powershell
# Từ workspace root
cd c:\django\assign5

# Build tất cả services
docker-compose up -d --build

# Hoặc chỉ rebuild recommender-ai-service
docker-compose up -d --build recommender-ai-service

# Kiểm tra service chạy chưa
docker ps
```

**Xác nhận services chạy:**
```bash
✓ api-gateway (port 8000)
✓ recommender-ai-service (port 8014)
✓ MySQL database
✓ Các services khác (customer, order, book, etc.)
```

---

## 📚 **BƯỚC 4: TRAIN MÔ HÌNH AI**

Đây là bước **rất quan trọng** - không train thì chatbot không hoạt động!

### **4a. Train từ Terminal PowerShell:**

```powershell
# Vào container recommender service
docker-compose exec recommender-ai-service bash

# Chạy training script
python manage.py train_behavior_model

# Hoặc tách biệt:
python manage.py train_behavior_model --model-only     # Chỉ behavior model
python manage.py train_behavior_model --kb-only         # Chỉ knowledge base
```

**Output mong đợi:**
```
[1/5] Fetching customers...
  ✓ Got 50 customers
[2/5] Fetching products from all services...
  ✓ Got 200 products from book-service
  ✓ Got 150 products from laptop-service
  ✓ Got 100 products from mobile-service
[3/5] Building ID mappings...
  ✓ Mapped 50 users and 450 items
[4/5] Extracting interactions from orders & carts...
  ✓ Extracted 500 interactions
[5/5] Converting to numpy array...
  ✓ Created matrix shape: (500, 3)

========================================
DATA PIPELINE SUMMARY
========================================
Total Users: 50
Total Items: 450
Total Interactions: 500
Matrix Sparsity: 99.78%
========================================

Starting training...

Epoch  1/30 | Train Loss: 0.4521 | Val Loss: 0.3892
Epoch  2/30 | Train Loss: 0.3124 | Val Loss: 0.2891
...
Epoch 30/30 | Train Loss: 0.0891 | Val Loss: 0.1234

✓ Training completed!
✓ Model saved to /app/recommender/behavior_model/pretrained_models/best_model.pt
✓ Saved customer ID mapping
✓ Saved item ID mapping

BEHAVIOR MODEL TRAINING PIPELINE
────────────────────────────────
  ✓ Data gathered from services
  ✓ Model trained successfully
  ✓ Metadata saved

BUILDING KNOWLEDGE BASE
────────────────────────────────
  ✓ Fetched products from Book Service: 200 docs
  ✓ Fetched products from Laptop Service: 150 docs
  ✓ Fetched products from Mobile Service: 100 docs
  ✓ Fetched products from Cloth Service: 80 docs
  ✓ Added service info documents: 3 docs
  Total documents: 533
  
  Embedding documents... [████████████░░░░] 75%
  ✓ Embeddings created - Shape: (533, 384)
  ✓ Saved 533 documents to knowledge base
  ✓ FAISS index built with 533 vectors

========================================
✓ KNOWLEDGE BASE BUILT SUCCESSFULLY!
========================================
```

### **4b. Train từ API:**

Hoặc gọi API endpoints để train:

```bash
# Train behavior model
curl -X POST http://localhost:8014/api/train-behavior-model/

# Build knowledge base
curl -X POST http://localhost:8014/api/build-knowledge-base/

# Response:
# {
#   "status": "success",
#   "message": "Behavior model trained successfully",
#   "timestamp": "2026-04-06T10:30:00"
# }
```

---

## 💬 **BƯỚC 5: TEST CHAT**

### **5a. Test Quick Answer (không cần đăng nhập):**

```bash
curl -X POST http://localhost:8000/api/ai/quick-answer/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Bạn gửi hàng ngoài TP HCM không?"
  }'

# Response:
# {
#   "query": "Bạn gửi hàng ngoài TP HCM không?",
#   "answer": "Có, chúng tôi gửi hàng trên toàn quốc...",
#   "status": "success"
# }
```

### **5b. Test Chat với Personalization (cần customer_id):**

```bash
curl -X POST http://localhost:8000/api/ai/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 123,
    "message": "Có laptop gaming nào dưới 20 triệu?"
  }'

# Response:
# {
#   "response": "Dựa trên sở thích gaming của bạn, tôi gợi ý...",
#   "recommended_products": [
#     {
#       "service_type": "laptop",
#       "product_id": 45,
#       "score": 0.95,
#       "confidence": 0.92
#     }
#   ],
#   "conversation_id": "conv_123_...",
#   "success": true
# }
```

### **5c. Test trên Browser:**

1. Vào: http://localhost:8000/customer/ (Trang chủ)
2. Nhìn góc dưới phải màn hình
3. Click nút chat 💬
4. Gõ câu hỏi và gửi!

**Kết quả mong đợi:**
```
💬 Button góc phải
│
└─ Click → Mở chat window
   │
   ├─ Bot: "Chào bạn! 👋 Tôi là trợ lý AI..."
   ├─ You: "Có laptop gaming dưới 20 triệu?"
   ├─ Bot: "Dựa trên sở thích của bạn, tôi gợi ý:
   │         1. ASUS TUF A15 - 19.5 triệu
   │         2. Lenovo Legion - 18.9 triệu
   │         ..."
   │
   └─ [Danh sách sản phẩm được gợi ý]
```

---

## 🐛 **TROUBLESHOOTING - KHẮC PHỤC LỖI**

### **❌ Lỗi 1: "GEMINI_API_KEY not found"**

**Nguyên Nhân:** Biến môi trường chưa được set
**Cách Sửa:**
```powershell
# Check biến env
docker-compose config | grep GEMINI_API_KEY

# Set biến (nếu chưa có)
$env:GEMINI_API_KEY = "AIza...xxxxxxxxxxxxx"

# Restart container
docker-compose restart recommender-ai-service
```

---

### **❌ Lỗi 2: "Knowledge base not found"**

**Nguyên Nhân:** Chưa train knowledge base
**Cách Sửa:**
```bash
docker-compose exec recommender-ai-service bash
python manage.py train_behavior_model --kb-only
```

---

### **❌ Lỗi 3: Chat widget không hiển thị**

**Nguyên Nhân:** Footer.html chưa include widget
**Cách Sửa:**
```html
<!-- Trong c:\django\assign5\api-gateway\templates\client\layout\footer.html -->
<!-- Thêm dòng này trước </script> -->
{% include "components/ai_chat_widget.html" %}
```

---

### **❌ Lỗi 4: API Gateway routing không hoạt động**

**Nguyên Nhân:** ROUTE_TABLE chưa được update
**Cách Check:**
```bash
# Xem xem routing config
curl http://localhost:8000/api/ai/chat/
# Nếu 404 → routing chưa setup

# Hoặc check logs
docker logs api-gateway
docker logs recommender-ai-service
```

---

### **❌ Lỗi 5: Chậm lần đầu (5-10 giây)**

**Nguyên Nhân:** Model đầu tiên tải mô hình từ disk
**Kết Quả:** Lần tiếp theo sẽ nhanh hơn (cached)

---

## 📊 **KIỂM TRA STATUS SERVICES**

```bash
# Xem tất cả containers
docker ps

# Output mong đợi:
# CONTAINER ID  IMAGE                        PORTS
# xxxxx         api-gateway:latest           0.0.0.0:8000->8000/tcp
# xxxxx         recommender-ai-service:latest 0.0.0.0:8014->8000/tcp
# xxxxx         book-service:latest          0.0.0.0:8005->8000/tcp
# xxxxx         order-service:latest         0.0.0.0:8007->8000/tcp
# xxxxx         mysql:latest                 0.0.0.0:3306->3306/tcp

# Xem logs của recommender service
docker logs recommender-ai-service -f

# Xem logs của api-gateway
docker logs api-gateway -f
```

---

## 🎯 **CUỐI CÙNG - CHECK LIST DEPLOY**

```
BEFORE GOING LIVE:

☐ GEMINI_API_KEY được set (miễn phí từ Google)
☐ docker-compose.yml đã update
☐ Chat widget included trong footer.html
☐ API Gateway routing updated (ROUTE_TABLE + ProxyView)
☐ Recommender model trained (behavior + KB)
☐ Database initialized (mysql)
☐ Tất cả services chạy (docker ps)
☐ Quick answer test thành công (curl)
☐ Chat test trên browser thành công
☐ Recommendation scores hợp lý (0.7 - 0.99)

✅ CÓ THỂ DEPLOY LIVE!
```

---

## 📝 **THAMHAM TRỪ THAM KHẢO**

| Endpoint | Phương Thức | Mô Tả | 
|----------|-----------|-------|
| `/api/ai/chat/` | POST | Chat với AI |
| `/api/ai/quick-answer/` | POST | Hỏi nhanh (FAQ) |
| `/api/ai/recommendations-ai/{customer_id}/` | GET | Gợi ý AI |
| `/api/ai/train-behavior-model/` | POST | Train model |
| `/api/ai/build-knowledge-base/` | POST | Build KB |
| `/api/ai/chat-history/{customer_id}/` | DELETE | Xóa chat history |

---

## 🎓 **THÊM THÔNG TIN**

- 📖 Full Implementation Guide: `IMPLEMENTATION_GUIDE.md`
- 📚 Research Report (5 pages): `AI_ECOMMERCE_RESEARCH_REPORT.md`
- 🔍 Project README: `README_AI_PROJECT.md`

---

**Tạo lúc:** 2026-04-06
**Version:** 1.0
**Status:** ✅ Ready to Deploy
