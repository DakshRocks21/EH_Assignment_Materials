import base64


with open("phase3.ps1", "r", encoding="utf-8") as f:
    text = f.read()
utf16le_bytes = text.encode("utf-16le")
encoded = base64.b64encode(utf16le_bytes).decode("utf-8")


def beta(data):
    encoded = bytes([b ^ 0x20 for b in data.encode('utf-8')])
    return encoded.hex().upper()


def sigma(prayers):
    decoded = bytes([b ^ 0x20 for b in bytes.fromhex(prayers)])
    return decoded.decode('utf-8')


print(beta(encoded)) 


