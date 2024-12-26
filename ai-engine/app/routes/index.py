from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def index():
    return {
        "message": "Welcome to Zorat AI Engine",
        "status": "active",
        "version": "1.0.0"
    } 