import time
import requests
import os
from dotenv import load_dotenv
from get_router_ip import get_router_ip
from tplink_security_encode import tplink_security_encode

load_dotenv()
requests.certs.verify = False
PLANE_PASSWORD = os.getenv("PANEL_PASSWORD")
PPPOE_USERNAME = os.getenv("PPPOE_USERNAME")
PPPOE_PASSWORD = os.getenv("PPPOE_PASSWORD")

router_ip = get_router_ip()
if not router_ip:
    print("Could not determine router IP address.")
    exit(1)

def check_ISP():
    response = requests.get(f"https://ipinfo.io/json",proxies={"http": None, "https": None},timeout=5)
    data = response.json()
    print(f"ISP: {data.get('org')}")
    return data.get("org")

#The payload below is based on TP-Link,
#it may not works on other brands of routers.
#If so, you need to replace the payload.
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
    print(json_response)
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
    print(response.text)


if __name__ == "__main__":
    #AS9808 is China Mobile, so we only run this code if the ISP is not China Mobile
    login_router(tplink_security_encode(PLANE_PASSWORD))
    ISP = check_ISP()
    while not ISP.startswith("AS9808"):
        print(f"Current ISP: {ISP}")
        stok = login_router(tplink_security_encode(PLANE_PASSWORD))
        set_credentials(PPPOE_USERNAME, PPPOE_PASSWORD, stok)
        pppoe("connect", stok)
        # Wait for a time to make sure DHCP has assgined a new IP address
        time.sleep(30)
        pppoe("disconnect", stok)