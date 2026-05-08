from tl_mr6400.dashboard import render_dashboard
from tl_mr6400.panel import display_width


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
    "DNSServers": "61.31.1.1,61.31.233.1",
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

VALID_STYLES = {"border", "title", "key", "value", "sms_unread", "sms_read", "empty"}


class TestRenderDashboard:
    def test_returns_styled_lines(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        assert isinstance(lines, list)
        for text, style in lines:
            assert isinstance(text, str)
            assert style in VALID_STYLES

    def test_contains_all_sections(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        text = "\n".join(t for t, _ in lines)
        assert "4G LTE" in text
        assert "-92" in text
        assert "10.2.153.186" in text
        assert "TP-Link_C3AC" in text
        assert "192.168.1.1" in text

    def test_signal_has_bar_graphic(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        text = "\n".join(t for t, _ in lines)
        assert "▰" in text or "█" in text

    def test_consistent_display_width(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for text, _ in lines:
            assert display_width(text) == 80, f"Width {display_width(text)} != 80: {repr(text)}"


class TestDashboardStyles:
    def test_top_border_has_title_style(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for text, style in lines:
            if text.lstrip().startswith("┌"):
                assert style == "title"
                break

    def test_bottom_border_has_border_style(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for text, style in lines:
            if text.lstrip().startswith("└"):
                assert style == "border"
                break

    def test_title_lines_have_title_style(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        title_lines = [(t, s) for t, s in lines if "LTE Signal" in t or "WAN" in t]
        for _, style in title_lines:
            assert style == "title"

    def test_key_value_lines_have_key_style(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for text, style in lines:
            if "Network" in text and "4G LTE" in text:
                assert style == "key"
                break

    def test_unread_sms_has_unread_style(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for text, style in lines:
            if "935188" in text:
                assert style == "sms_unread"
                break

    def test_read_sms_has_read_style(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for text, style in lines:
            if "091234" in text:
                assert style == "sms_read"
                break

    def test_unread_content_inherits_unread_style(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for text, style in lines:
            if "Hello World" in text:
                assert style == "sms_unread"
                break

    def test_empty_lines_have_empty_style(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for text, style in lines:
            if text.strip() == "│" + " " * (len(text) - 2) + "│" or (text.startswith("│") and text.strip("│ ") == ""):
                assert style in ("empty", "border")


class TestDashboardSms:
    def test_sender_and_time_on_same_line(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for text, _ in lines:
            if "935188" in text:
                assert "2026-05-08" in text
                break
        else:
            assert False, "Sender line not found"

    def test_content_on_next_line(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for i, (text, _) in enumerate(lines):
            if "935188" in text:
                assert "Hello World" in lines[i + 1][0]
                break

    def test_long_sms_wraps(self):
        long_sms = [
            {"from": "935188", "content": "A" * 200, "receivedTime": "2026-05-08 12:06:08", "unread": "1"},
        ]
        lines = render_dashboard(STATUS_DATA, long_sms, WLAN_DATA, LAN_DATA, width=80)
        content_lines = [t for t, _ in lines if "AAAA" in t]
        assert len(content_lines) >= 2

    def test_strips_control_characters(self):
        ctrl_sms = [
            {"from": "123", "content": "hello\r\nworld\r", "receivedTime": "2026-01-01 00:00", "unread": "0"},
        ]
        lines = render_dashboard(STATUS_DATA, ctrl_sms, WLAN_DATA, LAN_DATA, width=80)
        for text, _ in lines:
            assert "\r" not in text
            assert "\n" not in text

    def test_chinese_sms_consistent_width(self):
        chinese_sms = [
            {"from": "935188", "content": "提醒您4G上網吃到飽將於2026/05/08 13:34結束，儲值請至APP或官網(twm5g.co/NGBy)，短效卡不適用儲值展延", "receivedTime": "2026-05-08 12:06:08", "unread": "1"},
        ]
        lines = render_dashboard(STATUS_DATA, chinese_sms, WLAN_DATA, LAN_DATA, width=80)
        for text, _ in lines:
            assert display_width(text) == 80, f"Width {display_width(text)} != 80: {repr(text)}"

    def test_empty_sms(self):
        lines = render_dashboard(STATUS_DATA, [], WLAN_DATA, LAN_DATA, width=80)
        text = "\n".join(t for t, _ in lines)
        assert "No messages" in text


class TestDashboardRwd:
    def test_wide_layout_side_by_side(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=80)
        for text, _ in lines:
            if "LTE" in text and "WAN" in text:
                break
        else:
            assert False, "LTE and WAN should be on the same line"

    def test_narrow_layout_stacked(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=50)
        for text, _ in lines:
            assert display_width(text) == 50
            if "LTE" in text:
                assert "WAN" not in text

    def test_very_narrow(self):
        lines = render_dashboard(STATUS_DATA, SMS_DATA, WLAN_DATA, LAN_DATA, width=40)
        assert len(lines) > 0
        for text, _ in lines:
            assert display_width(text) == 40
