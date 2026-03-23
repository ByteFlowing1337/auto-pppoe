from sys import argv
from apis.routers.tplink.get_devices import tplink_get_devices

def main() -> None:
    if len(argv) == 1:
        tplink_get_devices()
    else:
        match argv[1]:
            case "--tplink":
                tplink_get_devices()
            case _:
                print(f"Unknown argument: {argv[1]}")
                if argv[0].startswith("python"):
                    print("Usage: python get_devices.py [--tplink]")
                else:
                    print("Usage: get_devices [--tplink]")
                exit(1)


if __name__ == "__main__":
    main()