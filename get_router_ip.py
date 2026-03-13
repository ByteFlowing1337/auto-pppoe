import platform

def get_router_ip_on_windows():
    import subprocess
    result = subprocess.run("ipconfig", capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if "Default Gateway" in line:
            ip = line.split(":")[-1].strip()
            if ip:
                return ip
    return None

def get_router_ip_on_linux():
    import subprocess
    result = subprocess.run("ip route", capture_output=True, text=True, shell=True)
    for line in result.stdout.splitlines():
        if "default" in line:
            ip = line.split()[2]
            return ip
    return None

##This should also work on macOS
def get_router_ip_on_freebsd():
    import subprocess
    result = subprocess.run("netstat -rn", capture_output=True, text=True, shell=True)
    for line in result.stdout.splitlines():
        if "default" in line:
            ip = line.split()[1]
            return ip
    return None

platform_system = platform.system()
if platform_system == "Windows":
    get_router_ip = get_router_ip_on_windows
elif platform_system == "Linux":
    get_router_ip = get_router_ip_on_linux
elif platform_system == "Darwin" or platform_system == "FreeBSD":
    get_router_ip = get_router_ip_on_freebsd