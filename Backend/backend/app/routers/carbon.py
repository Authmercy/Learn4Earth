from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.carbon import CarbonFootprint
from app.models.compensation import EcoCompensation
from app.schemas.carbon import CarbonFootprintResponse, CarbonSummary, CompensationResponse
from app.services.carbon_service import get_user_carbon_summary
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/carbon", tags=["Empreinte Carbone & Compensation"])


@router.get("/summary", response_model=CarbonSummary)
def get_carbon_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtenir le resume de l'empreinte carbone de l'utilisateur."""
    return get_user_carbon_summary(db, current_user.id)


@router.get("/footprints", response_model=List[CarbonFootprintResponse])
def get_carbon_footprints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lister toutes les empreintes carbone par session."""
    return (
        db.query(CarbonFootprint)
        .filter(CarbonFootprint.user_id == current_user.id)
        .order_by(CarbonFootprint.created_at.desc())
        .all()
    )


@router.get("/compensations", response_model=List[CompensationResponse])
def get_compensations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lister les actions de compensation ecologique."""
    return (
        db.query(EcoCompensation)
        .filter(EcoCompensation.user_id == current_user.id)
        .order_by(EcoCompensation.created_at.desc())
        .all()
    )
