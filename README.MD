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
    * You can use commands:
    ```bash
    echo PANEL_PASSWORD="your_secure_password" >> .env
    echo PPPOE_USERNAME="your_username" >> .env
    echo PPPOE_PASSWORD="your_pppoe_password" >> .env
    ```
2.  **Run the Script** Execute the tool from your terminal:
    ```bash
    python pppoe.py
    ```

---

###  Tips

* **TP-Link Focus:** The hardcoded API endpoints and JSON structures are currently based on **TP-Link** firmware logic.
* **ASN Targeting:** This tool is currently optimized to seek a specific **ASN**(i.e., China Mobile). You may need to modify the logic if you simply want any new IP address regardless of the network provider.

---
*Thanks for using!*