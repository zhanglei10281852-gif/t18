from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50))
    role = Column(String(20), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    region = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    plots = relationship("Plot", back_populates="farmer")


class Plot(Base):
    __tablename__ = "plots"

    id = Column(Integer, primary_key=True, index=True)
    plot_code = Column(String(50), unique=True, index=True, nullable=False)
    area_mu = Column(Float, nullable=False)
    crop_type = Column(String(20), nullable=False)
    soil_type = Column(String(20), nullable=False)
    irrigation_method = Column(String(20), nullable=False)
    water_source = Column(String(20), nullable=False)
    region = Column(String(100))
    growth_stage = Column(String(20), default="initial")
    farmer_id = Column(Integer, ForeignKey("users.id"))
    annual_quota = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="plots")
    irrigation_records = relationship("IrrigationRecord", back_populates="plot")
    water_usage = relationship("WaterUsage", back_populates="plot")


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    temperature_avg = Column(Float, nullable=False)
    temperature_max = Column(Float, nullable=False)
    temperature_min = Column(Float, nullable=False)
    rainfall = Column(Float, default=0)
    wind_speed = Column(Float, default=0)
    sunshine_hours = Column(Float, default=0)
    relative_humidity = Column(Float, default=0)
    region = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class IrrigationRecord(Base):
    __tablename__ = "irrigation_records"

    id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(Integer, ForeignKey("plots.id"), nullable=False)
    irrigation_date = Column(Date, nullable=False)
    water_amount_m3 = Column(Float, nullable=False)
    duration_hours = Column(Float, default=0)
    irrigation_method = Column(String(20))
    operator = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    plot = relationship("Plot", back_populates="irrigation_records")


class WaterUsage(Base):
    __tablename__ = "water_usage"

    id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(Integer, ForeignKey("plots.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    planned_usage = Column(Float, default=0)
    actual_usage = Column(Float, default=0)
    water_fee = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    plot = relationship("Plot", back_populates="water_usage")


class IrrigationSuggestion(Base):
    __tablename__ = "irrigation_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(Integer, ForeignKey("plots.id"), nullable=False)
    suggestion_date = Column(Date, nullable=False)
    et0 = Column(Float, default=0)
    etc = Column(Float, default=0)
    effective_rainfall = Column(Float, default=0)
    irrigation_need = Column(Float, default=0)
    suggested_water_mu = Column(Float, default=0)
    suggested_water_total = Column(Float, default=0)
    suggested_duration = Column(Float, default=0)
    urgency_level = Column(String(20), default="normal")
    created_at = Column(DateTime, default=datetime.utcnow)
