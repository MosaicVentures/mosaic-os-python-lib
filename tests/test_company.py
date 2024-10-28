import pytest
from google.cloud.datastore import Client, Entity, Key  # noqa: F401
from gql.transport.exceptions import TransportQueryError
from pytest_mock import MockerFixture

from mosaic_os.company import (
    create_company_master_id,
    get_all_company_details,
    lookup_company_master_id_by_domain,
)
from mosaic_os.models import Company

HARMONIC_RETURN_VALUE = {
    "enrichCompanyByIdentifiers": {
        "companyFound": True,
        "company": {
            "name": "Test",
            "id": 1,
            "website": {"domain": "test.com"},
            "watchlists": [{"name": "test", "id": 1}],
        },
    }
}

AFFINITY_SEARCH_RETURN_VALUE = [
    {
        "id": 64779194,
        "name": "Test",
        "domain": "test.com",
        "domains": ["test.com"],
        "global": True,
    }
]

AFFINITY_COMPANY_DETAILS_RETURN_VALUE = {
    "id": 64779194,
    "name": "Test",
    "domain": "test.com",
    "domains": ["test.com"],
    "global": True,
    "person_ids": [
        89734,
        117270,
        138123,
        274492,
        304848,
    ],
    "opportunity_ids": [
        4,
        11,
    ],
    "list_entries": [
        {
            "id": 389,
            "list_id": 13926,
            "creator_id": 38603,
            "entity_id": 64779194,
            "created_at": "2015-12-11T02:26:56.537-08:00",
        },
        {
            "id": 390,
            "list_id": 13926,
            "creator_id": 38603,
            "entity_id": 64779194,
            "created_at": "2015-12-12T02:26:56.537-08:00",
        },
    ],
}

AFFINITY_COMPANY_DETAILS_WITHOUT_LP_ENTRY_RETURN_VALUE = {
    "id": 64779194,
    "name": "Test",
    "domain": "test.com",
    "domains": ["test.com"],
    "global": True,
    "person_ids": [
        89734,
        117270,
        138123,
        274492,
        304848,
    ],
    "opportunity_ids": [
        4,
        11,
    ],
    "list_entries": [],
}

AFFINITY_COMPANY_FIELD_VALUES_RETURN_VALUE = [
    {
        "id": 2634897436,
        "field_id": 387543,
        "list_entry_id": None,
        "entity_type": 0,
        "value_type": 2,
        "entity_id": 64779194,
        "created_at": "2022-10-04T08:54:24.694-04:00",
        "updated_at": None,
        "value": "ON",
    },
    {
        "id": 2634897437,
        "field_id": 23986439,
        "list_entry_id": 390,
        "entity_type": 0,
        "value_type": 2,
        "entity_id": 64779194,
        "created_at": "2022-10-04T08:54:24.694-04:00",
        "updated_at": None,
        "value": "Track",
    },
    {
        "id": 2634897438,
        "field_id": 28964932,
        "list_entry_id": 390,
        "entity_type": 0,
        "value_type": 2,
        "entity_id": 64779194,
        "created_at": "2022-10-04T08:54:24.694-04:00",
        "updated_at": None,
        "value": "High",
    },
    {
        "id": 2634897438,
        "field_id": 396430,
        "list_entry_id": 390,
        "entity_type": 0,
        "value_type": 2,
        "entity_id": 64779194,
        "created_at": "2022-10-04T08:54:24.694-04:00",
        "updated_at": None,
        "value": "somebody",
    },
]

mock_affinity_config = {
    "lp_list_id": 13926,
    "lp_status_field_id": 23986439,
    "lp_priority_field_id": 28964932,
    "lp_owner_field_id": 396430,
    "ec_flag_field_id": 387543,
}


# This tests the case where the company is found in the SP but not in the CRM
@pytest.mark.asyncio
async def test_get_all_company_details_no_affinity_match(
    mocker: MockerFixture, tests_setup_and_teardown
):
    mocker.patch(
        "mosaic_os.sourcing_platform.HarmonicGql.query",
        return_value=HARMONIC_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.search_company_by_name_and_domains",
        return_value=[],
    )

    company_details = await get_all_company_details(
        "test.com", mock_affinity_config
    )
    assert company_details["crm"] is None
    assert company_details["sourcing_platform"] is not None
    assert company_details["sourcing_platform"]["name"] == "Test"
    assert (
        company_details["sourcing_platform"]["website"]["domain"] == "test.com"
    )
    assert (
        company_details["sourcing_platform"]["watchlists"][0]["name"] == "test"
    )


