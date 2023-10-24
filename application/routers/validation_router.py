import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Request, Depends, status, HTTPException

from application.logging.logger import get_logger
from application.services.json_schema_svc import JsonSchemaSvc, JSONSchemaMap

logger = get_logger(__name__)

router = APIRouter()


@lru_cache
def get_schema_svc():
    schema_path = Path("tests/data/json_schemas")
    return JsonSchemaSvc(schema_dir=schema_path)


@router.get("/")
async def validate(request: Request):
    return json.dumps({"status": "200"})


@router.post("/form/request")
async def dataset_validation_request(
    req: Request, schema_svc: JsonSchemaSvc = Depends(get_schema_svc)
):
    req_msg_dict = {"dataset": "", "collection": "", "organization": "", "filePath": ""}

    try:
        async with req.form() as form:
            req_msg_dict["dataset"] = form["dataset"]
            req_msg_dict["collection"] = form["collection"]
            req_msg_dict["organization"] = form["organization"]
            # req_msg_dict["filePath"] = form["upload_file"].filename

            # save file contents somewhere accessible to downstream services
            # contents = await form["upload_file"].read()

            # put the filepath of the saved file into the req_msg_dict
            # req_msg_dict["filePath"] = [save_dir] / form["upload_file"].filename

    except KeyError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"err_msg": f"test error message {str(err)}"},
        )

    # validate the resulting message and reject if invalid
    ok, err_msg = schema_svc.validate_json_dict(
        req_msg_dict, JSONSchemaMap.API_RUN_PIPELINE_REQUEST
    )

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"test error message {str(err_msg)}",
        )

    # the message is valid so we can continue with the request
    # TODO

    # return an appropriate response
    return {"status": "SUCCESS", "data": req_msg_dict}
