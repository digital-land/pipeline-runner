import os
import csv
import sys
from collections import OrderedDict
import json
import itertools
from application.logging.logger import get_logger
from digital_land.specification import Specification
from digital_land.log import DatasetResourceLog, IssueLog, ColumnFieldLog
from digital_land.organisation import Organisation
from digital_land.phase.combine import FactCombinePhase
from digital_land.phase.concat import ConcatFieldPhase
from digital_land.phase.convert import ConvertPhase
from digital_land.phase.default import DefaultPhase
from digital_land.phase.factor import FactorPhase
from digital_land.phase.filter import FilterPhase
from digital_land.phase.harmonise import HarmonisePhase
from digital_land.phase.lookup import (
    EntityLookupPhase,
    FactLookupPhase,
)

from digital_land.phase.map import MapPhase
from digital_land.phase.migrate import MigratePhase
from digital_land.phase.normalise import NormalisePhase
from digital_land.phase.organisation import OrganisationPhase
from digital_land.phase.parse import ParsePhase
from digital_land.phase.patch import PatchPhase
from digital_land.phase.pivot import PivotPhase
from digital_land.phase.prefix import EntityPrefixPhase
from digital_land.phase.prune import FieldPrunePhase, EntityPrunePhase, FactPrunePhase
from digital_land.phase.reference import EntityReferencePhase, FactReferencePhase
from digital_land.phase.save import SavePhase
from digital_land.pipeline import run_pipeline, Pipeline
from digital_land.commands import dataset_dump, dataset_create
from application.core.lookup_functions import (
    save_resource_unidentified_lookups,
    standardise_lookups,
    add_unnassigned_to_lookups,
)


from pathlib import Path

logger = get_logger(__name__)


def fetch_response_data(
    dataset,
    organisation,
    collection_dir,
    issue_dir,
    column_field_dir,
    transformed_dir,
    flattened_dir,
    dataset_dir,
    dataset_resource_dir,
    pipeline_dir,
    specification_dir,
    additional_col_mappings,
    additional_concats,
):
    # define variables for Pipeline and specification
    pipeline = Pipeline(pipeline_dir, dataset)
    specification = Specification(specification_dir)

    input_path = os.path.join(collection_dir, "resource")
    # List all files in the "resource" directory
    files_in_resource = os.listdir(input_path)
    os.makedirs(os.path.join(issue_dir, dataset), exist_ok=True)
    for file_name in files_in_resource:
        file_path = os.path.join(input_path, file_name)
        # retrieve unnassigned entities and assign
        assign_entries(
            resource_path=file_path,
            dataset=dataset,
            organisation=organisation,
            pipeline_dir=pipeline_dir,
            specification=specification,
        )

    # Create directories if they don't exist
    for directory in [
        collection_dir,
        issue_dir,
        column_field_dir,
        transformed_dir,
        flattened_dir,
        dataset_dir,
    ]:
        os.makedirs(directory, exist_ok=True)

    os.makedirs(os.path.join(transformed_dir, dataset))
    os.makedirs(os.path.join(flattened_dir, dataset))

    # Access each file in the "resource" directory
    for file_name in files_in_resource:
        file_path = os.path.join(input_path, file_name)

        os.makedirs(os.path.join(issue_dir, dataset), exist_ok=True)
        os.makedirs(os.path.join(column_field_dir, dataset), exist_ok=True)
        os.makedirs(os.path.join(dataset_resource_dir, dataset), exist_ok=True)

        pipeline_run(
            dataset=dataset,
            pipeline=pipeline,
            specification_dir=specification_dir,
            input_path=file_path,
            output_path=os.path.join(transformed_dir, dataset, f"{file_name}.csv"),
            issue_dir=os.path.join(issue_dir, dataset),
            column_field_dir=os.path.join(column_field_dir, dataset),
            dataset_resource_dir=os.path.join(dataset_resource_dir, dataset),
            organisation_path=os.path.join("var", "cache", "organisation.csv"),
            save_harmonised=False,
            organisations=[organisation],
            custom_temp_dir=os.path.join("var", "cache"),
        )

        # build dataset
        dataset_input_path = os.path.join(transformed_dir, dataset, f"{file_name}.csv")
        dataset_create(
            input_paths=[dataset_input_path],
            output_path=os.path.join(dataset_dir, f"{dataset}.sqlite3"),
            organisation_path=os.path.join("var", "cache", "organisation.csv"),
            pipeline=pipeline,
            dataset=dataset,
            specification=specification,
            issue_dir=issue_dir,
        )

        dataset_dump(
            os.path.join(dataset_dir, f"{dataset}.sqlite3"),
            os.path.join(dataset_dir, f"{dataset}.csv"),
        )
        if os.path.getsize(os.path.join(dataset_dir, f"{dataset}.csv")) != 0:
            dataset_dump_flattened(
                os.path.join(dataset_dir, f"{dataset}.csv"),
                flattened_dir,
                specification,
                dataset,
            )


