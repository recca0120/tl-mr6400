from unittest.mock import MagicMock, patch, call
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

        headers = session.post.call_args[1].get("headers") or session.post.call_args[0][1] if len(session.post.call_args[0]) > 1 else session.post.call_args[1]["headers"]
        assert headers["TokenID"] == "my_token"
