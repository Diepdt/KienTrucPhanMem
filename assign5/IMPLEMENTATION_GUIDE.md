# AI E-Commerce Behavior Analysis & Consultation Chatbot
## Implementation & Deployment Guide

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY (Repository)                     │
│  - Route requests to recommender-ai-service                     │
│  - Serve chat widget to frontend                                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│          RECOMMENDER-AI-SERVICE (New - This implementation)      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  BEHAVIOR MODEL (Deep Learning)                         │   │
│  │  ├─ Neural Collaborative Filtering (NCF)               │   │
│  │  ├─ Data Pipeline: Customer → Order → Cart data        │   │
│  │  ├─ Training: PyTorch-based                            │   │
│  │  └─ Output: Product recommendations (top_k)            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  KNOWLEDGE BASE (KD)                                    │   │
│  │  ├─ Data from: Book, Laptop, Mobile, Cloth service    │   │
│  │  ├─ Embedding: Sentence-Transformers (all-MiniLM)    │   │
│  │  ├─ Storage: FAISS vector database                     │   │
│  │  └─ Includes: Shipping, Payment, General policies     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  RAG CHAT SERVICE                                       │   │
│  │  ├─ LLM: Claude 3.5 Sonnet (Anthropic API)            │   │
│  │  ├─ Retrieval: Vector similarity search (FAISS)        │   │
│  │  ├─ Context: KB documents + AI recommendations        │   │
│  │  └─ Output: Personalized consultation responses        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Django API Endpoints:                                          │
│  ├─ POST /api/train-behavior-model/  (Train behavior model)   │
│  ├─ POST /api/build-knowledge-base/  (Build KB)               │
│  ├─ GET  /api/recommendations-ai/{customer_id}/  (Inference)  │
│  ├─ POST /api/chat/  (RAG Chat)                               │
│  └─ POST /api/quick-answer/  (FAQ)                            │
└─────────────────────────────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    Order Service  Cart Service  Other Services
    (lịch sử mua)  (quan tâm)    (sản phẩm + chính sách)
```

---

## 🚀 Implementation Steps

### Step 1: Set up Environment Variables

Add to `.env` or docker-compose environment:

```yaml
# Recommender AI Service
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Obtain from https://console.anthropic.com

# Service URLs (if not using docker-compose)
CUSTOMER_SERVICE_URL=http://customer-service:8003
ORDER_SERVICE_URL=http://order-service:8007
CART_SERVICE_URL=http://cart-service:8002
BOOK_SERVICE_URL=http://book-service:8005
LAPTOP_SERVICE_URL=http://laptop-service:8006
MOBILE_SERVICE_URL=http://mobile-service:8008
CLOTH_SERVICE_URL=http://cloth-service:8009
SHIP_SERVICE_URL=http://ship-service:8011
PAY_SERVICE_URL=http://pay-service:8012
```

### Step 2: Update Docker Compose

Update `docker-compose.yml`:

```yaml
services:
  recommender-ai-service:
    build:
      context: ./recommender-ai-service
      dockerfile: Dockerfile
    container_name: recommender-ai-service
    ports:
      - "8014:8000"  # Port for recommender-ai service
    environment:
      - DEBUG=True
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DB_NAME=db_recommender
      - DB_USER=root
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=mysql
      - DB_PORT=3306
      - CUSTOMER_SERVICE_URL=http://customer-service:8003
      - ORDER_SERVICE_URL=http://order-service:8007
      - CART_SERVICE_URL=http://cart-service:8002
      - BOOK_SERVICE_URL=http://book-service:8005
      - LAPTOP_SERVICE_URL=http://laptop-service:8006
      - MOBILE_SERVICE_URL=http://mobile-service:8008
      - CLOTH_SERVICE_URL=http://cloth-service:8009
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

  # ... other services
```

### Step 3: Install Dependencies

```bash
# On Windows with venv
cd recommender-ai-service
pip install -r requirements.txt

# Or using conda
conda create -n ai-env python=3.10
conda activate ai-env
pip install -r requirements.txt
```

### Step 4: Train Initial Models

From within the recommender-ai-service directory:

#### Option A: Using Django Management Command

```bash
# Train both behavior model and knowledge base
python manage.py train_behavior_model

# Train only behavior model
python manage.py train_behavior_model --model-only

