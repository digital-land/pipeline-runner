from fastapi import APIRouter, Request

import json

from application.logging.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# Temporary status check endpoint
@router.get("/")
async def validate(request: Request):
    return json.dumps({"status": "200"})
