from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {
        "system": "BRASA Meat Intelligence™",
        "status": "ONLINE",
        "engine": "Production"
    }
