import logging
import json
from sqlalchemy.orm import Session
from src.entrypoints.web.api.v1 import api_resource
from src import app_globals

logger = logging.getLogger(__name__)


@api_resource("/api-info")
class APIInfo:
    @classmethod
    def on_get(cls, req, resp):
        config = req.context["config"]
        db_session: Session = req.context["db_session"]

        db_connection_active = False

        try:
            db_session.execute("SELECT 1;")
            db_connection_active = True
        except Exception as e:
            logger.exception(e)
            pass

        resp.text = json.dumps({
            "name": config.app_name,
            "version": app_globals.api_version,
            "db_connection_active": db_connection_active
        })
