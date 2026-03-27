import platform
import subprocess


def get_gateway_ip_on_windows():
    result = subprocess.run("ipconfig", capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if "Default Gateway" in line:
            ip = line.split(":")[-1].strip()
            if ip:
                return ip
    return None


def get_gateway_ip_on_linux():
    result = subprocess.run("ip route", capture_output=True, text=True, shell=True)
    for line in result.stdout.splitlines():
        if "default" in line:
            ip = line.split()[2]
            return ip
    return None


def get_gateway_ip_on_unix():
    result = subprocess.run("netstat -rn", capture_output=True, text=True, shell=True)
    for line in result.stdout.splitlines():
        if "default" in line:
            ip = line.split()[1]
            return ip
    return None


platform_system = platform.system()
if platform_system == "Windows":
    get_gateway_ip = get_gateway_ip_on_windows
elif platform_system == "Linux":
    get_gateway_ip = get_gateway_ip_on_linux
elif platform_system == "Unix" or platform_system == "macOS":
    get_gateway_ip = get_gateway_ip_on_unix
