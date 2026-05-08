from tl_mr6400.http import HttpSession
from tl_mr6400.parser import parse_rsa_keys, parse_token, parse_entries
from tl_mr6400.encryption import encrypt_credentials


class LoginError(Exception):
    pass


class TlMr6400Client:
    def __init__(self, url: str, password: str, username: str = "admin", session=None):
        self.url = url.rstrip("/")
        self.password = password
        self.username = username
        self._session = session or HttpSession()
        self._token = None

    def _headers(self):
        h = {"Referer": f"{self.url}/"}
        if self._token:
            h["TokenID"] = self._token
        return h

    def _query(self, act_types: str, data: str) -> list[dict]:
        headers = {**self._headers(), "Content-Type": "text/plain"}
        r = self._session.post(
            f"{self.url}/cgi?{act_types}", data=data, headers=headers, timeout=5
        )
        if r.status_code != 200:
            return []
        return parse_entries(r.text)

    def login(self):
        r = self._session.get(
            f"{self.url}/cgi/getParm", headers=self._headers(), timeout=5
        )
        ee, nn = parse_rsa_keys(r.text)

        enc_user, enc_pass = encrypt_credentials(self.username, self.password, nn, ee)

        r = self._session.post(
            f"{self.url}/cgi/login?UserName={enc_user}&Passwd={enc_pass}&Action=1&LoginStatus=0",
            headers=self._headers(),
            timeout=5,
        )
        if "$.ret=0;" not in r.text:
            raise LoginError(f"Login failed: {r.text.strip()}")

        r = self._session.get(f"{self.url}/", headers=self._headers(), timeout=5)
        try:
            self._token = parse_token(r.text)
        except ValueError as e:
            raise LoginError(str(e)) from e

    def get_sms(self, page: int = 1) -> list[dict]:
        data = (
            f"[LTE_SMS_RECVMSGBOX#0,0,0,0,0,0#0,0,0,0,0,0]0,1\r\nPageNumber={page}\r\n"
            f"[LTE_SMS_RECVMSGENTRY#0,0,0,0,0,0#0,0,0,0,0,0]1,5\r\n"
            f"index\r\nfrom\r\ncontent\r\nreceivedTime\r\nunread\r\n"
        )
        return self._query("2&5", data)

    def get_status(self) -> dict:
        data = (
            "[LTE_NET_STATUS#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
            "[WAN_IP_CONN#0,0,0,0,0,0#0,0,0,0,0,0]1,0\r\n"
        )
        return self._query_merged("5&5", data)

    def _query_merged(self, act_types: str, data: str) -> dict:
        entries = self._query(act_types, data)
        if not entries:
            return {}
        merged = {}
        for entry in entries:
            merged.update(entry)
        return merged

    def get_wlan(self) -> dict:
        data = "[LAN_WLAN#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
        return self._query_merged("5", data)

    def set_sms_read(self, stack: str) -> None:
        data = f"[LTE_SMS_RECVMSGENTRY#{stack}#0,0,0,0,0,0]0,1\r\nunread=0\r\n"
        self._query("2", data)

    def delete_sms(self, stack: str) -> None:
        data = f"[LTE_SMS_RECVMSGENTRY#{stack}#0,0,0,0,0,0]0,0\r\n"
        self._query("4", data)

    def get_lan(self) -> dict:
        data = (
            "[LAN_IP_INTF#0,0,0,0,0,0#0,0,0,0,0,0]0,0\r\n"
            "[LAN_HOST_CFG#1,0,0,0,0,0#0,0,0,0,0,0]1,0\r\n"
        )
        return self._query_merged("5&1", data)
