from sys import argv
from config.config import ASN

import apis

def main(FORCE=False, ASN=ASN):
    isp = apis.check_isp()
    #No providing ASN, no --force, exit.
    if ASN is None and not FORCE:
        print("No ASN provided, exiting.")
        print("Try running the script with -f or --force flag or provide an ASN with the -a or --asn flag.")
        exit(1)

    router = apis.TPLinkAPI()

    if ASN and isp.startswith(f"{ASN}"):
        print(f"Current ISP: {isp}")
        print("Already connected to the desired ASN, no reconnection needed.")
        exit(0)

    print(f"Current ISP: {isp}")
    while not isp.startswith(f"{ASN}"):
        router.make_pppoe_reconnection()
        isp = apis.check_isp()
        print(f"ISP after reconnection: {isp}")
        if isp.startswith(f"{ASN}"):
            print("Successfully switched to the desired ASN.")
        if FORCE:
            print("Forced reconnection completed.")
            break

if __name__ == "__main__":
    if len(argv) == 1:
        main()
    else:
        match argv[1]:
            case "-f" | "--force":
                print("Forcing PPPoE reconnection...")
                main(FORCE=True)
            case "-a" | "--asn":
                if len(argv) < 3:
                    print("Please provide an ASN after the -a or --asn flag.")
                    exit(1)
                main(FORCE=False, ASN=argv[2])