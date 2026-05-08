from tl_mr6400.parser import parse_sms_response, parse_rsa_keys, parse_token


class TestParseRsaKeys:
    def test_extracts_ee_and_nn(self):
        response = (
            'var ee="010001";\n'
            'var nn="AABB";\n'
            "var userSetting=1;\n"
            "$.ret=0;"
        )
        ee, nn = parse_rsa_keys(response)
        assert ee == "010001"
        assert nn == "AABB"

    def test_raises_on_missing_keys(self):
        import pytest

        with pytest.raises(ValueError):
            parse_rsa_keys("some garbage")


class TestParseToken:
    def test_extracts_token(self):
        html = 'var token="abc123def"; some other stuff'
        assert parse_token(html) == "abc123def"

    def test_extracts_token_without_quotes(self):
        html = "var token=abc123def; some other stuff"
        assert parse_token(html) == "abc123def"

    def test_raises_on_missing_token(self):
        import pytest

        with pytest.raises(ValueError):
            parse_token("<html>no token here</html>")


class TestParseSmsResponse:
    def test_parses_multiple_messages(self):
        response = (
            "[1,0,0,0,0,0]1\n"
            "index=124\n"
            "from=935188\n"
            "content=Hello World\n"
            "receivedTime=2026-05-08 12:06:08\n"
            "unread=1\n"
            "[2,0,0,0,0,0]1\n"
            "index=123\n"
            "from=091234\n"
            "content=Test msg\n"
            "receivedTime=2026-05-07 10:09:22\n"
            "unread=0\n"
            "[error]0\n"
        )
        messages = parse_sms_response(response)
        assert len(messages) == 2
        assert messages[0]["from"] == "935188"
        assert messages[0]["content"] == "Hello World"
        assert messages[0]["unread"] == "1"
        assert messages[1]["from"] == "091234"
        assert messages[1]["unread"] == "0"

    def test_returns_empty_on_no_messages(self):
        assert parse_sms_response("[error]0\n") == []

    def test_handles_content_with_equals_sign(self):
        response = (
            "[1,0,0,0,0,0]1\n"
            "index=1\n"
            "from=123\n"
            "content=a=b=c\n"
            "receivedTime=2026-01-01 00:00:00\n"
            "unread=0\n"
            "[error]0\n"
        )
        messages = parse_sms_response(response)
        assert messages[0]["content"] == "a=b=c"
