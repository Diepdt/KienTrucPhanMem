# 🔍 SO SÁNH: Agent Service vs Recommender AI Service

**Nhận xét:** Bạn đã đúng! Agent Service cũng xây dựng chatbot bằng Gemini API. Cả hai service đều tương tự nhưng có **mục đích và kiến trúc khác biệt**.

---

## 📊 **BẢNG SO SÁNH TỔNG QUÁT**

| Tiêu Chí | Agent Service | Recommender AI Service |
|----------|---------------|----------------------|
| **Mục Đích** | Chatbot tư vấn + thực thi action | Gợi ý sản phẩm cá nhân hóa |
| **LLM** | Gemini API (OpenAI-compatible) | Claude API (hoặc Gemini) |
| **Kiến Trúc** | Function Calling (ReAct Agent) | RAG + Behavior Model |
| **Tools/Capabilities** | search_books, add_book_to_cart | Behavior Model, KB Search |
| **Input** | {message, session_id, user_id} | {customer_id, message} |
| **Output** | {reply, session_id} | {response, recommended_products} |
| **Endpoints** | 1 endpoint (POST /api/agent/chat/) | 7 endpoints (chat, train, build KB, etc.) |

---

## 🏗️ **KIẾN TRÚC KHÁC BIỆT**

### **Agent Service: Function Calling Loop (ReAct)**

```
┌─────────────────────────────────────┐
│  User: "Tìm sách của Nguyễn Nhật Ánh" │
└────────────────┬────────────────────┘
                 │
         ┌───────▼──────────┐
         │ Load Chat History │
         └───────┬──────────┘
                 │
    ┌────────────▼──────────────┐
    │ Build Messages + SYSTEM    │
    │ PROMPT + TOOL_DEFINITIONS  │
    └────────┬───────────────────┘
             │
    ┌────────▼──────────────────────┐
    │ Call Gemini LLM (with tools)  │  ◄─ API Key: GEMINI_API_KEY
    └────────┬──────────────────────┘
             │
    ◄─────────┴──────────────────────────────────────┐
    │ LLM returns tool_calls?                         │
    │ {name: "search_books", args: {...}}             │
    │                                                 │
    ├─ YES → Execute tool (search_books)            │
    │        └─ Call real API (book-service)         │
    │        └─ Get results                           │
    │        └─ Add results to messages               │
    │        └─ Call Gemini again (2nd time)         │
    │        └─ LLM summarizes & returns text         │
    │                                                 │
    └─ NO → LLM returns text answer directly         │
             │
    ┌────────▼──────────────────────────┐
    │ Save message to chat history       │
    │ Memory (chat_histories dict)       │
    └────────┬──────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │ Return {reply, session_id}         │
    └────────────────────────────────────┘
```

**Đặc điểm:**
- ✅ **Vòng lặp Function Calling** (gọi LLM nhiều lần)
- ✅ **Thực thi actions** (search, add to cart)
- ✅ **Tool execution** (tích hợp với book-service, cart-service)
- ✅ **ReAct Agent** (Reasoning + Acting)

---

### **Recommender AI Service: RAG + Behavior Model**

```
┌──────────────────────────────────────────────────┐
│ User: "Có laptop gaming dưới 20 triệu không?"    │
└────────────────┬─────────────────────────────────┘
                 │
     ┌───────────▼───────────┐
     │ Extract customer_id    │
     │ Extract message        │
     └───────────┬───────────┘
                 │
    ┌────────────▼─────────────────────────────┐
    │ [Step 1] Behavior Model Inference        │
    │  - Load pre-trained PyTorch model        │
    │  - Predict top-K products customer wants │
    │  - Output: [{item_id, score}, ...]       │
    └────────────┬────────────────────────────┘
                 │
    ┌────────────▼─────────────────────────────┐
    │ [Step 2] Knowledge Base Search (FAISS)   │
    │  - Embed query: "laptop gaming < 20M"    │
    │  - Search FAISS index                    │
    │  - Get top-5 documents from KB           │
    │  - Retrieve product info + policies      │
    └────────────┬────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────┐
    │ [Step 3] Construct Prompt for LLM             │
    │  Prompt = {                                    │
    │    "Customer query": "...",                    │
    │    "Behavior insights": "Customer likes...",   │
    │    "KB documents": [doc1, doc2, ...],          │
    │    "Instructions": "Reply in Vietnamese"       │
    │  }                                             │
    └────────────┬──────────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────┐
    │ [Step 4] Call LLM (Claude or Gemini)          │  ◄─ 1 API call
    │  - LLM generates response                      │
    │  - No tool calling (just text generation)      │
    └────────────┬──────────────────────────────────┘
                 │
    ┌────────────▼───────────────────────────────────┐
    │ [Step 5] Format & Return Response              │
    │  {                                              │
    │    "response": "Dựa trên sở thích...",          │
    │    "recommended_products": [...],               │
    │    "conversation_id": "...",                    │
    │    "success": true                              │
    │  }                                              │
    └───────────────────────────────────────────────┘
```

