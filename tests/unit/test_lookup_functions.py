import csv
from application.core.lookup_functions import add_unnassigned_to_lookups


def test_add_unnassigned_to_lookups():
    lookups_file = "tests/data/csvs/lookup.csv"
    with open(lookups_file, "r") as f:
        reader = csv.DictReader(f)
        lookup_data = list(reader)
    initial_lookup_length = len(lookup_data)
    unassigned_entries = [
        {
            "organisation": "local-authority-eng:CAT",
            "prefix": "conservation-area",
            "reference": "4",
        },
        {
            "organisation": "local-authority-eng:CAT",
            "prefix": "conservation-area",
            "reference": "6",
        },
    ]
    dataset = "conservation-area"
    specification = "specification"

    # Pass the path of the existing lookup file to the function
    add_unnassigned_to_lookups(unassigned_entries, lookups_file, dataset, specification)

    # Check if the lookup file has the expected content after the update
    with open(lookups_file, "r") as f:
        reader = csv.DictReader(f)
        lookup_data_appended = list(reader)

    expected_length = initial_lookup_length + len(unassigned_entries)
    assert len(lookup_data_appended) == expected_length

    for i, entry in enumerate(unassigned_entries):
        index = initial_lookup_length + i
        assert lookup_data_appended[index]["organisation"] == entry["organisation"]
        assert lookup_data_appended[index]["prefix"] == entry["prefix"]
        assert lookup_data_appended[index]["reference"] == entry["reference"]
        # Convert the last entity in the lookup file to an integer, add 1, and compare
        last_entity = int(lookup_data[-1]["entity"])
        assert int(lookup_data_appended[index]["entity"]) == last_entity + i + 1


def test_add_unnassigned_to_lookups_empty():
    lookups_file = "tests/data/csvs/lookup.csv"
    with open(lookups_file, "r") as f:
        reader = csv.DictReader(f)
        lookup_data = list(reader)
    initial_lookup_length = len(lookup_data)
    unassigned_entries = []
    dataset = "conservation-area"
    specification = "specification"

    # Pass the path of the existing lookup file to the function
    add_unnassigned_to_lookups(unassigned_entries, lookups_file, dataset, specification)

    # Check if the lookup file has the expected content after the update
    with open(lookups_file, "r") as f:
        reader = csv.DictReader(f)
        lookup_data_appended = list(reader)

    expected_length = initial_lookup_length + len(unassigned_entries)
    assert len(lookup_data_appended) == expected_length


# TO BE ADDED WHEN EMPTY FILE LOOKUP CASE IS HANDLED
# def test_add_unnassigned_to_lookups_with_empty_file():
#     lookups_file = "tests/data/csvs/lookup_empty.csv"
#     with open(lookups_file, "r") as f:
#         reader = csv.DictReader(f)
#         lookup_data = list(reader)
#     initial_lookup_length = len(lookup_data)
#     unassigned_entries = [
#         {"organisation": "local-authority-eng:CAT", "prefix": "conservation-area", "reference": "4"},
#         {"organisation": "local-authority-eng:CAT", "prefix": "conservation-area", "reference": "6"},
#     ]
#     dataset = "conservation-area"
#     specification = "specification"

#     # Pass the path of the existing lookup file to the function
#     add_unnassigned_to_lookups(unassigned_entries, lookups_file, dataset, specification)

#     # Check if the lookup file has the expected content after the update
#     with open(lookups_file, "r") as f:
#         reader = csv.DictReader(f)
#         lookup_data_appended = list(reader)

#     expected_length = initial_lookup_length + len(unassigned_entries)
#     assert len(lookup_data_appended) == expected_length
