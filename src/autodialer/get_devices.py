import logging
from pathlib import Path
from sys import argv
from autodialer.apis.utils.get_vendor_api import get_vendor_api
from autodialer.apis.routers.base_api import RouterAPI


logger = logging.getLogger(__name__)

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if len(argv) == 1:
        vendor = get_vendor_api()
        router: RouterAPI | None = vendor() if vendor is not None else None
        if router is not None:
            devices = router.get_connected_devices()
            from autodialer.apis.utils.print_devices_table import (
                print_devices_table,
            )

            print_devices_table(devices)
        else:
            logger.error("No router API available to fetch connected devices.")
    else:
        match argv[1]:
            case _:
                logger.error("Unknown argument: %s", argv[1])
                if Path(argv[0]).suffix.lower() == ".py":
                    logger.error("Usage: python get_devices.py")
                else:
                    logger.error("Usage: autodialer-devices")
                exit(1)


if __name__ == "__main__":
    main()
