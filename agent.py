
# import os, re
# from dataclasses import dataclass
# from typing import Any, Dict, List, Literal

# from dotenv import load_dotenv
# from langchain_core.prompts import ChatPromptTemplate
# from langgraph.graph import StateGraph, END
# from langchain_google_genai import ChatGoogleGenerativeAI
# from tavily import TavilyClient

# try:
#     from langchain_groq import ChatGroq
# except Exception:
#     ChatGroq = None  # optional fallback

# from app.rag import get_retriever, extract_course_info

# load_dotenv()

# GOOGLE_API_KEY = (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# PRIMARY_MODEL = "gemini-1.5-flash"
# _llm_primary = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, api_key=GOOGLE_API_KEY)
# _tavily = TavilyClient(api_key=TAVILY_API_KEY)

# _llm_fallback = None
# if ChatGroq and GROQ_API_KEY:
#     try:
#         _llm_fallback = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)
#     except Exception:
#         _llm_fallback = None

# _retriever = get_retriever(k=8, score_threshold=0.2)

# @dataclass
# class AgentState:
#     messages: List[Dict[str, str] | str]
#     context: str | None = None
#     source_tool: Literal["rag", "web"] | None = None
#     used_docs: List[str] | None = None
#     used_urls: List[str] | None = None
#     answer: str | None = None
#     extracted: Dict[str, str] | None = None

# COURSE_HINTS = (
#     "course,catalog,prerequisite,prereq,cs,comp sci,computer science,bio,biology,math,mathematics,"
#     "units,credits,semester,corequisite,section,enroll,enrollment,syllabus,department,subject,code"
# ).split(",")

# # --- helpers ---
# def _normalize_state(state_in: Any) -> Dict[str, Any]:
#     if isinstance(state_in, dict): return state_in
#     if isinstance(state_in, str): return {"mode": "auto","messages":[{"role":"user","content":state_in}]}
#     return {"mode":"auto","messages":[{"role":"user","content":str(state_in)}]}

# def _extract_query(state_in: Any) -> str:
#     s = _normalize_state(state_in)
#     msgs = s.get("messages") or []
#     if not msgs: return ""
#     last = msgs[-1]
#     return str(last.get("content","")) if isinstance(last,dict) else str(last)

# # --- nodes ---
# def router(state_in: Any) -> Literal["rag","web"]:
#     s = _normalize_state(state_in)
#     mode = str(s.get("mode") or "auto").lower()
#     print("🚦 Router got state:", s)
#     if mode == "rag": return "rag"
#     if mode == "web": return "web"
#     q = _extract_query(s).lower()
#     decision = "rag" if any(tok in q for tok in COURSE_HINTS) else "web"
#     print("🚦 Auto decision:", decision)
#     return decision

# def rag_node(state_in: Any) -> Dict[str,Any]:
#     state = _normalize_state(state_in)
#     query = _extract_query(state)
#     docs = _retriever.get_relevant_documents(query)

#     uniq = {}
#     for d in docs:
#         key = (d.metadata.get("source") or d.metadata.get("file_path","catalog"), d.metadata.get("page"))
#         if key not in uniq: uniq[key] = d
#     docs = list(uniq.values())

#     snippets, used = [], set()
#     for d in docs[:4]:
#         src = d.metadata.get("source") or d.metadata.get("file_path") or "catalog"
#         page = d.metadata.get("page","?")
#         used.add(src)
#         snippets.append(f"[{src}#p{page}] {d.page_content.strip()}")
#     context = "\n\n---\n\n".join(snippets) if snippets else "No relevant info found."

#     extracted = extract_course_info("\n".join(d.page_content for d in docs[:4]))
#     state.update({"context":context,"source_tool":"rag","used_docs":sorted(list(used)),"extracted":extracted})
#     return state

# def web_node(state_in: Any) -> Dict[str,Any]:
#     state = _normalize_state(state_in)
#     query = _extract_query(state)
#     try:
#         res = _tavily.search(query=query, include_images=False, include_answer=False, max_results=5)
#     except Exception as e:
#         state.update({"context":f"Tavily error: {e}","source_tool":"web","used_urls":[]})
#         return state
#     results = res.get("results",[]) if isinstance(res,dict) else res
#     urls,chunks=[],[]
#     for r in results[:4]:
#         title,content,url = r.get("title",""),r.get("content",""),r.get("url","")
#         if url: urls.append(url)
#         chunks.append(f"[{title}] {content}\n(Source: {url})")
#     state.update({"context":"\n\n---\n\n".join(chunks) or "No web results found.","source_tool":"web","used_urls":urls})
#     return state

