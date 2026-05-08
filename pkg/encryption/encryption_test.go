package encryption

import (
	"encoding/hex"
	"strings"
	"testing"
)

const testNN = "C7DC6CB6F1979B9E1008A1F09A606B03FAF8BCDA541FC9D0C4DD3A8106D23BBF" +
	"8044D37992F727B10A90EE59EED852714E5217CFDC0C7E02137067B412CF9CCB" +
	"9F117D3E05935BD3DFE180EE0A47DF9BD1689FBD9CDC4CE2ACCBBCEE24890E24" +
	"1727A7EBCDDF3BE3552CC3AC35C8DB230B8A909697C128A72F7B86F08B6CB469"

func TestRSAEncrypt_ReturnsHexString(t *testing.T) {
	result, err := RSAEncrypt([]byte("admin"), testNN, "010001")
	if err != nil {
		t.Fatal(err)
	}
	if len(result) != 256 {
		t.Errorf("len = %d, want 256", len(result))
	}
	if _, err := hex.DecodeString(result); err != nil {
		t.Errorf("not valid hex: %v", err)
	}
}

func TestRSAEncrypt_DifferentPlaintextGivesDifferentCiphertext(t *testing.T) {
	r1, _ := RSAEncrypt([]byte("aaa"), testNN, "010001")
	r2, _ := RSAEncrypt([]byte("bbb"), testNN, "010001")
	if r1 == r2 {
		t.Error("expected different ciphertexts")
	}
}

func TestRSAEncrypt_InvalidHexNN(t *testing.T) {
	_, err := RSAEncrypt([]byte("admin"), "not-hex!", "010001")
	if err == nil {
		t.Error("expected error for invalid nn hex")
	}
	if err != nil && !strings.Contains(err.Error(), "invalid") {
		t.Errorf("error should mention 'invalid': %v", err)
	}
}

func TestRSAEncrypt_InvalidHexEE(t *testing.T) {
	_, err := RSAEncrypt([]byte("admin"), testNN, "not-hex!")
	if err == nil {
		t.Error("expected error for invalid ee hex")
	}
}

func TestEncryptCredentials_ReturnsDifferentUserAndPass(t *testing.T) {
	encUser, encPass, err := EncryptCredentials("admin", "admin", testNN, "010001")
	if err != nil {
		t.Fatal(err)
	}
	if len(encUser) != 256 {
		t.Errorf("encUser len = %d, want 256", len(encUser))
	}
	if len(encPass) != 256 {
		t.Errorf("encPass len = %d, want 256", len(encPass))
	}
	if encUser == encPass {
		t.Error("expected different user and pass ciphertexts")
	}
}
