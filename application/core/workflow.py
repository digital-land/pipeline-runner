import os
import csv
import urllib
from urllib.error import HTTPError
import shutil
from application.logging.logger import get_logger
from application.core.pipeline import fetch_response_data, resource_from_path
from application.core.config import Directories, source_url


logger = get_logger(__name__)


def run_workflow(dataset, organisation, directories=None):
    additional_column_mappings = None
    additional_concats = None

    if not directories:
        directories = Directories

    try:
        # pipeline directory structure & download
        pipeline_dir = os.path.join(directories.PIPELINE_DIR)
        fetch_pipeline_csvs(dataset, pipeline_dir)

        fetch_response_data(
            dataset,
            organisation,
            directories.COLLECTION_DIR,
            directories.ISSUE_DIR,
            directories.COLUMN_FIELD_DIR,
            directories.TRANSFORMED_DIR,
            directories.FLATTENED_DIR,
            directories.DATASET_DIR,
            directories.DATASET_RESOURCE_DIR,
            directories.PIPELINE_DIR,
            directories.SPECIFICATION_DIR,
            directories.CACHE_DIR,
            additional_col_mappings=additional_column_mappings,
            additional_concats=additional_concats,
        )

        input_path = os.path.join(directories.COLLECTION_DIR, "resource")
        # List all files in the "resource" directory
        files_in_resource = os.listdir(input_path)

        for file_name in files_in_resource:
            file_path = os.path.join(input_path, file_name)
        resource = resource_from_path(file_path)

        converted_json = []
        if os.path.exists(os.path.join(directories.CONVERTED_DIR, f"{resource}.csv")):
            converted_json = csv_to_json(
                os.path.join(directories.CONVERTED_DIR, f"{resource}.csv")
            )
        else:
            converted_json = csv_to_json(
                os.path.join(directories.COLLECTION_DIR, "resource", f"{resource}")
            )

        issue_log_json = csv_to_json(
            os.path.join(directories.ISSUE_DIR, dataset, f"{resource}.csv")
        )
        column_field_json = csv_to_json(
            os.path.join(directories.COLUMN_FIELD_DIR, dataset, f"{resource}.csv")
        )
        # flattened_json = csv_to_json(
        #     os.path.join(directories.FLATTENED_DIR, dataset, f"{dataset}.csv")
        # )
        flattened_json = []
        response_data = {
            "converted-csv": converted_json,
            "issue-log": issue_log_json,
            "column-field-log": column_field_json,
            "flattened-csv": flattened_json,
        }
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        clean_up(
            directories.COLLECTION_DIR,
            directories.CONVERTED_DIR,
            directories.ISSUE_DIR,
            directories.COLUMN_FIELD_DIR,
            directories.TRANSFORMED_DIR,
            directories.FLATTENED_DIR,
            directories.DATASET_DIR,
            directories.DATASET_RESOURCE_DIR,
            directories.PIPELINE_DIR,
        )

    return response_data


def fetch_pipeline_csvs(dataset, pipeline_dir):
    os.makedirs(pipeline_dir, exist_ok=True)
    pipeline_csvs = [
        "column.csv",
    ]
    for pipeline_csv in pipeline_csvs:
        try:
            urllib.request.urlretrieve(
                f"{source_url}/{dataset + '-collection'}/main/pipeline/{pipeline_csv}",
                os.path.join(pipeline_dir, pipeline_csv),
            )
        except HTTPError as e:
            logger.error(f"Failed to retrieve pipeline CSV: {e}")


def clean_up(*directories):
    try:
        for directory in directories:
            if os.path.exists(directory):
                shutil.rmtree(directory)
    except Exception as e:
        logger.error(f"An error occurred during cleanup: {e}")


def csv_to_json(csv_file):
    json_data = []

    if os.path.isfile(csv_file):
        # Open the CSV file for reading
        with open(csv_file, "r") as csv_input:
            # Read the CSV data
            csv_data = csv.DictReader(csv_input)

            # Convert CSV to a list of dictionaries
            data_list = list(csv_data)

            for row in data_list:
                json_data.append(row)

    return json_data
