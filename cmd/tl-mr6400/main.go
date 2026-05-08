package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/recca0120/tl-mr6400/pkg/client"
	"github.com/recca0120/tl-mr6400/pkg/dashboard"
)

const (
	defaultRouterURL  = "http://192.168.1.1"
	defaultPassword   = "admin"
	defaultEnvFile    = ".env"
	defaultPage       = 1
	defaultInterval   = 5
)

func loadEnv(path string) {
	data, err := os.ReadFile(path)
	if err != nil {
		return
	}
	for _, line := range strings.Split(string(data), "\n") {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") || !strings.Contains(line, "=") {
			continue
		}
		k, v, _ := strings.Cut(line, "=")
		if os.Getenv(strings.TrimSpace(k)) == "" {
			os.Setenv(strings.TrimSpace(k), strings.TrimSpace(v))
		}
	}
}

func createClient() *client.Client {
	loadEnv(defaultEnvFile)
	url := os.Getenv("ROUTER_URL")
	if url == "" {
		url = defaultRouterURL
	}
	password := os.Getenv("ROUTER_PASSWORD")
	if password == "" {
		password = defaultPassword
	}
	c := client.New(url, password, client.WithHTTP(client.NewHTTPClient()))
	if err := c.Login(); err != nil {
		fmt.Fprintf(os.Stderr, "Login failed: %v\n", err)
		os.Exit(1)
	}
	return c
}

func usage() {
	fmt.Println("Usage: tl-mr6400 <command> [options]")
	fmt.Println()
	fmt.Println("Commands:")
	fmt.Println("  sms [--page N] [--json]    Read SMS messages")
	fmt.Println("  status [--json]            Show router status")
	fmt.Println("    --lte                    LTE signal only")
	fmt.Println("    --wlan                   Wireless only")
	fmt.Println("    --lan                    LAN only")
	fmt.Println("  dashboard [--interval N]   Live dashboard")
	os.Exit(1)
}

func main() {
	if len(os.Args) < 2 {
		cmdDashboard(defaultInterval)
		return
	}

	cmd := os.Args[1]
	args := os.Args[2:]
	jsonOut := hasFlag(args, "--json")

	switch cmd {
	case "sms":
		page := defaultPage
		if v, ok := flagValue(args, "--page"); ok {
			page, _ = strconv.Atoi(v)
		}
		cmdSMS(page, jsonOut)
	case "status":
		cmdStatus(args, jsonOut)
	case "dashboard":
		interval := defaultInterval
		if v, ok := flagValue(args, "--interval"); ok {
			interval, _ = strconv.Atoi(v)
		}
		cmdDashboard(interval)
	default:
		usage()
	}
}

func hasFlag(args []string, flag string) bool {
	for _, a := range args {
		if a == flag {
			return true
		}
	}
	return false
}

func flagValue(args []string, flag string) (string, bool) {
	for i, a := range args {
		if a == flag && i+1 < len(args) {
			return args[i+1], true
		}
	}
	return "", false
}

func cmdSMS(page int, jsonOut bool) {
	c := createClient()
	msgs := c.GetSMS(page)
	if jsonOut {
		printJSON(msgs)
		return
	}
	if len(msgs) == 0 {
		fmt.Println("No SMS messages found.")
		return
	}
	for _, msg := range msgs {
		status := "[read]"
		if msg["unread"] == "1" {
			status = "[unread]"
		}
		fmt.Printf("%s %s  From: %s\n", status, msg["receivedTime"], msg["from"])
		fmt.Printf("  %s\n\n", msg["content"])
	}
}

func cmdStatus(args []string, jsonOut bool) {
	c := createClient()
	showLTE := hasFlag(args, "--lte")
	showWLAN := hasFlag(args, "--wlan")
	showLAN := hasFlag(args, "--lan")
	showAll := !showLTE && !showWLAN && !showLAN

	if jsonOut {
		cmdStatusJSON(c, showAll, showLTE, showWLAN, showLAN)
		return
	}
	cmdStatusText(c, showAll, showLTE, showWLAN, showLAN)
}

func cmdStatusJSON(c *client.Client, showAll, showLTE, showWLAN, showLAN bool) {
	if showAll {
		printJSON(map[string]interface{}{
			"lte": c.GetStatus(), "wlan": c.GetWLAN(), "lan": c.GetLAN(),
		})
		return
	}
	if showLTE {
		printJSON(c.GetStatus())
	} else if showWLAN {
		printJSON(c.GetWLAN())
	} else if showLAN {
		printJSON(c.GetLAN())
	}
}

func cmdStatusText(c *client.Client, showAll, showLTE, showWLAN, showLAN bool) {
	if showAll || showLTE {
		status := c.GetStatus()
		if len(status) == 0 {
			fmt.Println("Failed to get status.")
			return
		}
		fmt.Println("=== LTE Signal ===")
		printKV(status, "netType", "sigLevel", "rfInfoRssi", "rfInfoRsrp", "rfInfoRsrq", "rfInfoSnr", "rfInfoBand")
		fmt.Println("\n=== WAN Connection ===")
		printKV(status, "connectionStatus", "externalIPAddress", "defaultGateway", "DNSServers", "MACAddress")
	}
	if showAll || showWLAN {
		wlan := c.GetWLAN()
		if len(wlan) > 0 {
			fmt.Println("\n=== Wireless ===")
			printKV(wlan, "SSID", "enable", "X_TP_Band", "channel", "X_TP_Bandwidth")
		}
	}
	if showAll || showLAN {
		lan := c.GetLAN()
		if len(lan) > 0 {
			fmt.Println("\n=== LAN ===")
			printKV(lan, "IPInterfaceIPAddress", "IPInterfaceSubnetMask", "X_TP_MACAddress", "DHCPServerEnable", "minAddress", "maxAddress")
		}
	}
}

func printKV(m map[string]string, keys ...string) {
	maxLen := 0
	for _, k := range keys {
		if len(k) > maxLen {
			maxLen = len(k)
		}
	}
	for _, k := range keys {
		v := m[k]
		if v == "" {
			v = "?"
		}
		fmt.Printf("  %-*s : %s\n", maxLen, k, v)
	}
}

func printJSON(v interface{}) {
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	enc.SetEscapeHTML(false)
	enc.Encode(v)
}

func cmdDashboard(interval int) {
	c := createClient()
	if err := dashboard.RunDashboard(c, time.Duration(interval)*time.Second); err != nil {
		fmt.Fprintf(os.Stderr, "Dashboard error: %v\n", err)
		os.Exit(1)
	}
}
