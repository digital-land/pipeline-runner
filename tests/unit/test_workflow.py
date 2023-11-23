import os
from application.core.workflow import csv_to_json


def test_csv_to_json():
    file_path = os.path.join("tests/data/csvs", "sample_file.csv")

    # Call the function
    result = csv_to_json(file_path)

    expected_result = [{"field1": "value1", "field2": "value2"}]
    assert result == expected_result


def test_csv_to_json_file_not_found():
    # Provide a non-existent file path
    file_path = os.path.join("tests/data/csv", "nonexistent_file.csv")

    # Call the function
    result = csv_to_json(file_path)

    # Assert that the result is an empty list
    assert result == []
