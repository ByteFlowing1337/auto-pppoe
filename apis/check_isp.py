import requests
def check_isp(verbose=False) -> str:
    response = requests.get(f"https://ipinfo.io/json",proxies={"http": "", "https": ""},timeout=4)
    data = response.json()
    if verbose:
        print(f"ISP: {data.get('org')}")
    return data.get("org")