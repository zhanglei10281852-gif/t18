from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="农田灌溉智能决策与用水量核算系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_initialized = False


@app.on_event("startup")
async def startup_event():
    global db_initialized
    max_retries = 30
    retry_delay = 2

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempt {attempt}/{max_retries}: Connecting to database...")
            from database import engine, Base
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")

            import init_data
            init_data.init_db()
            db_initialized = True
            logger.info("Database initialization completed!")
            break
        except Exception as e:
            logger.error(f"Database initialization failed (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Starting app without full DB initialization.")
                logger.error("Health check will return 'degraded' status.")


from routers.auth_router import router as auth_router
from routers.user_router import router as user_router
from routers.plot_router import router as plot_router
from routers.weather_router import router as weather_router
from routers.irrigation_router import router as irrigation_router
from routers.water_router import router as water_router

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(plot_router)
app.include_router(weather_router)
app.include_router(irrigation_router)
app.include_router(water_router)


@app.get("/api/health")
async def health_check():
    if db_initialized:
        return {"status": "ok", "message": "农业水利信息化系统运行正常"}
    else:
        return {"status": "degraded", "message": "系统运行中，数据库未完全初始化"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9174, reload=True)
