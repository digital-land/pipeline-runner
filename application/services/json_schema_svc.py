import json
import jsonschema
from enum import Enum
from functools import lru_cache
from jsonschema import validate
from pathlib import Path


class JSONSchemaMap(Enum):
    API_RESPONSE_ERROR = "api_error_schema.json"
    API_RUN_PIPELINE_REQUEST = "api_run_pipeline_req.json"
    API_RUN_PIPELINE_RESPONSE = "api_run_pipeline_resp.json"


class JsonSchemaSvc:
    def __init__(self, schema_dir: Path = None):
        self.schema_dir = schema_dir

    def load_schema(self, schema: JSONSchemaMap = None) -> dict:
        """
        loads the given schema from the schema directory
        :param schema:
        :return:
        """
        schema_json: dict

        schema_file_path = self.schema_dir / schema.value

        with open(schema_file_path) as schema_file:
            schema_json = json.load(schema_file)

        return schema_json

    def validate_json_dict(
        self, json_msg: dict = None, schema: JSONSchemaMap = None
    ) -> (bool, str):
        """
        Validates the given json_msg against the given schema.
        If an error occurs, info will be given in the 2nd output
        value.
        :param json_msg:
        :param schema:
        :return:
        """
        if not self.schema_dir:
            return False, "Schema directory not provided"
        if not json_msg:
            return False, "JSON dictionary param is empty"
        if not schema:
            return False, "JSON schema param is empty"

        try:
            schema = self.load_schema(schema)
            validate(instance=json_msg, schema=schema)
        except FileNotFoundError:
            return False, "Failed to load Schema"
        except jsonschema.exceptions.ValidationError as err:
            return False, f"JSON message failed schema validation: {str(err.message)}"

        return True, ""

    def validate_json_str(
        self, json_msg: str = None, schema: JSONSchemaMap = None
    ) -> (bool, str):
        """
        Utility function that wraps validate_json_dict.
        This function allows a user to pass the json_msg as a string
        :param json_msg:
        :param schema:
        :return:
        """
        if not json_msg:
            return False, "JSON dictionary param is empty"

        json_msg_dict = json.loads(json_msg)
        return self.validate_json_dict(json_msg_dict, schema)


@lru_cache
def get_schema_svc():
    schema_path = Path("tests/data/json_schemas")
    return JsonSchemaSvc(schema_dir=schema_path)
