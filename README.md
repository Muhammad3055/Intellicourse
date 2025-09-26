# Intellicourse
Perfect idea ✅ — a **README** will keep all the steps clear so you don’t get stuck again.
Here’s a clean **README.md** for your project:

---

# 📘 IntelliCourse – Course Catalog RAG + Web Agent

This project is a **FastAPI-based agent** that answers university course-related questions using **Retrieval-Augmented Generation (RAG)** from PDF catalogs and **web search** (Tavily) when catalog data is missing.

---

## 🚀 Features

* **RAG mode** → Answers strictly from your course PDFs (`CS`, `BIO`, `MATH`, etc.)
* **Web mode** → Answers from Tavily search engine
* **Auto mode** → Agent decides (`rag` if course-related, otherwise `web`)
* **Reindexing** → Rebuild vector DB from PDFs anytime
* **Health check** → Confirm API keys and server readiness

---

## 📂 Project Structure

```
app/
 ├── main.py        # FastAPI entrypoint (endpoints)
 ├── agent.py       # Agent logic (RAG + Web + LLM generation)
 ├── rag.py         # PDF loading, splitting, embedding, retriever
 ├── config.py      # Config paths, loads .env
 ├── schemas.py     # Pydantic request/response models
 └── data/          # Store all course catalog PDFs here
vector_db/          # Persisted Chroma DB
.env                # API keys
```

---

## 🔑 Requirements

* Python 3.10+
* Virtual environment (`venv`)
* Dependencies in `requirements.txt`:

  ```txt
  fastapi
  uvicorn
  python-dotenv
  langchain
  langchain-community
  langchain-google-genai
  langchain-chroma
  langchain-huggingface
  tavily
  pydantic
  ```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone and install

```bash
git clone <your-repo>
cd Intellicourse
python -m venv venv
venv\Scripts\activate    # Windows
# OR
source venv/bin/activate # Linux/Mac
pip install -r requirements.txt
```

### 2️⃣ Environment Variables

Create a `.env` file in the root:

```env
GEMINI_API_KEY=your_gemini_key
TAVILY_API_KEY=your_tavily_key
```

### 3️⃣ Add PDFs

Place your catalog files in `app/data/`, e.g.:

```
CS_Catalog_Fall_2025.pdf
MATH_Catalog_Fall_2025.pdf
BIO_Catalog_Fall_2025.pdf
LAW_Catalog_Fall_2025.pdf
BUS_Catalog_Fall_2025.pdf
```

### 4️⃣ Build Vector DB

```bash
uvicorn app.main:app --reload
```

Then call in Postman:

```
POST http://127.0.0.1:8000/reindex
Body (JSON):
{
  "rebuild": true
}
```

---

## 🔗 API Endpoints

### Health

```http
GET http://127.0.0.1:8000/health
```

✅ Returns `status: ok` if keys and server are fine.

### Chat

```http
POST http://127.0.0.1:8000/chat
Body (JSON):
{
  "query": "What are the prerequisites for CS 482 Applied Machine Learning?",
  "mode": "rag"
}
```

Modes:

* `"rag"` → force catalog lookup
* `"web"` → force Tavily lookup
* `"auto"` → let router decide

### Reindex

```http
POST http://127.0.0.1:8000/reindex
Body:
{
  "rebuild": true
}
```

---

## 🧪 Example Response

```json
{
  "answer": "- Course Code: CS 482\n- Prerequisites: CS 240\n- Note: Title: Applied Machine Learning",
  "source_tool": "rag",
  "context_snippets": [
    "[CS_Catalog_Fall_2025#p1] Course Code: CS 482 ... Prerequisites: CS 240"
  ],
  "used_docs": ["CS_Catalog_Fall_2025.pdf"],
  "used_urls": []
}
```

---

## 🛠 Troubleshooting

* **Got “LLM unavailable”** → Check `.env` has valid `GEMINI_API_KEY`.
* **Got “Not Found” on `/reindex`** → Make sure you’re running the latest `main.py`.
* **Wrong answers (web instead of catalog)** → Use `"mode": "rag"` in Postman to force catalog retrieval.
* **No docs retrieved** → Lower/remove `score_threshold` in `rag.py`.

---

⚡ Now you can query **any course across all catalogs**, not just CS.

---

👉 Do you want me to also include **ready-to-run Postman collection (JSON file)** so you can just import and test endpoints instantly?