# This tests the case where the company is found in the CRM and in the SP
@pytest.mark.asyncio
async def test_get_all_company_details_sp_and_crm_match(
    mocker: MockerFixture, tests_setup_and_teardown
):
    mocker.patch(
        "mosaic_os.sourcing_platform.HarmonicGql.query",
        return_value=HARMONIC_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.search_company_by_name_and_domains",
        return_value=AFFINITY_SEARCH_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.get_company_details",
        return_value=AFFINITY_COMPANY_DETAILS_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.get_field_values",
        return_value=AFFINITY_COMPANY_FIELD_VALUES_RETURN_VALUE,
    )

    company_details = await get_all_company_details(
        "test.com", mock_affinity_config
    )

    assert company_details["crm"] is not None
    assert company_details["sourcing_platform"] is not None
    assert company_details["crm"]["company_id"] == 64779194
    assert company_details["crm"]["company_name"] == "Test"
    assert company_details["crm"]["domain"] == "test.com"
    assert isinstance(company_details["crm"]["ec_flag"], dict)
    assert (
        company_details["crm"]["last_live_pipeline_list_entry"]["entry_id"]
        == 390
    )
    assert isinstance(
        company_details["crm"]["last_live_pipeline_list_entry"]["status"], dict
    )
    assert isinstance(
        company_details["crm"]["last_live_pipeline_list_entry"]["owner"], dict
    )
    assert isinstance(
        company_details["crm"]["last_live_pipeline_list_entry"]["priority"],
        dict,
    )


# This tests the case where the company is found in the CRM but not in the SP
@pytest.mark.asyncio
async def test_get_all_company_details_no_sp_match(
    mocker: MockerFixture, tests_setup_and_teardown
):
    harmonic_company_not_found_error = [
        {
            "message": "404: Not Found",
            "locations": [{"line": 2, "column": 3}],
            "path": ["enrichCompanyByIdentifiers"],
            "extensions": {
                "code": "INTERNAL_SERVER_ERROR",
                "response": {
                    "url": "http://midtier/companies?enrich_missing_company=true&hide_non_surfaceable_company=false&website_url=meetcopilot.app",  # noqa: E501
                    "status": 404,
                    "statusText": "Not Found",
                    "body": {
                        "detail": {
                            "message": "Company not found; scheduled for enrichment, check back in a few hours. Use /enrichment_status endpoint to get status of the enrichment.",  # noqa: E501
                            "enrichment_urn": "urn:harmonic:enrichment:300e63e6-7d23-4e98-9e3d-5a56b1e233e3",
                        }
                    },
                },
            },
        }
    ]
    mocker.patch(
        "mosaic_os.sourcing_platform.HarmonicGql.query",
        side_effect=TransportQueryError(
            msg="404: Not Found", errors=harmonic_company_not_found_error
        ),
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.search_company_by_name_and_domains",
        return_value=AFFINITY_SEARCH_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.get_company_details",
        return_value=AFFINITY_COMPANY_DETAILS_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.get_field_values",
        return_value=AFFINITY_COMPANY_FIELD_VALUES_RETURN_VALUE,
    )

    company_details = await get_all_company_details(
        "test.com", mock_affinity_config
    )

    assert company_details["crm"] is not None
    assert (
        company_details["sourcing_platform"]["enrichment_urn"]
        == "urn:harmonic:enrichment:300e63e6-7d23-4e98-9e3d-5a56b1e233e3"
    )


@pytest.mark.asyncio
async def test_get_all_company_details_no_sp_and_no_enrichment_urn(
    mocker: MockerFixture, tests_setup_and_teardown
):
    harmonic_company_not_found_error = [
        {
            "message": "404: Not Found",
            "locations": [{"line": 2, "column": 3}],
            "path": ["enrichCompanyByIdentifiers"],
            "extensions": {
                "code": "INTERNAL_SERVER_ERROR",
                "response": {
                    "url": "http://midtier/companies?enrich_missing_company=true&hide_non_surfaceable_company=false&website_url=meetcopilot.app",  # noqa: E501
                    "status": 404,
                    "statusText": "Not Found",
                    "body": {"detail": "Company not found!"},
                },
            },
        }
    ]
    mocker.patch(
        "mosaic_os.sourcing_platform.HarmonicGql.query",
        side_effect=TransportQueryError(
            msg="404: Not Found", errors=harmonic_company_not_found_error
        ),
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.search_company_by_name_and_domains",
        return_value=AFFINITY_SEARCH_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.get_company_details",
        return_value=AFFINITY_COMPANY_DETAILS_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.get_field_values",
        return_value=AFFINITY_COMPANY_FIELD_VALUES_RETURN_VALUE,
    )

    company_details = await get_all_company_details(
        "test.com", mock_affinity_config
    )

    assert company_details["crm"] is not None
    assert company_details["sourcing_platform"]["enrichment_urn"] is None


