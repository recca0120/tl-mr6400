import pytest
from tl_mr6400.parser import parse_rsa_keys, parse_token, parse_entries


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
        with pytest.raises(ValueError):
            parse_token("<html>no token here</html>")


class TestParseEntries:
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
        entries = parse_entries(response)
        assert len(entries) == 2
        assert entries[0]["from"] == "935188"
        assert entries[0]["content"] == "Hello World"
        assert entries[0]["unread"] == "1"
        assert entries[1]["from"] == "091234"
        assert entries[1]["unread"] == "0"

    def test_returns_empty_on_no_entries(self):
        assert parse_entries("[error]0\n") == []

    def test_handles_value_with_equals_sign(self):
        response = (
            "[1,0,0,0,0,0]1\n"
            "content=a=b=c\n"
            "[error]0\n"
        )
        entries = parse_entries(response)
        assert entries[0]["content"] == "a=b=c"

    def test_parses_lte_status(self):
        response = (
            "[2,1,0,0,0,0]0\n"
            "sigLevel=2\n"
            "connStat=4\n"
            "netType=3\n"
            "rfInfoRssi=-59\n"
            "rfInfoRsrp=-92\n"
            "rfInfoSnr=36\n"
            "[error]0\n"
        )
        entries = parse_entries(response)
        assert len(entries) == 1
        assert entries[0]["sigLevel"] == "2"
        assert entries[0]["rfInfoRssi"] == "-59"

    def test_parses_wan_ip_conn(self):
        response = (
            "[2,1,1,0,0,0]1\n"
            "connectionStatus=Connected\n"
            "externalIPAddress=10.2.153.186\n"
            "defaultGateway=10.2.153.185\n"
            "DNSServers=61.31.1.1,61.31.233.1\n"
            "[error]0\n"
        )
        entries = parse_entries(response)
        assert entries[0]["externalIPAddress"] == "10.2.153.186"
        assert entries[0]["DNSServers"] == "61.31.1.1,61.31.233.1"

    def test_preserves_stack(self):
        response = (
            "[1,0,0,0,0,0]1\n"
            "index=124\n"
            "from=935188\n"
            "[2,0,0,0,0,0]1\n"
            "index=123\n"
            "from=091234\n"
            "[error]0\n"
        )
        entries = parse_entries(response)
        assert entries[0]["__stack"] == "1,0,0,0,0,0"
        assert entries[1]["__stack"] == "2,0,0,0,0,0"

    def test_parses_mixed_entries(self):
        response = (
            "[2,1,0,0,0,0]0\n"
            "sigLevel=2\n"
            "connStat=4\n"
            "[2,1,1,0,0,0]1\n"
            "connectionStatus=Connected\n"
            "externalIPAddress=10.2.153.186\n"
            "[error]0\n"
        )
        entries = parse_entries(response)
        assert len(entries) == 2
        assert entries[0]["sigLevel"] == "2"
        assert entries[1]["externalIPAddress"] == "10.2.153.186"
