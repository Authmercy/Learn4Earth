from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class CarbonFootprintResponse(BaseModel):
    id: UUID
    user_id: UUID
    session_id: UUID
    duration_minutes: float
    energy_kwh: float
    carbon_kg: float
    server_region: str
    carbon_factor: float
    created_at: datetime

    class Config:
        from_attributes = True


class CarbonSummary(BaseModel):
    total_sessions: int
    total_duration_minutes: float
    total_energy_kwh: float
    total_carbon_kg: float
    total_trees_planted: int
    total_co2_compensated_kg: float
    compensation_threshold_kg: float
    next_compensation_in_kg: float


class CompensationResponse(BaseModel):
    id: UUID
    user_id: UUID
    trees_planted: int
    co2_compensated_kg: float
    partner_name: str
    partner_reference: Optional[str]
    status: str
    notes: Optional[str]
    triggered_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardData(BaseModel):
    # Pedagogical
    total_learning_paths: int
    active_learning_paths: int
    completed_learning_paths: int
    total_sessions: int
    completed_sessions: int
    average_score: Optional[float]
    total_learning_hours: float

    # Gamification
    total_xp: int
    level: str
    current_streak: int
    longest_streak: int
    achievements_unlocked: int

    # Carbon
    carbon_summary: CarbonSummary

    # Compensations
    compensations: List[CompensationResponse]
