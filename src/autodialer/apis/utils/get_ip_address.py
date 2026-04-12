import requests


def get_ip_address():
    ip: str = (
        requests.get("https://api.ipify.org", proxies={"http": "", "https": ""})
        .text.replace("\n", "")
        .replace(" ", "")
    )
    return ip
