
from falcon.request import Request
from falcon.response import Response


class CORSMiddleware(object):
    """CORS Middleware.

    This middleware provides a simple out-of-the box CORS policy, including handling
    of preflighted requests from the browser.

    See also:

    * https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
    * https://www.w3.org/TR/cors/#resource-processing-model

    Keyword Arguments:
        allow_origins (Union[str, Iterable[str]]): List of origins to allow (case
            sensitive). The string ``'*'`` acts as a wildcard, matching every origin.
            (default ``'*'``).
        expose_headers (Optional[Union[str, Iterable[str]]]): List of additional
            response headers to expose via the ``Access-Control-Expose-Headers``
            header. These headers are in addition to the CORS-safelisted ones:
            ``Cache-Control``, ``Content-Language``, ``Content-Length``,
            ``Content-Type``, ``Expires``, ``Last-Modified``, ``Pragma``.
            (default ``None``).

            See also:
            https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Expose-Headers
        allow_credentials (Optional[Union[str, Iterable[str]]]): List of origins
            (case sensitive) for which to allow credentials via the
            ``Access-Control-Allow-Credentials`` header.
            The string ``'*'`` acts as a wildcard, matching every allowed origin,
            while ``None`` disallows all origins. This parameter takes effect only
            if the origin is allowed by the ``allow_origins`` argument.
            (Default ``None``).

    """

    def __init__(
            self,
            allow_origins: Union[str, Iterable[str]] = '*',
            expose_headers: Optional[Union[str, Iterable[str]]] = None,
            allow_credentials: Optional[Union[str, Iterable[str]]] = None,
    ):
        if allow_origins == '*':
            self.allow_origins = allow_origins
        else:
            if isinstance(allow_origins, str):
                allow_origins = [allow_origins]
            self.allow_origins = frozenset(allow_origins)
            if '*' in self.allow_origins:
                raise ValueError(
                    'The wildcard string "*" may only be passed to allow_origins as a '
                    'string literal, not inside an iterable.'
                )

        if expose_headers is not None and not isinstance(expose_headers, str):
            expose_headers = ', '.join(expose_headers)
        self.expose_headers = expose_headers

        if allow_credentials is None:
            allow_credentials = frozenset()
        elif allow_credentials != '*':
            if isinstance(allow_credentials, str):
                allow_credentials = [allow_credentials]
            allow_credentials = frozenset(allow_credentials)
            if '*' in allow_credentials:
                raise ValueError(
                    'The wildcard string "*" may only be passed to allow_credentials '
                    'as a string literal, not inside an iterable.'
                )
        self.allow_credentials = allow_credentials

    def process_request(self, req: Request, resp: Response, *args, **kwargs):
        """Implement the CORS policy for all routes.

        This middleware provides a simple out-of-the box CORS policy,
        including handling of preflighted requests from the browser.

        See also: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

        See also: https://www.w3.org/TR/cors/#resource-processing-model
        """

        origin = req.get_header('Origin')
        if origin is None:
            return

        if self.allow_origins != '*':
            is_allow = False
            for allow_origin in self.allow_origins:
                if origin[-1 * len(allow_origin):len(origin)] == allow_origin:
                    is_allow = True
                    break

            if not is_allow:
                return

        if resp.get_header('Access-Control-Allow-Origin') is None:
            set_origin = '*' if self.allow_origins == '*' else origin
            if self.allow_credentials == '*' or self._is_credential_allowed(origin):
                set_origin = origin
                resp.set_header('Access-Control-Allow-Credentials', 'true')
            resp.set_header('Access-Control-Allow-Origin', set_origin)

        if self.expose_headers:
            resp.set_header('Access-Control-Expose-Headers', self.expose_headers)

        if (
                req.method == 'OPTIONS'
                and req.get_header('Access-Control-Request-Method')
        ):
            resp.delete_header('Allow')

            allow_headers = req.get_header(
                'Access-Control-Request-Headers', default='*'
            )

            resp.set_header('Access-Control-Allow-Methods', req.get_header('Access-Control-Request-Method'))
            resp.set_header('Access-Control-Allow-Headers', allow_headers)
            resp.set_header('Access-Control-Max-Age', '86400')  # 24 hours

    def _is_credential_allowed(self, origin) -> bool:
        is_allow = False
        for allow_credential in self.allow_credentials:
            if origin[-1 * len(allow_credential):len(origin)] == allow_credential:
                is_allow = True
                break

        return is_allow

    async def process_response_async(self, *args):
        self.process_request(*args)
