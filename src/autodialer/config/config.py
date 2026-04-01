import os
import dotenv  # type: ignore[import-not-found]

dotenv.load_dotenv()

PANEL_USERNAME: str = os.getenv("PANEL_USERNAME") or "admin"
PANEL_PASSWORD: str | None = os.getenv("PANEL_PASSWORD") or None
PPPOE_USERNAME: str | None = os.getenv("PPPOE_USERNAME") or None
PPPOE_PASSWORD: str | None = os.getenv("PPPOE_PASSWORD") or None
ASN: str | None = os.getenv("ASN") or None
