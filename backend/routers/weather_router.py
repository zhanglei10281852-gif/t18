from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_db
from models import User, WeatherData
from schemas import WeatherDataCreate, WeatherDataResponse
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/weather", tags=["气象数据"])


@router.get("", response_model=List[WeatherDataResponse])
def list_weather_data(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    region: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(WeatherData)
    if start_date:
        query = query.filter(WeatherData.date >= start_date)
    if end_date:
        query = query.filter(WeatherData.date <= end_date)
    if region:
        query = query.filter(WeatherData.region == region)
    elif current_user.role == "manager" and current_user.region:
        query = query.filter(WeatherData.region == current_user.region)
    weather_data = query.order_by(WeatherData.date.desc()).offset(skip).limit(limit).all()
    return weather_data


@router.get("/{weather_id}", response_model=WeatherDataResponse)
def get_weather_data(
    weather_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    weather = db.query(WeatherData).filter(WeatherData.id == weather_id).first()
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    return weather


@router.post("", response_model=WeatherDataResponse)
def create_weather_data(
    weather: WeatherDataCreate,
    current_user: User = Depends(require_role(["admin", "manager"])),
    db: Session = Depends(get_db)
):
    db_weather = db.query(WeatherData).filter(
        WeatherData.date == weather.date,
        WeatherData.region == weather.region
    ).first()
    if db_weather:
        raise HTTPException(status_code=400, detail="Weather data for this date already exists")
    db_weather = WeatherData(**weather.model_dump())
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather


@router.post("/batch")
def batch_create_weather_data(
    weather_list: List[WeatherDataCreate],
    current_user: User = Depends(require_role(["admin", "manager"])),
    db: Session = Depends(get_db)
):
    count = 0
    for weather in weather_list:
        db_weather = db.query(WeatherData).filter(
            WeatherData.date == weather.date,
            WeatherData.region == weather.region
        ).first()
        if not db_weather:
            db_weather = WeatherData(**weather.model_dump())
            db.add(db_weather)
            count += 1
    db.commit()
    return {"created": count}
