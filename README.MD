# auto-pppoe

**auto-pppoe** is a Python-based automation script designed to trigger PPPoE reconnection requests via your router's API to rotate your public IP address automatically.

###  Why use **auto-pppoe**?
* **Convenience:** Quickly rotate your public IP address (on dynamic lines) without manual router reboots.
* **Cross-Platform:** Compatible with Windows, Linux, FeeeBSD, macOS, etc.
* **Automation-Ready:** Easily integrated into workflows where frequent IP changes are required.

###  How to use **auto-pppoe**?

1.  **Set Environment Variables** Configure your router's administrative credentials and your ISP's PPPoE details:
    * `ROUTER_PASSWORD`: Your router's web management password.
    * `PPPOE_USER`: Your ISP-provided username.
    * `PPPOE_PASS`: Your ISP-provided password.
    * `ASN` : Your desired ASN that you want change to. <br>
    You can use commands:
    ```bash
    echo PANEL_PASSWORD="your_secure_password" >> .env
    echo PPPOE_USERNAME="your_username" >> .env
    echo PPPOE_PASSWORD="your_pppoe_password" >> .env
    echo ASN="your_desired_asn" >> .env
    ```
2.  **Run the Script** Execute the tool from your terminal:
    ```bash
    python pppoe.py
    ```
    arguments:<br>
    -f, --force: Force to make a DHCP request regardless ASN.<br>
    -a, --asn: Provide a ASN in form of CLI argument instead environment variable.<br>

---

###  Tips

* **TP-Link Focus:** The hardcoded API endpoints and JSON structures are currently based on **TP-Link** firmware logic.

---
*Thanks for using!*