import os
import base64


def _pkcs1_v1_5_pad(plaintext: bytes, key_length: int) -> bytes:
    max_msg_len = key_length - 11
    if len(plaintext) > max_msg_len:
        raise ValueError("Message too long for key size")

    padding_len = key_length - len(plaintext) - 3
    padding = b""
    while len(padding) < padding_len:
        byte = os.urandom(1)
        if byte != b"\x00":
            padding += byte

    return b"\x00\x02" + padding + b"\x00" + plaintext


def rsa_encrypt(plaintext: bytes, nn: str, ee: str) -> str:
    n = int(nn, 16)
    e = int(ee, 16)
    key_length = (n.bit_length() + 7) // 8

    padded = _pkcs1_v1_5_pad(plaintext, key_length)
    m = int.from_bytes(padded, "big")
    c = pow(m, e, n)

    return format(c, f"0{key_length * 2}x")


def encrypt_credentials(
    username: str, password: str, nn: str, ee: str
) -> tuple[str, str]:
    b64_pass = base64.b64encode(password.encode()).decode()
    enc_user = rsa_encrypt(username.encode(), nn, ee)
    enc_pass = rsa_encrypt(b64_pass.encode(), nn, ee)
    return enc_user, enc_pass
