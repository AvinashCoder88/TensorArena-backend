from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.services.grading_service import GradingService
from app.utils.docx_generator import DocxGenerator
import shutil
import os
import uuid

router = APIRouter()
grading_service = GradingService()
docx_generator = DocxGenerator()

# Ensure reports directory exists
REPORTS_DIR = "app/static/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

@router.post("/classroom/grade_paper")
async def grade_paper(file: UploadFile = File(...), student_name: str = "Student"):
    try:
        # Read file
        content = await file.read()
        
        # Grade with Gemini
        grading_result = await grading_service.grade_image(content, file.content_type)
        
        if "error" in grading_result:
            raise HTTPException(status_code=500, detail=grading_result["error"])
            
        # Generate DOCX
        docx_stream = docx_generator.generate_report(grading_result, student_name)
        
        # Save DOCX to static folder for download
        report_filename = f"report_{uuid.uuid4()}.docx"
        report_path = os.path.join(REPORTS_DIR, report_filename)
        
        with open(report_path, "wb") as f:
            f.write(docx_stream.getvalue())
            
        return {
            "grade": grading_result.get("grade"),
            "remarks": grading_result.get("remarks"),
            "details": grading_result,
            "report_url": f"/static/reports/{report_filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/static/reports/{filename}")
async def get_report(filename: str):
    file_path = os.path.join(REPORTS_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Report not found")
