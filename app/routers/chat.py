from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.mentor_service import MentorService
from app.services.system_design_service import SystemDesignService
from app.services.mock_interview_service import MockInterviewService

router = APIRouter()

mentor_service = MentorService()
system_design_service = SystemDesignService()
mock_interview_service = MockInterviewService()

class MentorChatRequest(BaseModel):
    message: str
    history: list = []

class SystemDesignChatRequest(BaseModel):
    message: str
    history: list = []
    topic: str = "General System Design"

class MockInterviewChatRequest(BaseModel):
    message: str
    history: list = []
    topic: str = "General"

@router.post("/mentor/chat")
async def mentor_chat(request: MentorChatRequest):
    try:
        response = await mentor_service.chat(request.message, request.history)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system-design/chat")
async def system_design_chat(request: SystemDesignChatRequest):
    try:
        response = await system_design_service.chat(request.message, request.history, request.topic)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mock-interview/chat")
async def mock_interview_chat(request: MockInterviewChatRequest):
    try:
        response = await mock_interview_service.chat(request.message, request.history, request.topic)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
