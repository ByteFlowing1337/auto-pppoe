from autodialer.apis.routers.base_api import RouterAPI
from autodialer.apis import check_isp_with_retries
from autodialer.apis.utils.is_target_asn import is_target_asn
from autodialer.config.config import ASN
from autodialer.apis.utils.get_vendor_api import get_vendor_api
from sys import argv
from pathlib import Path


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

        print(f"Unsupported WAN protocol: {proto}")
        return False

    def run_reconnection(self, force: bool = False, asn: str | None = ASN) -> None:

        proto = self._get_wan_proto()

        if proto is None:
            print("Unable to determine current WAN protocol.")
            exit(1)

        if force:
            if not self._apply_reconnection(proto):
                exit(1)
            isp = check_isp_with_retries()
            if isp is not None:
                print(f"ISP after forced reconnection: {isp}")
            return

        max_attempts = 5
        for _ in range(1, max_attempts + 1):
            if not self._apply_reconnection(proto):
                exit(1)
            isp = check_isp_with_retries()
            if isp is None:
                exit(1)

            if is_target_asn(isp, asn):
                return

        print(
            "Reached maximum reconnection attempts without switching to the desired ASN."
        )
        exit(1)

    def main(self) -> None:
        match argv[1]:
            case "-f" | "--force":
                self.run_reconnection(force=True)
            case "-a" | "--asn":
                self.run_reconnection(force=False, asn=argv[2])


def parse_arguments(asn: str | None) -> None:
    if len(argv) == 1:
        print("No ASN provided, exiting.")
        print("Try running with -f/--force or provide an ASN with -a/--asn <ASN>.")
        exit(1)

    match argv[1]:
        case "-f" | "--force":
            return
        case "-a" | "--asn":
            if len(argv) < 3:
                print("Please provide an ASN after the -a or --asn flag.")
                exit(1)
            isp = check_isp_with_retries()
            if isp is None:
                exit(1)

            if is_target_asn(isp, asn):
                print("Already connected to the desired ASN, no reconnection needed.")
                exit(0)
            return
        case _:
            print(f"Unknown argument: {argv[1]}")
            if Path(argv[0]).suffix.lower() == ".py":
                print("Usage: python reconnection.py [-f|--force] [-a|--asn <ASN>]")
            else:
                print("Usage: autodialer [-f|--force] [-a|--asn <ASN>]")
            exit(1)


def main():
    parse_arguments(
        asn=argv[2] if len(argv) > 2 else ASN
    )  # Parse arguments before initializing the router
    vendor = get_vendor_api()
    if vendor is None:
        print("Unable to determine router vendor. Exiting.")
        exit(1)
    router = vendor()
    reconnection = Reconnection(router)
    reconnection.main()


if __name__ == "__main__":
    main()
