import json

from fastapi import APIRouter, Request, Depends, status, HTTPException

from application.logging.logger import get_logger
from application.services.json_schema_svc import (
    JsonSchemaSvc,
    JSONSchemaMap,
    ErrorMap,
    get_schema_svc,
)
from datetime import datetime

logger = get_logger(__name__)

router = APIRouter()


@router.get("/")
async def validate(request: Request):
    return json.dumps({"status": "200"})


@router.post("/file/request/")
async def dataset_validation_request(
    req: Request, schema_svc: JsonSchemaSvc = Depends(get_schema_svc)
):
    req_msg_dict = {"dataset": "", "collection": "", "organization": "", "filePath": ""}

    try:
        async with req.form() as form:
            req_msg_dict["dataset"] = form["dataset"]
            req_msg_dict["collection"] = form["collection"]
            req_msg_dict["organization"] = form["organization"]
            req_msg_dict["filePath"] = form["upload_file"].filename

            # save file contents somewhere accessible to downstream services
            # contents = await form["upload_file"].read()

            # put the filepath of the saved file into the req_msg_dict
            # req_msg_dict["filePath"] = [save_dir] / form["upload_file"].filename

    except KeyError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "errCode": str(status.HTTP_400_BAD_REQUEST),
                "errType": ErrorMap.USER_ERROR.value,
                "errMsg": f"Missing required field: {str(err)}",
                "errTime": str(datetime.now()),
            },
        )

    # validate the resulting message and reject if invalid
    ok, err_msg = schema_svc.validate_json_dict(
        req_msg_dict, JSONSchemaMap.API_RUN_PIPELINE_REQUEST
    )

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "errCode": str(status.HTTP_400_BAD_REQUEST),
                "errType": ErrorMap.USER_ERROR.value,
                "errMsg": f"{str(err_msg)}",
                "errTime": str(datetime.now()),
            },
        )

    # the message is valid so we can continue with the request
    # TODO

    # return an appropriate response
    return {"status": "SUCCESS", "data": req_msg_dict}
