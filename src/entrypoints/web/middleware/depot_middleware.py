from depot.manager import DepotManager


class DepotMiddleware:
    def __init__(self, depot: DepotManager):
        self._depot = depot

    def process_request(self, req, resp):
        req.context["depot"] = self._depot
