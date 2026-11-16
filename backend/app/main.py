import uuid, time, logging
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .security import require_api_key
from .schemas import ChatRequest, ChatResponse, ApprovalRequest
from .rag import store_document
from .agents import run_workflow
from .observability import new_metrics
from .db import init_db
@app.on_event("startup")
def startup():
    init_db()
app=FastAPI(title="FieldLens AI",version="0.1.0",description="Enterprise RAG + governed agent workflows")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.allowed_origins.split(",")],allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["*"])
logging.basicConfig(level=logging.INFO)
@app.get("/health")
def health(): return {"status":"ok","service":"fieldlens-api"}
@app.get("/v1/health",dependencies=[Depends(require_api_key)])
def protected_health(): return {"status":"ok"}
@app.post("/v1/documents",dependencies=[Depends(require_api_key)])
async def upload_document(file: UploadFile=File(...)):
    raw=await file.read(settings.max_upload_mb*1024*1024+1)
    if len(raw)>settings.max_upload_mb*1024*1024: raise HTTPException(413,"File exceeds configured upload limit")
    try: doc_id=store_document(file.filename or "upload",file.content_type or "",raw)
    except Exception as e: raise HTTPException(400,str(e))
    return {"document_id":doc_id,"filename":file.filename,"status":"indexed"}
@app.post("/v1/chat",response_model=ChatResponse,dependencies=[Depends(require_api_key)])
def chat(req: ChatRequest):
    metrics=new_metrics()
    try: result=run_workflow(req.question,req.mode)
    except Exception as e:
        logging.exception("workflow_failed request_id=%s",metrics.request_id)
        raise HTTPException(500,"Workflow execution failed. Check server logs.")
    # Token counts are populated by provider response metadata in production instrumentation.
    metrics.model=settings.gemini_model if settings.llm_provider!="mock" else "mock"
    metrics.input_tokens=int(result.get("input_tokens",0))
    metrics.output_tokens=int(result.get("output_tokens",0))
    stats=metrics.finish()
    return ChatResponse(request_id=metrics.request_id,answer=result.get("answer",""),sources=result.get("sources",[]),metrics=stats,route=result.get("route","unknown"))
@app.post("/v1/actions/approve",dependencies=[Depends(require_api_key)])
def approve_action(req: ApprovalRequest):
    if not req.approved: return {"status":"rejected","approved_by":req.approved_by}
    # Demonstration boundary: this endpoint records approval but intentionally does not execute arbitrary actions.
    return {"status":"approved","action":req.action,"approved_by":req.approved_by,"execution":"not-configured"}
