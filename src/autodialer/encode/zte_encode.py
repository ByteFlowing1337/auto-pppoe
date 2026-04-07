import hashlib


def zte_security_encode(password: str | None, login_token: str | None) -> str:
    if password is None or login_token is None:
        raise ValueError("Password and login token must not be None.")
    combined = password + login_token
    hash_object = hashlib.sha256(combined.encode())
    return hash_object.hexdigest()
