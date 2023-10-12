import pytest

from mosaic_os.crm import AffinityApi


# This tests if AffinitApi initialises with an environment variable successfully
def test_affinity_api_initialises_with_env_var_successfully(tests_setup_and_teardown):
    AffinityApi()
    assert True


# This tests if AffinitApi initialises with an argument successfully
def test_affinity_api_initialises_with_arg_successfully():
    AffinityApi("test")
    assert True


# This tests if AffinityApi raises an error when no key is provided as an argument and no environment variable is set
def test_affinity_api_with_no_key_raises_error():
    with pytest.raises(ValueError):
        AffinityApi()


@pytest.mark.asyncio
async def test_affinity_api_get_field_values_raises_error_no_param():
    with pytest.raises(ValueError) as excinfo:
        affinity_client = AffinityApi("test")
        await affinity_client.get_field_values(param={})

    assert excinfo.type is ValueError
    assert (
        excinfo.value.args[0]
        == "Only one of the following keys should be specified: `organization_id`, `list_entry_id`, `person_id`"
    )


@pytest.mark.asyncio
async def test_affinity_api_get_field_values_raises_error_wrong_param():
    with pytest.raises(ValueError) as excinfo:
        affinity_client = AffinityApi("test")
        await affinity_client.get_field_values(param={"some_id": 1})

    assert excinfo.type is ValueError
    assert (
        excinfo.value.args[0]
        == "Only one of the following keys should be specified: `organization_id`, `list_entry_id`, `person_id`"
    )


# Test if _remove_duplicates removes duplicate dicts in a list
def test_affinity_remove_duplicates():
    list_with_duplicate_dicts = [{"id": 1}, {"id": 1}, {"id": 2}]

    assert len(AffinityApi._remove_duplicates(list_with_duplicate_dicts)) == 2


# Tests if filter_entries_by_list_id filters entries by list id
def test_affinity_filter_entries_by_list_id():
    list_entries = [
        {"id": 1, "list_id": 1},
        {"id": 2, "list_id": 2},
        {"id": 3, "list_id": 1},
        {"id": 4, "list_id": 2},
    ]

    assert len(AffinityApi.filter_entries_by_list_id(list_entries, 1)) == 2
    assert len(AffinityApi.filter_entries_by_list_id(list_entries, 2)) == 2
    assert len(AffinityApi.filter_entries_by_list_id(list_entries, 3)) == 0


# Tests if field_value_by_field_id returns the correct field value dict
def test_affinity_field_value_by_field_id():
    field_values = [
        {"id": 1, "field_id": 1},
        {"id": 2, "field_id": 2},
        {"id": 3, "field_id": 3},
        {"id": 4, "field_id": 4},
    ]

    assert AffinityApi.field_value_by_field_id(field_values, 1) == {"id": 1, "field_id": 1}
    assert AffinityApi.field_value_by_field_id(field_values, 2) == {"id": 2, "field_id": 2}
