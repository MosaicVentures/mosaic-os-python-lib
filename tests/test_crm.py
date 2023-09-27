import pytest

from mosaic_os.crm import AfinityApi


def test_affinity_api_initialises_with_env_var_successfully(tests_setup_and_teardown):
    AfinityApi()
    assert True


def test_affinity_api_initialises_with_arg_successfully():
    AfinityApi("test")
    assert True


def test_affinity_api_with_no_key_raises_error():
    with pytest.raises(ValueError):
        AfinityApi()


def test_affinity_remove_duplicates():
    list_with_duplicate_dicts = [{"id": 1}, {"id": 1}, {"id": 2}]

    assert len(AfinityApi._remove_duplicates(list_with_duplicate_dicts)) == 2


def test_affinity_filter_entries_by_list_id():
    list_entries = [
        {"id": 1, "list_id": 1},
        {"id": 2, "list_id": 2},
        {"id": 3, "list_id": 1},
        {"id": 4, "list_id": 2},
    ]

    assert len(AfinityApi.filter_entries_by_list_id(list_entries, 1)) == 2
    assert len(AfinityApi.filter_entries_by_list_id(list_entries, 2)) == 2
    assert len(AfinityApi.filter_entries_by_list_id(list_entries, 3)) == 0


def test_affinity_field_value_by_field_id():
    field_values = [
        {"id": 1, "field_id": 1},
        {"id": 2, "field_id": 2},
        {"id": 3, "field_id": 3},
        {"id": 4, "field_id": 4},
    ]

    assert AfinityApi.field_value_by_field_id(field_values, 1) == {"id": 1, "field_id": 1}
    assert AfinityApi.field_value_by_field_id(field_values, 2) == {"id": 2, "field_id": 2}
