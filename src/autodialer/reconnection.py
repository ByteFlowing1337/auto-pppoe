from autodialer.apis import TPLinkAPI, check_isp_with_retries
from autodialer.apis.utils.is_target_asn import is_target_asn
from autodialer.config.config import ASN
from sys import argv
from pathlib import Path


class Reconnection:
    def __init__(self, router: TPLinkAPI):
        self.router = router

    def _get_wan_proto(self) -> str | None:
        status = self.router.tplink_get_wan_status()
        wan_status = status.get("network", {}).get("wan_status", {})
        proto = wan_status.get("proto")
        return proto if isinstance(proto, str) else None

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
            print(f"Forced {proto} reconnection completed.")
            return

        isp = check_isp_with_retries()
        if isp is None:
            exit(1)

        print(f"Current ISP: {isp}")
        if is_target_asn(isp, asn):
            print("Already connected to the desired ASN, no reconnection needed.")
            exit(0)

        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            if not self._apply_reconnection(proto):
                exit(1)
            isp = check_isp_with_retries()
            if isp is None:
                exit(1)

            print(f"ISP after reconnection (attempt {attempt}): {isp}")
            if is_target_asn(isp, asn):
                print("Successfully switched to the desired ASN.")
                return

        print(
            "Reached maximum reconnection attempts without switching to the desired ASN."
        )
        exit(1)

    def main(self, proto: str | None) -> None:
        match argv[1]:
            case "-f" | "--force":
                print(f"Forcing {proto or 'WAN'} reconnection...")
                self.run_reconnection(force=True)
            case "-a" | "--asn":
                self.run_reconnection(force=False, asn=argv[2])



def parse_arguments() -> None:
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
            return
        case _:
            print(f"Unknown argument: {argv[1]}")
            if Path(argv[0]).suffix.lower() == ".py":
                print("Usage: python reconnection.py [-f|--force] [-a|--asn <ASN>]")
            else:
                print("Usage: autodialer [-f|--force] [-a|--asn <ASN>]")
            exit(1)


def main():
    parse_arguments()  # Parse arguments before initializing the router
    router = TPLinkAPI()
    reconnection = Reconnection(router)
    reconnection.main(reconnection._get_wan_proto())


if __name__ == "__main__":
    main()