**Đặc điểm:**
- ✅ **RAG Pipeline** (Retrieval + Generation)
- ✅ **Behavior Model** (Deep Learning dự đoán sở thích)
- ✅ **Vector Search** (FAISS - nhanh, offline)
- ✅ **Single LLM Call** (hiệu quả hơn)
- ✅ **Knowledge Base** (lưu toàn bộ thông tin sản phẩm)

---

## 💡 **FUNCTION CALLING vs SINGLE CALL**

### **Agent Service: Function Calling (Multiple LLM Calls)**

```python
# Lần 1: LLM quyết định tool nào gọi
LLM_Call_1({
    messages: [...],
    tools: [
        {name: "search_books", ...},
        {name: "add_book_to_cart", ...},
        ...
    ]
})
# Response: {"tool_calls": [{"name": "search_books", "args": {...}}]}

# Thực thi tool
search_books("Nguyễn Nhật Ánh")  # → API call to book-service
# Result: [{id: 1, title: "Dắt tôi...", ...}]

# Lần 2: LLM xử lý kết quả tool & sinh response
LLM_Call_2({
    messages: [
        ...previous,
        {role: "assistant", tool_calls: [...]},
        {role: "tool", content: "search results..."}
    ]
})
# Response: "Tôi tìm được 5 cuốn sách của tác giả này..."
```

**Ưu/Nhược:**
- ✅ Có thể thực thi actions (interactive)
- ✅ LLM quyết định gọi tool nào
- ❌ Gọi LLM 2 lần → chậm hơn
- ❌ Chi phí cao (2 API calls)

---

### **Recommender AI Service: Single Call + Pre-Processing**

```python
# Pre-process: Lấy data từ behavior model + KB
behavior_insights = predict_customer_preference(123)
# Output: "Customer likes gaming products (DTF: 0.92)"

kb_docs = search_kb("laptop gaming < 20M")
# Output: [doc1: "ASUS TUF A15 19.5M", ...]

# Xây dựng prompt hoàn chỉnh
prompt = f"""
Customer query: "Có laptop gaming < 20M?"
Behavior insight: {behavior_insights}
KB documents: {kb_docs}
System instruction: "Trả lời tiếng Việt..."
"""

# LLM Call 1 lần duy nhất
response = claude.generate({prompt: prompt})
# Response: "Dựa trên sở thích gaming của bạn..."
```

**Ưu/Nhược:**
- ✅ Một lần gọi LLM → nhanh
- ✅ Chi phí thấp hơn
- ✅ Kết hợp behavior model + KB trước
- ❌ Không có interactive tool calling (không thể search real-time)

---

## 🎯 **MỤC ĐÍCH KHÁC BIỆT**

### **Agent Service: General Conversational AI**

```
Mục tiêu: "Chatbot tư vấn có khả năng action"

Use Cases:
  1. Customer: "Tìm sách của tác giả X"
     → Agent: search_books("tác giả X")
     → Agent: "Tìm được 5 cuốn..."
  
  2. Customer: "Thêm cuốn này vào giỏ"
     → Agent: add_book_to_cart(user_id, book_id)
     → Agent: "Đã thêm vào giỏ hàng"
  
  3. Customer: "Có sách gì mới hay?"
     → Agent: search_books("")
     → Agent: "Mới có Dắt tôi qua bóng tối..."

Tính chất: Interactive, action-oriented, open-ended
```

---

### **Recommender AI Service: Personalized Recommendation**

