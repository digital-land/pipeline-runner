# from application.core.workflow import updateColumnFieldLog


# def test_getMissingColumns_no_missing_fields():
#     column_field_log = [
#         {
#             "dataset": "conservation-area",
#             "column": "documentation-url",
#             "field": "documentation-url",
#         },
#         {"dataset": "conservation-area", "column": "geometry", "field": "geometry"},
#         {"dataset": "conservation-area", "column": "reference", "field": "reference"},
#     ]
#     required_fields = ["reference", "geometry"]
#     assert updateColumnFieldLog(column_field_log, required_fields) == []


# def test_getMissingColumns_some_missing_fields():
#     column_field_log = [
#         {
#             "dataset": "conservation-area",
#             "column": "documentation-url",
#             "field": "documentation-url",
#         },
#         {"dataset": "conservation-area", "column": "geometry", "field": "geometry"},
#     ]
#     required_fields = ["reference", "geometry", "other_field"]
#     assert updateColumnFieldLog(column_field_log, required_fields) == [
#         "reference",
#         "other_field",
#     ]


# def test_getMissingColumns_all_missing_fields():
#     column_field_log = []
#     required_fields = ["reference", "geometry"]
#     assert updateColumnFieldLog(column_field_log, required_fields) == [
#         "reference",
#         "geometry",
#     ]
