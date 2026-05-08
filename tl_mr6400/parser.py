import re


def parse_rsa_keys(response: str) -> tuple[str, str]:
    ee_match = re.search(r'var ee="(.*?)"', response)
    nn_match = re.search(r'var nn="(.*?)"', response)
    if not ee_match or not nn_match:
        raise ValueError("Failed to parse RSA keys from response")
    return ee_match.group(1), nn_match.group(1)


def parse_token(html: str) -> str:
    match = re.search(r"var\s+token\s*=\s*[\"']?(\w+)", html)
    if not match:
        raise ValueError("Failed to extract token from page")
    return match.group(1)


def parse_entries(text: str) -> list[dict]:
    messages = []
    current = {}
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("[error]"):
            break
        if line.startswith("["):
            if current:
                messages.append(current)
            current = {}
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            current[key] = val
    if current:
        messages.append(current)
    return messages
