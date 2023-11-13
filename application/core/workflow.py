import os
import csv
import urllib
from urllib.error import HTTPError
from application.logging.logger import get_logger
from application.core.pipeline import fetch_response_data, resource_from_path


logger = get_logger(__name__)

source_url = "https://raw.githubusercontent.com/digital-land/"


def run_workflow(dataset, organisation):
    collection_dir = "collection/"
    issue_dir = "issue/"
    column_field_dir = "var/column-field/"
    transformed_dir = "transformed/"
    flattened_dir = "flattened/"
    converted_dir = "converted/"
    additional_column_mappings = None
    additional_concats = None

    # pipeline directory structure & download
    pipeline_dir = os.path.join("pipeline")
    os.makedirs(pipeline_dir, exist_ok=True)
    pipeline_csvs = [
        "column.csv",
        "concat.csv",
        "convert.csv",
        "default.csv",
        "filter.csv",
        "lookup.csv",
        "patch.csv",
        "skip.csv",
        "transform.csv",
        "combine.csv",
    ]
    for pipeline_csv in pipeline_csvs:
        try:
            urllib.request.urlretrieve(
                f"{source_url}/{dataset + '-collection'}/main/pipeline/{pipeline_csv}",
                os.path.join(pipeline_dir, pipeline_csv),
            )
        except HTTPError as e:
            print(e)

    fetch_response_data(
        dataset,
        organisation,
        collection_dir,
        issue_dir,
        column_field_dir,
        transformed_dir,
        flattened_dir,
        additional_col_mappings=additional_column_mappings,
        additional_concats=additional_concats,
    )

    input_path = os.path.join(collection_dir, "resource")
    # List all files in the "resource" directory
    files_in_resource = os.listdir(input_path)

    for file_name in files_in_resource:
        file_path = os.path.join(input_path, file_name)
    resource = resource_from_path(file_path)

    converted_json = []
    if os.path.exists(os.path.join(converted_dir, f"{resource}.csv")):
        converted_json = csv_to_json(os.path.join(converted_dir, f"{resource}.csv"))
    else:
        converted_json = csv_to_json(
            os.path.join(collection_dir, "resource", f"{resource}")
        )

    issue_log_json = csv_to_json(os.path.join(issue_dir, dataset, f"{resource}.csv"))
    column_field_json = csv_to_json(
        os.path.join(column_field_dir, dataset, f"{resource}.csv")
    )
    flattened_json = csv_to_json(os.path.join(flattened_dir, dataset, f"{dataset}.csv"))

    response_data = {
        "converted-csv": converted_json,
        "issue-log": issue_log_json,
        "column-field-log": column_field_json,
        "flattened-csv": flattened_json,
    }
    return response_data


def csv_to_json(csv_file):
    json_data = []
    # Open the CSV file for reading
    with open(csv_file, "r") as csv_input:
        # Read the CSV data
        csv_data = csv.DictReader(csv_input)

        # Convert CSV to a list of dictionaries
        data_list = list(csv_data)

        for row in data_list:
            json_data.append(row)

    return json_data
