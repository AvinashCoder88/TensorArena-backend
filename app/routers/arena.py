from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.question_generator import QuestionGenerator
from app.services.code_executor import CodeExecutor

router = APIRouter()

question_generator = QuestionGenerator()
code_executor = CodeExecutor(timeout=5)

class GenerateRequest(BaseModel):
    topic: str
    difficulty: str
    user_context: str = None

class ExecuteCodeRequest(BaseModel):
    code: str

class GradeRequest(BaseModel):
    code: str
    question_title: str
    question_description: str
    language: str = "python"

@router.post("/generate_question")
async def generate_question(request: GenerateRequest):
    try:
        question = await question_generator.generate_question(
            request.topic, 
            request.difficulty, 
            request.user_context
        )
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute_code")
async def execute_code(request: ExecuteCodeRequest):
    try:
        result = code_executor.execute_python(request.code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/grade_submission")
async def grade_submission(request: GradeRequest):
    try:
        grading = await question_generator.grade_submission(
            request.code,
            request.question_title,
            request.question_description
        )
        return grading
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
