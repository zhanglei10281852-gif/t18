from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers.auth_router import router as auth_router
from routers.user_router import router as user_router
from routers.plot_router import router as plot_router
from routers.weather_router import router as weather_router
from routers.irrigation_router import router as irrigation_router
from routers.water_router import router as water_router
import init_data

app = FastAPI(title="农田灌溉智能决策与用水量核算系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(plot_router)
app.include_router(weather_router)
app.include_router(irrigation_router)
app.include_router(water_router)


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    init_data.init_db()


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "农业水利信息化系统运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9174, reload=True)
