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
import application.core.workflow as workflow
from application.exceptions.customExceptions import URLException

logger = get_logger(__name__)

router = APIRouter()


@router.post("/file/request/")
async def dataset_validation_request(
    req: Request, schema_svc: JsonSchemaSvc = Depends(get_schema_svc)
):
    req_msg_dict = {"dataset": "", "collection": "", "organisation": ""}

    try:
        async with req.form() as form:
            req_msg_dict["dataset"] = form["dataset"]
            req_msg_dict["collection"] = form["collection"]
            if "organisation" in form:
                req_msg_dict["organisation"] = form["organisation"]

            organisation = req_msg_dict["organisation"]
            collection = req_msg_dict["collection"]
            dataset = form["dataset"]
            if "upload_file" in form:
                req_msg_dict["filePath"] = form["upload_file"].filename
                file = form["upload_file"]
                utils.save_uploaded_file(file)
            elif "upload_url" in form:
                req_msg_dict["urlPath"] = form["upload_url"]
                url = form["upload_url"]
                log, content = utils.get_request(url)
                if content:
                    utils.save_content(content)
                else:
                    raise URLException(log)

            else:
                raise KeyError("upload_file or upload_url")

    except KeyError as err:
        logger.error(f"Exception occured: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "errCode": str(status.HTTP_400_BAD_REQUEST),
                "errType": ErrorMap.USER_ERROR.value,
                "errMsg": f"Missing required field: {str(err)}",
                "errTime": str(datetime.now()),
            },
        )

    except URLException as err:
        logger.error(f"Exception occured: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                **err.detail,
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

    response_data = workflow.run_workflow(collection, dataset, organisation)
    return response_data
