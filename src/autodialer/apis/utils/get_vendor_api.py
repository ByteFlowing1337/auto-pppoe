from functools import lru_cache
from importlib import import_module
from inspect import getmembers, isclass
from pathlib import Path

from autodialer.apis.utils.check_vendor import check_router_vendor


def _read_supported_vendors(candidate: type) -> tuple[str, ...]:
    supported_vendors = getattr(candidate, "SUPPORTED_VENDORS", ())
    if isinstance(supported_vendors, str):
        return (supported_vendors,)
    if isinstance(supported_vendors, (list, set, tuple)):
        return tuple(
            vendor for vendor in supported_vendors if isinstance(vendor, str) and vendor
        )
    return ()


def _iter_router_api_module_names() -> list[str]:
    routers_dir = Path(__file__).resolve().parent.parent / "routers"
    module_names: list[str] = []

    for api_file in routers_dir.rglob("*_api.py"):
        if api_file.name == "base_api.py":
            continue

        relative_path = api_file.relative_to(routers_dir).with_suffix("")
        module_suffix = ".".join(relative_path.parts)
        module_names.append(f"autodialer.apis.routers.{module_suffix}")

    return sorted(module_names)


@lru_cache(maxsize=1)
def _get_vendor_api_registry() -> dict[str, type]:
    registry: dict[str, type] = {}

    for module_name in _iter_router_api_module_names():
        module = import_module(module_name)

        for _, candidate in getmembers(module, isclass):
            if candidate.__module__ != module.__name__:
                continue

            supported_vendors = _read_supported_vendors(candidate)
            if not supported_vendors:
                continue

            for supported_vendor in supported_vendors:
                vendor_key = supported_vendor.casefold()
                existing_candidate = registry.get(vendor_key)
                if existing_candidate not in (None, candidate):
                    raise ValueError(
                        f"Duplicate router API mapping for vendor '{supported_vendor}'."
                    )
                registry[vendor_key] = candidate

    return registry


def get_vendor_api() -> type | None:
    vendor = check_router_vendor()
    if vendor is None:
        return None

    api_class = _get_vendor_api_registry().get(vendor.casefold())
    if api_class is None:
        print(f"No API implementation for vendor: {vendor}")

    return api_class
