from tl_mr6400.dashboard import render_dashboard


STATUS_DATA = {
    "sigLevel": "3",
    "netType": "3",
    "rfInfoRssi": "-59",
    "rfInfoRsrp": "-92",
    "rfInfoRsrq": "-14",
    "rfInfoSnr": "36",
    "rfInfoBand": "3",
    "connectionStatus": "Connected",
    "externalIPAddress": "10.2.153.186",
    "MACAddress": "B0:95:75:73:C3:AD",
}

SMS_DATA = [
    {"from": "935188", "content": "Hello World", "receivedTime": "2026-05-08 12:06:08", "unread": "1"},
    {"from": "091234", "content": "Test msg", "receivedTime": "2026-05-07 10:09:22", "unread": "0"},
]

WLAN_DATA = {
    "enable": "1",
    "SSID": "TP-Link_C3AC",
    "channel": "11",
    "X_TP_Band": "2.4GHz",
}

LAN_DATA = {
    "IPInterfaceIPAddress": "192.168.1.1",
    "IPInterfaceSubnetMask": "255.255.255.0",
    "DHCPServerEnable": "1",
}


class TestRenderDashboard:
    def test_returns_list_of_lines(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA)
        assert isinstance(lines, list)
        assert all(isinstance(line, tuple) and len(line) == 2 for line in lines)

    def test_contains_signal_info(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA)
        text = "\n".join(t for t, _ in lines)
        assert "4G LTE" in text
        assert "-92" in text
        assert "3/4" in text

    def test_contains_wan_info(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA)
        text = "\n".join(t for t, _ in lines)
        assert "10.2.153.186" in text
        assert "Connected" in text

    def test_contains_wlan_info(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA)
        text = "\n".join(t for t, _ in lines)
        assert "TP-Link_C3AC" in text

    def test_contains_lan_info(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA)
        text = "\n".join(t for t, _ in lines)
        assert "192.168.1.1" in text

    def test_contains_sms(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA)
        text = "\n".join(t for t, _ in lines)
        assert "935188" in text
        assert "Hello World" in text

    def test_lines_have_color_attr(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA)
        for _, attr in lines:
            assert attr in ("header", "normal", "key", "unread", "read")

    def test_empty_sms(self):
        lines = render_dashboard(STATUS_DATA, [], WLAN_DATA, LAN_DATA)
        text = "\n".join(t for t, _ in lines)
        assert "No messages" in text

    def test_empty_status(self):
        lines = render_dashboard({}, SMS_DATA, {}, {})
        assert isinstance(lines, list)
        assert len(lines) > 0
