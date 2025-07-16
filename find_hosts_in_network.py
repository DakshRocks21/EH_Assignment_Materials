
import os

for i in range(1, 255):
    ip = f"10.10.1.{i}"
    response = os.system(f"ping -n 1 {ip} > null.txt")

    with open("null.txt", "r") as file:
        content = file.read()
        if "TTL" in content:
            print(f"{ip} is up")
        else:
            print(f"{ip} is down")
            