import requests
import time

def check_isp(verbose: bool = False) -> str | None:
    """Return the current ISP org string, or ``None`` on failure.

    Network/request and JSON parsing errors are handled internally: a
    diagnostic message is printed and the error does not propagate to
    callers.

    Args:
        verbose: If True, print ``"ISP: <org>"`` on successful lookup.
            This flag does not affect error reporting; error messages are
            always printed on failure.
    """
    try:
        response = requests.get(f"https://ipinfo.io/json",
                                proxies={"http": "", "https": ""}, timeout=4)
        response.raise_for_status()
        data = response.json()
        org = data.get("org")
        if verbose:
            print(f"ISP: {org}")
        return org if isinstance(org, str) else None

    except requests.Timeout:
        print("Timeout while checking ISP. Check your internet connection.")
        return None
    except requests.RequestException as e:
        print(f"Error checking ISP: {e}")
        return None
    except ValueError:
        print("Error parsing ISP response.")
        return None

def check_isp_with_retries(retries: int = 3, delay: int = 5) -> str | None:
    """Check the ISP with retries if the initial check fails.

    Args:
        retries: The number of times to retry checking the ISP if it fails.
        delay: The delay in seconds between retries.

    Returns:
        The ISP string if successful, or None if all retries fail.
    """
    isp = check_isp()
    if isp is not None:
        return isp


    if retries < 0 or delay <= 0:
        print("Invalid retries or delay parameters. Retries and delay should be positive integers.")
        return None

    if retries == 0:
        print("No retries configured, exiting.")
        return None

    print("Failed to check ISP, retrying...")
    for _ in range(retries):
        time.sleep(delay)
        isp = check_isp()
        if isp is not None:
            return isp

    print("Failed to verify ISP after retries. Check your internet connection.")
    return None