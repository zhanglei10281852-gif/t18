import logging
from datetime import date, timedelta, datetime
import random
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import User, Plot, WeatherData, IrrigationRecord, WaterUsage, IrrigationSuggestion
from auth import hash_password
from irrigation_engine import calculate_et0, calculate_etc, get_ra_by_month, get_effective_rainfall, get_flow_rate, calculate_water_fee
from config import settings

logger = logging.getLogger(__name__)


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        steps = [
            ("users", _init_users),
            ("plots", _init_plots),
            ("weather_data", _init_weather_data),
            ("irrigation_records", _init_irrigation_records),
            ("water_usage", _init_water_usage),
            ("irrigation_suggestions", _generate_irrigation_suggestions),
        ]
        for name, func in steps:
            try:
                func(db)
                logger.info(f"Init step '{name}' completed")
            except Exception as e:
                logger.error(f"Init step '{name}' failed: {e}")
                db.rollback()
        logger.info("Database initialization completed!")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        db.rollback()
    finally:
        db.close()


def _init_users(db: Session):
    users = [
        {"username": "admin", "password": "admin123", "real_name": "系统管理员", "role": "admin", "phone": "13800138000", "email": "admin@agri.com", "region": None},
        {"username": "manager1", "password": "mgr123", "real_name": "东灌区管理员", "role": "manager", "phone": "13800138001", "email": "mgr1@agri.com", "region": "东区"},
        {"username": "manager2", "password": "mgr123", "real_name": "西灌区管理员", "role": "manager", "phone": "13800138002", "email": "mgr2@agri.com", "region": "西区"},
        {"username": "farmer1", "password": "farm123", "real_name": "张农户", "role": "farmer", "phone": "13900139001", "email": "farmer1@agri.com", "region": "东区"},
        {"username": "farmer2", "password": "farm123", "real_name": "李农户", "role": "farmer", "phone": "13900139002", "email": "farmer2@agri.com", "region": "东区"},
        {"username": "farmer3", "password": "farm123", "real_name": "王农户", "role": "farmer", "phone": "13900139003", "email": "farmer3@agri.com", "region": "西区"},
    ]

    for u in users:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if not existing:
            user = User(
                username=u["username"],
                password_hash=hash_password(u["password"]),
                real_name=u["real_name"],
                role=u["role"],
                phone=u["phone"],
                email=u["email"],
                region=u["region"],
            )
            db.add(user)
            print(f"Created user: {u['username']}")
    db.commit()


def _init_plots(db: Session):
    farmer1 = db.query(User).filter(User.username == "farmer1").first()
    farmer2 = db.query(User).filter(User.username == "farmer2").first()
    farmer3 = db.query(User).filter(User.username == "farmer3").first()

    plots = [
        {"plot_code": "P001", "area_mu": 50, "crop_type": "rice", "soil_type": "loam", "irrigation_method": "flood", "water_source": "reservoir", "region": "东区", "growth_stage": "mid", "farmer_id": farmer1.id if farmer1 else None},
        {"plot_code": "P002", "area_mu": 30, "crop_type": "wheat", "soil_type": "sandy", "irrigation_method": "sprinkler", "water_source": "river", "region": "东区", "growth_stage": "development", "farmer_id": farmer1.id if farmer1 else None},
        {"plot_code": "P003", "area_mu": 45, "crop_type": "corn", "soil_type": "loam", "irrigation_method": "drip", "water_source": "groundwater", "region": "东区", "growth_stage": "initial", "farmer_id": farmer2.id if farmer2 else None},
        {"plot_code": "P004", "area_mu": 25, "crop_type": "cotton", "soil_type": "clay", "irrigation_method": "drip", "water_source": "groundwater", "region": "东区", "growth_stage": "late", "farmer_id": farmer2.id if farmer2 else None},
        {"plot_code": "P005", "area_mu": 60, "crop_type": "rice", "soil_type": "loam", "irrigation_method": "flood", "water_source": "reservoir", "region": "西区", "growth_stage": "mid", "farmer_id": farmer3.id if farmer3 else None},
        {"plot_code": "P006", "area_mu": 35, "crop_type": "wheat", "soil_type": "sandy", "irrigation_method": "sprinkler", "water_source": "river", "region": "西区", "growth_stage": "development", "farmer_id": farmer3.id if farmer3 else None},
        {"plot_code": "P007", "area_mu": 40, "crop_type": "corn", "soil_type": "loam", "irrigation_method": "sprinkler", "water_source": "river", "region": "西区", "growth_stage": "initial", "farmer_id": farmer3.id if farmer3 else None},
        {"plot_code": "P008", "area_mu": 20, "crop_type": "cotton", "soil_type": "clay", "irrigation_method": "drip", "water_source": "groundwater", "region": "西区", "growth_stage": "mid", "farmer_id": farmer3.id if farmer3 else None},
    ]

    for p in plots:
        existing = db.query(Plot).filter(Plot.plot_code == p["plot_code"]).first()
        if not existing:
            annual_quota = p["area_mu"] * settings.BASE_QUOTA_PER_MU
            plot = Plot(**p, annual_quota=annual_quota)
            db.add(plot)
            print(f"Created plot: {p['plot_code']}")
    db.commit()


