"""REST client handling, including SurvicateStream base class."""

from __future__ import annotations

import sys
from typing import Any, Callable, Iterable

import requests
from requests.auth import AuthBase
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator, JSONPathPaginator
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources

SCHEMAS_DIR = importlib_resources.files(__package__) / "schemas"

DEFAULT_START_DATE = '2023-01-01T10:00:00.000000Z'

class SurvicateAuthenticator(AuthBase):
    """Custom Authenticator for Survicate API."""

    def __init__(self, auth_token: str):
        self.auth_token = auth_token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["Authorization"] = f"Basic {self.auth_token}"
        return r

class SurvicateStream(RESTStream):
    """Survicate stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root."""
        return "https://data-api.survicate.com/v2/"

    records_jsonpath = "$.data[*]"  # Adjust this JSONPath if necessary

    next_page_token_jsonpath = "$.pagination_data.next_url"  
    @property
    def authenticator(self) -> SurvicateAuthenticator:
        """Return a new authenticator object."""
        return SurvicateAuthenticator(auth_token=self.config["auth_token"])


    def get_new_paginator(self) -> BaseAPIPaginator:
        """Create a new pagination helper instance."""
        return JSONPathPaginator(self.next_page_token_jsonpath)

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["start"] = next_page_token.split("start=")[-1].split("&")[0]
            params["items_per_page"] = 20 
        elif self.config.get("start_date"):
            params["start"]  = self.config("start_date")
        else:
            params["start"] = DEFAULT_START_DATE
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.debug(f"API response content: {response.json()}")

        yield from extract_jsonpath(self.records_jsonpath, input=response.json())
