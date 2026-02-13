from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.role_question_generator import RoleBasedQuestionGenerator

router = APIRouter()
role_question_generator = RoleBasedQuestionGenerator()

class GenerateRoleQuestionsRequest(BaseModel):
    role: str
    count: int = 3

@router.post("/generate_role_questions")
async def generate_role_questions(request: GenerateRoleQuestionsRequest):
    """
    Generate role-based scenario questions for specific AI/ML roles.
    """
    try:
        questions = await role_question_generator.generate_role_questions(
            request.role,
            request.count
        )
        return questions
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