# def generator_node(state_in: Any) -> Dict[str,Any]:
#     state = _normalize_state(state_in)
#     query = _extract_query(state)
#     context = state.get("context") or ""
#     source_tool = state.get("source_tool","")

#     if source_tool=="rag":
#         ex = state.get("extracted") or {}
#         code,title,prereq = ex.get("code",""),ex.get("title",""),ex.get("prereq","")
#         if code or title or prereq:
#             state["answer"] = f"- Course Code: {code or 'unknown'}\n- Title: {title or 'unknown'}\n- Prerequisites: {prereq or 'not stated'}"
#             return state

#     prompt = ChatPromptTemplate.from_template(
#         "You are IntelliCourse.\nIf source_tool=='rag', only answer from context.\n"
#         "Context:\n{context}\n\nQuestion: {query}\n\n"
#         "- Course Code: ...\n- Prerequisites: ...\n- Note: ..."
#     )
#     data={"context":context,"query":query,"source_tool":source_tool}
#     try:
#         resp=(prompt|_llm_primary).invoke(data)
#         state["answer"]=getattr(resp,"content",str(resp))
#         return state
#     except Exception as e_primary:
#         if _llm_fallback:
#             try:
#                 resp=(prompt|_llm_fallback).invoke(data)
#                 state["answer"]=getattr(resp,"content",str(resp))
#                 return state
#             except: pass
#         snippet=(context or "No context").split("\n\n---\n\n")[0][:400]
#         state["answer"]=f"LLM unavailable. Closest context:\n{snippet}"
#         return state

# def build_agent():
#     g=StateGraph(dict)
#     g.add_node("router",router)
#     g.add_node("rag",rag_node)
#     g.add_node("web",web_node)
#     g.add_node("generator",generator_node)
#     g.set_entry_point("router")
#     g.add_conditional_edges("router",router,{"rag":"rag","web":"web"})
#     g.add_edge("rag","generator")
#     g.add_edge("web","generator")
#     g.add_edge("generator",END)
#     return g.compile()
# filepath: app/agent.py
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Literal

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient

try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None  # fallback safe

from app.rag import get_retriever, extract_course_info

# --- Load envs ---
load_dotenv()
GOOGLE_API_KEY = (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# --- Clients ---
PRIMARY_MODEL = "gemini-1.5-flash"
_llm_primary = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, api_key=GOOGLE_API_KEY)
_tavily = TavilyClient(api_key=TAVILY_API_KEY)

_llm_fallback = None
if ChatGroq and GROQ_API_KEY:
    try:
        _llm_fallback = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)
    except Exception:
        _llm_fallback = None

# --- Retriever ---
_retriever = get_retriever(k=8, use_mmr=True, score_threshold=0.2)

# --- State ---
@dataclass
class AgentState:
    messages: List[Dict[str, str] | str]
    context: str | None = None
    source_tool: Literal["rag", "web"] | None = None
    used_docs: List[str] | None = None
    used_urls: List[str] | None = None
    answer: str | None = None
    extracted: Dict[str, str] | None = None

COURSE_HINTS = (
    "course,catalog,prerequisite,prereq,cs,comp sci,computer science,"
    "bio,biology,math,mathematics,units,credits,semester,corequisite,"
    "section,enroll,enrollment,syllabus,department,subject,code"
).split(",")

# --- Helpers ---
def _normalize_state(state_in: Any) -> Dict[str, Any]:
    if isinstance(state_in, dict):
        return state_in
    if isinstance(state_in, str):
        return {"mode": "auto", "messages": [{"role": "user", "content": state_in}]}
    return {"mode": "auto", "messages": [{"role": "user", "content": str(state_in)}]}

def _get_last_message(state_in: Any) -> str:
    """Safely extract the last message as plain text."""
    s = _normalize_state(state_in)
    msgs = s.get("messages") or []
    if not msgs:
        return ""
    last = msgs[-1]
    if isinstance(last, dict):
        return last.get("content", "")
    try:
        return last.content
    except AttributeError:
        return str(last)

# --- Nodes ---
def router(state_in: Any) -> Literal["rag", "web"]:
    s = _normalize_state(state_in)
    mode = str(s.get("mode") or "auto").lower()
    if mode in ("rag", "web"):
        return mode
    q = _get_last_message(s).lower()
    return "rag" if any(tok in q for tok in COURSE_HINTS) else "web"

