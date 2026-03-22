import os
import dotenv

dotenv.load_dotenv()

PLANE_PASSWORD = os.getenv("PANEL_PASSWORD")
PPPOE_USERNAME = os.getenv("PPPOE_USERNAME")
PPPOE_PASSWORD = os.getenv("PPPOE_PASSWORD")
ASN: str | None = os.getenv("ASN") if os.getenv("ASN") else None