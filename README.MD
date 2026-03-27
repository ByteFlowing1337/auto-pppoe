# AutoDialer

AutoDialer is a cross-platform Python CLI package for router APIs, designed to rotate public IP addresses automatically and streamline router interactions.

## Why AutoDialer?
- Convenient IP rotation on dynamic lines without manual router reboot.
- Cross-platform (Windows, Linux, macOS, FreeBSD).
- CLI-first usage for scripts and automation.

## Installation

### Using pip (recommended)
```bash
pip install autodialer
```

### Using uv
If you prefer `uv` for faster environment and dependency management:

```bash
# install from PyPI
uv tool install autodialer

# run directly
autodialer
```

For local development:

```bash
uv sync
uv pip install -e .
uv run autodialer --help
```

### From source (development)
```bash
python -m venv .venv

# Windows (PowerShell)
. .\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

python -m pip install -e .
```

## Configuration

Create a `.env` file in your working directory:

| Variable | Description |
| :--- | :--- |
| `PANEL_PASSWORD` | Router panel password |
| `PPPOE_USERNAME` | ISP PPPoE username (required for PPPoE lines) |
| `PPPOE_PASSWORD` | ISP PPPoE password (required for PPPoE lines) |
| `ASN` | Target ASN (optional unless not using `--force`) |

Example:
```bash
PANEL_PASSWORD='your_router_panel_password'
PPPOE_USERNAME='your_pppoe_username'
PPPOE_PASSWORD='your_pppoe_password'
ASN='AS9929'
```

## Usage

After installation, use the CLI directly:

```bash
autodialer
autodialer --force
autodialer --asn AS9929
autodialer-devices --tplink
```

Arguments:
- `-f`, `--force`: force reconnection even if ASN is already matched.
- `-a`, `--asn`: target ASN (for example `AS9929` or `9929`).

Behavior:
- AutoDialer detects current WAN protocol and applies matching reconnection action.
- PPPoE uses disconnect/connect flow with configured PPPoE credentials.
- DHCP uses DHCP renew flow and shares the same ASN/check/retry control logic.

## Notes
- Current API payloads are primarily tailored for TP-Link router firmware behavior.
- Keep `.env` private and never commit credentials.

---
Thanks for using AutoDialer.