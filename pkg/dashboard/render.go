package dashboard

import (
	"fmt"
	"strings"

	"github.com/mattn/go-runewidth"
)

const (
	minSideBySide    = 60
	smsViewportSize  = 5
	ltePanelH        = 9
	wanPanelH        = 9
	wlanPanelH       = 6
	lanPanelH        = 6
	ltePanelHNarrow  = 9
	wanPanelHNarrow  = 7
	wlanPanelHNarrow = 6
	lanPanelHNarrow  = 5

	unreadTrue = "1"

	rsrpMin = -140
	rsrpMax = -44
	rsrqMin = -20
	rsrqMax = -3
	snrMin  = -5
	snrMax  = 40
	barWidth = 10
)

var netTypes = map[string]string{
	"0": "No Service", "1": "2G", "2": "3G", "3": "4G LTE",
}

func RenderDashboard(status map[string]string, sms []map[string]string, wlan, lan map[string]string, width, smsCursor, smsScroll int) string {
	wide := width >= minSideBySide
	var lines []string

	if wide {
		half := width / 2
		other := width - half
		lte := buildLTEPanel(status, half, ltePanelH)
		wan := buildWANPanel(status, other, wanPanelH)
		lines = append(lines, sideBySide(lte.Render(), wan.Render())...)

		wlP := buildWLANPanel(wlan, half, wlanPanelH)
		laP := buildLANPanel(lan, other, lanPanelH)
		lines = append(lines, sideBySide(wlP.Render(), laP.Render())...)
	} else {
		for _, p := range []*Panel{
			buildLTEPanel(status, width, ltePanelHNarrow),
			buildWANPanel(status, width, wanPanelHNarrow),
			buildWLANPanel(wlan, width, wlanPanelHNarrow),
			buildLANPanel(lan, width, lanPanelHNarrow),
		} {
			lines = append(lines, p.Render()...)
		}
	}

	smsP := buildSMSPanel(sms, width, smsCursor, smsScroll)
	lines = append(lines, smsP.Render()...)

	return strings.Join(lines, "\n")
}

func sideBySide(left, right []string) []string {
	maxH := max(len(left), len(right))
	for len(left) < maxH {
		w := runewidth.StringWidth(left[0])
		left = append(left, "│"+strings.Repeat(" ", w-2)+"│")
	}
	for len(right) < maxH {
		w := runewidth.StringWidth(right[0])
		right = append(right, "│"+strings.Repeat(" ", w-2)+"│")
	}
	lines := make([]string, maxH)
	for i := range maxH {
		lines[i] = left[i] + right[i]
	}
	return lines
}

func signalBar(level, maxLevel int) string {
	filled := max(0, min(level, maxLevel))
	return strings.Repeat("▰", filled) + strings.Repeat("▱", maxLevel-filled) + fmt.Sprintf(" %d/%d", level, maxLevel)
}

func levelBar(value, minVal, maxVal, width int) string {
	ratio := float64(value-minVal) / float64(maxVal-minVal)
	ratio = max(0.0, min(1.0, ratio))
	filled := int(ratio*float64(width) + 0.5)
	return strings.Repeat("█", filled) + strings.Repeat("░", width-filled) + fmt.Sprintf(" %d", value)
}

func intOrDefault(s string, def int) int {
	n := def
	fmt.Sscanf(s, "%d", &n)
	return n
}

func buildLTEPanel(status map[string]string, width, height int) *Panel {
	p := NewPanel("LTE Signal", width, height)
	if len(status) == 0 {
		p.AddKV("Status", "No data")
		return p
	}
	net := netTypes[status["netType"]]
	if net == "" {
		net = status["netType"]
	}
	p.AddKV("Network", net)
	p.AddKV("Signal", signalBar(intOrDefault(status["sigLevel"], 0), 4))
	p.AddKV("RSRP", levelBar(intOrDefault(status["rfInfoRsrp"], rsrpMin), rsrpMin, rsrpMax, barWidth)+" dBm")
	p.AddKV("RSRQ", levelBar(intOrDefault(status["rfInfoRsrq"], rsrqMin), rsrqMin, rsrqMax, barWidth)+" dB")
	p.AddKV("SNR", levelBar(intOrDefault(status["rfInfoSnr"], 0), snrMin, snrMax, barWidth)+" dB")
	p.AddKV("Band", status["rfInfoBand"])
	return p
}

