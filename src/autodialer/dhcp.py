from .apis import TPLinkAPI


def dhcp_renew():
    router = TPLinkAPI()
    router.dhcp_renew()


if __name__ == "__main__":
    dhcp_renew()
