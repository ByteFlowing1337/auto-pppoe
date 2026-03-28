from autodialer.apis.utils.check_router_vendor import check_router_vendor


def get_vendor_api():
    vendor = check_router_vendor()
    if vendor == "TP-Link":
        from autodialer.apis.routers.tplink.tplink_api import TPLinkAPI

        return TPLinkAPI
    # TODO: Add more vendors and their corresponding API classes here as needed
    print(f"No API implementation for vendor: {vendor}")
    return None
