package encryption

import (
	"crypto/rand"
	"crypto/rsa"
	"encoding/base64"
	"fmt"
	"math/big"
)

func RSAEncrypt(plaintext []byte, nn, ee string) (string, error) {
	n := new(big.Int)
	if _, ok := n.SetString(nn, 16); !ok {
		return "", fmt.Errorf("invalid hex for nn: %q", nn)
	}
	e := new(big.Int)
	if _, ok := e.SetString(ee, 16); !ok {
		return "", fmt.Errorf("invalid hex for ee: %q", ee)
	}

	pub := &rsa.PublicKey{N: n, E: int(e.Int64())}
	keyLen := (pub.N.BitLen() + 7) / 8

	ciphertext, err := rsa.EncryptPKCS1v15(rand.Reader, pub, plaintext)
	if err != nil {
		return "", err
	}

	return fmt.Sprintf("%0*x", keyLen*2, new(big.Int).SetBytes(ciphertext)), nil
}

func EncryptCredentials(username, password, nn, ee string) (encUser, encPass string, err error) {
	b64Pass := base64.StdEncoding.EncodeToString([]byte(password))

	encUser, err = RSAEncrypt([]byte(username), nn, ee)
	if err != nil {
		return "", "", err
	}
	encPass, err = RSAEncrypt([]byte(b64Pass), nn, ee)
	if err != nil {
		return "", "", err
	}
	return encUser, encPass, nil
}
