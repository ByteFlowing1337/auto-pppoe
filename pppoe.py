from sys import argv
from utils import ASN, check_isp, make_pppoe_reconnection

def main(FORCE=False, ASN=ASN):
    isp = check_isp()
    #No providing ASN, no --force, exit.
    if ASN is None and not FORCE:
        print("No ASN provided, exiting.")
        print("Try running the script with -f or --force flag or provide an ASN with the -a or --asn flag.")
        exit(1)

    while not isp.startswith(f"{ASN}"):
        print(f"Current ISP: {isp}")
        make_pppoe_reconnection()
        isp = check_isp()
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