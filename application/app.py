from fastapi import FastAPI

from application.routers import validation_router


app = FastAPI()

app.include_router(validation_router.router, prefix="/api/dataset/validate")