def rag_node(state_in: Any) -> Dict[str, Any]:
    state = _normalize_state(state_in)
    query = _get_last_message(state)

    docs = _retriever.get_relevant_documents(query)

    # De-dup by (source,page)
    uniq = {}
    for d in docs:
        key = (d.metadata.get("source") or d.metadata.get("file_path") or "catalog", d.metadata.get("page"))
        if key not in uniq:
            uniq[key] = d
    docs = list(uniq.values())

    # Boost scoring
    hints = ["prerequisite", "applied machine learning"]
    m = re.search(r"\b([A-Z]{2,4})\s*0?(\d{3})\b", query, re.I)
    if m:
        dept, num = m.group(1).lower(), m.group(2)
        hints += [f"{dept}{num}", f"{dept} {num}"]

    def score(doc) -> int:
        t = (doc.page_content or "").lower()
        s = 0
        for h in hints:
            if h in t:
                s += 5
        return s

    top = sorted(docs, key=score, reverse=True)[:6]

    snippets, used = [], set()
    for d in top[:4]:
        src = d.metadata.get("source") or d.metadata.get("file_path") or "catalog"
        page = d.metadata.get("page", "?")
        used.add(src)
        snippets.append(f"[{src}#p{page}] {d.page_content.strip()}")

    context = "\n\n---\n\n".join(snippets) if snippets else "No relevant info found."
    extracted = extract_course_info("\n".join(d.page_content for d in top[:4]))

    state["context"] = context
    state["source_tool"] = "rag"
    state["used_docs"] = sorted(list(used))
    state["extracted"] = extracted
    return state

def web_node(state_in: Any) -> Dict[str, Any]:
    state = _normalize_state(state_in)
    query = _get_last_message(state)
    try:
        res = _tavily.search(query=query, include_images=False, include_answer=False, max_results=5)
    except Exception as e:
        state["context"] = f"Tavily error: {e}"
        state["source_tool"] = "web"
        state["used_urls"] = []
        return state

    results = res.get("results", []) if isinstance(res, dict) else (res if isinstance(res, list) else [])

    urls, chunks = [], []
    for r in results[:4]:
        title = r.get("title", "") if isinstance(r, dict) else ""
        content = r.get("content", "") if isinstance(r, dict) else str(r)
        url = r.get("url", "") if isinstance(r, dict) else ""
        if url:
            urls.append(url)
        chunks.append(f"[{title}] {content}\n(Source: {url})")

    state["context"] = "\n\n---\n\n".join(chunks) if chunks else "No web results found."
    state["source_tool"] = "web"
    state["used_urls"] = urls
    return state

def generator_node(state_in: Any) -> Dict[str, Any]:
    state = _normalize_state(state_in)
    query = _get_last_message(state)
    context = state.get("context") or ""
    source_tool = state.get("source_tool", "")

    if source_tool == "rag":
        ex = (state.get("extracted") or {})
        code, title, prereq = ex.get("code", ""), ex.get("title", ""), ex.get("prereq", "")
        if code or title or prereq:
            state["answer"] = (
                f"- Course Code: {code or 'unknown'}\n"
                f"- Title: {title or 'unknown'}\n"
                f"- Prerequisites: {prereq or 'not stated'}"
            )
            return state

    prompt = ChatPromptTemplate.from_template(
        "You are IntelliCourse, a precise university course advisor.\n"
        "If source_tool == 'rag', answer ONLY from catalog context.\n"
        "Context:\n{context}\n\nQuestion: {query}\n\n"
        "Format:\n- Course Code: ...\n- Title: ...\n- Prerequisites: ..."
    )
    data = {"context": context, "query": query, "source_tool": source_tool}

    try:
        resp = (prompt | _llm_primary).invoke(data)
        state["answer"] = getattr(resp, "content", str(resp))
        return state
    except Exception as e_primary:
        if _llm_fallback:
            try:
                resp = (prompt | _llm_fallback).invoke(data)
                state["answer"] = getattr(resp, "content", str(resp))
                return state
            except Exception:
                pass
        snippet = (context or "No context").split("\n\n---\n\n")[0][:400]
        state["answer"] = f"LLM unavailable.\nError: {e_primary}\nNearest context:\n{snippet}"
        return state

# --- Graph ---
def build_agent():
    graph = StateGraph(dict)
    graph.add_node("router", router)
    graph.add_node("rag", rag_node)
    graph.add_node("web", web_node)
    graph.add_node("generator", generator_node)
    graph.set_entry_point("router")
    graph.add_conditional_edges("router", router, {"rag": "rag", "web": "web"})
    graph.add_edge("rag", "generator")
    graph.add_edge("web", "generator")
    graph.add_edge("generator", END)
    return graph.compile()
