import logging
import requests
import time


logger = logging.getLogger(__name__)


def check_isp(verbose: bool = False) -> str | None:
    """Return the current ISP org string, or ``None`` on failure.

    Network/request and JSON parsing errors are handled internally: a
    diagnostic message is logged and the error does not propagate to
    callers.

    Args:
        verbose: If True, log ``"ISP: <org>"`` on successful lookup.
            This flag does not affect error reporting; error messages are
            always logged on failure.
    """
    try:
        response = requests.get(
            "https://ipinfo.io/json", proxies={"http": "", "https": ""}, timeout=4
        )
        response.raise_for_status()
        data = response.json()
        org = data.get("org")
        if not isinstance(org, str):
            logger.error(
                "Unexpected ISP response format: missing or invalid 'org' field."
            )
            return None
        if verbose:
            logger.info("ISP: %s", org)
        return org

    except requests.Timeout:
        logger.error("Timeout while checking ISP. Check your internet connection.")
        return None
    except requests.RequestException as e:
        logger.error("Error checking ISP: %s", e)
        return None
    except ValueError:
        logger.error("Error parsing ISP response.")
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
        logger.error(
            "Invalid retries or delay parameters. Retries must be non-negative and delay must be a positive integer."
        )
        return None

    if retries == 0:
        logger.warning("ISP check failed. No retries left.")
        return None

    for _ in range(retries):
        time.sleep(delay)
        isp = check_isp()
        if isp is not None:
            return isp

    logger.error("Failed to verify ISP after retries. Check your internet connection.")
    return None
