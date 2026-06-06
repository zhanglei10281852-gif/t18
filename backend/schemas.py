from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str
    real_name: Optional[str] = None
    role: str
    phone: Optional[str] = None
    email: Optional[str] = None
    region: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None


class PlotBase(BaseModel):
    plot_code: str
    area_mu: float
    crop_type: str
    soil_type: str
    irrigation_method: str
    water_source: str
    region: Optional[str] = None
    growth_stage: Optional[str] = "initial"
    farmer_id: Optional[int] = None
    annual_quota: Optional[float] = 0


class PlotCreate(PlotBase):
    pass


class PlotUpdate(BaseModel):
    area_mu: Optional[float] = None
    crop_type: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation_method: Optional[str] = None
    water_source: Optional[str] = None
    region: Optional[str] = None
    growth_stage: Optional[str] = None
    farmer_id: Optional[int] = None
    annual_quota: Optional[float] = None


class PlotResponse(PlotBase):
    id: int
    farmer: Optional[UserResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WeatherDataBase(BaseModel):
    date: date
    temperature_avg: float
    temperature_max: float
    temperature_min: float
    rainfall: Optional[float] = 0
    wind_speed: Optional[float] = 0
    sunshine_hours: Optional[float] = 0
    relative_humidity: Optional[float] = 0
    region: Optional[str] = None


class WeatherDataCreate(WeatherDataBase):
    pass


class WeatherDataResponse(WeatherDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class IrrigationRecordBase(BaseModel):
    plot_id: int
    irrigation_date: date
    water_amount_m3: float
    duration_hours: Optional[float] = 0
    irrigation_method: Optional[str] = None
    operator: Optional[str] = None
    notes: Optional[str] = None


class IrrigationRecordCreate(IrrigationRecordBase):
    pass


class IrrigationRecordResponse(IrrigationRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class IrrigationSuggestionResponse(BaseModel):
    id: int
    plot_id: int
    suggestion_date: date
    et0: float
    etc: float
    effective_rainfall: float
    irrigation_need: float
    suggested_water_mu: float
    suggested_water_total: float
    suggested_duration: float
    urgency_level: str
    plot: Optional[PlotResponse] = None

    class Config:
        from_attributes = True


class WaterUsageResponse(BaseModel):
    id: int
    plot_id: int
    year: int
    month: int
    planned_usage: float
    actual_usage: float
    water_fee: float

    class Config:
        from_attributes = True


class MonthlyStats(BaseModel):
    plot_id: int
    plot_code: str
    year: int
    month: int
    planned_usage: float
    actual_usage: float
    water_saving_rate: float
    water_fee: float


class SoilWaterBalanceItem(BaseModel):
    date: date
    et: float
    rainfall: float
    irrigation: float
    balance: float
