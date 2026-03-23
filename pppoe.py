from sys import argv
from config.config import ASN

import apis

def run_reconnection(force: bool = False, asn: str | None = ASN) -> None:
    isp = apis.check_isp()
    #No providing ASN, no --force, exit.
    if asn is None and not force:
        print("No ASN provided, exiting.")
        print("Try running the script with -f or --force flag or provide an ASN with the -a or --asn flag.")
        exit(1)

    router = apis.TPLinkAPI()

    if asn and isp.startswith(f"{asn}"):
        print(f"Current ISP: {isp}")
        print("Already connected to the desired ASN, no reconnection needed.")
        exit(0)

    print(f"Current ISP: {isp}")
    while not isp.startswith(f"{asn}"):
        router.make_pppoe_reconnection()
        isp = apis.check_isp()
        print(f"ISP after reconnection: {isp}")
        if isp.startswith(f"{asn}"):
            print("Successfully switched to the desired ASN.")
        if force:
            print("Forced reconnection completed.")
            break


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
                if argv[0].startswith("python"):
                    print("Usage: python pppoe.py [-f|--force] [-a|--asn <ASN>]")
                else:
                    print("Usage: autodialer [-f|--force] [-a|--asn <ASN>]")
                exit(1)

if __name__ == "__main__":
    main()