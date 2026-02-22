from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.services.workflow_runner import WorkflowRunner

router = APIRouter(prefix="/services", tags=["services"])
runner = WorkflowRunner()


class ServiceRunRequest(BaseModel):
    service_id: str
    input: Dict[str, Any]


@router.post("/run")
async def run_service(payload: ServiceRunRequest):
    try:
        result = await runner.run(payload.service_id, payload.input)
        return {"service_id": payload.service_id, "result": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
