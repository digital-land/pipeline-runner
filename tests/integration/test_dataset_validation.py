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
def test_bad_validation_request_has_invalid_response(api_client: TestClient):
    endpoint_url = VALIDATE_FILE_REQ_URL
    upload_file = []
    form_data = {}

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
    assert len(resp_json["detail"]["errMsg"]) > 0
    assert resp.status_code != 200
