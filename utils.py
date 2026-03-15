import os
import requests

from dotenv import load_dotenv
from tplink_security_encode import tplink_security_encode
from get_router_ip import get_router_ip
from time import sleep

router_ip = get_router_ip()
if not router_ip:
    print("Could not determine router IP address.")
    exit(1)

load_dotenv()

PLANE_PASSWORD = os.getenv("PANEL_PASSWORD")
PPPOE_USERNAME = os.getenv("PPPOE_USERNAME")
PPPOE_PASSWORD = os.getenv("PPPOE_PASSWORD")
ASN: str | None = os.getenv("ASN") if os.getenv("ASN") else None

def check_isp():
    response = requests.get(f"https://ipinfo.io/json",proxies={"http": "", "https": ""},timeout=5)
    data = response.json()
    print(f"ISP: {data.get('org')}")
    return data.get("org")

"""
    The payload below is based on TP-Link,it may not works on other brands of routers.
    If so, you need to replace the payload.
"""
def login_router(password) -> str:
    url = f"http://{router_ip}"
    payload = {
        "method": "do",
        "login": {
            "password": password
        }
    }
    response = requests.post(url, json=payload)
    json_response = response.json()
    if '0' in response.text:
        print("Login router successful.")
    else:
        print("Failed to login router.")
        print(response.text)
        exit(1)
    return json_response.get("stok")


def set_credentials(username, password, stok):
    url = f"http://{router_ip}/stok={stok}/ds"
    payload = {
        "protocol": {
            "wan": {"wan_type": "pppoe"},
            "pppoe": {"username": username, "password": password}
        },
        "method": "set"
    }
    
    response = requests.post(url, json=payload)
    if '0' in response.text:
        print("PPPoE credentials set successfully.")
    else:
        print("Failed to set PPPoE credentials.")
        print(response.text)

def pppoe(action, stok):
    url = f"http://{router_ip}/stok={stok}/ds"
    payload = {
        "network": {
            "change_wan_status": {
                "proto": "pppoe",
                "operate": action
            }
        },
            "method": "do"
    }
    response = requests.post(url, json=payload)
    if '0' in response.text:
        print(f"PPPoE {action} successful.")
    else:
        print(f"Failed to {action} PPPoE.")
        print(response.text)

def make_pppoe_reconnection():
    stok = login_router(tplink_security_encode(PLANE_PASSWORD))
    set_credentials(PPPOE_USERNAME, PPPOE_PASSWORD, stok)
    pppoe("disconnect", stok)
    # Wait for a time to make sure DHCP has assigned a new IP address
    sleep(30)
    pppoe("connect", stok)