MONTHLY_RA_VALUES = {
    1: 8.0,
    2: 10.5,
    3: 14.0,
    4: 18.5,
    5: 22.0,
    6: 24.5,
    7: 25.0,
    8: 23.5,
    9: 19.5,
    10: 15.0,
    11: 10.0,
    12: 7.5,
}

CROP_KC_VALUES = {
    "rice": {
        "initial": 0.4,
        "development": 0.8,
        "mid": 1.15,
        "late": 0.7,
    },
    "wheat": {
        "initial": 0.35,
        "development": 0.75,
        "mid": 1.05,
        "late": 0.55,
    },
    "corn": {
        "initial": 0.35,
        "development": 0.75,
        "mid": 1.15,
        "late": 0.6,
    },
    "cotton": {
        "initial": 0.35,
        "development": 0.75,
        "mid": 1.1,
        "late": 0.65,
    },
}

IRRIGATION_FLOW_RATE = {
    "flood": 30,
    "sprinkler": 15,
    "drip": 8,
}

CROP_TYPE_NAMES = {
    "rice": "水稻",
    "wheat": "小麦",
    "corn": "玉米",
    "cotton": "棉花",
}

SOIL_TYPE_NAMES = {
    "sandy": "砂土",
    "loam": "壤土",
    "clay": "粘土",
}

IRRIGATION_METHOD_NAMES = {
    "flood": "漫灌",
    "sprinkler": "喷灌",
    "drip": "滴灌",
}

WATER_SOURCE_NAMES = {
    "reservoir": "水库",
    "river": "河流",
    "groundwater": "地下水",
}

ROLE_NAMES = {
    "admin": "管理员",
    "manager": "灌区管理员",
    "farmer": "农户",
}

GROWTH_STAGE_NAMES = {
    "initial": "初期",
    "development": "发育期",
    "mid": "中期",
    "late": "末期",
}

WATER_PRICE_TIERS = [
    {"max_ratio": 1.0, "price": 0.15},
    {"max_ratio": 1.5, "price": 0.30},
    {"max_ratio": float("inf"), "price": 0.60},
]


def calculate_et0(t_avg: float, t_max: float, t_min: float, ra: float) -> float:
    if t_max <= t_min:
        return 0
    return 0.0023 * (t_avg + 17.8) * (t_max - t_min) ** 0.5 * ra


def calculate_etc(et0: float, crop_type: str, growth_stage: str) -> float:
    kc_table = CROP_KC_VALUES.get(crop_type, CROP_KC_VALUES["corn"])
    kc = kc_table.get(growth_stage, kc_table["mid"])
    return et0 * kc


def get_ra_by_month(month: int) -> float:
    return MONTHLY_RA_VALUES.get(month, 15.0)


def get_effective_rainfall(rainfall: float) -> float:
    return rainfall * 0.7


def get_flow_rate(irrigation_method: str) -> float:
    return IRRIGATION_FLOW_RATE.get(irrigation_method, 15)


def calculate_water_fee(usage: float, quota: float) -> float:
    if quota <= 0:
        return usage * 0.15

    if usage <= quota:
        return usage * 0.15
    elif usage <= quota * 1.5:
        return quota * 0.15 + (usage - quota) * 0.30
    else:
        return quota * 0.15 + quota * 0.5 * 0.30 + (usage - quota * 1.5) * 0.60
