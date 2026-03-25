from autodialer.apis import TPLinkAPI

def print_devices_table(devices: list) -> None:
    if not devices:
        print("No devices connected.")
        return
    header = f"{'HOSTNAME':25} {'IP':15} {'MAC':18} {'TYPE':9} {'UP':>6} {'DOWN':>6} {'ME':>3}"
    print(header)
    print("-" * len(header))
    for d in devices:
        print(
            f"{d['hostname'][:25]:25} "
            f"{d['ip'][:15]:15} "
            f"{d['mac'][:18]:18} "
            f"{d['type'][:9]:9} "
            f"{d['up_kbps']:>6} "
            f"{d['down_kbps']:>6} "
            f"{'Y' if d['is_current'] else 'N':>3}"
        )

def tplink_get_devices():
    router = TPLinkAPI()
    devices = router.get_connected_devices()
    print_devices_table(devices)