from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from application.app import app
from application.services.json_schema_svc import (
    JsonSchemaSvc,
    JSONSchemaMap,
    get_schema_svc,
)

schema_svc: JsonSchemaSvc = None

VALIDATE_FILE_REQ_URL = "/api/dataset/validate/file/request/"

BAD_FORM_DATA_1 = {}
BAD_FORM_DATA_2 = {
    "dataset": "test-dataset",
}
BAD_FORM_DATA_3 = {
    "dataset": "test-dataset",
    "collection": "test-collection",
}
BAD_FORM_DATA_4 = {
    "dataset": "",
    "collection": "test-collection",
    "organization": "test-organization",
}
GOOD_FORM_DATA = {
    "dataset": "test-dataset",
    "collection": "test-collection",
    "organization": "test-organization",
}


async def json_schema_svc():
    global schema_svc
    schema_path = Path("tests/data/json_schemas")
    schema_svc = JsonSchemaSvc(schema_dir=schema_path)
    return schema_svc


@pytest.fixture(scope="session")
def api_client():
    client = TestClient(app)
    app.dependency_overrides[get_schema_svc] = json_schema_svc
    return client


# @pytest.mark.skip(reason="")
def test_good_validation_request_has_valid_response(api_client: TestClient):
    endpoint_url = VALIDATE_FILE_REQ_URL
    upload_file = [("upload_file", open("tests/data/json_schemas/dummy.csv", "rb"))]
    form_data = {
        "dataset": "test-dataset",
        "collection": "test-collection",
        "organization": "test-organization",
    }

    resp = api_client.post(url=endpoint_url, data=form_data, files=upload_file)
    resp_json = resp.json()

    if resp.status_code == 200:
        ok, err_msg = schema_svc.validate_json_dict(
            resp_json, JSONSchemaMap.API_RUN_PIPELINE_RESPONSE
        )
    else:
        ok, err_msg = schema_svc.validate_json_dict(
            resp_json, JSONSchemaMap.API_RESPONSE_ERROR
        )

    assert ok is True
    assert len(err_msg) == 0
    assert resp.status_code == 200


# @pytest.mark.skip(reason="")
@pytest.mark.parametrize(
    "form_data, upload_file",
    [
        pytest.param(BAD_FORM_DATA_1, None, id="1"),
        pytest.param(BAD_FORM_DATA_2, None, id="2"),
        pytest.param(BAD_FORM_DATA_3, None, id="3"),
        pytest.param(BAD_FORM_DATA_4, "tests/data/json_schemas/dummy.csv", id="4"),
        pytest.param(GOOD_FORM_DATA, None, id="5"),
        pytest.param(GOOD_FORM_DATA, "tests/data/json_schemas/dummy.txt", id="6"),
    ],
)
def test_bad_validation_request_has_invalid_response(
    request, api_client: TestClient, form_data, upload_file
):
    endpoint_url = VALIDATE_FILE_REQ_URL
    upload_file = (
        [] if not upload_file else [("upload_file", open(f"{upload_file}", "rb"))]
    )

    resp = api_client.post(url=endpoint_url, data=form_data, files=upload_file)
    resp_json = resp.json()

    if resp.status_code == 200:
        ok, err_msg = schema_svc.validate_json_dict(
            resp_json, JSONSchemaMap.API_RUN_PIPELINE_RESPONSE
        )
    else:
        ok, err_msg = schema_svc.validate_json_dict(
            resp_json, JSONSchemaMap.API_RESPONSE_ERROR
        )

    assert ok is True
    assert len(err_msg) == 0
    assert resp.status_code != 200

    if request.node.name == "test_bad_validation_request_has_invalid_response[1]":
        assert resp_json["detail"]["errMsg"] == "Missing required field: 'dataset'"

    if request.node.name == "test_bad_validation_request_has_invalid_response[2]":
        assert resp_json["detail"]["errMsg"] == "Missing required field: 'collection'"

    if request.node.name == "test_bad_validation_request_has_invalid_response[3]":
        assert resp_json["detail"]["errMsg"] == "Missing required field: 'organization'"

    if request.node.name == "test_bad_validation_request_has_invalid_response[4]":
        assert (
            resp_json["detail"]["errMsg"]
            == "JSON message failed schema validation: dataset is too short"
        )

    if request.node.name == "test_bad_validation_request_has_invalid_response[5]":
        assert resp_json["detail"]["errMsg"] == "Missing required field: 'upload_file'"

    if request.node.name == "test_bad_validation_request_has_invalid_response[6]":
        assert "'dummy.txt' does not match" in resp_json["detail"]["errMsg"]
