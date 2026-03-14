# auto-pppoe

**auto-pppoe** is a Python-based automation script designed to trigger PPPoE reconnection requests via your router's API to rotate your public IP address automatically.

###  Why use **auto-pppoe**?
* **Convenience:** Quickly rotate your public IP address (on dynamic lines) without manual router reboots.
* **Cross-Platform:** Compatible with Windows, Linux, FeeeBSD, macOS, etc.
* **Automation-Ready:** Easily integrated into workflows where frequent IP changes are required.

### How to use **auto-pppoe**?

#### 1. Set Environment Variables
To get started, you need to configure your router's administrative credentials and your ISP's PPPoE details. These variables allow the script to authenticate and manage your connection.

| Variable | Description |
| :--- | :--- |
| **`ROUTER_PASSWORD`** | The web management password for your router. |
| **`PPPOE_USER`** | Your ISP-provided username. |
| **`PPPOE_PASS`** | Your ISP-provided password. |
| **`ASN`** | The specific Autonomous System Number you wish to switch to. |

---

#### Quick Setup
You can quickly initialize your environment by running the following commands in your terminal. This will create (or append to) a `.env` file:

```bash
# Set your credentials
echo "ROUTER_PASSWORD='your_secure_password'" >> .env
echo "PPPOE_USER='your_username'" >> .env
echo "PPPOE_PASS='your_pppoe_password'" >> .env
echo "ASN='your_desired_asn'" >> .env
```
[IMPORTANT] <br>
Keep your .env file secure! Ensure it is added to your .gitignore to prevent accidentally sharing your credentials on public repositories.

#### 2.  **Run the Script** Execute the tool from your terminal:
    python pppoe.py

    arguments:
    -f, --force: Force to make a DHCP request regardless ASN.<br>
    -a, --asn: Provide a ASN in form of CLI argument instead environment variable.<br>

---

###  Tips

* **TP-Link Focus:** The hardcoded API endpoints and JSON structures are currently based on **TP-Link** firmware logic.

---
*Thanks for using!*