from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_db
from models import User, Plot, WaterUsage
from schemas import WaterUsageResponse, MonthlyStats, SoilWaterBalanceItem
from auth import get_current_user, require_role
from irrigation_engine import calculate_water_fee

router = APIRouter(prefix="/api/water", tags=["用水管理"])


@router.get("/usage/monthly", response_model=List[MonthlyStats])
def get_monthly_usage(
    plot_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not year:
        year = date.today().year

    query = db.query(WaterUsage)
    if plot_id:
        query = query.filter(WaterUsage.plot_id == plot_id)
    if year:
        query = query.filter(WaterUsage.year == year)
    if month:
        query = query.filter(WaterUsage.month == month)

    usages = query.all()

    results = []
    for usage in usages:
        plot = db.query(Plot).filter(Plot.id == usage.plot_id).first()
        if not plot:
            continue
        if current_user.role == "farmer" and plot.farmer_id != current_user.id:
            continue
        if current_user.role == "manager" and plot.region != current_user.region:
            continue

        planned = usage.planned_usage
        actual = usage.actual_usage
        saving_rate = ((planned - actual) / planned * 100) if planned > 0 else 0

        fee = calculate_water_fee(actual, plot.annual_quota / 12 if plot.annual_quota else 0)

        results.append(MonthlyStats(
            plot_id=usage.plot_id,
            plot_code=plot.plot_code,
            year=usage.year,
            month=usage.month,
            planned_usage=round(planned, 2),
            actual_usage=round(actual, 2),
            water_saving_rate=round(saving_rate, 2),
            water_fee=round(fee, 2)
        ))

    return results


@router.get("/quota/{plot_id}")
def get_quota_status(
    plot_id: int,
    year: Optional[int] = None,
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

    if not year:
        year = date.today().year

    annual_quota = plot.annual_quota

    monthly_usages = db.query(WaterUsage).filter(
        WaterUsage.plot_id == plot_id,
        WaterUsage.year == year
    ).all()

    total_used = sum(u.actual_usage for u in monthly_usages)
    remaining = max(0, annual_quota - total_used)
    usage_percent = (total_used / annual_quota * 100) if annual_quota > 0 else 0

    return {
        "plot_id": plot_id,
        "plot_code": plot.plot_code,
        "year": year,
        "annual_quota": round(annual_quota, 2),
        "total_used": round(total_used, 2),
        "remaining": round(remaining, 2),
        "usage_percent": round(usage_percent, 2),
    }


@router.get("/stats/saving-rate-trend")
def get_saving_rate_trend(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()
    result = []

    for i in range(months - 1, -1, -1):
        month_date = today.replace(day=1)
        if i > 0:
            month_date = _add_months(today.replace(day=1), -i)

        year = month_date.year
        month = month_date.month

        query = db.query(WaterUsage).filter(
            WaterUsage.year == year,
            WaterUsage.month == month
        )

        usages = query.all()
        filtered_usages = []

        for u in usages:
            plot = db.query(Plot).filter(Plot.id == u.plot_id).first()
            if not plot:
                continue
            if current_user.role == "farmer" and plot.farmer_id != current_user.id:
                continue
            if current_user.role == "manager" and plot.region != current_user.region:
                continue
            filtered_usages.append(u)

        total_planned = sum(u.planned_usage for u in filtered_usages)
        total_actual = sum(u.actual_usage for u in filtered_usages)
        saving_rate = ((total_planned - total_actual) / total_planned * 100) if total_planned > 0 else 0

        result.append({
            "year": year,
            "month": month,
            "label": f"{year}-{month:02d}",
            "planned_usage": round(total_planned, 2),
            "actual_usage": round(total_actual, 2),
            "saving_rate": round(saving_rate, 2),
        })

    return result


@router.get("/stats/water-bills")
def get_water_bills(
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not year:
        year = date.today().year

    plots = db.query(Plot).all()
    bills = []

    for plot in plots:
        if current_user.role == "farmer" and plot.farmer_id != current_user.id:
            continue
        if current_user.role == "manager" and plot.region != current_user.region:
            continue

        monthly_usages = db.query(WaterUsage).filter(
            WaterUsage.plot_id == plot.id,
            WaterUsage.year == year
        ).all()

        total_usage = sum(u.actual_usage for u in monthly_usages)
        total_fee = calculate_water_fee(total_usage, plot.annual_quota)

        bills.append({
            "plot_id": plot.id,
            "plot_code": plot.plot_code,
            "crop_type": plot.crop_type,
            "annual_quota": round(plot.annual_quota, 2),
            "total_usage": round(total_usage, 2),
            "total_fee": round(total_fee, 2),
        })

    return bills


def _add_months(d, months):
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
    return date(year, month, day)
