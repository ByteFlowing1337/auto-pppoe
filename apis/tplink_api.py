import os
import requests
import encode

from dotenv import load_dotenv
from apis.get_gateway import get_gateway_ip
from time import sleep

from config.config import PLANE_PASSWORD, PPPOE_USERNAME, PPPOE_PASSWORD






"""
    The payload below is based on TP-Link,it may not works on other brands of routers.
    If so, you need to replace the payload.
"""
class TPLinkAPI:
    """A class to interact with TP-Link routers using their API.
    
    Attributes:

        router_ip: The IP address of the router, obtained from the default gateway, 
        using get_gateway_ip().

        password: The **encoded** password for logging into the router.

        username: The PPPoE username for authentication.

        pppoe_password: The PPPoE password for authentication.

        stok: The session token obtained after logging into the router, used for authenticated requests.
    """
    router_ip: str
    password: str
    username: str
    pppoe_password: str
    stok: str | None = None

    def __init__(self):
        self.router_ip = get_gateway_ip()
        if not self.router_ip:
            print("Could not determine router IP address.")
            exit(1)
        self.password = encode.tplink_security_encode(PLANE_PASSWORD)
        self.username = PPPOE_USERNAME
        self.pppoe_password = PPPOE_PASSWORD
        self.stok = self.__login_router()

    def __login_router(self) -> str:
        url = f"http://{self.router_ip}"
        payload = {
            "method": "do",
            "login": {
                "password": self.password
            }
        }
        response = requests.post(url, json=payload)
        json_response = response.json()
        if json_response.get("error_code") == 0 and json_response.get("stok") != None:
            print("Login successful.")
            return json_response.get("stok")
        else:
            print("Login failed.")
            print(response.text)
            exit(1) 


    def set_credentials(self):
        url = f"http://{self.router_ip}/stok={self.stok}/ds"
        payload = {
            "protocol": {
                "wan": {"wan_type": "pppoe"},
                "pppoe": {"username": self.username, "password": self.pppoe_password}
            },
            "method": "set"
        }
        
        response = requests.post(url, json=payload)
        json_response = response.json()
        if json_response.get("error_code") == 0:
            print("PPPoE credentials set successfully.")
        else:
            print("Failed to set PPPoE credentials.")
            print(response.text)
            exit(1)
            
    def pppoe(self, action):
        url = f"http://{self.router_ip}/stok={self.stok}/ds"
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
        json_response = response.json()
        if json_response.get("error_code") == 0:
            print(f"PPPoE {action} successful.")
        else:
            print(f"Failed to {action} PPPoE.")
            print(response.text)
            exit(1)

    def make_pppoe_reconnection(self):
        self.set_credentials()
        self.pppoe("disconnect")
        # Wait for a time to make sure DHCP has assigned a new IP address
        sleep(30)
        self.pppoe("connect")