@pytest.mark.asyncio
async def test_get_all_company_details_no_sp_status_422(
    mocker: MockerFixture, tests_setup_and_teardown
):
    harmonic_company_not_found_error = [
        {
            "message": "422: Unprocessable Entity",
            "locations": [{"line": 2, "column": 3}],
            "path": ["enrichCompanyByIdentifiers"],
            "extensions": {
                "code": "INTERNAL_SERVER_ERROR",
                "response": {
                    "url": "http://midtier/companies?enrich_missing_company=true&hide_non_surfaceable_company=false&website_url=meetcopilot.app",  # noqa: E501
                    "status": 422,
                    "statusText": "Not Found",
                    "body": {"detail": "Company not found!"},
                },
            },
        }
    ]
    mocker.patch(
        "mosaic_os.sourcing_platform.HarmonicGql.query",
        side_effect=TransportQueryError(
            msg="404: Not Found", errors=harmonic_company_not_found_error
        ),
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.search_company_by_name_and_domains",
        return_value=AFFINITY_SEARCH_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.get_company_details",
        return_value=AFFINITY_COMPANY_DETAILS_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.get_field_values",
        return_value=AFFINITY_COMPANY_FIELD_VALUES_RETURN_VALUE,
    )

    company_details = await get_all_company_details(
        "test.com", mock_affinity_config
    )

    assert company_details["crm"] is not None
    assert company_details["sourcing_platform"]["enrichment_urn"] is None


@pytest.mark.asyncio
async def test_company_found_in_crm_but_no_live_pipeline_entry_found(
    mocker: MockerFixture, tests_setup_and_teardown
):
    mocker.patch(
        "mosaic_os.sourcing_platform.HarmonicGql.query",
        return_value=HARMONIC_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.search_company_by_name_and_domains",
        return_value=AFFINITY_SEARCH_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.get_company_details",
        return_value=AFFINITY_COMPANY_DETAILS_WITHOUT_LP_ENTRY_RETURN_VALUE,
    )
    mocker.patch(
        "mosaic_os.crm.AffinityApi.get_field_values",
        return_value=AFFINITY_COMPANY_FIELD_VALUES_RETURN_VALUE,
    )

    company_details = await get_all_company_details(
        "test.com", mock_affinity_config
    )

    assert company_details["crm"] is not None
    assert company_details["crm"]["company_id"] == 64779194
    assert company_details["crm"]["company_name"] == "Test"
    assert company_details["crm"]["domain"] == "test.com"
    assert isinstance(company_details["crm"]["ec_flag"], dict)
    assert company_details["crm"]["last_live_pipeline_list_entry"] is None


def test_lookup_company_master_id_by_domain_no_match(
    mocker: MockerFixture, tests_setup_and_teardown
):
    client = mocker.patch("tests.test_company.Client")

    company = lookup_company_master_id_by_domain("test.com", client)
    assert company is None


def test_lookup_company_master_id_by_domain_match(
    mocker: MockerFixture, tests_setup_and_teardown
):
    client = mocker.patch("tests.test_company.Client")
    client.key.return_value = Key("Company", 123, project="test-project")
    company_entity = Entity(key=client.key("Company", 123))
    company_entity.update(
        Company(
            id=123,
            name="Test",
            primary_domain="test.com",
            domains=["test.com"],
            sp_id="12345",
            crm_id="12",
        ).model_dump(exclude={"id"})
    )
    existing_company_record = [company_entity]
    client.query.return_value.fetch.return_value = existing_company_record

    company = lookup_company_master_id_by_domain("test.com", client)
    assert company.id == 123
    assert company.domains[0] == "test.com"
    assert company.sp_id == "12345"
    assert company.crm_id == "12"


def test_create_company_master_id(
    mocker: MockerFixture, tests_setup_and_teardown
):
    client = mocker.patch("tests.test_company.Client")
    mocked_key = Key("Company", 123, project="test-project")
    client.allocate_ids.return_value = [mocked_key]
    client.entity.return_value = Entity(key=mocked_key)
    client.put.return_value = None

    company = Company(
        id=None,
        name="Test",
        primary_domain="test.com",
        domains=["test.com"],
        sp_id="12345",
        crm_id="12",
    )
    company = create_company_master_id(company, client)

    assert company.id == 123
    assert company.domains[0] == "test.com"
    assert company.sp_id == "12345"
    assert company.crm_id == "12"
    assert company.created_at is not None
    assert company.updated_at is None