def pipeline_run(
    dataset,
    pipeline,
    specification_dir,
    input_path,
    output_path,
    organisations,
    null_path=None,  # TBD: remove this
    issue_dir=None,
    organisation_path=None,
    save_harmonised=False,
    column_field_dir=None,
    dataset_resource_dir=None,
    custom_temp_dir=None,  # TBD: rename to "tmpdir"
    endpoints=[],
    entry_date="",
):
    resource = resource_from_path(input_path)

    specification = Specification(specification_dir)
    schema = specification.pipeline[pipeline.name]["schema"]
    intermediate_fieldnames = specification.intermediate_fieldnames(pipeline)
    issue_log = IssueLog(dataset=dataset, resource=resource)
    column_field_log = ColumnFieldLog(dataset=dataset, resource=resource)
    dataset_resource_log = DatasetResourceLog(dataset=dataset, resource=resource)

    # load pipeline configuration
    skip_patterns = pipeline.skip_patterns(resource)
    columns = pipeline.columns(resource, endpoints=endpoints)
    concats = pipeline.concatenations(resource, endpoints=endpoints)
    patches = pipeline.patches(resource=resource)
    lookups = pipeline.lookups(resource=resource)
    default_fields = pipeline.default_fields(resource=resource)
    default_values = pipeline.default_values(endpoints=endpoints)
    combine_fields = pipeline.combine_fields(endpoints=endpoints)

    # load organisations
    organisation = Organisation(organisation_path, Path(pipeline.path))

    # severity_csv_path = os.path.join(specification_dir, "issue-type.csv")
    # Load the severity mapping CSV file into a DataFrame
    # severity_mapping = pd.read_csv(severity_csv_path)

    # resource specific default values
    if len(organisations) == 1:
        default_values["organisation"] = organisations[0]

    run_pipeline(
        ConvertPhase(
            path=input_path,
            dataset_resource_log=dataset_resource_log,
            custom_temp_dir=custom_temp_dir,
            output_path=os.path.join("converted", f"{resource}.csv"),
        ),
        NormalisePhase(skip_patterns=skip_patterns, null_path=null_path),
        ParsePhase(),
        ConcatFieldPhase(concats=concats, log=column_field_log),
        MapPhase(
            fieldnames=intermediate_fieldnames,
            columns=columns,
            log=column_field_log,
        ),
        FilterPhase(filters=pipeline.filters(resource)),
        PatchPhase(
            issues=issue_log,
            patches=patches,
        ),
        HarmonisePhase(
            specification=specification,
            issues=issue_log,
        ),
        DefaultPhase(
            default_fields=default_fields,
            default_values=default_values,
            issues=issue_log,
        ),
        # TBD: move migrating columns to fields to be immediately after map
        # this will simplify harmonisation and remove intermediate_fieldnames
        # but effects brownfield-land and other pipelines which operate on columns
        MigratePhase(
            fields=specification.schema_field[schema],
            migrations=pipeline.migrations(),
        ),
        OrganisationPhase(organisation=organisation, issues=issue_log),
        FieldPrunePhase(fields=specification.current_fieldnames(schema)),
        EntityReferencePhase(
            dataset=dataset,
            specification=specification,
        ),
        EntityPrefixPhase(dataset=dataset),
        EntityLookupPhase(lookups),
        SavePhase(
            default_output_path("harmonised", input_path),
            fieldnames=intermediate_fieldnames,
            enabled=save_harmonised,
        ),
        EntityPrunePhase(
            issue_log=issue_log, dataset_resource_log=dataset_resource_log
        ),
        PivotPhase(),
        FactCombinePhase(issue_log=issue_log, fields=combine_fields),
        FactorPhase(),
        FactReferencePhase(dataset=dataset, specification=specification),
        FactLookupPhase(lookups),
        FactPrunePhase(),
        SavePhase(
            output_path,
            fieldnames=specification.factor_fieldnames(),
        ),
    )

    # Add the 'severity' column based on the mapping
    # issue_log.add_severity_column(severity_csv_path)
    issue_log.save(os.path.join(issue_dir, resource + ".csv"))
    column_field_log.save(os.path.join(column_field_dir, resource + ".csv"))
    dataset_resource_log.save(os.path.join(dataset_resource_dir, resource + ".csv"))


