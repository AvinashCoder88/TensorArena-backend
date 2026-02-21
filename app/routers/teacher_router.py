from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from app.services.grading_service import GradingService
import os
import uuid
import json

router = APIRouter(prefix="/teacher", tags=["teacher"])
grading_service = GradingService()

# Ensure upload directory exists
UPLOADS_DIR = "app/static/uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)


# ============ PYDANTIC MODELS ============

class GradeCreate(BaseModel):
    name: str  # e.g. "10th Grade"

class DivisionCreate(BaseModel):
    name: str  # e.g. "Division A"

class SubjectCreate(BaseModel):
    name: str  # e.g. "Mathematics"

class ClassroomCreate(BaseModel):
    teacherId: str
    divisionId: str
    subjectId: str

class StudentEnroll(BaseModel):
    studentId: str
    divisionId: str


# ============ GRADE ENDPOINTS ============

@router.get("/grades")
async def list_grades():
    """List all grades."""
    # This data lives in the frontend Prisma DB
    # Return placeholder — frontend calls its own API routes
    return {"message": "Use frontend /api/teacher/grades endpoint"}

@router.post("/grades")
async def create_grade(grade: GradeCreate):
    return {"message": "Use frontend /api/teacher/grades endpoint", "name": grade.name}


# ============ QUESTION PAPER PROCESSING ============

@router.post("/extract-paper")
async def extract_question_paper(file: UploadFile = File(...)):
    """
    Upload a question paper image/PDF.
    Uses Gemini to extract all questions, marks per question, and total marks.
    """
    try:
        content = await file.read()
        mime_type = file.content_type or "image/jpeg"

        # Save file
        filename = f"qp_{uuid.uuid4()}{_get_extension(file.filename)}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(content)

        # Extract questions using Gemini
        extraction = await grading_service.extract_question_paper(content, mime_type)

        if "error" in extraction:
            raise HTTPException(status_code=500, detail=extraction["error"])

        return {
            "file_url": f"/static/uploads/{filename}",
            "title": extraction.get("title", "Untitled Exam"),
            "total_marks": extraction.get("total_marks", 0),
            "questions": extraction.get("questions", []),
            "full_text": extraction.get("full_text", ""),
            "mark_scheme": json.dumps(extraction.get("questions", []))
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grade-answer")
async def grade_answer_sheet(
    file: UploadFile = File(...),
    question_paper_text: str = Form(""),
    mark_scheme: str = Form("[]"),
    total_marks: int = Form(0),
    student_id: str = Form(""),
    question_paper_id: str = Form("")
):
    """
    Upload a student's answer sheet and grade it against the question paper.
    Uses contextual AI grading with the question paper text and mark scheme.
    """
    try:
        content = await file.read()
        mime_type = file.content_type or "image/jpeg"

        # Save file
        filename = f"as_{uuid.uuid4()}{_get_extension(file.filename)}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(content)

        # Grade with context
        grading_result = await grading_service.grade_with_context(
            answer_image_bytes=content,
            mime_type=mime_type,
            question_paper_text=question_paper_text,
            mark_scheme=mark_scheme,
            total_marks=total_marks
        )

        if "error" in grading_result:
            raise HTTPException(status_code=500, detail=grading_result["error"])

        return {
            "file_url": f"/static/uploads/{filename}",
            "student_id": student_id,
            "question_paper_id": question_paper_id,
            "grading": grading_result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Legacy upload endpoint for backward compatibility
@router.post("/upload")
async def upload_exam(file: UploadFile = File(...)):
    """Legacy endpoint — grades a single paper without question paper context."""
    try:
        content = await file.read()
        mime_type = file.content_type or "image/jpeg"

        result = await grading_service.grade_image(content, mime_type)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "student_name": "Unknown",
            "score": _extract_score(result.get("grade", "N/A")),
            "status": "Graded",
            "summary": result.get("remarks", ""),
            "details": json.dumps(result)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _get_extension(filename: str) -> str:
    """Get file extension from filename."""
    if not filename:
        return ".jpg"
    _, ext = os.path.splitext(filename)
    return ext or ".jpg"


def _extract_score(grade_str: str) -> int:
    """Try to extract a numeric score from grade string."""
    try:
        if "/" in grade_str:
            num, denom = grade_str.split("/")
            return int(float(num.strip()) / float(denom.strip()) * 100)
        grade_map = {"A+": 95, "A": 90, "B+": 85, "B": 80, "C+": 75, "C": 70, "D": 60, "F": 30}
        return grade_map.get(grade_str.strip(), 50)
    except Exception:
        return 50
