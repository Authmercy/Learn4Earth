from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.carbon import CarbonFootprint
from app.models.compensation import EcoCompensation
from app.models.session import LearningSession
from app.config import settings


# Regional carbon factors (kg CO2 per kWh)
REGION_CARBON_FACTORS = {
    "europe-west": 0.276,
    "europe-north": 0.030,
    "us-east": 0.420,
    "us-west": 0.180,
    "asia-east": 0.555,
    "africa-west": 0.500,
    "default": 0.475,
}


def calculate_session_carbon(duration_minutes: float, server_region: str = "europe-west") -> dict:
    """
    Calculate the carbon footprint for a learning session.

    Formula:
    - Energy (kWh) = duration_hours * ENERGY_PER_HOUR_KWH
    - Carbon (kg) = energy_kwh * carbon_factor_for_region
    """
    duration_hours = duration_minutes / 60.0
    energy_kwh = duration_hours * settings.ENERGY_PER_HOUR_KWH
    carbon_factor = REGION_CARBON_FACTORS.get(server_region, REGION_CARBON_FACTORS["default"])
    carbon_kg = energy_kwh * carbon_factor

    return {
        "duration_minutes": duration_minutes,
        "energy_kwh": round(energy_kwh, 6),
        "carbon_kg": round(carbon_kg, 6),
        "server_region": server_region,
        "carbon_factor": carbon_factor,
    }


def create_carbon_record(db: Session, user_id, session_id, duration_minutes: float, server_region: str = "europe-west") -> CarbonFootprint:
    """Create a carbon footprint record for a session."""
    carbon_data = calculate_session_carbon(duration_minutes, server_region)

    record = CarbonFootprint(
        user_id=user_id,
        session_id=session_id,
        **carbon_data,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_user_carbon_summary(db: Session, user_id) -> dict:
    """Get aggregated carbon data for a user."""
    result = db.query(
        func.count(CarbonFootprint.id).label("total_sessions"),
        func.coalesce(func.sum(CarbonFootprint.duration_minutes), 0).label("total_duration"),
        func.coalesce(func.sum(CarbonFootprint.energy_kwh), 0).label("total_energy"),
        func.coalesce(func.sum(CarbonFootprint.carbon_kg), 0).label("total_carbon"),
    ).filter(CarbonFootprint.user_id == user_id).first()

    comp_result = db.query(
        func.coalesce(func.sum(EcoCompensation.trees_planted), 0).label("total_trees"),
        func.coalesce(func.sum(EcoCompensation.co2_compensated_kg), 0).label("total_compensated"),
    ).filter(EcoCompensation.user_id == user_id).first()

    total_carbon = float(result.total_carbon)
    total_compensated = float(comp_result.total_compensated)
    remaining = total_carbon - total_compensated
    next_compensation = max(0, settings.CO2_THRESHOLD_KG - (remaining % settings.CO2_THRESHOLD_KG)) if remaining > 0 else settings.CO2_THRESHOLD_KG

    return {
        "total_sessions": result.total_sessions,
        "total_duration_minutes": float(result.total_duration),
        "total_energy_kwh": round(float(result.total_energy), 4),
        "total_carbon_kg": round(total_carbon, 4),
        "total_trees_planted": int(comp_result.total_trees),
        "total_co2_compensated_kg": round(total_compensated, 4),
        "compensation_threshold_kg": settings.CO2_THRESHOLD_KG,
        "next_compensation_in_kg": round(next_compensation, 4),
    }


def check_and_trigger_compensation(db: Session, user_id) -> EcoCompensation | None:
    """
    Check if user has reached carbon threshold and trigger tree planting compensation.
    """
    summary = get_user_carbon_summary(db, user_id)
    uncompensated = summary["total_carbon_kg"] - summary["total_co2_compensated_kg"]

    if uncompensated >= settings.CO2_THRESHOLD_KG:
        compensable_kg = (uncompensated // settings.CO2_THRESHOLD_KG) * settings.CO2_THRESHOLD_KG
        trees = int(compensable_kg / 1000 * settings.TREES_PER_TON_CO2) or 1

        compensation = EcoCompensation(
            user_id=user_id,
            trees_planted=trees,
            co2_compensated_kg=compensable_kg,
            partner_name="EcoTree Partner",
            status="confirmed",
            notes=f"Compensation automatique : {compensable_kg:.2f} kg CO2 -> {trees} arbre(s) plante(s)",
        )
        db.add(compensation)
        db.commit()
        db.refresh(compensation)
        return compensation

    return None
