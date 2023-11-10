import json
from os import environ

from httpx import AsyncClient

from mosaic_os.constants import AFFINITY_API_BASE_URL


class AffinityApi:
    """
    Affinity API Wrapper. See https://api-docs.affinity.co/ for more information

    Args:
        affinity_api_key (str, optional): API key for Affinity which can be set by passing through here or
        setting environment variable `AFFINITY_API_KEY`  Defaults to None.

    Raises:
        ValueError: If affinity_api_key is not set
    """

    def __init__(self, affinity_api_key: str = None):
        _affinity_api_key = environ.get("AFFINITY_API_KEY", affinity_api_key)

        if _affinity_api_key is None:
            raise ValueError("Affinity API key not found in environment variables or passed as argument")

        self.requests = AsyncClient(
            auth=("", _affinity_api_key), headers={"Content-Type": "application/json"}, base_url=AFFINITY_API_BASE_URL
        )

    # API methods

    # Company related API calls
    async def search_company(self, term: str) -> dict:
        """Search company by term in Affinity

        Args:
            term (str): Search term which can be name or comany domain name

        Returns:
            dict: Response with `organizations` key containing list of companies
        """
        response = await self.requests.get(f"/organizations?term={term}")
        response.raise_for_status()
        return response.json()

    async def create_company(self, name: str, domain: str) -> dict:
        """Create company in Affinity

        Args:
            name (str): Name of company
            domain (str): Domain name of company

        Returns:
            dict: Response with created company details
        """
        data = {"name": name, "domain": domain}
        response = await self.requests.post("/organizations", json=data)
        response.raise_for_status()
        return response.json()

    async def get_company_details(self, entity_id: int) -> dict:
        """Get company details by ID

        Args:
            entity_id (int): ID of company

        Returns:
            dict: Response with company details
        """
        response = await self.requests.get(
            f"/organizations/{entity_id}?with_opportunities=true&with_interaction_dates=true&with_interaction_persons=true"  # noqa: E501
        )
        response.raise_for_status()
        return response.json()

    # Person related API calls
    async def search_person(self, term: str) -> dict:
        """Search person by term in Affinity

        Args:
            term (str): Search term which can be name or email

        Returns:
            dict: Response with `persons` key containing list of persons
        """
        response = await self.requests.get(f"/persons?term={term}")
        response.raise_for_status()
        return response.json()

    async def get_person_details(self, entity_id: int) -> dict:
        """Get person details by ID

        Args:
            entity_id (int): ID of person

        Returns:
            dict: Response with person details
        """
        response = await self.requests.get(f"/persons/{entity_id}")  # noqa: E501
        response.raise_for_status()
        return response.json()

    # Field value related API calls
    async def get_field_values(self, param: dict) -> list[dict]:
        """Get field values by Company ID, List Entry ID, or Person ID via params

        Args:
            param (dict): Query param to filter field values by Company ID, List Entry ID, or Person ID.
                Only one of the following keys should be specified: `organization_id`, `list_entry_id`, `person_id
                or `opportunity_id`

        Returns:
            list[dict]: List of field values
        """

        if len(param) != 1 or not any(
            k in param for k in ("organization_id", "list_entry_id", "person_id", "opportunity_id")
        ):
            raise ValueError(
                "Only one of the following keys should be specified: `organization_id`, `list_entry_id`, `person_id` or `opportunity_id`"  # noqa: E501
            )

        response = await self.requests.get(url="/field-values", params=param)
        response.raise_for_status()
        return response.json()

    async def create_field_value(
        self, field_id: int, entity_id: int, value: str | int, list_entry_id: int = None
    ) -> dict:
        """Create field value

        Args:
            field_id (int): ID of field
            entity_id (int): ID of entity
            value (str | int): Value of field
            list_entry_id (int, optional): ID of list entry. Only specify the list_entry_id if the
                field that the field value is associated with is list specific. Defaults to None.

        Returns:
            dict: Response with created field value
        """
        data = {"field_id": field_id, "entity_id": entity_id, "value": value}
        if list_entry_id is not None:
            data.update({"list_entry_id": list_entry_id})

        response = await self.requests.post("/field-values", json=data)
        response.raise_for_status()
        return response.json()

    async def update_field_value(self, field_value_id: int, new_value: str | int) -> dict:
        """Update field value

        Args:
            field_value_id (int): ID of field value
            new_value (str | int): New value of field

        Returns:
            dict: Response with updated field value
        """
        data = {"value": new_value}
        response = await self.requests.put(f"/field-values/{field_value_id}", json=data)
        response.raise_for_status()
        return response.json()

    async def upsert_field_value(
        self, field_id: int, entity_id: int, value: str | int, list_entry_id: int = None
    ) -> dict:
        """Upserts field value.

        Note: This API call is a bit of a hack as it is not documented in the Affinity API docs.

        Args:
            field_id (int): Field ID to upsert
            entity_id (int): Entity ID
            value (str | int): Value of field to set. If field is a ranked dropdown this should be the
                ID of the value to set
            list_entry_id (int, optional): Set if the field belongs to a list. Defaults to None.

        Returns:
            dict: Response with upserted field value
        """
        data = {"field_id": field_id, "entity_id": entity_id, "value": value}
        if list_entry_id:
            data.update({"list_entry_id": list_entry_id})

        response = await self.requests.put("/field-values", json=data)
        response.raise_for_status()
        return response.json()

    async def get_field_value_changes(self, params: dict) -> list[dict]:
        """Get field value changes by Field ID and filtered by Company ID, List Entry ID, Action Type
        or Person ID via params
        Args:
            param (dict): Query parameter should contain `field_id` and can be filtered by:
            - `organization_id` (Company ID)
            - `list_entry_id` (List Entry ID)
            - `action_type` (Action Type)
            - `person_id` (Person ID)
        Returns:
            list[dict]: List of field value changes
        """

        if "field_id" not in params:
            raise ValueError("Field ID must be specified")

        response = await self.requests.get(url="/field-value-changes", params=params)
        response.raise_for_status()
        return response.json()

    # List related API calls
    async def create_list_entry(self, list_id: int, entity_id: int, creator_id: int = None) -> dict:
        """Create list entry

        Args:
            list_id (int): ID of list
            entity_id (int): ID of entity
            creator_id (int): ID of creator. Defaults to None.

        Returns:
            dict: Response with created list entry
        """
        data = {"entity_id": entity_id}
        if creator_id is not None:
            data.update({"creator_id": creator_id})

        response = await self.requests.post(f"lists/{list_id}/list-entries", json=data)
        response.raise_for_status()
        return response.json()

    async def get_list_entries(self, list_id: int) -> list[dict]:
        """Get list entries by list ID

        Args:
            list_id (int): ID of list

        Returns:
            list[dict]: List of list entries
        """
        response = await self.requests.get(f"/lists/{list_id}/list-entries")
        response.raise_for_status()
        return response.json()

    # Opportunity related API calls
    async def get_opportunity_details(self, opportunity_id: int) -> dict:
        """Get opportunity details by ID

        Args:
            opportunity_id (int): ID of opportunity

        Returns:
            dict: Response with opportunity details
        """
        response = await self.requests.get(f"/opportunities/{opportunity_id}")
        response.raise_for_status()
        return response.json()

    # Helper methods
    async def search_company_by_name_and_domains(self, name: str, domains: list[str]) -> list[dict]:
        """Search company by name and domains

        Args:
            name (str): Name of company
            domains (list[str]): List of domain names of company

        Returns:
            list[dict]: List of companies found. Results are deduplicated
        """
        # search affinity based on company name and known domains
        affinity_company_name_results = await self.search_company(name)
        affinity_results = affinity_company_name_results["organizations"]
        for domain in domains:
            results = await self.search_company(domain)
            for result in results["organizations"]:
                affinity_results.append(result)

        affinity_results = self._remove_duplicates(affinity_results)
        return affinity_results

    @staticmethod
    def filter_entries_by_list_id(list_entries: list[dict], list_id: int) -> list[dict]:
        """Filter list entries by list id

        Args:
            list_entries (list[dict]): List of list entries
            list_id (int): ID of list

        Returns:
            list[dict]: List of list entries filtered by list id
        """
        return list(filter(lambda list_entry: list_entry["list_id"] == list_id, list_entries))

    @staticmethod
    def field_value_by_field_id(field_values: list[dict], field_id: int) -> dict:
        """Filter field values by field id

        Args:
            field_values (list[dict]): List of field values
            field_id (int): ID of field

        Returns:
            dict: Field value filtered by field id
        """
        return next((field_value for field_value in field_values if field_value["field_id"] == field_id), None)

    @staticmethod
    def _remove_duplicates(list_to_dedupe: list[dict]) -> list[dict]:
        """Remove duplicates from list of dictionaries

        Args:
            list_to_dedupe (list[dict]): List of dictionaries

        Returns:
            list[dict]: List of dictionaries with duplicates removed
        """
        list_to_dedupe_json_set = {json.dumps(dictionary, sort_keys=True) for dictionary in list_to_dedupe}
        return [json.loads(t) for t in list_to_dedupe_json_set]
