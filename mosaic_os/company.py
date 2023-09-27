from os import environ

from gql.transport.exceptions import TransportQueryError
from tldextract import extract

from mosaic_os.constants import affinity_config
from mosaic_os.crm import AfinityApi
from mosaic_os.sourcing_platform import HarmonicGql


async def get_all_company_details(domain: str) -> dict:
    """Get company details from CRM and Sourcing Platform

    Args:
        domain (str): Domain name of company

    Returns:
        dict: Dictionary with keys `crm` and `sourcing_platform` containing company details
    """
    harmonic_client = HarmonicGql()
    affinity_client = AfinityApi()
    affinity_env_config = affinity_config[environ.get("ENVIRONMENT", "prod")]

    domain_clean = extract(domain).registered_domain

    # get harmonic company information
    query = """
    mutation ($identifiers: CompanyEnrichmentIdentifiersInput!) {
        enrichCompanyByIdentifiers(identifiers: $identifiers) {
            companyFound
            company {
                name
                id
                website {
                    domain
                }
                watchlists {
                    name
                    id
                }
            }
        }
    }"""

    try:
        harmonic_company_details = await harmonic_client.query(
            query=query, variables={"identifiers": {"websiteUrl": domain_clean}}
        )
        harmonic_company = harmonic_company_details["enrichCompanyByIdentifiers"]["company"]
        harmonic_company.update({"enrichment_urn": None})
    except TransportQueryError as e:
        for error in e.errors:
            if error.get("extensions", {}).get("response", {}).get("status", 400) == 404:
                harmonic_company = {
                    "name": None,
                    "id": None,
                    "website": None,
                    "watchlists": [],
                    "enrichment_urn": error.get("extensions", {})
                    .get("response", {})
                    .get("body", {})
                    .get("detail", {})
                    .get("enrichment_urn", None),
                }
                break

    # combine clean domain and harmonic domain to increase likelihood of matching in Affinity
    known_domains = [domain_clean]
    if harmonic_company["website"] is not None:
        known_domains.append(harmonic_company["website"]["domain"])
    deduped_known_domains = list(set(known_domains))

    affinity_results = await affinity_client.search_company_by_name_and_domains(
        name=harmonic_company["name"], domains=deduped_known_domains
    )

    # find id of matching company
    affinity_entity_id = next(
        (
            int(company["id"])
            for company in affinity_results
            if set(deduped_known_domains).issubset(set(company["domains"]))
        ),
        None,
    )

    if affinity_entity_id is None:
        return {"crm": None, "sourcing_platform": harmonic_company}

    # get company id of match and retrieve company information by id from affinity
    affinity_company_details = await affinity_client.get_company_details(affinity_entity_id)

    # loop through list entries, get live pipeline entries only, and pick most recent one
    lp_entries = affinity_client.filter_entries_by_list_id(
        list_entries=affinity_company_details["list_entries"], list_id=affinity_env_config["lp_list_id"]
    )
    last_entry = max(lp_entries, key=lambda entry: entry["created_at"])

    # get all field values for company (includes list entries)
    all_company_field_values = await affinity_client.get_organization_field_values(affinity_entity_id)

    last_lp_list_entry_field_values = list(
        filter(
            lambda field_value: (field_value["list_entry_id"] == last_entry["id"])
            and (field_value["field_id"] in affinity_env_config["lp_fields"]),
            all_company_field_values,
        )
    )

    company_field_values = list(
        filter(
            lambda field_value: (field_value["list_entry_id"] is None)
            and (field_value["field_id"] in affinity_env_config["company_fields"]),
            all_company_field_values,
        )
    )

    # create affinity return
    # issue with field values currently returned as lists as throws error if indexing empty list (in case
    # field not populated)
    affinity_return = {
        "company_id": affinity_entity_id,
        "company_name": affinity_company_details["name"],
        "domain": affinity_company_details["domain"],
        "ec_flag": affinity_client.field_value_by_field_id(
            field_values=company_field_values, field_id=affinity_env_config["company_field_ec_flag"]
        ),
        "last_live_pipeline_list_entry": {
            "entry_id": last_entry["id"],
            "status": affinity_client.field_value_by_field_id(
                field_values=last_lp_list_entry_field_values, field_id=affinity_env_config["lp_field_status"]
            ),
            "priority": affinity_client.field_value_by_field_id(
                field_values=last_lp_list_entry_field_values, field_id=affinity_env_config["lp_field_priority"]
            ),
            "owner": affinity_client.field_value_by_field_id(
                field_values=last_lp_list_entry_field_values, field_id=affinity_env_config["lp_field_owner"]
            ),
        },
    }

    return {"crm": affinity_return, "sourcing_platform": harmonic_company}
