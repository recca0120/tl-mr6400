import json
from unittest.mock import patch, MagicMock
from main import cmd_sms, cmd_status


def _args(**kwargs):
    args = MagicMock()
    args.json = False
    args.page = 1
    args.lte = False
    args.wlan = False
    args.lan = False
    for k, v in kwargs.items():
        setattr(args, k, v)
    return args


def _mock_client(status=None, wlan=None, lan=None, sms=None):
    client = MagicMock()
    client.get_status.return_value = status or {}
    client.get_wlan.return_value = wlan or {}
    client.get_lan.return_value = lan or {}
    client.get_sms.return_value = sms or []
    return client


SMS_DATA = [
    {"from": "935188", "content": "Hello", "receivedTime": "2026-05-08 12:00:00", "unread": "1"},
    {"from": "091234", "content": "World", "receivedTime": "2026-05-07 10:00:00", "unread": "0"},
]

STATUS_DATA = {
    "sigLevel": "2",
    "netType": "3",
    "rfInfoRssi": "-59",
    "rfInfoRsrp": "-92",
    "rfInfoRsrq": "-14",
    "rfInfoSnr": "36",
    "rfInfoBand": "3",
    "connectionStatus": "Connected",
    "externalIPAddress": "10.2.153.186",
    "defaultGateway": "10.2.153.185",
    "DNSServers": "61.31.1.1,61.31.233.1",
    "MACAddress": "B0:95:75:73:C3:AD",
}

WLAN_DATA = {
    "enable": "1",
    "SSID": "TP-Link_C3AC",
    "channel": "11",
    "X_TP_Band": "2.4GHz",
    "X_TP_Bandwidth": "20M",
    "SSIDAdvertisementEnabled": "0",
    "transmitPower": "100",
    "totalAssociations": "1",
}

LAN_DATA = {
    "IPInterfaceIPAddress": "192.168.1.1",
    "IPInterfaceSubnetMask": "255.255.255.0",
    "X_TP_MACAddress": "B0:95:75:73:C3:AC",
    "DHCPServerEnable": "1",
    "minAddress": "192.168.1.100",
    "maxAddress": "192.168.1.199",
}


class TestCmdSms:
    @patch("main.create_client")
    def test_prints_messages(self, mock_create, capsys):
        mock_create.return_value = _mock_client(sms=SMS_DATA)
        cmd_sms(_args())

        output = capsys.readouterr().out
        assert "[unread]" in output
        assert "935188" in output
        assert "[read]" in output

    @patch("main.create_client")
    def test_prints_no_messages(self, mock_create, capsys):
        mock_create.return_value = _mock_client()
        cmd_sms(_args())
        assert "No SMS" in capsys.readouterr().out

    @patch("main.create_client")
    def test_json_output(self, mock_create, capsys):
        mock_create.return_value = _mock_client(sms=SMS_DATA)
        cmd_sms(_args(json=True))
        result = json.loads(capsys.readouterr().out)
        assert len(result) == 2


class TestCmdStatusAll:
    @patch("main.create_client")
    def test_shows_all_sections_by_default(self, mock_create, capsys):
        mock_create.return_value = _mock_client(
            status=STATUS_DATA, wlan=WLAN_DATA, lan=LAN_DATA
        )
        cmd_status(_args())

        output = capsys.readouterr().out
        assert "LTE Signal" in output
        assert "WAN Connection" in output
        assert "Wireless" in output
        assert "LAN" in output
        assert "10.2.153.186" in output
        assert "TP-Link_C3AC" in output
        assert "192.168.1.1" in output

    @patch("main.create_client")
    def test_json_output_all(self, mock_create, capsys):
        mock_create.return_value = _mock_client(
            status=STATUS_DATA, wlan=WLAN_DATA, lan=LAN_DATA
        )
        cmd_status(_args(json=True))

        result = json.loads(capsys.readouterr().out)
        assert "lte" in result
        assert "wlan" in result
        assert "lan" in result
        assert result["lte"]["sigLevel"] == "2"
        assert result["wlan"]["SSID"] == "TP-Link_C3AC"
        assert result["lan"]["IPInterfaceIPAddress"] == "192.168.1.1"


class TestCmdStatusLte:
    @patch("main.create_client")
    def test_shows_only_lte(self, mock_create, capsys):
        mock_create.return_value = _mock_client(status=STATUS_DATA)
        cmd_status(_args(lte=True))

        output = capsys.readouterr().out
        assert "LTE Signal" in output
        assert "WAN Connection" in output
        assert "Wireless" not in output
        assert "LAN" not in output

    @patch("main.create_client")
    def test_json_lte_only(self, mock_create, capsys):
        mock_create.return_value = _mock_client(status=STATUS_DATA)
        cmd_status(_args(lte=True, json=True))

        result = json.loads(capsys.readouterr().out)
        assert result["sigLevel"] == "2"


class TestCmdStatusWlan:
    @patch("main.create_client")
    def test_shows_only_wlan(self, mock_create, capsys):
        mock_create.return_value = _mock_client(wlan=WLAN_DATA)
        cmd_status(_args(wlan=True))

        output = capsys.readouterr().out
        assert "Wireless" in output
        assert "TP-Link_C3AC" in output
        assert "LTE Signal" not in output
        assert "LAN" not in output

    @patch("main.create_client")
    def test_json_wlan_only(self, mock_create, capsys):
        mock_create.return_value = _mock_client(wlan=WLAN_DATA)
        cmd_status(_args(wlan=True, json=True))

        result = json.loads(capsys.readouterr().out)
        assert result["SSID"] == "TP-Link_C3AC"


class TestCmdStatusLan:
    @patch("main.create_client")
    def test_shows_only_lan(self, mock_create, capsys):
        mock_create.return_value = _mock_client(lan=LAN_DATA)
        cmd_status(_args(lan=True))

        output = capsys.readouterr().out
        assert "LAN" in output
        assert "192.168.1.1" in output
        assert "LTE Signal" not in output
        assert "Wireless" not in output

    @patch("main.create_client")
    def test_json_lan_only(self, mock_create, capsys):
        mock_create.return_value = _mock_client(lan=LAN_DATA)
        cmd_status(_args(lan=True, json=True))

        result = json.loads(capsys.readouterr().out)
        assert result["IPInterfaceIPAddress"] == "192.168.1.1"


class TestDefaultCommand:
    @patch("main.cmd_dashboard")
    def test_no_args_defaults_to_dashboard(self, mock_dashboard):
        from main import main
        import sys
        with patch.object(sys, "argv", ["main.py"]):
            main()
        mock_dashboard.assert_called_once()
