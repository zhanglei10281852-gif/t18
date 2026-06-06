from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import User, Plot
from schemas import PlotCreate, PlotUpdate, PlotResponse
from auth import get_current_user, require_role
from config import settings

router = APIRouter(prefix="/api/plots", tags=["地块管理"])


def filter_plots_by_user(query, user: User):
    if user.role == "admin":
        return query
    elif user.role == "manager":
        return query.filter(Plot.region == user.region)
    elif user.role == "farmer":
        return query.filter(Plot.farmer_id == user.id)
    return query.filter(False)


@router.get("", response_model=List[PlotResponse])
def list_plots(
    crop_type: Optional[str] = None,
    region: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Plot)
    query = filter_plots_by_user(query, current_user)
    if crop_type:
        query = query.filter(Plot.crop_type == crop_type)
    if region:
        query = query.filter(Plot.region == region)
    plots = query.offset(skip).limit(limit).all()
    return plots


@router.get("/{plot_id}", response_model=PlotResponse)
def get_plot(
    plot_id: int,
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
    return plot


@router.post("", response_model=PlotResponse)
def create_plot(
    plot: PlotCreate,
    current_user: User = Depends(require_role(["admin", "manager"])),
    db: Session = Depends(get_db)
):
    db_plot = db.query(Plot).filter(Plot.plot_code == plot.plot_code).first()
    if db_plot:
        raise HTTPException(status_code=400, detail="Plot code already exists")
    if plot.annual_quota == 0 and plot.area_mu > 0:
        annual_quota = plot.area_mu * settings.BASE_QUOTA_PER_MU
    else:
        annual_quota = plot.annual_quota
    db_plot = Plot(
        plot_code=plot.plot_code,
        area_mu=plot.area_mu,
        crop_type=plot.crop_type,
        soil_type=plot.soil_type,
        irrigation_method=plot.irrigation_method,
        water_source=plot.water_source,
        region=plot.region,
        growth_stage=plot.growth_stage,
        farmer_id=plot.farmer_id,
        annual_quota=annual_quota,
    )
    db.add(db_plot)
    db.commit()
    db.refresh(db_plot)
    return db_plot


@router.put("/{plot_id}", response_model=PlotResponse)
def update_plot(
    plot_id: int,
    plot_update: PlotUpdate,
    current_user: User = Depends(require_role(["admin", "manager"])),
    db: Session = Depends(get_db)
):
    plot = db.query(Plot).filter(Plot.id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    update_data = plot_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plot, key, value)
    db.commit()
    db.refresh(plot)
    return plot


@router.delete("/{plot_id}")
def delete_plot(
    plot_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    plot = db.query(Plot).filter(Plot.id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    db.delete(plot)
    db.commit()
    return {"message": "Plot deleted successfully"}
