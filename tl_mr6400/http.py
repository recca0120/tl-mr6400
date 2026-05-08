import urllib.request
import http.cookiejar


class HttpResponse:
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text


class HttpSession:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        cookie_jar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cookie_jar)
        )

    def get(self, url: str, headers: dict = None, **kwargs) -> HttpResponse:
        return self._request(url, headers=headers, **kwargs)

    def post(self, url: str, data: str = None, headers: dict = None, **kwargs) -> HttpResponse:
        return self._request(url, data=data, headers=headers, **kwargs)

    def _request(self, url: str, data: str = None, headers: dict = None, **kwargs) -> HttpResponse:
        body = data.encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body)
        for key, val in (headers or {}).items():
            req.add_header(key, val)

        timeout = kwargs.get("timeout", self.timeout)
        try:
            resp = self._opener.open(req, timeout=timeout)
            return HttpResponse(resp.status, resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return HttpResponse(e.code, e.read().decode("utf-8"))
