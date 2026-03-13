import time
import requests
import os

requests.certs.verify = False

def check_ISP():
    response = requests.get(f"https://ipinfo.io/json",proxies={"http": None, "https": None},timeout=5)
    data = response.json()
    print(f"ISP: {data.get('org')}")
    return data.get("org")


def login_router(password) -> str:
    url = "http://192.168.1.1"
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
    url = f"http://192.168.1.1/stok={stok}/ds"
    payload = {
        "protocol": {
            "wan": {"wan_type": "pppoe"},
            "pppoe": {"username": username, "password": password}
        },
        "method": "set"
    }
    
    response = requests.post(url, json=payload)
    print(response.text)

def pppoe(stok,action):
    url = f"http://192.168.1.1/stok={stok}/ds"
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
    ISP = check_ISP()
    while not ISP.startswith("AS9808"):
        print(f"Current ISP: {ISP}")
        panel_password = os.getenv("PANEL_PASSWORD")
        pppoe_username = os.getenv("PPPOE_USERNAME")
        pppoe_password = os.getenv("PPPOE_PASSWORD")
        stok = login_router(panel_password)
        set_credentials(pppoe_username, pppoe_password, stok)
        pppoe(stok,"connect")
        # Wait for a time to make sure DHCP has assgined a new IP address
        time.sleep(30)
        pppoe(stok,"disconnect")