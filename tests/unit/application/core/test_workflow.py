from application.core.workflow import updateColumnFieldLog


def test_updateColumnFieldLog():
    column_field_log = [
        {
            "dataset": "conservation-area",
            "column": "documentation-url",
            "field": "documentation-url",
        },
        {
            "dataset": "conservation-area",
            "column": "name",
            "field": "name",
        },
    ]

    required_fields = ["reference", "geometry"]

    assert len(column_field_log) == 2
    updateColumnFieldLog(column_field_log, required_fields)

    assert len(column_field_log) == 4  # Two new entries added
    assert any(
        entry["field"] == "reference" and entry["missing"] for entry in column_field_log
    )
    assert any(
        entry["field"] == "geometry" and entry["missing"] for entry in column_field_log
    )
    assert any(
        entry["field"] == "documentation-url" and not entry["missing"]
        for entry in column_field_log
    )
    assert any(
        entry["field"] == "name" and not entry["missing"] for entry in column_field_log
    )


def test_updateColumnFieldLog_no_missing_fields():
    column_field_log = [
        {
            "dataset": "conservation-area",
            "column": "documentation-url",
            "field": "documentation-url",
        },
        {"dataset": "conservation-area", "column": "geometry", "field": "geometry"},
        {"dataset": "conservation-area", "column": "reference", "field": "reference"},
    ]
    required_fields = ["reference", "geometry"]
    updateColumnFieldLog(column_field_log, required_fields)
    assert len(column_field_log) == 3
    assert any(
        entry["field"] == "geometry" and not entry["missing"]
        for entry in column_field_log
    )
    assert any(
        entry["field"] == "reference" and not entry["missing"]
        for entry in column_field_log
    )
