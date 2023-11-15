from os import environ
from typing import Any

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


class HarmonicGql:
    """GraphQL wrapper for Harmonic GraphQL API

    Args:
        harmonic_api_key (str): API key for Harmonic which can be set by passing through here or
        setting environment variable `HARMONIC_API_KEY`. Defaults to None.

    Raises:
        ValueError: If harmonic_api_key is not set
    """

    def __init__(self, harmonic_api_key: str = None, timeout: int = 10):
        _harmonic_api_key = environ.get("HARMONIC_API_KEY", harmonic_api_key)
        if _harmonic_api_key is None:
            raise ValueError("Harmonic API Key not found in environment variables or passed as argument")

        self.transport = AIOHTTPTransport(url="https://api.harmonic.ai/graphql", headers={"apikey": _harmonic_api_key})
        self.client = Client(transport=self.transport, execute_timeout=timeout)
        self.session = None

    async def connect(self):
        self.session = await self.client.connect_async(reconnecting=True)

    async def query(self, query: str, variables: dict = None) -> dict[str, Any]:
        if self.session:
            return await self.session.execute(gql(query), variable_values=variables)
        async with self.client as session:
            response = await session.execute(gql(query), variable_values=variables)

        return response

    async def disconnect(self):
        await self.client.close_async()
