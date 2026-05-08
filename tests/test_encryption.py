import base64
from tl_mr6400.encryption import rsa_encrypt, encrypt_credentials


class TestRsaEncrypt:
    def test_returns_hex_string(self):
        ee = "010001"
        nn = (
            "C7DC6CB6F1979B9E1008A1F09A606B03FAF8BCDA541FC9D0C4DD3A8106D23BBF"
            "8044D37992F727B10A90EE59EED852714E5217CFDC0C7E02137067B412CF9CCB"
            "9F117D3E05935BD3DFE180EE0A47DF9BD1689FBD9CDC4CE2ACCBBCEE24890E24"
            "1727A7EBCDDF3BE3552CC3AC35C8DB230B8A909697C128A72F7B86F08B6CB469"
        )
        result = rsa_encrypt(b"admin", nn, ee)
        assert isinstance(result, str)
        assert len(result) == 256
        int(result, 16)

    def test_different_plaintext_gives_different_ciphertext(self):
        nn = (
            "C7DC6CB6F1979B9E1008A1F09A606B03FAF8BCDA541FC9D0C4DD3A8106D23BBF"
            "8044D37992F727B10A90EE59EED852714E5217CFDC0C7E02137067B412CF9CCB"
            "9F117D3E05935BD3DFE180EE0A47DF9BD1689FBD9CDC4CE2ACCBBCEE24890E24"
            "1727A7EBCDDF3BE3552CC3AC35C8DB230B8A909697C128A72F7B86F08B6CB469"
        )
        r1 = rsa_encrypt(b"aaa", nn, "010001")
        r2 = rsa_encrypt(b"bbb", nn, "010001")
        assert r1 != r2


class TestEncryptCredentials:
    def test_returns_encrypted_user_and_pass(self):
        nn = (
            "C7DC6CB6F1979B9E1008A1F09A606B03FAF8BCDA541FC9D0C4DD3A8106D23BBF"
            "8044D37992F727B10A90EE59EED852714E5217CFDC0C7E02137067B412CF9CCB"
            "9F117D3E05935BD3DFE180EE0A47DF9BD1689FBD9CDC4CE2ACCBBCEE24890E24"
            "1727A7EBCDDF3BE3552CC3AC35C8DB230B8A909697C128A72F7B86F08B6CB469"
        )
        enc_user, enc_pass = encrypt_credentials("admin", "admin", nn, "010001")
        assert len(enc_user) == 256
        assert len(enc_pass) == 256
        assert enc_user != enc_pass
