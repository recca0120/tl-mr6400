package parser

import (
	"testing"
)

func TestParseRSAKeys_ExtractsEeAndNn(t *testing.T) {
	response := "var ee=\"010001\";\nvar nn=\"AABB\";\nvar userSetting=1;\n$.ret=0;"
	ee, nn, err := ParseRSAKeys(response)
	if err != nil {
		t.Fatal(err)
	}
	if ee != "010001" {
		t.Errorf("ee = %q, want %q", ee, "010001")
	}
	if nn != "AABB" {
		t.Errorf("nn = %q, want %q", nn, "AABB")
	}
}

func TestParseRSAKeys_ErrorOnMissing(t *testing.T) {
	_, _, err := ParseRSAKeys("some garbage")
	if err == nil {
		t.Error("expected error, got nil")
	}
}

func TestParseToken_ExtractsToken(t *testing.T) {
	html := `var token="abc123def"; some other stuff`
	token, err := ParseToken(html)
	if err != nil {
		t.Fatal(err)
	}
	if token != "abc123def" {
		t.Errorf("token = %q, want %q", token, "abc123def")
	}
}

func TestParseToken_WithoutQuotes(t *testing.T) {
	html := "var token=abc123def; some other stuff"
	token, err := ParseToken(html)
	if err != nil {
		t.Fatal(err)
	}
	if token != "abc123def" {
		t.Errorf("token = %q, want %q", token, "abc123def")
	}
}

func TestParseToken_ErrorOnMissing(t *testing.T) {
	_, err := ParseToken("<html>no token here</html>")
	if err == nil {
		t.Error("expected error, got nil")
	}
}

func TestParseEntries_MultipleMessages(t *testing.T) {
	response := "[1,0,0,0,0,0]1\nindex=124\nfrom=935188\ncontent=Hello World\nreceivedTime=2026-05-08 12:06:08\nunread=1\n[2,0,0,0,0,0]1\nindex=123\nfrom=091234\ncontent=Test msg\nreceivedTime=2026-05-07 10:09:22\nunread=0\n[error]0\n"

	entries := ParseEntries(response)
	if len(entries) != 2 {
		t.Fatalf("len = %d, want 2", len(entries))
	}
	if entries[0]["from"] != "935188" {
		t.Errorf("from = %q, want %q", entries[0]["from"], "935188")
	}
	if entries[0]["content"] != "Hello World" {
		t.Errorf("content = %q, want %q", entries[0]["content"], "Hello World")
	}
	if entries[0]["unread"] != "1" {
		t.Errorf("unread = %q, want %q", entries[0]["unread"], "1")
	}
	if entries[1]["from"] != "091234" {
		t.Errorf("from = %q, want %q", entries[1]["from"], "091234")
	}
}

func TestParseEntries_Empty(t *testing.T) {
	entries := ParseEntries("[error]0\n")
	if len(entries) != 0 {
		t.Errorf("len = %d, want 0", len(entries))
	}
}

func TestParseEntries_ValueWithEquals(t *testing.T) {
	response := "[1,0,0,0,0,0]1\ncontent=a=b=c\n[error]0\n"
	entries := ParseEntries(response)
	if entries[0]["content"] != "a=b=c" {
		t.Errorf("content = %q, want %q", entries[0]["content"], "a=b=c")
	}
}

func TestParseEntries_PreservesStack(t *testing.T) {
	response := "[1,0,0,0,0,0]1\nindex=124\n[2,0,0,0,0,0]1\nindex=123\n[error]0\n"
	entries := ParseEntries(response)
	if entries[0]["__stack"] != "1,0,0,0,0,0" {
		t.Errorf("stack = %q, want %q", entries[0]["__stack"], "1,0,0,0,0,0")
	}
	if entries[1]["__stack"] != "2,0,0,0,0,0" {
		t.Errorf("stack = %q, want %q", entries[1]["__stack"], "2,0,0,0,0,0")
	}
}

func TestParseEntries_MixedEntries(t *testing.T) {
	response := "[2,1,0,0,0,0]0\nsigLevel=2\nconnStat=4\n[2,1,1,0,0,0]1\nconnectionStatus=Connected\nexternalIPAddress=10.2.153.186\n[error]0\n"
	entries := ParseEntries(response)
	if len(entries) != 2 {
		t.Fatalf("len = %d, want 2", len(entries))
	}
	if entries[0]["sigLevel"] != "2" {
		t.Errorf("sigLevel = %q, want %q", entries[0]["sigLevel"], "2")
	}
	if entries[1]["externalIPAddress"] != "10.2.153.186" {
		t.Errorf("ip = %q, want %q", entries[1]["externalIPAddress"], "10.2.153.186")
	}
}