def resource_from_path(path):
    return Path(path).stem


def default_output_path(command, input_path):
    directory = "" if command in ["harmonised", "transformed"] else "var/"
    return f"{directory}{command}/{resource_from_path(input_path)}.csv"


def assign_entries(resource_path, dataset, organisation, pipeline_dir, specification):
    """
    assuming that the endpoint is new (strictly it doesn't have to be) then we neeed to assign new entity numbers
    """

    # define log
    lookup_path = os.path.join(pipeline_dir, "lookup.csv")
    save_resource_unidentified_lookups(
        resource_path,
        dataset,
        [organisation],
        pipeline_dir=pipeline_dir,
        specification=specification,
    )
    unassigned_entries = []
    with open("./var/cache/unassigned-entries.csv") as f:
        dictreader = csv.DictReader(f)
        for row in dictreader:
            if row["reference"] == "":
                logger.info("The 'reference' column is empty")
            else:
                unassigned_entries.append(row)
    standardise_lookups(lookup_path)
    # if unassigned_entries is not None
    if len(unassigned_entries) > 0:
        add_unnassigned_to_lookups(
            unassigned_entries, lookup_path, dataset, specification
        )


def dataset_dump_flattened(csv_path, flattened_dir, specification, dataset):
    if isinstance(csv_path, str):
        path = Path(csv_path)
        dataset_name = path.stem
    elif isinstance(csv_path, Path):
        dataset_name = csv_path.stem
    else:
        # logging.error(f"Can't extract datapackage name from {csv_path}")
        sys.exit(-1)

    flattened_csv_path = os.path.join(flattened_dir, dataset, f"{dataset_name}.csv")
    with open(csv_path, "r") as read_file, open(flattened_csv_path, "w+") as write_file:
        reader = csv.DictReader(read_file)

        spec_field_names = [
            field
            for field in itertools.chain(
                *[
                    specification.current_fieldnames(schema)
                    for schema in specification.dataset_schema[dataset]
                ]
            )
        ]
        reader_fieldnames = [
            field.replace("_", "-")
            for field in list(reader.fieldnames)
            if field != "json"
        ]

        flattened_field_names = set(spec_field_names).difference(set(reader_fieldnames))
        # Make sure we put flattened fieldnames last
        field_names = reader_fieldnames + sorted(list(flattened_field_names))

        writer = csv.DictWriter(write_file, fieldnames=field_names)
        writer.writeheader()
        entities = []
        for row in reader:
            row.pop("geojson", None)
            row = OrderedDict(row)
            json_string = row.pop("json") or "{}"
            row.update(json.loads(json_string))
            kebab_case_row = dict(
                [(key.replace("_", "-"), val) for key, val in row.items()]
            )
            writer.writerow(kebab_case_row)
            entities.append(kebab_case_row)
