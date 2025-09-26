
# # from __future__ import annotations
# # import os
# # from fastapi import FastAPI, HTTPException
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel, Field

# # from app.agent import build_agent

# # app = FastAPI(title="IntelliCourse", version="1.0.0")

# # # CORS open for local dev
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
# # )

# # class Query(BaseModel):
# #     query: str = Field(..., min_length=2)
# #     mode: str | None = Field(default="auto", description="auto|rag|web")

# # @app.on_event("startup")
# # def _startup() -> None:
# #     # Why: fail fast instead of vague runtime 500s
# #     if not os.getenv("GEMINI_API_KEY"):
# #         raise RuntimeError("GEMINI_API_KEY missing in environment/.env")
# #     if not os.getenv("TAVILY_API_KEY"):
# #         raise RuntimeError("TAVILY_API_KEY missing in environment/.env")
# #     global _agent
# #     _agent = build_agent()
# #     print("✅ Agent ready.")

# # @app.get("/health")
# # def health():
# #     return {
# #         "status": "ok",
# #         "gemini": bool(os.getenv("GEMINI_API_KEY")),
# #         "tavily": bool(os.getenv("TAVILY_API_KEY")),
# #     }

# # @app.post("/chat")
# # async def chat(user_query: Query):
# #     q = (user_query.query or "").strip()
# #     if not q:
# #         raise HTTPException(status_code=400, detail="Empty query")

# #     # Pass optional mode to the agent so you can force RAG/WEB in Postman
# #     state = {
# #         "mode": (user_query.mode or "auto"),
# #         "messages": [{"role": "user", "content": q}],
# #     }
# #     try:
# #         result = _agent.invoke(state)
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Agent error: {e}") from e

# #     # Defensive: normalize non-dict return to avoid 'str'.get crashes
# #     if not isinstance(result, dict):
# #         result = {"answer": str(result), "source_tool": "rag", "context": ""}

# #     ctx_str = str(result.get("context") or "")
# #     ctx_snips = [s[:400] for s in ctx_str.split("\n\n---\n\n")[:4]]

# #     return {
# #         "answer": result.get("answer", "No answer generated."),
# #         "source_tool": result.get("source_tool", "rag"),
# #         "context_snippets": ctx_snips,
# #         "used_docs": result.get("used_docs") or [],
# #         "used_urls": result.get("used_urls") or [],
# #     }
# # =========================================
# # filepath: app/main.py
# # =========================================
# # from __future__ import annotations
# # import os
# # from fastapi import FastAPI, HTTPException
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel, Field

# # from app.agent import build_agent

# # app = FastAPI(title="IntelliCourse", version="1.0.0")

# # # Open CORS for local dev
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
# # )

# # class Query(BaseModel):
# #     query: str = Field(..., min_length=2)
# #     mode: str | None = Field(default="auto", description="auto|rag|web")

# # @app.on_event("startup")
# # def _startup() -> None:
# #     # why: fail fast instead of vague runtime 500s
# #     if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
# #         raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY missing in environment/.env")
# #     if not os.getenv("TAVILY_API_KEY"):
# #         raise RuntimeError("TAVILY_API_KEY missing in environment/.env")
# #     global _agent
# #     _agent = build_agent()
# #     print("✅ Agent ready.")

# # @app.get("/health")
# # def health():
# #     return {
# #         "status": "ok",
# #         "gemini": bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")),
# #         "tavily": bool(os.getenv("TAVILY_API_KEY")),
# #     }

# # @app.post("/chat")
# # async def chat(user_query: Query):
# #     q = (user_query.query or "").strip()
# #     if not q:
# #         raise HTTPException(status_code=400, detail="Empty query")

# #     state = {
# #         "mode": (user_query.mode or "auto"),
# #         "messages": [{"role": "user", "content": q}],
# #     }
# #     try:
# #         result = _agent.invoke(state)
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Agent error: {e}") from e

# #     # Defensive: normalize non-dict return to avoid 'str'.get crashes
# #     if not isinstance(result, dict):
# #         result = {"answer": str(result), "source_tool": "rag", "context": ""}

# #     ctx_str = str(result.get("context") or "")
# #     ctx_snips = [s[:400] for s in ctx_str.split("\n\n---\n\n")[:4]]

# #     return {
# #         "answer": result.get("answer", "No answer generated."),
# #         "source_tool": result.get("source_tool", "rag"),
# #         "context_snippets": ctx_snips,
# #         "used_docs": result.get("used_docs") or [],
# #         "used_urls": result.get("used_urls") or [],
# #     }
# # filepath: app/main.py
# # =========================================
# # from __future__ import annotations
# # import os
# # from fastapi import FastAPI, HTTPException
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel, Field

# # from app.agent import build_agent
# # from app.rag import prepare_vector_store

# # app = FastAPI(title="IntelliCourse", version="1.1.0")

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
# # )

# # class Query(BaseModel):
# #     query: str = Field(..., min_length=2)
# #     mode: str | None = Field(default="auto", description="auto|rag|web")

# # class ReindexRequest(BaseModel):
# #     rebuild: bool = False

# # @app.on_event("startup")
# # def _startup() -> None:
# #     if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
# #         raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY missing in environment/.env")
# #     if not os.getenv("TAVILY_API_KEY"):
# #         raise RuntimeError("TAVILY_API_KEY missing in environment/.env")
# #     global _agent
# #     _agent = build_agent()
# #     print("✅ Agent ready.")

# # @app.get("/health")
# # def health():
# #     return {
# #         "status": "ok",
# #         "gemini": bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")),
# #         "tavily": bool(os.getenv("TAVILY_API_KEY")),
# #     }