func buildWANPanel(status map[string]string, width, height int) *Panel {
	p := NewPanel("WAN Connection", width, height)
	if len(status) == 0 {
		p.AddKV("Status", "No data")
		return p
	}
	p.AddKV("Status", status["connectionStatus"])
	p.AddKV("IP", status["externalIPAddress"])
	p.AddKV("MAC", status["MACAddress"])
	dns := strings.SplitN(status["DNSServers"], ",", 2)
	p.AddKV("DNS 1", dns[0])
	if len(dns) > 1 {
		p.AddKV("DNS 2", dns[1])
	}
	return p
}

func buildWLANPanel(wlan map[string]string, width, height int) *Panel {
	p := NewPanel("Wireless", width, height)
	if len(wlan) == 0 {
		p.AddKV("Status", "No data")
		return p
	}
	p.AddKV("SSID", wlan["SSID"])
	radio := "Off"
	if wlan["enable"] == "1" {
		radio = "On"
	}
	p.AddKV("Radio", radio)
	p.AddKV("Band", wlan["X_TP_Band"])
	p.AddKV("Channel", wlan["channel"])
	return p
}

func buildLANPanel(lan map[string]string, width, height int) *Panel {
	p := NewPanel("LAN", width, height)
	if len(lan) == 0 {
		p.AddKV("Status", "No data")
		return p
	}
	p.AddKV("IP", lan["IPInterfaceIPAddress"])
	p.AddKV("Mask", lan["IPInterfaceSubnetMask"])
	dhcp := "Off"
	if lan["DHCPServerEnable"] == "1" {
		dhcp = "On"
	}
	p.AddKV("DHCP", dhcp)
	return p
}

const (
	smsPanelH   = 14
	smsPadding  = 1
)

func buildSMSPanel(sms []map[string]string, width, cursor, scrollOffset int) *Panel {
	pad := smsPadding
	contentWidth := width - 2 - pad*2 - 4

	var rawLines []string
	if len(sms) == 0 {
		rawLines = append(rawLines, " No messages")
	} else {
		for i, msg := range sms {
			if i > 0 {
				rawLines = append(rawLines, "")
			}
			marker := " "
			if msg["unread"] == unreadTrue {
				marker = "●"
			}
			prefix := " "
			if i == cursor {
				prefix = "▶"
			}
			rawLines = append(rawLines, fmt.Sprintf("%s%s %-12s %s", prefix, marker, msg["from"], msg["receivedTime"]))
			content := sanitize(msg["content"])
			for _, wrapped := range wrapText(content, contentWidth) {
				rawLines = append(rawLines, "   "+wrapped)
			}
		}
	}

	p := NewPanel("SMS", width, smsPanelH)
	p.SetPadding(pad)
	p.SetScrollOffset(scrollOffset)
	for _, line := range rawLines {
		p.AddRaw(line)
	}
	return p
}

func sanitize(s string) string {
	s = strings.ReplaceAll(s, "\r", "")
	s = strings.ReplaceAll(s, "\n", "")
	return s
}

func wrapText(s string, maxWidth int) []string {
	var lines []string
	for runewidth.StringWidth(s) > maxWidth {
		cut := 0
		w := 0
		for _, ch := range s {
			cw := runewidth.RuneWidth(ch)
			if w+cw > maxWidth {
				break
			}
			w += cw
			cut += len(string(ch))
		}
		lines = append(lines, s[:cut])
		s = s[cut:]
	}
	if s != "" {
		lines = append(lines, s)
	}
	return lines
}

