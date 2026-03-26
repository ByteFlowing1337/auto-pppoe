from pathlib import Path
from sys import argv
from .reconnection import run_reconnection


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
