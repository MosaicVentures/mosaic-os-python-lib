import pytest
from gql.transport.exceptions import TransportQueryError
from pytest_mock import MockerFixture

from mosaic_os.company import get_all_company_details
from mosaic_os.constants import affinity_config

config = affinity_config["prod"]

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
    {"id": 64779194, "name": "Test", "domain": "test.com", "domains": ["test.com"], "global": True}
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
            "list_id": config["lp_list_id"],
            "creator_id": 38603,
            "entity_id": 64779194,
            "created_at": "2015-12-11T02:26:56.537-08:00",
        },
        {
            "id": 390,
            "list_id": config["lp_list_id"],
            "creator_id": 38603,
            "entity_id": 64779194,
            "created_at": "2015-12-12T02:26:56.537-08:00",
        },
    ],
}

AFFINITY_COMPANY_FIELD_VALUES_RETURN_VALUE = [
    {
        "id": 2634897436,
        "field_id": config["company_field_ec_flag"],
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
        "field_id": config["lp_field_status"],
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
        "field_id": config["lp_field_priority"],
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
        "field_id": config["lp_field_owner"],
        "list_entry_id": 390,
        "entity_type": 0,
        "value_type": 2,
        "entity_id": 64779194,
        "created_at": "2022-10-04T08:54:24.694-04:00",
        "updated_at": None,
        "value": "somebody",
    },
]


# This tests the case where the company is found in the SP but not in the CRM
@pytest.mark.asyncio
async def test_get_all_company_details_no_affinity_match(mocker: MockerFixture, tests_setup_and_teardown):
    mocker.patch("mosaic_os.sourcing_platform.HarmonicGql.query", return_value=HARMONIC_RETURN_VALUE)
    mocker.patch("mosaic_os.crm.AfinityApi.search_company_by_name_and_domains", return_value=[])

    company_details = await get_all_company_details("test.com")
    assert company_details["crm"] is None
    assert company_details["sourcing_platform"] is not None
    assert company_details["sourcing_platform"]["name"] == "Test"
    assert company_details["sourcing_platform"]["website"]["domain"] == "test.com"
    assert company_details["sourcing_platform"]["watchlists"][0]["name"] == "test"


# This tests the case where the company is found in the CRM and in the SP
@pytest.mark.asyncio
async def test_get_all_company_details_sp_and_crm_match(mocker: MockerFixture, tests_setup_and_teardown):
    mocker.patch("mosaic_os.sourcing_platform.HarmonicGql.query", return_value=HARMONIC_RETURN_VALUE)
    mocker.patch(
        "mosaic_os.crm.AfinityApi.search_company_by_name_and_domains", return_value=AFFINITY_SEARCH_RETURN_VALUE
    )
    mocker.patch("mosaic_os.crm.AfinityApi.get_company_details", return_value=AFFINITY_COMPANY_DETAILS_RETURN_VALUE)
    mocker.patch(
        "mosaic_os.crm.AfinityApi.get_organization_field_values",
        return_value=AFFINITY_COMPANY_FIELD_VALUES_RETURN_VALUE,
    )

    company_details = await get_all_company_details("test.com")

    assert company_details["crm"] is not None
    assert company_details["sourcing_platform"] is not None
    assert company_details["crm"]["company_id"] == 64779194
    assert company_details["crm"]["company_name"] == "Test"
    assert company_details["crm"]["domain"] == "test.com"
    assert isinstance(company_details["crm"]["ec_flag"], dict)
    assert company_details["crm"]["last_live_pipeline_list_entry"]["entry_id"] == 390
    assert isinstance(company_details["crm"]["last_live_pipeline_list_entry"]["status"], dict)
    assert isinstance(company_details["crm"]["last_live_pipeline_list_entry"]["owner"], dict)
    assert isinstance(company_details["crm"]["last_live_pipeline_list_entry"]["priority"], dict)


# This tests the case where the company is found in the CRM but not in the SP
@pytest.mark.asyncio
async def test_get_all_company_details_no_sp_match(mocker: MockerFixture, tests_setup_and_teardown):
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
        side_effect=TransportQueryError(msg="404: Not Found", errors=harmonic_company_not_found_error),
    )
    mocker.patch(
        "mosaic_os.crm.AfinityApi.search_company_by_name_and_domains", return_value=AFFINITY_SEARCH_RETURN_VALUE
    )
    mocker.patch("mosaic_os.crm.AfinityApi.get_company_details", return_value=AFFINITY_COMPANY_DETAILS_RETURN_VALUE)
    mocker.patch(
        "mosaic_os.crm.AfinityApi.get_organization_field_values",
        return_value=AFFINITY_COMPANY_FIELD_VALUES_RETURN_VALUE,
    )

    company_details = await get_all_company_details("test.com")

    assert company_details["crm"] is not None
    assert (
        company_details["sourcing_platform"]["enrichment_urn"]
        == "urn:harmonic:enrichment:300e63e6-7d23-4e98-9e3d-5a56b1e233e3"
    )
