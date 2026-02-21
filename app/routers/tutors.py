from fastapi import APIRouter

router = APIRouter(prefix="/tutors", tags=["tutors"])

# Available subjects
SUBJECTS = [
    "Python", "Machine Learning", "Deep Learning", "Natural Language Processing",
    "Computer Vision", "Data Science", "Mathematics", "Statistics",
    "TensorFlow", "PyTorch", "LLM Engineering", "Prompt Engineering",
    "System Design", "Data Structures & Algorithms", "Web Development",
    "Cloud Computing", "MLOps", "Reinforcement Learning",
]


@router.get("/subjects")
async def get_subjects():
    """Return list of available subjects that tutors can teach."""
    return {"subjects": SUBJECTS}


@router.get("/browse")
async def browse_tutors(subject: str = None, page: int = 1, limit: int = 10):
    """Browse approved tutors. This endpoint is intended to be backed by the
    frontend Prisma DB — it provides a backend reference for future integration.
    For now, it returns a placeholder structure.
    """
    # In production, this would query the database for approved tutors
    return {
        "tutors": [],
        "total": 0,
        "page": page,
        "limit": limit,
        "message": "Tutor browsing powered by frontend Prisma DB. Use /api/tutors routes in Next.js.",
    }