```
Mục tiêu: "Chat tư vấn cá nhân hóa dựa trên hành vi"

Use Cases:
  1. Customer: "Có laptop gaming dưới 20M không?"
     → Behavior: "Customer usually buys gaming laptops"
     → KB: "ASUS TUF A15 19.5M, Lenovo Legion 18.9M"
     → Response: "Dựa trên sở thích, tôi gợi ý..."
  
  2. Customer: "Laptop nào tốt nhất?"
     → Behavior: "Top-3 products for this customer"
     → Response: "Tuỳ tiêu chí, có thể xem..."
  
  3. Customer: "Có sản phẩm mới không?"
     → Behavior prediction + KB search
     → Response: "Mới có X sản phẩm phù hợp..."

Tính chất: Personalized, ML-driven, recommendation-oriented
```

---

## 🔑 **API KEY VÀ LLM PROVIDER**

### **Agent Service:**
```
Provider: Google Gemini
API Key: GEMINI_API_KEY
Endpoint: https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
Format: OpenAI-compatible (dùng requests.post)
Pricing: Free tier 60 req/min
```

### **Recommender AI Service (Hiện Tại in Code):**
```
Provider: Anthropic Claude
API Key: ANTHROPIC_API_KEY
Endpoint: https://api.anthropic.com/v1/messages
Format: Anthropic-native (dùng anthropic.Anthropic())
Pricing: Tính tiền (~$0.01/request)

Alternative (Khuyên dùng - free):
Provider: Google Gemini
API Key: GEMINI_API_KEY
Endpoint: Same as Agent Service
Chi phí: Free
```

---

## ✅ **SUMMARY: Bạn Nên Làm Gì?**

### **Option 1: Tái sử dụng Agent Service (Nhanh nhất)**

```
Agent Service đã có:
  ✅ Gemini API integration
  ✅ Function calling logic
  ✅ Chat history management
  ✅ Tool execution (search_books, add_to_cart)

Tôi có thể:
  1. Modify Agent Service để thêm Behavior Model + RAG
  2. Reuse Gemini API setup từ Agent Service
  3. Thêm recommendation logic vào tool definitions

Time: 30 phút
Result: 1 service xử lý tất cả (chat + recommendation)
```

### **Option 2: Dùng Recommender Service Mới (Logic rõ ràng)**

```
Recommender Service là:
  ✅ Specialized cho recommendation task
  ✅ RAG pipeline rõ ràng (retrieval → generation)
  ✅ Behavior Model dedicate
  ✅ Separate concerns (KB, model, chat)

Lợi ích:
  - Dễ maintain
  - Dễ scale
  - Dễ test từng component

Time: ~1 giờ (setup Gemini + integrate)
Result: Microservice xử lý recommendation riêng
```

### **Option 3: Merge Both (Comprehensive)**

```
Agent Service → General chat (search, action)
Recommender Service → Personalized recommendations

Agent khi cần gợi ý → Call Recommender Service API
Recommender dùng Gemini API (free tier)

Time: 1-2 giờ
Result: Separation of concerns + reusable components
```

---

## 🎯 **KHUYẾN NGHỊ CUỐI CÙNG**

**Bạn nên dùng: Recommender Service (Option 2)**

**Vì sao:**
1. ✅ **Đáp spec đề tài rõ ràng**
   - "Behavior model + KB + RAG"
   - Logic hiển thị qua 4 bước rõ ràng

2. ✅ **Khác biệt so với Agent Service**
   - Agent: Function calling (interactive)
   - Recommender: RAG + Behavior Model (predictive)

3. ✅ **Dùng Gemini API free (như Agent)**
   - Cùng provider → consistent
   - Free tier đủ dùng

4. ✅ **Dễ demo cho thầy**
   - Behavior Model: "Dự đoán sở thích"
   - KB: "Lưu tài liệu sản phẩm"
   - RAG: "Kết hợp và trả lời"

---

**Kết luận:** Recommender Service mà tôi xây dựng là **bổ sung** cho Agent Service, không phải **thay thế**. Cả hai cùng tồn tại:
- Agent = General chatbot (search, action)
- Recommender = Personalized AI (behavior + recommendation)

**Bạn đồng ý?** 👍

