package dashboard

import (
	"strings"
	"testing"

	"github.com/mattn/go-runewidth"
)

func testData() (status, wlan, lan map[string]string, sms []map[string]string) {
	status = map[string]string{
		"sigLevel": "3", "netType": "3", "rfInfoRsrp": "-92",
		"rfInfoRsrq": "-11", "rfInfoSnr": "36", "rfInfoBand": "3",
		"connectionStatus": "Connected", "externalIPAddress": "10.2.153.186",
		"MACAddress": "AA:BB", "DNSServers": "1.1.1.1,8.8.8.8",
	}
	wlan = map[string]string{"SSID": "TP-Link", "enable": "1", "X_TP_Band": "2.4GHz", "channel": "11"}
	lan = map[string]string{"IPInterfaceIPAddress": "192.168.1.1", "IPInterfaceSubnetMask": "255.255.255.0", "DHCPServerEnable": "1"}
	sms = []map[string]string{
		{"from": "935188", "content": "Hello", "receivedTime": "2026-05-08 12:06", "unread": "1"},
		{"from": "091234", "content": "World", "receivedTime": "2026-05-07 10:09", "unread": "0"},
	}
	return
}

func TestRenderDashboard_ContainsAllSections(t *testing.T) {
	status, wlan, lan, sms := testData()
	output := RenderDashboard(status, sms, wlan, lan, 80, -1, 0)
	if !strings.Contains(output, "LTE Signal") {
		t.Error("missing LTE Signal")
	}
	if !strings.Contains(output, "WAN") {
		t.Error("missing WAN")
	}
	if !strings.Contains(output, "Wireless") {
		t.Error("missing Wireless")
	}
	if !strings.Contains(output, "LAN") {
		t.Error("missing LAN")
	}
	if !strings.Contains(output, "SMS") {
		t.Error("missing SMS")
	}
}

func TestRenderDashboard_ContainsData(t *testing.T) {
	status, wlan, lan, sms := testData()
	output := RenderDashboard(status, sms, wlan, lan, 80, -1, 0)
	for _, want := range []string{"10.2.153.186", "TP-Link", "192.168.1.1", "935188", "Hello"} {
		if !strings.Contains(output, want) {
			t.Errorf("missing %q", want)
		}
	}
}

func TestRenderDashboard_ConsistentWidth(t *testing.T) {
	status, wlan, lan, sms := testData()
	output := RenderDashboard(status, sms, wlan, lan, 80, -1, 0)
	for _, line := range strings.Split(output, "\n") {
		if line == "" {
			continue
		}
		w := runewidth.StringWidth(line)
		if w != 80 {
			t.Errorf("width = %d, want 80: %q", w, line)
		}
	}
}

func TestRenderDashboard_NarrowStacked(t *testing.T) {
	status, wlan, lan, sms := testData()
	output := RenderDashboard(status, sms, wlan, lan, 50, -1, 0)
	for _, line := range strings.Split(output, "\n") {
		if line == "" {
			continue
		}
		w := runewidth.StringWidth(line)
		if w != 50 {
			t.Errorf("width = %d, want 50: %q", w, line)
		}
	}
	// LTE and WAN should NOT be on same line
	for _, line := range strings.Split(output, "\n") {
		if strings.Contains(line, "LTE") && strings.Contains(line, "WAN") {
			t.Error("LTE and WAN should not be on same line in narrow")
		}
	}
}

func TestRenderDashboard_SMSHasPaddingBetweenMessages(t *testing.T) {
	status, wlan, lan, sms := testData()
	output := RenderDashboard(status, sms, wlan, lan, 80, -1, 0)
	lines := strings.Split(output, "\n")

	// Find content lines of first SMS, then check there's a blank line before second SMS sender
	foundFirst := false
	for i, line := range lines {
		if strings.Contains(line, "091234") {
			// The line before the second sender should be a blank-ish padding line
			if i > 0 {
				prev := strings.Trim(lines[i-1], "│ ")
				if prev != "" && strings.Contains(lines[i-1], "Hello") {
					t.Error("no padding between SMS messages — content of first SMS directly above second sender")
				}
			}
			foundFirst = true
			break
		}
	}
	if !foundFirst {
		t.Error("second SMS sender not found")
	}
}

func TestRenderDashboard_WideSideBySide(t *testing.T) {
	status, wlan, lan, sms := testData()
	output := RenderDashboard(status, sms, wlan, lan, 80, -1, 0)
	found := false
	for _, line := range strings.Split(output, "\n") {
		if strings.Contains(line, "LTE") && strings.Contains(line, "WAN") {
			found = true
			break
		}
	}
	if !found {
		t.Error("LTE and WAN should be on same line in wide")
	}
}
