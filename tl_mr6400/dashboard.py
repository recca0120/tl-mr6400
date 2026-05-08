from tl_mr6400.panel import Panel, PanelGrid

NET_TYPES = {"0": "No Service", "1": "2G", "2": "3G", "3": "4G LTE"}


def render_dashboard(
    status: dict, sms: list[dict], wlan: dict, lan: dict, width: int = 80
) -> list[str]:
    half = width // 2
    top_h = 10
    bot_h = 6

    lte_panel = _build_lte_panel(status, half, top_h)
    wan_panel = _build_wan_panel(status, width - half, top_h)
    wlan_panel = _build_wlan_panel(wlan, half, bot_h)
    lan_panel = _build_lan_panel(lan, width - half, bot_h)
    sms_panel = _build_sms_panel(sms, width, 4 + min(len(sms), 5) * 2)

    lines = []
    lines.extend(PanelGrid.horizontal([lte_panel, wan_panel]))
    lines.extend(PanelGrid.horizontal([wlan_panel, lan_panel]))
    lines.extend(sms_panel.render())

    return lines


def _build_lte_panel(status: dict, width: int, height: int) -> Panel:
    p = Panel("LTE Signal", width, height)
    if not status:
        p.add("Status", "No data")
        return p
    net = NET_TYPES.get(status.get("netType", ""), status.get("netType", "?"))
    p.add("Network", net)
    p.add("Signal", f'{status.get("sigLevel", "?")}/4')
    p.add("RSRP", f'{status.get("rfInfoRsrp", "?")} dBm')
    p.add("RSRQ", f'{status.get("rfInfoRsrq", "?")} dB')
    p.add("SNR", f'{status.get("rfInfoSnr", "?")} dB')
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


def _build_sms_panel(sms: list[dict], width: int, height: int) -> Panel:
    p = Panel("SMS (Recent)", width, max(height, 4))
    if not sms:
        p.add("", "No messages")
        return p
    for msg in sms[:5]:
        marker = "*" if msg.get("unread") == "1" else " "
        sender = msg.get("from", "?")
        time = msg.get("receivedTime", "?")
        content = msg.get("content", "")
        p.add(f"{marker} {time}", sender)
        p.add("", content)
    return p
