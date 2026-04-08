# Getting Started

## Requirements

- Python 3.10 or newer
- Access to the local network where the router is reachable from the machine running AutoDialer
- Router panel credentials
- A router and firmware combination that matches one of the implemented integrations

## Installation

### pip

```bash
pip install autodialer
```

### uv

```bash
uv tool install autodialer
autodialer --force
```

### Local development install

```bash
python -m venv .venv

# Windows (PowerShell)
. .\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

python -m pip install -e .
```

## Configuration

AutoDialer reads configuration from a `.env` file in the current working directory.

| Variable | Required | Notes |
| :--- | :--- | :--- |
| `PANEL_USERNAME` | No | Defaults to `admin`. |
| `PANEL_PASSWORD` | Yes | Required by the implemented ASUS and TP-Link integrations. |
| `PPPOE_USERNAME` | No | PPPoE username override. Used by the TP-Link integration when updating saved PPPoE credentials before reconnecting. |
| `PPPOE_PASSWORD` | No | PPPoE password override. Used by the TP-Link integration when updating saved PPPoE credentials before reconnecting. |
| `ASN` | No | Present in configuration code, but the CLI currently expects `--asn <ASN>` explicitly instead of reading the target ASN from `.env`. |

Example:

```dotenv
PANEL_USERNAME=admin
PANEL_PASSWORD=your_router_panel_password
PPPOE_USERNAME=your_pppoe_username
PPPOE_PASSWORD=your_pppoe_password
ASN=AS9929
```

## CLI Usage

### Force a reconnection

```bash
autodialer --force
```

This reconnects the active WAN link once and then checks the ISP/org value reported by `https://ipinfo.io/json`.

### Reconnect until the target ASN is reached

```bash
autodialer --asn AS9929
```

In ASN mode:

- AutoDialer checks the current ISP first.
- If the current ISP already matches the requested ASN, the process exits successfully without reconnecting.
- Otherwise it reconnects and re-checks the ISP.
- The current implementation makes up to 5 reconnection attempts before exiting with an error.

### Show connected devices

```bash
autodialer-devices
```

This prints a table containing hostname, IP, MAC address, connection type, transfer rates, and whether the device is the current machine.

## Current CLI Constraints

- `autodialer` without arguments is currently treated as invalid usage.
- `autodialer-devices` does not currently accept vendor flags; vendor selection is automatic.
- Router support depends on the vendor fingerprint and the specific firmware behavior matching the implementation in this repository.

## Troubleshooting

If AutoDialer fails before reconnecting, the most common causes are:

- `PANEL_PASSWORD` is missing or incorrect.
- The default gateway could not be detected on the current operating system.
- The router vendor could not be fingerprinted from the router's web interface.
- The router vendor was detected, but the firmware/API does not match the implemented request payloads closely enough.
- The public IP check against `ipinfo.io` failed because the connection was unavailable or timed out.
