from autodialer.apis import TPLinkAPI, check_isp_with_retries
from autodialer.apis.is_target_asn import is_target_asn
from autodialer.config.config import ASN
from sys import argv
from pathlib import Path


def _get_wan_proto(router: TPLinkAPI) -> str | None:
    status = router.tplink_get_wan_status()
    wan_status = status.get("network", {}).get("wan_status", {})
    proto = wan_status.get("proto")
    return proto if isinstance(proto, str) else None


def _apply_reconnection(router: TPLinkAPI, proto: str) -> bool:
    if proto == "pppoe":
        return router.make_pppoe_reconnection()
    if proto == "dhcp":
        router.dhcp_renew()
        return True

    print(f"Unsupported WAN protocol: {proto}")
    return False


def run_reconnection(force: bool = False, asn: str | None = ASN) -> None:
    router = TPLinkAPI()
    proto = _get_wan_proto(router)

    if proto is None:
        print("Unable to determine current WAN protocol.")
        exit(1)

    if not force and asn is None:
        print("No ASN provided, exiting.")
        print("Try running with -f/--force or provide an ASN with -a/--asn <ASN>.")
        exit(1)

    if force:
        if not _apply_reconnection(router, proto):
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
        if not _apply_reconnection(router, proto):
            exit(1)
        isp = check_isp_with_retries()
        if isp is None:
            exit(1)

        print(f"ISP after reconnection (attempt {attempt}): {isp}")
        if is_target_asn(isp, asn):
            print("Successfully switched to the desired ASN.")
            return

    print("Reached maximum reconnection attempts without switching to the desired ASN.")
    exit(1)


def main(proto: str | None) -> None:
    if len(argv) == 1:
        run_reconnection()
    else:
        match argv[1]:
            case "-f" | "--force":
                print(f"Forcing {proto or 'WAN'} reconnection...")
                run_reconnection(force=True)
            case "-a" | "--asn":
                if len(argv) < 3:
                    print("Please provide an ASN after the -a or --asn flag.")
                    exit(1)
                run_reconnection(force=False, asn=argv[2])
            case _:
                print(f"Unknown argument: {argv[1]}")
                if Path(argv[0]).suffix.lower() == ".py":
                    print("Usage: python reconnection.py [-f|--force] [-a|--asn <ASN>]")
                else:
                    print("Usage: autodialer [-f|--force] [-a|--asn <ASN>]")
                exit(1)


if __name__ == "__main__":
    proto = _get_wan_proto(TPLinkAPI())
    main(proto=proto)
