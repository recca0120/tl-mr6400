from unittest.mock import MagicMock
import pytest
from tl_mr6400.client import TlMr6400Client, LoginError

RSA_RESPONSE = (
    'var ee="010001";\n'
    'var nn="C7DC6CB6F1979B9E1008A1F09A606B03FAF8BCDA541FC9D0C4DD3A8106D23BBF'
    "8044D37992F727B10A90EE59EED852714E5217CFDC0C7E02137067B412CF9CCB"
    "9F117D3E05935BD3DFE180EE0A47DF9BD1689FBD9CDC4CE2ACCBBCEE24890E24"
    '1727A7EBCDDF3BE3552CC3AC35C8DB230B8A909697C128A72F7B86F08B6CB469";\n'
    "var userSetting=1;\n"
    "$.ret=0;"
)

TOKEN_PAGE = 'var token="abc123token"; some html'

SMS_RESPONSE = (
    "[1,0,0,0,0,0]1\n"
    "index=124\n"
    "from=935188\n"
    "content=Hello\n"
    "receivedTime=2026-05-08 12:06:08\n"
    "unread=1\n"
    "[error]0\n"
)

STATUS_RESPONSE = (
    "[2,1,0,0,0,0]0\n"
    "sigLevel=2\n"
    "connStat=4\n"
    "netType=3\n"
    "rfInfoRssi=-59\n"
    "rfInfoRsrp=-92\n"
    "rfInfoSnr=36\n"
    "[2,1,1,0,0,0]1\n"
    "connectionStatus=Connected\n"
    "externalIPAddress=10.2.153.186\n"
    "defaultGateway=10.2.153.185\n"
    "DNSServers=61.31.1.1,61.31.233.1\n"
    "[error]0\n"
)


def _mock_response(text="", status_code=200):
    r = MagicMock()
    r.text = text
    r.status_code = status_code
    return r


class TestLogin:
    def test_successful_login(self):
        session = MagicMock()
        session.get.side_effect = [
            _mock_response(RSA_RESPONSE),
            _mock_response(TOKEN_PAGE),
        ]
        session.post.return_value = _mock_response("$.ret=0;")

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)
        client.login()

        assert client._token == "abc123token"
        assert session.get.call_count == 2
        assert session.post.call_count == 1

    def test_login_failure_raises_error(self):
        session = MagicMock()
        session.get.return_value = _mock_response(RSA_RESPONSE)
        session.post.return_value = _mock_response("$.ret=-1;")

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)

        with pytest.raises(LoginError):
            client.login()

    def test_missing_token_raises_error(self):
        session = MagicMock()
        session.get.side_effect = [
            _mock_response(RSA_RESPONSE),
            _mock_response("<html>no token</html>"),
        ]
        session.post.return_value = _mock_response("$.ret=0;")

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)

        with pytest.raises(LoginError):
            client.login()


class TestGetSms:
    def test_returns_parsed_messages(self):
        session = MagicMock()
        session.post.return_value = _mock_response(SMS_RESPONSE)

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)
        client._token = "fake_token"

        messages = client.get_sms()

        assert len(messages) == 1
        assert messages[0]["from"] == "935188"
        assert messages[0]["unread"] == "1"

    def test_returns_empty_on_http_error(self):
        session = MagicMock()
        session.post.return_value = _mock_response(status_code=500)

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)
        client._token = "fake_token"

        assert client.get_sms() == []

    def test_sends_correct_token_header(self):
        session = MagicMock()
        session.post.return_value = _mock_response(SMS_RESPONSE)

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)
        client._token = "my_token"
        client.get_sms()

        headers = session.post.call_args[1]["headers"]
        assert headers["TokenID"] == "my_token"


class TestGetStatus:
    def test_returns_lte_and_wan_status(self):
        session = MagicMock()
        session.post.return_value = _mock_response(STATUS_RESPONSE)

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)
        client._token = "fake_token"

        status = client.get_status()

        assert status["sigLevel"] == "2"
        assert status["rfInfoRssi"] == "-59"
        assert status["rfInfoRsrp"] == "-92"
        assert status["rfInfoSnr"] == "36"
        assert status["connectionStatus"] == "Connected"
        assert status["externalIPAddress"] == "10.2.153.186"
        assert status["defaultGateway"] == "10.2.153.185"
        assert status["DNSServers"] == "61.31.1.1,61.31.233.1"

    def test_returns_empty_on_http_error(self):
        session = MagicMock()
        session.post.return_value = _mock_response(status_code=500)

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)
        client._token = "fake_token"

        assert client.get_status() == {}


WLAN_RESPONSE = (
    "[1,1,0,0,0,0]0\n"
    "enable=1\n"
    "SSID=TP-Link_C3AC\n"
    "channel=11\n"
    "X_TP_Band=2.4GHz\n"
    "X_TP_Bandwidth=20M\n"
    "SSIDAdvertisementEnabled=0\n"
    "transmitPower=100\n"
    "totalAssociations=1\n"
    "[error]0\n"
)

LAN_RESPONSE = (
    "[1,1,0,0,0,0]0\n"
    "IPInterfaceIPAddress=192.168.1.1\n"
    "IPInterfaceSubnetMask=255.255.255.0\n"
    "X_TP_MACAddress=B0:95:75:73:C3:AC\n"
    "[1,0,0,0,0,0]1\n"
    "DHCPServerEnable=1\n"
    "minAddress=192.168.1.100\n"
    "maxAddress=192.168.1.199\n"
    "[error]0\n"
)


class TestGetWlan:
    def test_returns_wlan_info(self):
        session = MagicMock()
        session.post.return_value = _mock_response(WLAN_RESPONSE)

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)
        client._token = "fake_token"

        wlan = client.get_wlan()

        assert wlan["SSID"] == "TP-Link_C3AC"
        assert wlan["channel"] == "11"
        assert wlan["X_TP_Band"] == "2.4GHz"
        assert wlan["enable"] == "1"

    def test_returns_empty_on_http_error(self):
        session = MagicMock()
        session.post.return_value = _mock_response(status_code=500)

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)
        client._token = "fake_token"

        assert client.get_wlan() == {}


class TestGetLan:
    def test_returns_lan_info(self):
        session = MagicMock()
        session.post.return_value = _mock_response(LAN_RESPONSE)

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)
        client._token = "fake_token"

        lan = client.get_lan()

        assert lan["IPInterfaceIPAddress"] == "192.168.1.1"
        assert lan["IPInterfaceSubnetMask"] == "255.255.255.0"
        assert lan["X_TP_MACAddress"] == "B0:95:75:73:C3:AC"
        assert lan["DHCPServerEnable"] == "1"
        assert lan["minAddress"] == "192.168.1.100"
        assert lan["maxAddress"] == "192.168.1.199"

    def test_returns_empty_on_http_error(self):
        session = MagicMock()
        session.post.return_value = _mock_response(status_code=500)

        client = TlMr6400Client("http://192.168.1.1", "admin", session=session)
        client._token = "fake_token"

        assert client.get_lan() == {}
