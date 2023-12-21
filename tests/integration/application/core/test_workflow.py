import pytest
from collections import namedtuple
import os
import csv
import shutil
from application.core.workflow import run_workflow
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


@pytest.fixture
def mock_directories(tmpdir):
    Directories = namedtuple(
        "Directories",
        [
            "COLLECTION_DIR",
            "CONVERTED_DIR",
            "ISSUE_DIR",
            "COLUMN_FIELD_DIR",
            "TRANSFORMED_DIR",
            "FLATTENED_DIR",
            "DATASET_DIR",
            "DATASET_RESOURCE_DIR",
            "PIPELINE_DIR",
            "SPECIFICATION_DIR",
            "CACHE_DIR",
        ],
    )
    VAR_DIR = tmpdir.mkdir("var")
    return Directories(
        COLLECTION_DIR=tmpdir.mkdir("collection"),
        CONVERTED_DIR=tmpdir.mkdir("converted"),
        ISSUE_DIR=tmpdir.mkdir("issue"),
        COLUMN_FIELD_DIR=VAR_DIR.mkdir("column-field"),
        TRANSFORMED_DIR=tmpdir.mkdir("transformed"),
        FLATTENED_DIR=tmpdir.mkdir("flattened"),
        DATASET_DIR=tmpdir.mkdir("dataset"),
        DATASET_RESOURCE_DIR=VAR_DIR.mkdir("dataset-resource"),
        PIPELINE_DIR=tmpdir.mkdir("pipeline"),
        SPECIFICATION_DIR="specification",
        CACHE_DIR=VAR_DIR.mkdir("cache"),
    )


@pytest.fixture
def uploaded_csv(mock_directories):
    collection_dir = mock_directories.COLLECTION_DIR
    resource_dir = os.path.join(collection_dir, "resource")
    os.makedirs(resource_dir, exist_ok=True)
    mock_csv = os.path.join(resource_dir, "7e9a0e71f3ddfe")
    row = {
        "geometry": "MULTIPOLYGON (((-1.799316 53.717797, "
        "-1.790771 53.717797, -1.790771 53.721066, -1.799316 53.721066, -1.799316 53.717797)))",
        "reference": "4",
        "name": "South Jesmond",
    }
    fieldnames = row.keys()
    with open(mock_csv, "w") as f:
        dictwriter = csv.DictWriter(f, fieldnames=fieldnames)
        dictwriter.writeheader()
        dictwriter.writerow(row)


@pytest.fixture
def mock_fetch_pipeline_csvs(tmpdir, mock_directories):
    # create a mock column.csv in the pipeline folder
    mock_column_csv = os.path.join(tmpdir, mock_directories.PIPELINE_DIR, "column.csv")
    row = {
        "dataset": "conservation-area",
        "resource": "",
        "column": "wkt",
        "field": "geometry",
    }
    fieldnames = row.keys()
    with open(mock_column_csv, "w") as f:
        dictwriter = csv.DictWriter(f, fieldnames=fieldnames)
        dictwriter.writeheader()
        dictwriter.writerow(row)


def test_run_workflow(mocker, mock_directories, mock_fetch_pipeline_csvs, uploaded_csv):
    dataset = "conservation-area"
    organisation = "local-authority-eng:CAT"

    source_organisation_csv = "tests/data/csvs/organisation.csv"
    destination_organisation_csv = os.path.join(
        mock_directories.CACHE_DIR, "organisation.csv"
    )
    shutil.copy(source_organisation_csv, destination_organisation_csv)

    mocker.patch(
        "application.core.workflow.fetch_pipeline_csvs",
        side_effect=mock_fetch_pipeline_csvs,
    )

    response_data = run_workflow(dataset, organisation, mock_directories)

    assert "converted-csv" in response_data
    assert "issue-log" in response_data
    assert "column-field-log" in response_data
    assert "flattened-csv" in response_data
