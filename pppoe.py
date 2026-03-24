from pathlib import Path
from sys import argv
from config.config import ASN

import apis


def is_target_asn(isp: str | None, asn: str | None) -> bool:
    if not asn or not isinstance(isp, str):
        return False

    raw_asn = asn.strip().upper()
    if raw_asn.startswith("AS"):
        raw_asn = raw_asn[2:].strip()

    if not raw_asn:
        return False

    normalized_asn = f"AS{raw_asn}"

    first_token = isp.split(maxsplit=1)[0].strip().upper()

    return first_token == normalized_asn

def run_reconnection(force: bool = False, asn: str | None = ASN) -> None:
    #No providing ASN, no --force, exit.
    if asn is None and not force:
        print("No ASN provided, exiting.")
        print("Try running the script with -f or --force flag or provide an ASN with the -a or --asn flag.")
        exit(1)

    router = apis.TPLinkAPI()

    if force:
        router.make_pppoe_reconnection()
        isp = apis.check_isp_with_retries()
        if isp is not None:
            print(f"ISP after forced reconnection: {isp}")
        print("Forced reconnection completed.")
        return

    isp = apis.check_isp_with_retries()

    if is_target_asn(isp, asn):
        print(f"Current ISP: {isp}")
        print("Already connected to the desired ASN, no reconnection needed.")
        exit(0)

    print(f"Current ISP: {isp}")
    max_attempts: int = 5
    tries: int = 0
    while True:
        router.make_pppoe_reconnection()
        isp = apis.check_isp_with_retries()
        if isp is None:
            exit(1)
        print(f"ISP after reconnection: {isp}")
        tries += 1
        if is_target_asn(isp, asn):
            print("Successfully switched to the desired ASN.")
            break
        if tries >= max_attempts:
            print("Reached maximum reconnection attempts without switching to the desired ASN.")
            exit(1)


def main() -> None:
    if len(argv) == 1:
        run_reconnection()
    else:
        match argv[1]:
            case "-f" | "--force":
                print("Forcing PPPoE reconnection...")
                run_reconnection(force=True)
            case "-a" | "--asn":
                if len(argv) < 3:
                    print("Please provide an ASN after the -a or --asn flag.")
                    exit(1)
                run_reconnection(force=False, asn=argv[2])
            case _:
                print(f"Unknown argument: {argv[1]}")
                if Path(argv[0]).suffix.lower() == ".py":
                    print("Usage: python pppoe.py [-f|--force] [-a|--asn <ASN>]")
                else:
                    print("Usage: autodialer [-f|--force] [-a|--asn <ASN>]")
                exit(1)

if __name__ == "__main__":
    main()