# Welcome
AutoDialer is a cross-platform Python CLI package for router APIs, designed to rotate public IP addresses automatically and streamline router interactions.

## Why AutoDialer?
- Convenient IP rotation on dynamic lines without manual router reboot.
- Cross-platform (Windows, Linux, macOS, BSD).
- CLI-first usage for scripts and automation.

## Installation

```bash
pip install autodialer
```

## Notes
- **Only** TP-Link, ZTE and ASUS routers are supported now.
- Keep `.env` private and never commit credentials.

## Configuration

Create a `.env` file in your working directory:

| Variable | Description |
| :--- | :--- |
| `PANEL_USERNAME` | Router panel username (defaults to `admin`) |
| `PANEL_PASSWORD` | Router panel password |
| `PPPOE_USERNAME` | ISP PPPoE username override (optional) |
| `PPPOE_PASSWORD` | ISP PPPoE password override (optional) |
| `ASN` | Optional library-level default ASN. The CLI currently expects the ASN to be passed explicitly with `--asn <ASN>`. |

Example:
```bash
PANEL_USERNAME='admin'
PANEL_PASSWORD='your_router_panel_password'
PPPOE_USERNAME='your_pppoe_username'
PPPOE_PASSWORD='your_pppoe_password'
ASN='AS9929'
```

## Usage

After installation, use the CLI directly:

```bash
autodialer --force
autodialer --asn AS9929
autodialer-devices
```

Arguments:
- `-f`, `--force`: force reconnection even if ASN is already matched.
- `-a`, `--asn`: target ASN (for example `AS9929` or `9929`).

Behavior:
- `autodialer` currently requires either `--force` or `--asn <ASN>`.
- AutoDialer detects current WAN protocol and applies matching reconnection action.
- PPPoE uses disconnect/connect flow and reuses the router's saved credentials by default.
- If `PPPOE_USERNAME` and `PPPOE_PASSWORD` are set, AutoDialer updates the router's PPPoE config before reconnecting.
- DHCP uses DHCP renew flow and shares the same ASN/check/retry control logic.

## Documentation

- Setup and CLI details: [`getting-started.md`](getting-started.md)
- Detection and reconnection flow: [`how-it-works.md`](how-it-works.md)

---
Thanks for using AutoDialer.
