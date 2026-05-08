NET_TYPES = {"0": "No Service", "1": "2G", "2": "3G", "3": "4G LTE"}


def render_dashboard(
    status: dict, sms: list[dict], wlan: dict, lan: dict
) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []

    _render_status(lines, status)
    lines.append(("", "normal"))
    _render_wlan(lines, wlan)
    lines.append(("", "normal"))
    _render_lan(lines, lan)
    lines.append(("", "normal"))
    _render_sms(lines, sms)

    return lines


def _kv(lines, key, value, max_key=15):
    lines.append((f"  {key.ljust(max_key)} : {value}", "key"))


def _render_status(lines, status):
    lines.append(("=== LTE Signal ===", "header"))
    if not status:
        lines.append(("  No data", "normal"))
        return
    net = NET_TYPES.get(status.get("netType", ""), status.get("netType", "?"))
    _kv(lines, "Network Type", net)
    _kv(lines, "Signal Level", f'{status.get("sigLevel", "?")}/4')
    _kv(lines, "RSRP", f'{status.get("rfInfoRsrp", "?")} dBm')
    _kv(lines, "RSRQ", f'{status.get("rfInfoRsrq", "?")} dB')
    _kv(lines, "SNR", f'{status.get("rfInfoSnr", "?")} dB')
    _kv(lines, "Band", status.get("rfInfoBand", "?"))

    lines.append(("", "normal"))
    lines.append(("=== WAN Connection ===", "header"))
    _kv(lines, "Status", status.get("connectionStatus", "?"))
    _kv(lines, "IP Address", status.get("externalIPAddress", "?"))
    _kv(lines, "MAC Address", status.get("MACAddress", "?"))


def _render_wlan(lines, wlan):
    lines.append(("=== Wireless ===", "header"))
    if not wlan:
        lines.append(("  No data", "normal"))
        return
    _kv(lines, "SSID", wlan.get("SSID", "?"))
    _kv(lines, "Radio", "On" if wlan.get("enable") == "1" else "Off")
    _kv(lines, "Band", wlan.get("X_TP_Band", "?"))
    _kv(lines, "Channel", wlan.get("channel", "?"))


def _render_lan(lines, lan):
    lines.append(("=== LAN ===", "header"))
    if not lan:
        lines.append(("  No data", "normal"))
        return
    _kv(lines, "IP Address", lan.get("IPInterfaceIPAddress", "?"))
    _kv(lines, "Subnet Mask", lan.get("IPInterfaceSubnetMask", "?"))
    dhcp = "On" if lan.get("DHCPServerEnable") == "1" else "Off"
    _kv(lines, "DHCP", dhcp)


def _render_sms(lines, sms):
    lines.append(("=== SMS (Recent) ===", "header"))
    if not sms:
        lines.append(("  No messages", "normal"))
        return
    for msg in sms[:5]:
        unread = msg.get("unread") == "1"
        attr = "unread" if unread else "read"
        marker = "*" if unread else " "
        sender = msg.get("from", "?")
        time = msg.get("receivedTime", "?")
        content = msg.get("content", "")
        if len(content) > 60:
            content = content[:57] + "..."
        lines.append((f" {marker} {time}  {sender}", attr))
        lines.append((f"    {content}", attr))
