JSON_CONTENT_TYPE = 'application/json'
REQUEST_ID = "OPERATION-REQUEST-ID"


class Headers:
    def __init__(self):
        self._headers = {
            "content-type": JSON_CONTENT_TYPE,
        }

    def set_auth(self, value: str):
        self._headers["Authorization"] = value

    def set_bearer_token(self, token: str):
        self.set_auth(f"Bearer {token}")

    def set_service_token(self, token: str):
        self._headers["SERVICE-TOKEN"] = token

    def set_content_type(self, value: str):
        self._headers["content-type"] = value

    def set_request_id(self, value: str):
        self._headers[REQUEST_ID] = value

    def set_header(self, key: str, value: str):
        self._headers[key] = value

    def get(self):
        return self._headers
