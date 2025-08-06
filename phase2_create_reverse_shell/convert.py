import base64
import sys

if len(sys.argv) != 2:
    print("Usage: python convert.py <path_to_script >")
    sys.exit(1) 

with open(sys.argv[1], "r", encoding="utf-8") as f:
    text = f.read()
utf16le_bytes = text.encode("utf-16le")
encoded = base64.b64encode(utf16le_bytes).decode("utf-8")


def beta(data): 
    """Encodes the input string using a custom XOR operation."""
    encoded = bytes([b ^ 0x20 for b in data.encode('utf-8')])
    return encoded.hex().upper()


def sigma(prayers): 
    """Decodes the input hex string using a custom XOR operation."""
    decoded = bytes([b ^ 0x20 for b in bytes.fromhex(prayers)])
    return decoded.decode('utf-8')


print(beta(encoded)) 


