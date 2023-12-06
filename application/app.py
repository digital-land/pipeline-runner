from fastapi import FastAPI
from application.logging.logger import get_logger
from application.routers import validation_router

logger = get_logger(__name__)
app = FastAPI()

app.include_router(validation_router.router, prefix="/api/dataset/validate")


@app.get("/health", include_in_schema=False)
def health():
    try:
        status = {
            "status": "OK",
        }
        logger.info(f"healthcheck {status}")
        return status
    except Exception as e:
        logger.exception(e)
        raise e
