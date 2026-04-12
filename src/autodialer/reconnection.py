import logging

from autodialer.apis.routers.base_api import RouterAPI
from autodialer.apis import check_isp_with_retries
from autodialer.apis.utils.is_target_asn import is_target_asn
from autodialer.config.config import ASN
from autodialer.apis.utils.get_vendor_api import get_vendor_api
from autodialer.apis.utils.get_ip_address import get_ip_address
from sys import argv
from pathlib import Path


logger = logging.getLogger(__name__)


class Reconnection:
    def __init__(self, router: RouterAPI):
        self.router = router

    def _get_wan_proto(self) -> str | None:
        return self.router.get_wan_proto()

    def _apply_reconnection(self, proto: str) -> bool:
        if proto == "pppoe":
            return self.router.make_pppoe_reconnection()
        if proto == "dhcp":
            return self.router.dhcp_renew()

        logger.error("Unsupported WAN protocol: %s", proto)
        return False

    def run_reconnection(
        self, force: bool = False, asn: str | None = ASN, change: bool = False
    ) -> None:

        proto = self._get_wan_proto()

        if proto is None:
            logger.error("Unable to determine current WAN protocol.")
            exit(1)

        if force:
            if not self._apply_reconnection(proto):
                exit(1)
            isp = check_isp_with_retries()
            if isp is not None:
                logger.info("ISP after forced reconnection: %s", isp)
            return

        if change:
            current_ip: str = get_ip_address()
            after_reconnection_ip: str = current_ip
            attemps = 0
            while (current_ip == after_reconnection_ip) and attemps < 5:
                if not self._apply_reconnection(proto):
                    exit(1)
                after_reconnection_ip = get_ip_address()
                attemps += 1
            if attemps == 5:
                logger.error("Failed to change IP address after 5 attempts.")
                exit(1)

        max_attempts = 5
        for _ in range(max_attempts):
            if not self._apply_reconnection(proto):
                exit(1)
            isp = check_isp_with_retries()
            if isp is None:
                exit(1)

            if is_target_asn(isp, asn):
                return

        logger.error(
            "Reached maximum reconnection attempts without switching to the desired ASN."
        )
        exit(1)

    def main(self) -> None:
        match argv[1]:
            case "-f" | "--force":
                self.run_reconnection(force=True)
            case "-a" | "--asn":
                self.run_reconnection(force=False, asn=argv[2])
            case "-c" | "--change":
                self.run_reconnection(force=False, change=True)


def parse_arguments(asn: str | None) -> None:
    if len(argv) == 1:
        logger.error("No ASN provided, exiting.")
        logger.error(
            "Try running with -f/--force or provide an ASN with -a/--asn <ASN>."
        )
        exit(1)

    match argv[1]:
        case "-f" | "--force":
            return
        case "-a" | "--asn":
            if len(argv) < 3:
                logger.error("Please provide an ASN after the -a or --asn flag.")
                exit(1)
            isp = check_isp_with_retries()
            if isp is None:
                exit(1)

            if is_target_asn(isp, asn):
                exit(0)
            return
        case "-c" | "--change":
            return
        case _:
            logger.error("Unknown argument: %s", argv[1])
            if Path(argv[0]).suffix.lower() == ".py":
                logger.error(
                    "Usage: python reconnection.py [-f|--force] [-a|--asn <ASN>]"
                )
            else:
                logger.error("Usage: autodialer [-f|--force] [-a|--asn <ASN>]")
            exit(1)


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parse_arguments(
        asn=argv[2] if len(argv) > 2 else ASN
    )  # Parse arguments before initializing the router
    vendor = get_vendor_api()
    if vendor is None:
        logger.error("Unable to determine router vendor. Exiting.")
        exit(1)
    router = vendor()
    reconnection = Reconnection(router)
    reconnection.main()


if __name__ == "__main__":
    main()
