import copy
from typing import Type
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from config import Config
from src import app_globals


def save_log(path, filename, message):
    dir_path = Path(str(Path().absolute()) + path)
    file_path = str(dir_path) + "/" + filename
    try:
        dir_path.mkdir()
        with open(file_path, "a+") as log:
            log.write(message)
    except FileExistsError:
        with open(file_path, "a+") as log:
            log.write(message)


class LoggingMiddleware:
    def __init__(self, config: Type[Config]):
        self._config = config

    def process_request(self, req, resp):
        if not self._config.enable_logging:
            return

        request_id = str(uuid4())
        req.context.request_id = request_id

        req_body = copy.deepcopy(req.text)
        if "password" in req_body:
            req_body["password"] = "***********"

        req_headers = copy.deepcopy(req.headers)

        if "AUTHORIZATION" in req_headers:
            req_headers["AUTHORIZATION"] = "**********"

        if "SERVICE-TOKEN" in req_headers:
            req_headers["SERVICE-TOKEN"] = "***********"

        request = f"[{datetime.now()}]: request_id={request_id} {req.remote_addr} " \
                  f"{req.access_route} {req.forwarded_host} {req.host} {req.method} " \
                  f"{req.url} params={req.params} body={req_body} " \
                  f"headers={req_headers} api_version={app_globals.api_version}\n"

        # save file
        save_log("/logs", "requests_log.txt", request)

    def process_response(self, req, resp, resource, is_success):
        if not is_success:
            if not self._config.enable_logging:
                return

            request_id = req.context.get("request_id")
            response = f"[{datetime.now()}]: request_id={request_id} {resp.status} " \
                       f"{req.method} {req.url} error_message={resp.data}\n"

            # save file
            save_log("/logs", "error_log.txt", response)
