# AutoDialer

**AutoDialer** is a cross-platform, API-driven, Python-based automation script designed to trigger PPPoE reconnection requests via your router API and rotate your public IP address automatically.

##  Why use **AutoDialer**?
* **Convenience:** Quickly rotate your public IP address (on dynamic lines) without manual router reboots.
* **Cross-Platform:** Compatible with Windows, Linux, FreeBSD, macOS, etc.
* **Automation-Ready:** Easily integrated into workflows where frequent IP changes are required.


## How to use **AutoDialer**?

### 0) Install Dependencies

#### Option A: Use `uv` (recommended)

```bash
uv sync
```

#### Option B: Use `pip` (without `uv`)

```bash
python -m venv .venv

# Windows (PowerShell)
. .\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

pip install requests "python-dotenv>=1,<2"
```

#### Option C: Install as package with `uv`

```bash
uv sync
uv pip install -e .
```

Then run via project scripts:

```bash
uv run autodialer
uv run autodialer-devices
```

### 1) Set Environment Variables
To get started, you need to configure your router's administrative credentials and your ISP's PPPoE details. These variables allow the script to authenticate and manage your connection.

| Variable | Description |
| :--- | :--- |
| **`PANEL_PASSWORD`** | The web management password for your router. |
| **`PPPOE_USERNAME`** | Your ISP-provided username. |
| **`PPPOE_PASSWORD`** | Your ISP-provided password. |
| **`ASN`** | The specific Autonomous System Number you wish to switch to. |

---

#### Quick Setup
You can quickly initialize your environment by running the following commands in your terminal. This will create (or append to) a `.env` file:

```bash
# Set your credentials
echo "PANEL_PASSWORD='your_secure_password'" >> .env
echo "PPPOE_USERNAME='your_username'" >> .env
echo "PPPOE_PASSWORD='your_pppoe_password'" >> .env
echo "ASN='your_desired_asn'" >> .env
```
**[IMPORTANT]** <br>
Keep your .env file secure! Ensure it is added to your .gitignore to prevent accidentally sharing your credentials on public repositories.

### 2)  **Run the Script** Execute the tool from your terminal:
    # Standard Python
    python pppoe.py

    # Using uv
    uv run python pppoe.py

    # Using package scripts
    uv run autodialer
    uv run autodialer-devices

    arguments:
    -f, --force: Force reconnection regardless of ASN.<br>
    -a, --asn: Pass ASN via CLI<br>

---

##  Tips

* **Specific API Focus:** The hardcoded API endpoints and JSON structures are currently based on **TP-Link** firmware logic.

---
*Thanks for using!*