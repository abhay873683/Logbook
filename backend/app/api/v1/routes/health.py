from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()

@router.get("/health")

def health_check(db: Session = Depends(get_db)):

    return {
        "status": "success",
        "database": "connected"
    }