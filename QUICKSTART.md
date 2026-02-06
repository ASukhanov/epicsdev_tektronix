# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/ASukhanov/epicsdev_tektronix.git
cd epicsdev_tektronix

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Running the Server

### Simulation Mode (No Hardware Required)

```bash
# Start the server in simulation mode
python -m epicsdev_tektronix.tektronix_mso -s -p TEK:MSO: -v 1
```

### Hardware Mode

```bash
# Connect to a real oscilloscope
python -m epicsdev_tektronix.tektronix_mso -a TCPIP::192.168.1.100::INSTR -p TEK:MSO:
```

## Testing the Server

Open a new terminal and test with pvget/pvput:

```bash
# Get server information
pvget TEK:MSO:host
pvget TEK:MSO:version

# Configure Channel 1
pvput TEK:MSO:ch1State ON
pvput TEK:MSO:ch1Scale 1.0

# Enable waveform updates
pvput TEK:MSO:updateRate 2.0
pvput TEK:MSO:enableUpdates Enabled

# Monitor waveform
pvget TEK:MSO:ch1Waveform
pvget TEK:MSO:ch1Mean
```

## Using the Example Client

```bash
# In a new terminal
cd examples
python basic_usage.py -p TEK:MSO:
```

## Common VISA Resource Addresses

- **Ethernet**: `TCPIP::192.168.1.100::INSTR`
- **USB**: `USB0::0x0699::0x0522::SERIALNUM::INSTR`
- **GPIB**: `GPIB0::1::INSTR`

## Finding Your Oscilloscope

Use pyvisa to find available instruments:

```python
import pyvisa
rm = pyvisa.ResourceManager('@py')
print(rm.list_resources())
```

## Troubleshooting

### Cannot connect to oscilloscope
- Check network connectivity: `ping 192.168.1.100`
- Verify oscilloscope IP address in settings
- Ensure firewall allows port 4000 (VXI-11) or 5025 (socket)

### pyvisa not found
```bash
pip install pyvisa pyvisa-py
```

### Server already running
```bash
# Check for running instances
ps aux | grep tektronix_mso

# Stop existing instance
pkill -f tektronix_mso
```

## Advanced Usage

### Custom PV Prefix
```bash
python -m epicsdev_tektronix.tektronix_mso -s -p SCOPE1:
```

### High Verbosity for Debugging
```bash
python -m epicsdev_tektronix.tektronix_mso -s -p TEK:MSO: -v 3
```

### Custom PV List Location
```bash
python -m epicsdev_tektronix.tektronix_mso -s -p TEK:MSO: -l /path/to/pvlists/
```

## Next Steps

- See `examples/basic_usage.py` for client example
- Read the full documentation in `README.md`
- Create custom control scripts using p4p.client.thread
