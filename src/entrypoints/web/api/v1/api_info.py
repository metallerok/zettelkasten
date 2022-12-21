import json
from src.entrypoints.web.api.v1 import api_resource
from src import app_globals


@api_resource("/api-info")
class APIInfo:
    @classmethod
    def on_get(cls, req, resp):
        config = req.context["config"]
        resp.text = json.dumps({
            "name": config.app_name,
            "version": app_globals.api_version,
        })
