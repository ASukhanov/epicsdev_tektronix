# epicsdev_tektronix

EPICS PVAccess device support for Tektronix MSO (Mixed Signal Oscilloscope) series.

This module provides comprehensive device support for Tektronix MSO oscilloscopes using the `epicsdev` framework. It enables remote control and monitoring of oscilloscope parameters, waveform acquisition, and measurements through EPICS PVAccess.

## Features

- **Complete oscilloscope control**: Configure timebase, trigger, channels, and acquisition modes
- **Waveform acquisition**: Retrieve and publish waveform data from all channels
- **Automatic measurements**: Calculate and publish mean, peak-to-peak, and RMS values
- **Simulation mode**: Test without hardware for development and testing
- **SCPI/VISA communication**: Standard interface for Tektronix instruments
- **PVAccess protocol**: Modern EPICS protocol with improved performance

## Installation

### Prerequisites

```bash
pip install epicsdev pyvisa pyvisa-py numpy
```

### Install from source

```bash
git clone https://github.com/ASukhanov/epicsdev_tektronix.git
cd epicsdev_tektronix
pip install -e .
```

## Usage

### Hardware Mode

Connect to a real Tektronix MSO oscilloscope:

```bash
# Using module
python -m epicsdev_tektronix.tektronix_mso -a TCPIP::192.168.1.100::INSTR -p TEK:MSO:

# Using installed command
epicsdev-tektronix -a TCPIP::192.168.1.100::INSTR -p TEK:MSO:
```

### Simulation Mode

Run without hardware for testing:

```bash
python -m epicsdev_tektronix.tektronix_mso -s -p TEK:MSO:
```

### Command-line Options

```
-a, --address       VISA resource address (e.g., TCPIP::192.168.1.100::INSTR)
-p, --prefix        PV name prefix (default: TEK:MSO:)
-v, --verbose       Verbosity level 0-3 (default: 0)
-s, --simulate      Run in simulation mode without hardware
-l, --list-dir      Directory to save PV list (default: /tmp/pvlist/)
```

## Process Variables (PVs)

The module creates the following PVs (with prefix `TEK:MSO:` by default):

### System PVs (from epicsdev)
- `host` - Server hostname
- `version` - Software version
- `status` - Server status messages
- `server` - Server control (Start/Stop/Exit)
- `verbose` - Debug verbosity level
- `sleep` - Main loop pause duration

### Horizontal (Timebase) Settings
- `horizontalScale` - Time per division (s/div)
- `recordLength` - Record length in points
- `sampleRate` - Sample rate (Sa/s)

### Trigger Settings
- `triggerLevel` - Trigger level (V)
- `triggerSource` - Trigger source (CH1/CH2/CH3/CH4/EXT)

### Acquisition Settings
- `acquireMode` - Acquisition mode (SAMple/PEAKdetect/HIRes/AVErage/ENVelope)
- `acquireState` - Acquisition state (STOP/RUN)
- `acquireSingle` - Trigger single acquisition

### Channel Settings (ch1-ch4)
For each channel (1-4):
- `ch{N}Scale` - Vertical scale (V/div)
- `ch{N}Offset` - Vertical offset (V)
- `ch{N}Coupling` - Coupling mode (DC/AC/GND)
- `ch{N}State` - Display state (OFF/ON)
- `ch{N}Waveform` - Waveform data array (V)
- `ch{N}Mean` - Mean value (V)
- `ch{N}Peak2Peak` - Peak-to-peak amplitude (V)
- `ch{N}RMS` - RMS value (V)

### Measurement PVs
- `frequency` - Measured frequency (Hz)
- `period` - Measured period (s)

### Update Controls
- `updateRate` - Waveform update rate (Hz)
- `enableUpdates` - Enable automatic waveform updates (Disabled/Enabled)

## Examples

### Basic Control with pvput/pvget

```bash
# Get oscilloscope identification
pvget TEK:MSO:host

# Enable channel 1
pvput TEK:MSO:ch1State ON

# Set channel 1 vertical scale to 1 V/div
pvput TEK:MSO:ch1Scale 1.0

# Set horizontal timebase to 1 ms/div
pvput TEK:MSO:horizontalScale 0.001

# Set trigger level to 0.5 V
pvput TEK:MSO:triggerLevel 0.5

# Enable waveform updates at 10 Hz
pvput TEK:MSO:updateRate 10.0
pvput TEK:MSO:enableUpdates Enabled

# Get waveform data
pvget TEK:MSO:ch1Waveform

# Get channel statistics
pvget TEK:MSO:ch1Mean
pvget TEK:MSO:ch1Peak2Peak
pvget TEK:MSO:ch1RMS
```

### Using with pypeto Control Interface

```bash
pip install pypeto pvplot
python -m pypeto -c config -f tektronix
```

### Using with Phoebus

Create a display file (`.bob`) referencing the PVs above for a full GUI control interface.

## Architecture

The module follows the epicsdev framework patterns:

1. **Device Interface**: `TektronixMSO` class handles SCPI/VISA communication
2. **PV Definitions**: `myPVDefs()` defines all Process Variables with metadata
3. **Setters**: Functions like `set_channel_scale()` handle PV write operations
4. **Main Loop**: Periodic waveform updates and statistics calculation
5. **Simulation**: Mock device for testing without hardware

## Supported Oscilloscopes

This module is designed for Tektronix MSO series oscilloscopes including:
- MSO5 Series (MSO54, MSO56, MSO58)
- MSO6 Series (MSO64)
- MSO4 Series (MSO44, MSO46)
- Other models supporting SCPI commands via VISA

## Development

### Running Tests

```bash
# Test in simulation mode
python -m epicsdev_tektronix.tektronix_mso -s -v 2

# Test with hardware (replace with your oscilloscope address)
python -m epicsdev_tektronix.tektronix_mso -a TCPIP::192.168.1.100::INSTR -v 2
```

### Adding New Features

1. Add PV definitions in `myPVDefs()`
2. Implement setter functions for writable PVs
3. Add SCPI commands in `TektronixMSO` class
4. Update documentation

## License

MIT License - See LICENSE file for details

## References

- [epicsdev framework](https://github.com/ASukhanov/epicsdev)
- [EPICS PVAccess](https://epics-base.github.io/p4p/)
- [PyVISA documentation](https://pyvisa.readthedocs.io/)
- [Tektronix MSO Series Programmer Manual](https://www.tek.com/)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
