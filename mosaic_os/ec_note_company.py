# Input
# url domain e.g. fatllama.com
# apikey_affinity
# apikey_harmonic

# Output
# affinity_id INT
# list memberships INT
# EC Flag T/F
# in LP T/F
# status of last lp listentry DICT
# harmonic_id INT
# harmonic_list_memberships


# status, priority, owners


import os


class EC_Note_Company:
    def __init__(self, apikey_affinity, apikey_harmonic):
        self.apikey_affinity = os.environ("AFFINITY_API_KEY", apikey_affinity)
        self.apikey_harmonic = apikey_harmonic
        self.requests = __import__("requests")
        self.json = __import__("json")
        self.re = __import__("re")
        self.config = {
            "lp_list_id": 13926,
            "lp_fields": [139981, 120060, 120059],
            "company_fields": [3542734],
            "lp_field_status": 139981,
            "lp_field_priority": 120060,
            "lp_field_owner": 120059,
            "company_field_ec_flag": 3542734,
        }

    ######################
    # Affinity Functions #
    ######################

    # affinity - search company by term
    def affinity_search_company(self, term):
        url = f"https://api.affinity.co/organizations?term={term}"
        headers = {"Content-Type": "application/json"}
        response = self.requests.get(url, auth=("", self.apikey_affinity), headers=headers)
        return response.json()

    # create affinity company
    def affinity_create_company(self, name, domain):
        url = "https://api.affinity.co/organizations"
        headers = {"Content-Type": "application/json"}
        data = {"name": name, "domain": domain}
        response = self.requests.post(url, auth=("", self.apikey_affinity), headers=headers, data=self.json.dumps(data))
        return response.json()

    # affinity - get company details by ID
    def affinity_get_company_details(self, entity_id):
        url = f"https://api.affinity.co/organizations/{entity_id}?with_opportunities=true&with_interaction_dates=true&with_interaction_persons=true"
        response = self.requests.get(url, auth=("", self.apikey_affinity))
        return response.json()

    # affinity - get field values for entity
    def affinity_get_organization_field_values(self, entity_id):
        url = f"https://api.affinity.co/field-values?organization_id={entity_id}"
        response = self.requests.get(url, auth=("", self.apikey_affinity))
        return response.json()

    ######################
    # harmonic Functions #
    ######################

    def harmonic_find_company(self, domain):
        query = """mutation ($identifiers: CompanyEnrichmentIdentifiersInput!) {
        enrichCompanyByIdentifiers(identifiers: $identifiers) {
            companyFound
            company {
            name
            id
            website {domain
            }
            watchlists {
                name
                id
            }
            }
        }
        }"""

        url = "https://api.harmonic.ai/graphql"
        identifiers = {"identifiers": {"websiteUrl": domain}}

        payload = {"query": query, "variables": identifiers}
        headers = {"apikey": self.apikey_harmonic}
        response = self.requests.post(url, json=payload, headers=headers)
        return response.json()

    #####################
    # Generic Functions #
    #####################

    def get_all_company_details(self, domain):
        domain_pattern = self.re.compile(r"^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)")
        domain_clean = self.re.findall(domain_pattern, domain)[0]

        # get harmonic company information
        harmonic_response = self.harmonic_find_company(domain_clean)

        # if company exists get info
        if harmonic_response["data"]["enrichCompanyByIdentifiers"]["companyFound"]:
            harmonic_company = harmonic_response["data"]["enrichCompanyByIdentifiers"]["company"]
            harmonic_company.update({"enrichment_urn": None})
        # company not found - create dummy response and add enrichment urn
        else:
            harmonic_company = {
                "name": None,
                "id": None,
                "website": None,
                "watchlists": None,
                "watchlists": [],
                "enrichment_urn": str,
            }

        # combine clean domain and harmonic domain to increase likelihood of matching in Affinity
        known_domains = list(set([domain_clean, harmonic_company["website"]["domain"]]))

        # search affinity based on company name and unpack domains of matches
        affinity_results = self.affinity_search_company(harmonic_company["name"])
        domains = [d.get("domains", None) for d in affinity_results["organizations"]]

        # iterate through matches & domains - first match will return index of match
        i = -1
        for org in domains:
            i += 1
            for d in org:
                if d in known_domains:
                    match_comp = i
                else:
                    continue

        # get company id of match and retrieve company information by id from affinity
        affinity_entity_id = affinity_results["organizations"][match_comp]["id"]
        affinity_company_details = self.affinity_get_company_details(affinity_entity_id)

        # loop through list entries, get lp entries only, and pick most recent one
        lp_entries = [d for d in affinity_company_details["list_entries"] if d["list_id"] == self.config["lp_list_id"]]
        lp_entries.reverse()
        last_entry = lp_entries[0]

        # get all field values for company (includes list entries)
        all_company_field_values = self.affinity_get_organization_field_values(affinity_entity_id)

        lp_listentry_field_values = [
            d
            for d in all_company_field_values
            if (d["list_entry_id"] == last_entry["id"]) & (d["field_id"] in self.config["lp_fields"])
        ]
        company_field_values = [
            d
            for d in all_company_field_values
            if (d["list_entry_id"] == None) & (d["field_id"] in self.config["company_fields"])
        ]

        # create affinitnity return
        # issue with field values currently returned as lists as throws error if indexing empty list (in case
        # field not populated)
        affinity_return = {
            "company_id": affinity_entity_id,
            "company_name": affinity_company_details["name"],
            "domain": affinity_company_details["domain"],
            "ec_flag": [d for d in company_field_values if (d["field_id"] == self.config["company_field_ec_flag"])],
            "live_pipeline": {
                "list_entry_id": last_entry["id"],
                "status": [d for d in lp_listentry_field_values if (d["field_id"] == self.config["lp_field_status"])],
                "priority": [
                    d for d in lp_listentry_field_values if (d["field_id"] == self.config["lp_field_priority"])
                ],
                "owner": [d for d in lp_listentry_field_values if (d["field_id"] == self.config["lp_field_owner"])],
            },
        }

        output = {"domain": domain, "affinity": affinity_return, "harmonic": harmonic_company}

        return output