# Build only knowledge base
python manage.py train_behavior_model --kb-only
```

#### Option B: Using API Endpoints

```bash
# Train behavior model (POST request)
curl -X POST http://localhost:8014/api/train-behavior-model/

# Build knowledge base (POST request)
curl -X POST http://localhost:8014/api/build-knowledge-base/
```

### Step 5: Update API Gateway Routing

In `api-gateway/gateway/views.py` or wherever your routing is handled, add:

```python
import requests
from rest_framework.views import APIView
from rest_framework.response import Response

AI_SERVICE_URL = 'http://recommender-ai-service:8000'

class AIProxyView(APIView):
    """Proxy requests to recommender-ai-service"""
    
    def post(self, request, *args, **kwargs):
        """Proxy POST requests"""
        path = request.path.replace('/api/gateway/ai/', '/api/')
        
        try:
            response = requests.post(
                f'{AI_SERVICE_URL}{path}',
                json=request.data,
                timeout=30
            )
            return Response(response.json(), status=response.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def get(self, request, *args, **kwargs):
        """Proxy GET requests"""
        path = request.path.replace('/api/gateway/ai/', '/api/')
        
        try:
            response = requests.get(
                f'{AI_SERVICE_URL}{path}',
                params=request.query_params,
                timeout=30
            )
            return Response(response.json(), status=response.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
```

In `api-gateway/gateway_config/urls.py`:

```python
from django.urls import path, re_path
from gateway.views import AIProxyView

urlpatterns = [
    # AI Service proxy
    re_path(r'^api/gateway/ai/(?P<path>.*)$', AIProxyView.as_view()),
]
```

### Step 6: Integrate Chat Widget into Templates

Add to your base template or any page where you want the chat to appear:

```html
<!-- In any Django template (e.g., base.html, client layout, etc.) -->
{% include "components/ai_chat_widget.html" %}
```

Or in API Gateway templates:

```html
<!-- api-gateway/templates/client/base.html or similar -->
<!DOCTYPE html>
<html>
<head>
    <!-- ... existing head content ... -->
</head>
<body>
    <!-- ... your content ... -->
    
    <!-- AI Chat Widget -->
    {% include "components/ai_chat_widget.html" %}
    
    <!-- ... existing scripts ... -->
</body>
</html>
```

---

## 📝 API Documentation

### 1. Train Behavior Model
```
POST /api/train-behavior-model/

Response:
{
    "status": "success",
    "message": "Behavior model trained successfully",
    "timestamp": "2026-04-06T10:30:00"
}
```

### 2. Build Knowledge Base
```
POST /api/build-knowledge-base/

Response:
{
    "status": "success",
    "message": "Knowledge base built successfully",
    "timestamp": "2026-04-06T10:30:00"
}
```

### 3. Get Recommendations (AI-based)
```
GET /api/recommendations-ai/{customer_id}/?top_k=5

Response:
{
    "customer_id": 123,
    "total": 5,
    "recommendations": [
        {
            "service_type": "laptop",
            "product_id": 45,
            "score": 0.87,
            "confidence": 0.82
        },
        ...
    ],
    "source": "behavior_model_deep_learning"
}
```

### 4. Chat (Personalized Consultation)
```
POST /api/chat/

Body:
{
    "customer_id": 123,
    "message": "Có laptop gaming nào dưới 20 triệu?",
    "conversation_id": "optional"
}

Response:
{
    "response": "Dựa trên lịch sử mua sắm của bạn và nhu cầu gaming...",
    "recommended_products": [
        {
            "service_type": "laptop",
            "product_id": 45,
            "score": 0.87,
            "confidence": 0.82
        }
    ],
    "conversation_id": "conv_123_16811234567",
    "success": true
}
```

### 5. Quick Answer (No personalization)
```
POST /api/quick-answer/

Body:
{
    "query": "Bạn gửi hàng ngoài TP HCM không?"
}

Response:
{
    "query": "Bạn gửi hàng ngoài TP HCM không?",
    "answer": "Có, chúng tôi giao hàng trên toàn quốc...",
    "status": "success"
}
```

### 6. Clear Chat History
```
DELETE /api/chat-history/{customer_id}/

Response:
{
    "status": "success",
    "message": "Chat history cleared for customer 123"
}
```

---

## 🔧 Troubleshooting

### Issue: ANTHROPIC_API_KEY not found
**Solution:** Ensure the API key is set in your environment variables or `.env` file.

### Issue: Knowledge base not found when running chat
**Solution:** Run `python manage.py train_behavior_model --kb-only` to build KB.

### Issue: Behavior model not trained
**Solution:** Ensure you have order/cart data. Run `python manage.py train_behavior_model --model-only`.

### Issue: FAISS import error
**Solution:** Install FAISS: `pip install faiss-cpu` (or `faiss-gpu` for GPU support)

### Issue: Service connection timeouts
**Solution:** Check that all microservices are running and accessible at the configured URLs.

---

## 📈 Performance Tips

1. **Periodic Model Retraining:**
   - Schedule weekly/monthly model retraining using a task scheduler (Celery, APScheduler)
   - Keeps recommendations fresh with new user behavior

2. **Cache KB Embeddings:**
   - FAISS index is loaded once on service startup
   - Add Redis caching for frequently asked questions

3. **Batch Recommendations:**
   - Pre-compute recommendations for active users in off-peak hours
   - Store in cache for instant retrieval

4. **Vector DB Optimization:**
   - Use GPU-accelerated FAISS for large-scale deployments
   - Consider Pinecone or Weaviate for cloud-hosted solutions

---

## 🔐 Security Considerations

1. **API Key Management:**
   - Never commit ANTHROPIC_API_KEY to version control
   - Use environment variables or secret management tools

2. **Rate Limiting:**
   - Implement rate limiting on chat endpoints to prevent abuse
   - Monitor API usage to Anthropic

3. **Data Privacy:**
   - Customer data is only used for personalization, not stored externally
   - Chat history is kept in-memory (can be persisted to DB if needed)

4. **Input Validation:**
   - Messages are validated for length and content
   - Malicious inputs are sanitized before being sent to LLM

---

## 📊 Model Monitoring

Monitor these metrics:

- **Training Metrics:** Model loss, validation accuracy
- **Chat Metrics:** Response time, user satisfaction, recommendation click-through rate
- **KB Quality:** Embedding similarity scores, retrieval precision

---

## 🎓 Files Structure

```
recommender-ai-service/
├── recommender/
│   ├── behavior_model/
│   │   ├── model.py              # PyTorch NCF model definition
│   │   ├── data_pipeline.py      # Data fetching & preprocessing
│   │   ├── train.py              # Training script
│   │   ├── inference.py          # Model inference for production
│   │   └── pretrained_models/    # Saved models & ID mappings
│   │
│   ├── rag/
│   │   ├── kb_builder.py         # Knowledge base builder
│   │   ├── vector_store.py       # FAISS vector store manager
│   │   ├── chat_service.py       # RAG chat using Claude API
│   │   └── knowledge_base/       # KB documents & embeddings
│   │
│   ├── views.py                  # Django API views
│   ├── urls.py                   # URL routing
│   ├── models.py                 # Django models
│   └── management/commands/
│       └── train_behavior_model.py
│
├── recommender_config/
│   └── settings.py              # Service configuration
│
└── requirements.txt             # Python dependencies
```

---

## ✅ Deployment Checklist

- [ ] Environment variables configured (.env or docker-compose)
- [ ] All microservices running (customer, order, cart, product services)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrations run (`python manage.py migrate`)
- [ ] Behavior model trained (`python manage.py train_behavior_model --model-only`)
- [ ] Knowledge base built (`python manage.py train_behavior_model --kb-only`)
- [ ] API Gateway routing configured
- [ ] Chat widget integrated into frontend templates
- [ ] API keys validated (ANTHROPIC_API_KEY, etc.)
- [ ] Service accessible at expected port (e.g., 8014)

---

## 🎯 Next Steps

1. **Monitoring & Logging:**
   - Integrate with ELK stack or CloudWatch for logs
   - Set up alerts for API failures

2. **Advanced Features:**
   - Multi-language support (translate before/after LLM)
   - Sentiment analysis on chat messages
   - A/B testing different recommendation strategies

3. **Scaling:**
   - Use Kubernetes for container orchestration
   - Scale recommender-ai-service replicas based on load
   - Use managed vector DB (Pinecone) for unlimited scale

---

**Created:** 2026-04-06
**Version:** 1.0
