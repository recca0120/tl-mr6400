import re
from tl_mr6400.panel import Panel, PanelGrid, display_width
from tl_mr6400.formatter import signal_bar, level_bar

NET_TYPES = {"0": "No Service", "1": "2G", "2": "3G", "3": "4G LTE"}
MIN_SIDE_BY_SIDE = 60


def _sanitize(text: str) -> str:
    return re.sub(r"[\x00-\x1f\x7f]", "", text)


def render_dashboard(
    status: dict, sms: list[dict], wlan: dict, lan: dict,
    width: int = 80, sms_cursor: int | None = None
) -> list[tuple[str, str]]:
    wide = width >= MIN_SIDE_BY_SIDE

    if wide:
        half = width // 2
        other = width - half
        lte = _build_lte_panel(status, half, 9)
        wan = _build_wan_panel(status, other, 9)
        wl = _build_wlan_panel(wlan, half, 6)
        la = _build_lan_panel(lan, other, 6)
        lines = []
        lines.extend(PanelGrid.horizontal([lte, wan]))
        lines.extend(PanelGrid.horizontal([wl, la]))
    else:
        lte = _build_lte_panel(status, width, 9)
        wan = _build_wan_panel(status, width, 7)
        wl = _build_wlan_panel(wlan, width, 6)
        la = _build_lan_panel(lan, width, 5)
        lines = PanelGrid.vertical([lte, wan, wl, la])

    sms_panel = _build_sms_panel(sms, width, sms_cursor)
    lines.extend(sms_panel.render())

    return lines


def _build_lte_panel(status: dict, width: int, height: int) -> Panel:
    p = Panel("LTE Signal", width, height)
    if not status:
        p.add("Status", "No data")
        return p
    net = NET_TYPES.get(status.get("netType", ""), status.get("netType", "?"))
    p.add("Network", net)
    sig = int(status.get("sigLevel", 0))
    p.add("Signal", signal_bar(sig, 4))
    rsrp = int(status.get("rfInfoRsrp", -140))
    p.add("RSRP", level_bar(rsrp, -140, -44, width=10) + " dBm")
    rsrq = int(status.get("rfInfoRsrq", -20))
    p.add("RSRQ", level_bar(rsrq, -20, -3, width=10) + " dB")
    snr = int(status.get("rfInfoSnr", 0))
    p.add("SNR", level_bar(snr, -5, 40, width=10) + " dB")
    p.add("Band", status.get("rfInfoBand", "?"))
    return p


def _build_wan_panel(status: dict, width: int, height: int) -> Panel:
    p = Panel("WAN Connection", width, height)
    if not status:
        p.add("Status", "No data")
        return p
    p.add("Status", status.get("connectionStatus", "?"))
    p.add("IP", status.get("externalIPAddress", "?"))
    p.add("MAC", status.get("MACAddress", "?"))
    dns = status.get("DNSServers", "")
    parts = dns.split(",") if dns else []
    p.add("DNS 1", parts[0] if parts else "?")
    p.add("DNS 2", parts[1] if len(parts) > 1 else "?")
    return p


def _build_wlan_panel(wlan: dict, width: int, height: int) -> Panel:
    p = Panel("Wireless", width, height)
    if not wlan:
        p.add("Status", "No data")
        return p
    p.add("SSID", wlan.get("SSID", "?"))
    p.add("Radio", "On" if wlan.get("enable") == "1" else "Off")
    p.add("Band", wlan.get("X_TP_Band", "?"))
    p.add("Channel", wlan.get("channel", "?"))
    return p


def _build_lan_panel(lan: dict, width: int, height: int) -> Panel:
    p = Panel("LAN", width, height)
    if not lan:
        p.add("Status", "No data")
        return p
    p.add("IP", lan.get("IPInterfaceIPAddress", "?"))
    p.add("Mask", lan.get("IPInterfaceSubnetMask", "?"))
    dhcp = "On" if lan.get("DHCPServerEnable") == "1" else "Off"
    p.add("DHCP", dhcp)
    return p


def _wrap_text(text: str, max_width: int) -> list[str]:
    lines = []
    while display_width(text) > max_width:
        cut = 0
        w = 0
        for ch in text:
            import unicodedata
            cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
            if w + cw > max_width:
                break
            w += cw
            cut += 1
        lines.append(text[:cut])
        text = text[cut:]
    if text:
        lines.append(text)
    return lines


def _build_sms_panel(sms: list[dict], width: int, sms_cursor: int | None = None) -> Panel:
    inner = width - 2
    content_indent = 3
    content_width = inner - content_indent

    raw_lines: list[tuple[str, str]] = []
    if not sms:
        raw_lines.append(("  No messages", "value"))
    else:
        for idx, msg in enumerate(sms[:5]):
            unread = msg.get("unread") == "1"
            selected = sms_cursor is not None and idx == sms_cursor
            if selected:
                style = "sms_selected"
            elif unread:
                style = "sms_unread"
            else:
                style = "sms_read"
            marker = "●" if unread else " "
            prefix = "▶" if selected else " "
            sender = msg.get("from", "?")
            time = msg.get("receivedTime", "?")
            raw_lines.append((f"{prefix}{marker} {sender:<12} {time}", style))
            content = _sanitize(msg.get("content", ""))
            for wrapped in _wrap_text(content, content_width):
                raw_lines.append((f"   {wrapped}", style))

    height = len(raw_lines) + 2
    p = Panel("SMS", width, height)
    for text, style in raw_lines:
        p.add_raw(text, style)
    return p
