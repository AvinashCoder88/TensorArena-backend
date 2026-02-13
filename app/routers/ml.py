from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.services.ml_service import MLService
import uuid

router = APIRouter()
ml_service = MLService()

# Simple In-Memory Storage for Demo
csv_storage = {}

class TrainRequest(BaseModel):
    file_id: str
    target_column: str
    model_type: str
    task_type: str = "classification"

class InsightRequest(BaseModel):
    results: dict
    model_type: str

@router.post("/ml/process_csv")
async def process_csv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        result = ml_service.process_csv(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ml/upload")
async def upload_csv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_id = str(uuid.uuid4())
        csv_storage[file_id] = content # In-memory
        
        # Process meta
        meta = ml_service.process_csv(content)
        return {"file_id": file_id, "metadata": meta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ml/train")
async def train_model(request: TrainRequest):
    try:
        if request.file_id not in csv_storage:
             raise HTTPException(status_code=404, detail="File session expired or not found")
             
        content = csv_storage[request.file_id]
        result = ml_service.train_model(content, request.target_column, request.model_type, request.task_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ml/insight")
async def get_insight(request: InsightRequest):
    try:
        insight = await ml_service.generate_insight(request.results, request.model_type)
        return {"insight": insight}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
