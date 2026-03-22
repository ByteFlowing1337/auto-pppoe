from sys import argv
from apis.routers.tplink.get_devices import tplink_get_devices

if __name__ == "__main__":
    if len(argv) == 1:
        tplink_get_devices()
    else:
        match argv[1]:
            case "--tplink":
                tplink_get_devices()
            case _:
                print(f"Unknown argument: {argv[1]}")
                print("Usage: python get_devices.py [--tplink]")
        