def _init_weather_data(db: Session):
    today = date.today()
    regions = ["东区", "西区"]

    for region in regions:
        for i in range(30):
            d = today - timedelta(days=i)
            existing = db.query(WeatherData).filter(
                WeatherData.date == d,
                WeatherData.region == region
            ).first()
            if existing:
                continue

            month = d.month
            base_temp = {
                1: 0, 2: 5, 3: 12, 4: 18, 5: 24, 6: 28,
                7: 30, 8: 29, 9: 24, 10: 18, 11: 10, 12: 3
            }.get(month, 15)

            temp_max = base_temp + random.uniform(2, 8)
            temp_min = base_temp - random.uniform(2, 6)
            temp_avg = (temp_max + temp_min) / 2

            rainfall = random.uniform(0, 25) if random.random() < 0.4 else 0
            wind_speed = random.uniform(1, 6)
            sunshine = random.uniform(3, 11)
            humidity = random.uniform(40, 85)

            weather = WeatherData(
                date=d,
                temperature_avg=round(temp_avg, 1),
                temperature_max=round(temp_max, 1),
                temperature_min=round(temp_min, 1),
                rainfall=round(rainfall, 1),
                wind_speed=round(wind_speed, 1),
                sunshine_hours=round(sunshine, 1),
                relative_humidity=round(humidity, 1),
                region=region,
            )
            db.add(weather)
    db.commit()
    print("Created 30 days of weather data")


def _init_irrigation_records(db: Session):
    plots = db.query(Plot).all()
    today = date.today()

    for plot in plots:
        existing_count = db.query(IrrigationRecord).filter(
            IrrigationRecord.plot_id == plot.id
        ).count()
        if existing_count > 0:
            continue

        num_records = random.randint(3, 8)
        for i in range(num_records):
            days_ago = random.randint(1, 30)
            d = today - timedelta(days=days_ago)

            flow_rate = get_flow_rate(plot.irrigation_method)
            duration = random.uniform(1, 6)
            water_amount = flow_rate * duration * plot.area_mu * 0.1

            record = IrrigationRecord(
                plot_id=plot.id,
                irrigation_date=d,
                water_amount_m3=round(water_amount, 2),
                duration_hours=round(duration, 1),
                irrigation_method=plot.irrigation_method,
                operator="system",
                notes=f"自动生成的历史灌溉记录-{i+1}",
            )
            db.add(record)
    db.commit()
    print("Created irrigation records")


def _init_water_usage(db: Session):
    plots = db.query(Plot).all()
    today = date.today()
    current_year = today.year

    for plot in plots:
        for month in range(1, today.month + 1):
            existing = db.query(WaterUsage).filter(
                WaterUsage.plot_id == plot.id,
                WaterUsage.year == current_year,
                WaterUsage.month == month
            ).first()
            if existing:
                continue

            monthly_quota = plot.annual_quota / 12
            records = db.query(IrrigationRecord).filter(
                IrrigationRecord.plot_id == plot.id
            ).all()

            month_usage = 0
            for r in records:
                if r.irrigation_date.year == current_year and r.irrigation_date.month == month:
                    month_usage += r.water_amount_m3

            if month_usage == 0:
                month_usage = monthly_quota * random.uniform(0.6, 1.1)

            fee = calculate_water_fee(month_usage, monthly_quota)

            usage = WaterUsage(
                plot_id=plot.id,
                year=current_year,
                month=month,
                planned_usage=round(monthly_quota, 2),
                actual_usage=round(month_usage, 2),
                water_fee=round(fee, 2),
            )
            db.add(usage)
    db.commit()
    print("Created water usage records")


def _generate_irrigation_suggestions(db: Session):
    plots = db.query(Plot).all()
    today = date.today()
    yesterday = today - timedelta(days=1)

    for target_date in [yesterday, today]:
        for region in ["东区", "西区"]:
            weather = db.query(WeatherData).filter(
                WeatherData.date == target_date,
                WeatherData.region == region
            ).first()
            if not weather:
                continue

            ra = get_ra_by_month(target_date.month)

            region_plots = [p for p in plots if p.region == region]

            for plot in region_plots:
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

                if not existing:
                    suggestion = IrrigationSuggestion(
                        plot_id=plot.id,
                        suggestion_date=target_date,
                        et0=round(et0, 3),
                        etc=round(etc, 3),
                        effective_rainfall=round(effective_rain, 2),
                        irrigation_need=round(max(0, irrigation_need), 3),
                        suggested_water_mu=round(suggested_water_mu, 2),
                        suggested_water_total=round(suggested_water_total, 2),
                        suggested_duration=round(duration, 2),
                        urgency_level=urgency,
                    )
                    db.add(suggestion)
    db.commit()
    print("Generated irrigation suggestions")


if __name__ == "__main__":
    init_db()
