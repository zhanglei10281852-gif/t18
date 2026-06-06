from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta, datetime
from database import get_db
from models import User, Plot, WeatherData, IrrigationRecord, IrrigationSuggestion
from schemas import IrrigationRecordCreate, IrrigationRecordResponse, IrrigationSuggestionResponse
from auth import get_current_user, require_role
from irrigation_engine import (
    calculate_et0, calculate_etc, get_ra_by_month,
    get_effective_rainfall, get_flow_rate
)

router = APIRouter(prefix="/api/irrigation", tags=["灌溉管理"])


def filter_plots_by_user(query, user: User, plot_model=Plot):
    if user.role == "admin":
        return query
    elif user.role == "manager":
        return query.filter(plot_model.region == user.region)
    elif user.role == "farmer":
        return query.filter(plot_model.farmer_id == user.id)
    return query.filter(False)


@router.get("/suggestions/today", response_model=List[IrrigationSuggestionResponse])
def get_today_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()
    suggestions = db.query(IrrigationSuggestion).filter(
        IrrigationSuggestion.suggestion_date == today
    ).all()

    if not suggestions:
        generate_suggestions_for_date(db, today)
        suggestions = db.query(IrrigationSuggestion).filter(
            IrrigationSuggestion.suggestion_date == today
        ).all()

    filtered = []
    for s in suggestions:
        plot = db.query(Plot).filter(Plot.id == s.plot_id).first()
        if not plot:
            continue
        if current_user.role == "admin":
            s.plot = plot
            filtered.append(s)
        elif current_user.role == "manager" and plot.region == current_user.region:
            s.plot = plot
            filtered.append(s)
        elif current_user.role == "farmer" and plot.farmer_id == current_user.id:
            s.plot = plot
            filtered.append(s)
    return filtered


@router.get("/suggestions/{plot_id}", response_model=List[IrrigationSuggestionResponse])
def get_plot_suggestions(
    plot_id: int,
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plot = db.query(Plot).filter(Plot.id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    if current_user.role == "farmer" and plot.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user.role == "manager" and plot.region != current_user.region:
        raise HTTPException(status_code=403, detail="Access denied")

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    suggestions = db.query(IrrigationSuggestion).filter(
        IrrigationSuggestion.plot_id == plot_id,
        IrrigationSuggestion.suggestion_date >= start_date,
        IrrigationSuggestion.suggestion_date <= end_date
    ).order_by(IrrigationSuggestion.suggestion_date.desc()).all()

    return suggestions


def generate_suggestions_for_date(db: Session, target_date: date):
    plots = db.query(Plot).all()
    weather = db.query(WeatherData).filter(WeatherData.date == target_date).first()

    if not weather:
        weather = db.query(WeatherData).order_by(WeatherData.date.desc()).first()

    if not weather:
        return

    ra = get_ra_by_month(target_date.month)

    for plot in plots:
        et0 = calculate_et0(
            weather.temperature_avg,
            weather.temperature_max,
            weather.temperature_min,
            ra
        )
        etc = calculate_etc(et0, plot.crop_type, plot.growth_stage)
        effective_rain = get_effective_rainfall(weather.rainfall)
        irrigation_need = etc - effective_rain

        if irrigation_need > 0:
            suggested_water_mu = irrigation_need
            suggested_water_total = irrigation_need * plot.area_mu
            flow_rate = get_flow_rate(plot.irrigation_method)
            duration = suggested_water_total / flow_rate if flow_rate > 0 else 0

            if irrigation_need > 5:
                urgency = "urgent"
            elif irrigation_need > 2:
                urgency = "suggested"
            else:
                urgency = "normal"
        else:
            suggested_water_mu = 0
            suggested_water_total = 0
            duration = 0
            urgency = "no_need"

        existing = db.query(IrrigationSuggestion).filter(
            IrrigationSuggestion.plot_id == plot.id,
            IrrigationSuggestion.suggestion_date == target_date
        ).first()

        if existing:
            existing.et0 = et0
            existing.etc = etc
            existing.effective_rainfall = effective_rain
            existing.irrigation_need = max(0, irrigation_need)
            existing.suggested_water_mu = suggested_water_mu
            existing.suggested_water_total = suggested_water_total
            existing.suggested_duration = duration
            existing.urgency_level = urgency
        else:
            suggestion = IrrigationSuggestion(
                plot_id=plot.id,
                suggestion_date=target_date,
                et0=et0,
                etc=etc,
                effective_rainfall=effective_rain,
                irrigation_need=max(0, irrigation_need),
                suggested_water_mu=suggested_water_mu,
                suggested_water_total=suggested_water_total,
                suggested_duration=duration,
                urgency_level=urgency,
            )
            db.add(suggestion)

    db.commit()


@router.get("/records", response_model=List[IrrigationRecordResponse])
def list_irrigation_records(
    plot_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(IrrigationRecord)
    if plot_id:
        query = query.filter(IrrigationRecord.plot_id == plot_id)
    if start_date:
        query = query.filter(IrrigationRecord.irrigation_date >= start_date)
    if end_date:
        query = query.filter(IrrigationRecord.irrigation_date <= end_date)

    records = query.order_by(IrrigationRecord.irrigation_date.desc()).offset(skip).limit(limit).all()

    if current_user.role in ["manager", "farmer"]:
        filtered = []
        for r in records:
            plot = db.query(Plot).filter(Plot.id == r.plot_id).first()
            if not plot:
                continue
            if current_user.role == "farmer" and plot.farmer_id != current_user.id:
                continue
            if current_user.role == "manager" and plot.region != current_user.region:
                continue
            filtered.append(r)
        return filtered

    return records


@router.post("/records", response_model=IrrigationRecordResponse)
def create_irrigation_record(
    record: IrrigationRecordCreate,
    current_user: User = Depends(require_role(["admin", "manager"])),
    db: Session = Depends(get_db)
):
    plot = db.query(Plot).filter(Plot.id == record.plot_id).first()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    db_record = IrrigationRecord(**record.model_dump())
    db.add(db_record)
    db.flush()

    from models import WaterUsage
    year = record.irrigation_date.year
    month = record.irrigation_date.month

    water_usage = db.query(WaterUsage).filter(
        WaterUsage.plot_id == record.plot_id,
        WaterUsage.year == year,
        WaterUsage.month == month
    ).first()

    if water_usage:
        water_usage.actual_usage += record.water_amount_m3
    else:
        monthly_quota = plot.annual_quota / 12 if plot.annual_quota else 0
        water_usage = WaterUsage(
            plot_id=record.plot_id,
            year=year,
            month=month,
            planned_usage=monthly_quota,
            actual_usage=record.water_amount_m3,
            water_fee=0
        )
        db.add(water_usage)

    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/records/{record_id}")
def delete_irrigation_record(
    record_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    record = db.query(IrrigationRecord).filter(IrrigationRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Record deleted successfully"}