# # @app.post("/reindex")
# # def reindex(body: ReindexRequest):
# #     try:
# #         _, created = prepare_vector_store(rebuild=body.rebuild)
# #         return {"status": "ok", "rebuild": body.rebuild, "created": created}
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Reindex error: {e}") from e

# # @app.post("/chat")
# # async def chat(user_query: Query):
# #     q = (user_query.query or "").strip()
# #     if not q:
# #         raise HTTPException(status_code=400, detail="Empty query")

# #     state = {"mode": (user_query.mode or "auto"), "messages": [{"role": "user", "content": q}]}
# #     try:
# #         result = _agent.invoke(state)
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Agent error: {e}") from e

# #     if not isinstance(result, dict):
# #         result = {"answer": str(result), "source_tool": "rag", "context": ""}

# #     ctx_str = str(result.get("context") or "")
# #     ctx_snips = [s[:400] for s in ctx_str.split("\n\n---\n\n")[:4]]

# #     return {
# #         "answer": result.get("answer", "No answer generated."),
# #         "source_tool": result.get("source_tool", "rag"),
# #         "context_snippets": ctx_snips,
# #         "used_docs": result.get("used_docs") or [],
# #         "used_urls": result.get("used_urls") or [],
# #     }
# from __future__ import annotations
# import os
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field

# from app.agent import build_agent
# from app.rag import prepare_vector_store

# app = FastAPI(title="IntelliCourse", version="1.1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
# )

# class Query(BaseModel):
#     query: str = Field(..., min_length=2)
#     mode: str | None = Field(default="auto", description="auto|rag|web")

# class ReindexRequest(BaseModel):
#     rebuild: bool = False

# @app.on_event("startup")
# def _startup() -> None:
#     if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
#         raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY missing in environment/.env")
#     if not os.getenv("TAVILY_API_KEY"):
#         raise RuntimeError("TAVILY_API_KEY missing in environment/.env")
#     global _agent
#     _agent = build_agent()
#     print("✅ Agent ready.")

# @app.get("/health")
# def health():
#     return {
#         "status": "ok",
#         "gemini": bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")),
#         "tavily": bool(os.getenv("TAVILY_API_KEY")),
#     }

# @app.post("/reindex")
# def reindex(body: ReindexRequest):
#     try:
#         _, created = prepare_vector_store(rebuild=body.rebuild)
#         return {"status": "ok", "rebuild": body.rebuild, "created": created}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Reindex error: {e}") from e

# @app.post("/chat")
# async def chat(user_query: Query):
#     q = (user_query.query or "").strip()
#     if not q:
#         raise HTTPException(status_code=400, detail="Empty query")

#     state = {"mode": (user_query.mode or "auto"), "messages": [{"role": "user", "content": q}]}
#     try:
#         result = _agent.invoke(state)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Agent error: {e}") from e

#     if not isinstance(result, dict):
#         result = {"answer": str(result), "source_tool": "rag", "context": ""}

#     ctx_str = str(result.get("context") or "")
#     ctx_snips = [s[:400] for s in ctx_str.split("\n\n---\n\n")[:4]]

#     return {
#         "answer": result.get("answer", "No answer generated."),
#         "source_tool": result.get("source_tool", "rag"),
#         "context_snippets": ctx_snips,
#         "used_docs": result.get("used_docs") or [],
#         "used_urls": result.get("used_urls") or [],
#     }
# class ReindexRequest(BaseModel):
#     rebuild: bool = False

# @app.post("/reindex")
# def reindex(body: ReindexRequest):
#     try:
#         _, created = prepare_vector_store(rebuild=body.rebuild)
#         return {"status": "ok", "rebuild": body.rebuild, "created": created}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Reindex error: {e}") from e
# filepath: app/main.py
from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agent import build_agent
from app.rag import prepare_vector_store

app = FastAPI(title="IntelliCourse", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

class Query(BaseModel):
    query: str = Field(..., min_length=2)
    mode: str | None = Field(default="auto", description="auto|rag|web")

class ReindexRequest(BaseModel):
    rebuild: bool = False

@app.on_event("startup")
def _startup():
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        raise RuntimeError("Missing GOOGLE_API_KEY or GEMINI_API_KEY in env")
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("Missing TAVILY_API_KEY in env")
    global _agent
    _agent = build_agent()
    print("✅ Agent ready.")

@app.get("/health")
def health():
    return {"status":"ok","gemini":bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")),
            "tavily":bool(os.getenv("TAVILY_API_KEY"))}

@app.post("/reindex")
def reindex(body: ReindexRequest):
    try:
        _, created = prepare_vector_store(rebuild=body.rebuild)
        return {"status":"ok","rebuild":body.rebuild,"created":created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindex error: {e}")

@app.post("/chat")
async def chat(user_query: Query):
    q=(user_query.query or "").strip()
    if not q: raise HTTPException(status_code=400, detail="Empty query")
    state={"mode":(user_query.mode or "auto"),"messages":[{"role":"user","content":q}]}
    try:
        result=_agent.invoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}") from e
    if not isinstance(result,dict):
        result={"answer":str(result),"source_tool":"rag","context":""}
    ctx_str=str(result.get("context") or "")
    ctx_snips=[s[:400] for s in ctx_str.split("\n\n---\n\n")[:4]]
    return {"answer":result.get("answer","No answer generated."),
            "source_tool":result.get("source_tool","rag"),
            "context_snippets":ctx_snips,
            "used_docs":result.get("used_docs") or [],
            "used_urls":result.get("used_urls") or []}
