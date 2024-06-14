from __future__ import annotations

from singer_sdk import Tap, typing as th  
from tap_survicate import streams

class Tapsurvicate(Tap):
    """Survicate tap class."""

    name = "tap-survicate"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True,
            description="The token to authenticate against the API service",
        ),
        # th.Property(
        #     "start_date",
        #     th.DateTimeType,
        #     description="The earliest record date to sync",
        # ),
        th.Property(
            "api_url",
            th.StringType,
            default="https://data-api.survicate.com/v2/",
            description="The URL for the API service",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.SurvicateStream]:
        """Return a list of discovered streams."""
        return [
            streams.SurveysStream(self),
            streams.ResponsesStream(self)
            # streams.RespondentsStream(self)
        ]
    
if __name__ == "__main__":
    Tapsurvicate.cli()