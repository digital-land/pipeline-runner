import json

from fastapi import APIRouter, Request, Depends, status, HTTPException
import application.core.utils as utils
from application.logging.logger import get_logger
from application.services.json_schema_svc import (
    JsonSchemaSvc,
    JSONSchemaMap,
    ErrorMap,
    get_schema_svc,
)
from datetime import datetime
import application.core.pipeline as pipeline


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
            file = form["upload_file"]
            dataset = form["dataset"]
            organisation = form["organization"]
            # save the uploaded file
            utils.save_uploaded_file(file)

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

    data_dir = "collection/"
    issue_dir = "issue/"
    column_field_dir = "column-field/"
    transformed_dir = "transformed/"
    additional_column_mappings = None
    additional_concats = None

    pipeline.run_endpoint_workflow(
        dataset,
        organisation,
        data_dir,
        issue_dir,
        column_field_dir,
        transformed_dir,
        additional_col_mappings=additional_column_mappings,
        additional_concats=additional_concats,
    )

    # return an appropriate response
    mock_final_response: dict
    with open("tests/data/example_jsons/API_RUN_PIPELINE_RESPONSE.json") as f:
        mock_final_response = json.load(f)

    return mock_final_response
