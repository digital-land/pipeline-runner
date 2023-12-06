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
    "collection": "conservation-area-collection",
    "organisation": "test-organisation",
}
GOOD_FORM_DATA = {
    "dataset": "conservation-area",
    "collection": "conservation-area-collection",
    "organisation": "local-authority-eng:CAT",
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


def test_good_validation_request_has_valid_response(api_client: TestClient):
    endpoint_url = VALIDATE_FILE_REQ_URL
    upload_file = [
        ("upload_file", open("tests/data/csvs/conservation_areas.csv", "rb"))
    ]

    resp = api_client.post(url=endpoint_url, data=GOOD_FORM_DATA, files=upload_file)
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


def test_validation_request_without_dataset(api_client: TestClient):
    endpoint_url = VALIDATE_FILE_REQ_URL
    upload_file = [
        ("upload_file", open("tests/data/csvs/conservation_areas.csv", "rb"))
    ]

    resp = api_client.post(url=endpoint_url, data=BAD_FORM_DATA_2, files=upload_file)
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
    assert resp_json["detail"]["errMsg"] == "Missing required field: 'dataset'"
    assert resp.status_code == 400


def test_validation_request_with_invalid_data(api_client: TestClient):
    endpoint_url = VALIDATE_FILE_REQ_URL
    upload_file = [
        ("upload_file", open("tests/data/csvs/conservation_areas_invalid.csv", "rb"))
    ]

    resp = api_client.post(url=endpoint_url, data=GOOD_FORM_DATA, files=upload_file)
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
    assert resp_json["flattened-csv"] == []
    assert resp.status_code == 200
