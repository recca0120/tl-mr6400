package parser

import (
	"errors"
	"regexp"
	"strings"
)

const errorPrefix = "[error]"

var (
	eeRegex    = regexp.MustCompile(`var ee="(.*?)"`)
	nnRegex    = regexp.MustCompile(`var nn="(.*?)"`)
	tokenRegex = regexp.MustCompile(`var\s+token\s*=\s*["']?(\w+)`)
	stackRegex = regexp.MustCompile(`^\[([0-9,]+)\]`)
)

func ParseRSAKeys(response string) (ee, nn string, err error) {
	eeMatch := eeRegex.FindStringSubmatch(response)
	nnMatch := nnRegex.FindStringSubmatch(response)
	if eeMatch == nil || nnMatch == nil {
		return "", "", errors.New("failed to parse RSA keys from response")
	}
	return eeMatch[1], nnMatch[1], nil
}

func ParseToken(html string) (string, error) {
	match := tokenRegex.FindStringSubmatch(html)
	if match == nil {
		return "", errors.New("failed to extract token from page")
	}
	return match[1], nil
}

func ParseEntries(text string) []map[string]string {
	var entries []map[string]string
	var current map[string]string

	for _, line := range strings.Split(text, "\n") {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, errorPrefix) {
			break
		}
		if strings.HasPrefix(line, "[") {
			if current != nil && len(current) > 0 {
				entries = append(entries, current)
			}
			current = make(map[string]string)
			if m := stackRegex.FindStringSubmatch(line); m != nil {
				current["__stack"] = m[1]
			}
			continue
		}
		if idx := strings.Index(line, "="); idx >= 0 {
			key := line[:idx]
			val := line[idx+1:]
			current[key] = val
		}
	}
	if current != nil && len(current) > 0 {
		entries = append(entries, current)
	}
	return entries
}
