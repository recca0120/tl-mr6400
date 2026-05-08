import json
from unittest.mock import patch, MagicMock
from main import cmd_sms, cmd_status, cmd_wlan, cmd_lan


def _args(**kwargs):
    args = MagicMock()
    args.json = False
    args.page = 1
    for k, v in kwargs.items():
        setattr(args, k, v)
    return args


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
        client = MagicMock()
        client.get_sms.return_value = SMS_DATA
        mock_create.return_value = client

        cmd_sms(_args())

        output = capsys.readouterr().out
        assert "[unread]" in output
        assert "935188" in output
        assert "Hello" in output
        assert "[read]" in output
        assert "091234" in output

    @patch("main.create_client")
    def test_prints_no_messages(self, mock_create, capsys):
        client = MagicMock()
        client.get_sms.return_value = []
        mock_create.return_value = client

        cmd_sms(_args())

        assert "No SMS" in capsys.readouterr().out

    @patch("main.create_client")
    def test_json_output(self, mock_create, capsys):
        client = MagicMock()
        client.get_sms.return_value = SMS_DATA
        mock_create.return_value = client

        cmd_sms(_args(json=True))

        result = json.loads(capsys.readouterr().out)
        assert len(result) == 2
        assert result[0]["from"] == "935188"


class TestCmdStatus:
    @patch("main.create_client")
    def test_prints_signal_and_wan(self, mock_create, capsys):
        client = MagicMock()
        client.get_status.return_value = STATUS_DATA
        mock_create.return_value = client

        cmd_status(_args())

        output = capsys.readouterr().out
        assert "4G" in output
        assert "2/4" in output
        assert "-59" in output
        assert "-92" in output
        assert "36" in output
        assert "10.2.153.186" in output
        assert "Connected" in output
        assert "61.31.1.1" in output

    @patch("main.create_client")
    def test_prints_failure_on_empty(self, mock_create, capsys):
        client = MagicMock()
        client.get_status.return_value = {}
        mock_create.return_value = client

        cmd_status(_args())

        assert "Failed" in capsys.readouterr().out

    @patch("main.create_client")
    def test_json_output(self, mock_create, capsys):
        client = MagicMock()
        client.get_status.return_value = STATUS_DATA
        mock_create.return_value = client

        cmd_status(_args(json=True))

        result = json.loads(capsys.readouterr().out)
        assert result["sigLevel"] == "2"
        assert result["externalIPAddress"] == "10.2.153.186"


class TestCmdWlan:
    @patch("main.create_client")
    def test_prints_wlan_info(self, mock_create, capsys):
        client = MagicMock()
        client.get_wlan.return_value = WLAN_DATA
        mock_create.return_value = client

        cmd_wlan(_args())

        output = capsys.readouterr().out
        assert "TP-Link_C3AC" in output
        assert "2.4GHz" in output
        assert "11" in output
        assert "Enabled" in output

    @patch("main.create_client")
    def test_prints_failure_on_empty(self, mock_create, capsys):
        client = MagicMock()
        client.get_wlan.return_value = {}
        mock_create.return_value = client

        cmd_wlan(_args())

        assert "Failed" in capsys.readouterr().out

    @patch("main.create_client")
    def test_json_output(self, mock_create, capsys):
        client = MagicMock()
        client.get_wlan.return_value = WLAN_DATA
        mock_create.return_value = client

        cmd_wlan(_args(json=True))

        result = json.loads(capsys.readouterr().out)
        assert result["SSID"] == "TP-Link_C3AC"


class TestCmdLan:
    @patch("main.create_client")
    def test_prints_lan_info(self, mock_create, capsys):
        client = MagicMock()
        client.get_lan.return_value = LAN_DATA
        mock_create.return_value = client

        cmd_lan(_args())

        output = capsys.readouterr().out
        assert "192.168.1.1" in output
        assert "255.255.255.0" in output
        assert "B0:95:75:73:C3:AC" in output
        assert "192.168.1.100" in output
        assert "192.168.1.199" in output

    @patch("main.create_client")
    def test_prints_failure_on_empty(self, mock_create, capsys):
        client = MagicMock()
        client.get_lan.return_value = {}
        mock_create.return_value = client

        cmd_lan(_args())

        assert "Failed" in capsys.readouterr().out

    @patch("main.create_client")
    def test_json_output(self, mock_create, capsys):
        client = MagicMock()
        client.get_lan.return_value = LAN_DATA
        mock_create.return_value = client

        cmd_lan(_args(json=True))

        result = json.loads(capsys.readouterr().out)
        assert result["IPInterfaceIPAddress"] == "192.168.1.1"
