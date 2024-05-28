from __future__ import annotations

import typing as t
from pathlib import Path

from tap_survicate.client import SurvicateStream

if t.TYPE_CHECKING:
    import requests

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class SurveysStream(SurvicateStream):
    """A stream for the surveys endpoint."""

    name = "surveys"
    path = "/surveys"
    schema_filepath = SCHEMAS_DIR / "surveys.json"
    primary_keys = ["id"]

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        context = context or {}
        context["survey_id"] = record["id"]

        return super().get_child_context(record, context) 


class ResponsesStream(SurvicateStream):
    """A stream for the responses endpoint."""

    name = "responses"
    path = "surveys/{survey_id}/responses"
    schema_filepath = SCHEMAS_DIR / "responses.json"
    parent_stream_type = SurveysStream
    primary_keys = ["uuid"]

    def post_process(self, row: dict, context: dict) -> dict | None:
        row["survey_id"] = context["survey_id"]
        return row

