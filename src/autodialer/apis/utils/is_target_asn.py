def is_target_asn(isp: str | None, asn: str | None) -> bool:
    if not asn or not isinstance(isp, str):
        return False

    raw_asn = asn.strip().upper()
    if raw_asn.startswith("AS"):
        raw_asn = raw_asn[2:].strip()
    if not raw_asn:
        return False

    normalized_asn = f"AS{raw_asn}"

    tokens = isp.split()
    if not tokens:
        return False
    first_token = tokens[0].upper()

    return first_token == normalized_asn
