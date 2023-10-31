import os
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


from pathlib import Path


def run_endpoint_workflow(
    dataset,
    organisation,
    data_dir,
    issue_dir,
    column_field_dir,
    transformed_dir,
    additional_col_mappings,
    additional_concats,
):
    # Create directories if they don't exist
    for directory in [data_dir, issue_dir, column_field_dir, transformed_dir]:
        os.makedirs(directory, exist_ok=True)

    # define variables for Pipeline
    pipeline_dir = os.path.join("pipeline/")
    pipeline = Pipeline(pipeline_dir, dataset)
    specification_dir = os.path.join("specification/")
    specification = Specification(specification_dir)

    pipeline_run(
        dataset=dataset,
        pipeline=pipeline,
        specification=specification,
        input_path=os.path.join(data_dir, "resource", "conservation-area.csv"),
        output_path=os.path.join(
            "transformed", dataset + ".csv"
        ),  # Can we get flattened directly somehow?
        issue_dir=os.path.join("issue"),
        column_field_dir=os.path.join("column-field"),
        # dataset_resource_dir=os.path.join('var','dataset-resource',dataset),  #Required????
        organisation_path=os.path.join("var", "cache", "organisation.csv"),
        save_harmonised=False,
        organisations=[organisation],
        custom_temp_dir=os.path.join(data_dir, "var", "cache"),
    )


def pipeline_run(
    dataset,
    pipeline,
    specification,
    input_path,
    output_path,
    collection_dir="./collection",  # TBD: remove, replaced by endpoints, organisations and entry_date
    null_path=None,  # TBD: remove this
    issue_dir=None,
    organisation_path=None,
    save_harmonised=False,
    column_field_dir=None,
    dataset_resource_dir=None,
    custom_temp_dir=None,  # TBD: rename to "tmpdir"
    endpoints=[],
    organisations=[],
    entry_date="",
):
    resource = resource_from_path(input_path)
    print("resource path is::: ", resource)
    dataset = dataset
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

    # resource specific default values
    if len(organisations) == 1:
        default_values["organisation"] = organisations[0]

    run_pipeline(
        ConvertPhase(
            path=input_path,
            dataset_resource_log=dataset_resource_log,
            custom_temp_dir=custom_temp_dir,
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

    issue_log.save(os.path.join(issue_dir, resource + ".csv"))
    column_field_log.save(os.path.join(column_field_dir, resource + ".csv"))
    # dataset_resource_log.save(os.path.join(dataset_resource_dir, resource + ".csv"))


def resource_from_path(path):
    return Path(path).stem


def default_output_path(command, input_path):
    directory = "" if command in ["harmonised", "transformed"] else "var/"
    return f"{directory}{command}/{resource_from_path(input_path)}.csv"
