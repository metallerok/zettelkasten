from sqlalchemy.orm import Session


class SADBSessionMiddleware:
    def __init__(self, db_session: Session):
        self._db_session = db_session

    def process_request(self, req, resp):
        req.context["db_session"] = self._db_session

    def process_response(self, req, resp, resource, is_success, *args, **kwargs):
        if not is_success:
            self._db_session.rollback()
        self._db_session.close()
