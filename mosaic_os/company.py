from typing import Any

from google.cloud.datastore import Client
from google.cloud.datastore.query import And, PropertyFilter
from gql.transport.exceptions import TransportQueryError
from tldextract import extract

from mosaic_os.crm import AffinityApi
from mosaic_os.models import Company
from mosaic_os.sourcing_platform import HarmonicGql


async def get_all_company_details(domain: str, affinity_config: dict[str, Any]) -> dict:
    """Get company details from CRM and Sourcing Platform

    Args:
        domain (str): Domain name of company

    Returns:
        dict: Dictionary with keys `crm` and `sourcing_platform` containing company details
    """
    harmonic_client = HarmonicGql()
    affinity_client = AffinityApi()

    live_pipeline_fields = [
        affinity_config["lp_status_field_id"],
        affinity_config["lp_priority_field_id"],
        affinity_config["lp_owner_field_id"],
    ]

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
                socials {
                    pitchbook {
                        url
                    }
                    crunchbase {
                        url
                    }
                    linkedin {
                        url
                    }
                    twitter {
                        url
                    }
                    stackoverflow {
                        url
                    }
                    angellist {
                        url
                    }
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
                response_detail = error.get("extensions", {}).get("response", {}).get("body", {}).get("detail", {})
                if isinstance(response_detail, dict):
                    enrichment_urn = response_detail.get("enrichment_urn", None)
                else:
                    enrichment_urn = None
                harmonic_company = {
                    "name": None,
                    "id": None,
                    "website": None,
                    "watchlists": [],
                    "socials": {},
                    "enrichment_urn": enrichment_urn,
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
    all_company_field_values = await affinity_client.get_field_values(param={"organization_id": affinity_entity_id})

    # loop through list entries, get live pipeline entries only, and pick most recent one
    lp_entries = affinity_client.filter_entries_by_list_id(
        list_entries=affinity_company_details["list_entries"], list_id=affinity_config["lp_list_id"]
    )

    if len(lp_entries):
        last_entry = max(lp_entries, key=lambda entry: entry["created_at"])
        last_lp_list_entry_field_values = list(
            filter(
                lambda field_value: (field_value["list_entry_id"] == last_entry["id"])
                and (field_value["field_id"] in live_pipeline_fields),
                all_company_field_values,
            )
        )
        last_live_pipeline_list_entry = {
            "entry_id": last_entry["id"],
            "status": affinity_client.field_value_by_field_id(
                field_values=last_lp_list_entry_field_values, field_id=affinity_config["lp_status_field_id"]
            ),
            "priority": affinity_client.field_value_by_field_id(
                field_values=last_lp_list_entry_field_values, field_id=affinity_config["lp_priority_field_id"]
            ),
            "owner": affinity_client.field_value_by_field_id(
                field_values=last_lp_list_entry_field_values, field_id=affinity_config["lp_owner_field_id"]
            ),
        }
    else:
        last_live_pipeline_list_entry = None

    # get all field values for company (includes list entries)

    company_field_values = list(
        filter(
            lambda field_value: (field_value["list_entry_id"] is None)
            and (field_value["field_id"] == affinity_config["ec_flag_field_id"]),
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
        "domains": affinity_company_details["domains"],
        "ec_flag": affinity_client.field_value_by_field_id(
            field_values=company_field_values, field_id=affinity_config["ec_flag_field_id"]
        ),
        "last_live_pipeline_list_entry": last_live_pipeline_list_entry,
    }

    return {"crm": affinity_return, "sourcing_platform": harmonic_company}


def lookup_company_master_id_by_domain(domain: str, db_client: Client) -> Company | None:
    """Lookup company master id by domain

    Args:
        domain (str): Domain name of company
        db_client (Client): Datastore client

    Returns:
        Company: Company details
    """
    clean_domain = extract(domain).registered_domain
    query = db_client.query(kind="Company")
    query.add_filter(
        filter=And([PropertyFilter("primary_domain", "=", clean_domain), PropertyFilter("current", "=", True)])
    )
    results = list(query.fetch())
    if not len(results):
        return None

    return Company(id=results[0].key.id, **results[0])


def create_company_master_id(company: Company, db_client: Client) -> Company:
    """Create company master id

    Args:
        company (Company): Company details
        db_client (Client): Datastore client

    Returns:
        Company: Company details
    """
    partial_key = db_client.key("Company")
    allocated_keys = db_client.allocate_ids(partial_key, 1)
    company_entity = db_client.entity(key=allocated_keys[0])
    company.id = company_entity.key.id
    company_entity.update(company.model_dump(exclude={"id"}))
    db_client.put(company_entity)
    return company
