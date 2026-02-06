"""EPICS PVAccess server for Tektronix MSO oscilloscopes.

This module provides device support for Tektronix MSO (Mixed Signal Oscilloscope)
series using the epicsdev framework. It communicates with the oscilloscope via
VISA/SCPI commands and publishes waveform data and settings as EPICS PVs.

Usage:
    python -m epicsdev_tektronix.tektronix_mso -a TCPIP::192.168.1.100::INSTR -p TEK:MSO:

Example with simulation:
    python -m epicsdev_tektronix.tektronix_mso -s -p TEK:MSO:
"""
# pylint: disable=invalid-name
__version__ = 'v0.1.0 26-02-06'

import sys
import time
import argparse
import numpy as np
from epicsdev import epicsdev

# Try to import pyvisa, but allow simulation mode without it
try:
    import pyvisa
    PYVISA_AVAILABLE = True
except ImportError:
    PYVISA_AVAILABLE = False
    print("Warning: pyvisa not available. Only simulation mode will work.")


class TektronixMSO:
    """Interface to Tektronix MSO oscilloscope via VISA."""
    
    def __init__(self, resource_address=None, simulate=False):
        """Initialize oscilloscope connection.
        
        Args:
            resource_address: VISA resource string (e.g., 'TCPIP::192.168.1.100::INSTR')
            simulate: If True, run in simulation mode without hardware
        """
        self.simulate = simulate
        self.instrument = None
        self.connected = False
        
        if not simulate:
            if not PYVISA_AVAILABLE:
                raise RuntimeError("pyvisa is required for hardware connection. "
                                   "Use --simulate flag for simulation mode.")
            try:
                rm = pyvisa.ResourceManager('@py')
                self.instrument = rm.open_resource(resource_address)
                self.instrument.timeout = 5000  # 5 second timeout
                # Test connection
                idn = self.query('*IDN?')
                epicsdev.printi(f"Connected to: {idn}")
                self.connected = True
            except Exception as e:
                epicsdev.printe(f"Failed to connect to oscilloscope: {e}")
                self.connected = False
        else:
            epicsdev.printi("Running in simulation mode")
            self.connected = True
    
    def write(self, command):
        """Send command to oscilloscope."""
        if self.simulate:
            epicsdev.printv(f"SIM: write {command}")
            return
        if self.instrument:
            try:
                self.instrument.write(command)
            except Exception as e:
                epicsdev.printw(f"Write failed: {e}")
    
    def query(self, command):
        """Query oscilloscope and return response."""
        if self.simulate:
            epicsdev.printv(f"SIM: query {command}")
            # Return simulated responses for common queries
            if command == '*IDN?':
                return "TEKTRONIX,MSO58,SIMULATED,CF:91.1CT FV:1.0.0"
            elif 'HORIZONTAL:RECORDLENGTH?' in command:
                return "10000"
            elif ':SCALE?' in command:
                return "1.0"
            elif ':POSITION?' in command or ':OFFSET?' in command:
                return "0.0"
            return "0"
        
        if self.instrument:
            try:
                return self.instrument.query(command).strip()
            except Exception as e:
                epicsdev.printw(f"Query failed: {e}")
                return ""
        return ""
    
    def query_binary(self, command):
        """Query oscilloscope for binary data."""
        if self.simulate:
            # Return simulated waveform data
            return np.random.randn(1000) * 0.1
        
        if self.instrument:
            try:
                return self.instrument.query_binary_values(command, 
                                                          datatype='f',
                                                          is_big_endian=True)
            except Exception as e:
                epicsdev.printw(f"Binary query failed: {e}")
                return []
        return []
    
    def get_waveform(self, channel=1):
        """Acquire waveform from specified channel.
        
        Args:
            channel: Channel number (1-4 typically)
            
        Returns:
            numpy array of waveform data
        """
        if self.simulate:
            # Generate simulated waveform
            t = np.linspace(0, 1, 1000)
            # Simulated sine wave with noise
            waveform = np.sin(2 * np.pi * 5 * t) + np.random.randn(1000) * 0.1
            return waveform
        
        try:
            # Set data source to channel
            self.write(f'DATa:SOUrce CH{channel}')
            # Set data encoding
            self.write('DATa:ENCdg RPBinary')
            self.write('DATa:WIDth 2')
            # Set data range to full record
            self.write('DATa:STARt 1')
            record_length = int(self.query('HORizontal:RECOrdlength?'))
            self.write(f'DATa:STOP {record_length}')
            
            # Get waveform preamble for scaling
            ymult = float(self.query('WFMOutpre:YMUlt?'))
            yoff = float(self.query('WFMOutpre:YOFf?'))
            yzero = float(self.query('WFMOutpre:YZEro?'))
            
            # Get binary waveform data
            raw_data = self.query_binary('CURVe?')
            
            # Convert to voltage
            waveform = (np.array(raw_data) - yoff) * ymult + yzero
            
            return waveform
        except Exception as e:
            epicsdev.printw(f"Failed to get waveform: {e}")
            return np.array([])


# Global oscilloscope instance
scope = None


def set_channel_scale(value, spv):
    """Setter for channel vertical scale."""
    channel = int(spv.name.replace('ch', '').replace('Scale', ''))
    if scope and scope.connected:
        scope.write(f'CH{channel}:SCAle {value}')
        epicsdev.printi(f'Set CH{channel} scale to {value} V/div')


def set_channel_offset(value, spv):
    """Setter for channel vertical offset."""
    channel = int(spv.name.replace('ch', '').replace('Offset', ''))
    if scope and scope.connected:
        scope.write(f'CH{channel}:OFFSet {value}')
        epicsdev.printi(f'Set CH{channel} offset to {value} V')


def set_channel_coupling(value, spv):
    """Setter for channel coupling mode."""
    channel = int(spv.name.replace('ch', '').replace('Coupling', ''))
    if scope and scope.connected:
        scope.write(f'CH{channel}:COUPling {value}')
        epicsdev.printi(f'Set CH{channel} coupling to {value}')


def set_horizontal_scale(value, *_):
    """Setter for horizontal (time) scale."""
    if scope and scope.connected:
        scope.write(f'HORizontal:SCAle {value}')
        epicsdev.printi(f'Set horizontal scale to {value} s/div')


def set_record_length(value, *_):
    """Setter for record length."""
    if scope and scope.connected:
        scope.write(f'HORizontal:RECOrdlength {int(value)}')
        epicsdev.printi(f'Set record length to {int(value)} points')


def set_trigger_level(value, *_):
    """Setter for trigger level."""
    if scope and scope.connected:
        scope.write(f'TRIGger:A:LEVel:CH1 {value}')
        epicsdev.printi(f'Set trigger level to {value} V')


def set_acquire_mode(value, *_):
    """Setter for acquire mode."""
    if scope and scope.connected:
        scope.write(f'ACQuire:MODe {value}')
        epicsdev.printi(f'Set acquire mode to {value}')


def acquire_single(*_):
    """Trigger single acquisition."""
    if scope and scope.connected:
        scope.write('ACQuire:STATE RUN')
        scope.write('ACQuire:STOPAfter SEQuence')
        epicsdev.printi('Triggered single acquisition')


def myPVDefs():
    """Define PVs for Tektronix oscilloscope."""
    SET, U, LL, LH = 'setter', 'units', 'limitLow', 'limitHigh'
    
    pvs = []
    
    # Horizontal (timebase) settings
    pvs.extend([
        ['horizontalScale', 'Time per division', 
         epicsdev.SPV(1e-6, 'W'), {U: 's/div', LL: 1e-9, LH: 1000.0, SET: set_horizontal_scale}],
        ['recordLength', 'Record length in points',
         epicsdev.SPV(10000, 'W', 'u32'), {U: 'pts', LL: 100, LH: 10000000, SET: set_record_length}],
        ['sampleRate', 'Sample rate',
         epicsdev.SPV(0.0), {U: 'Sa/s'}],
    ])
    
    # Trigger settings
    pvs.extend([
        ['triggerLevel', 'Trigger level',
         epicsdev.SPV(0.0, 'W'), {U: 'V', LL: -10.0, LH: 10.0, SET: set_trigger_level}],
        ['triggerSource', 'Trigger source',
         epicsdev.SPV(['CH1', 'CH2', 'CH3', 'CH4', 'EXT'], 'WD'), 
         {SET: lambda v, _: scope.write(f'TRIGger:A:EDGE:SOUrce {v}') if scope else None}],
    ])
    
    # Acquisition settings
    pvs.extend([
        ['acquireMode', 'Acquisition mode',
         epicsdev.SPV(['SAMple', 'PEAKdetect', 'HIRes', 'AVErage', 'ENVelope'], 'WD'),
         {SET: set_acquire_mode}],
        ['acquireState', 'Acquisition state',
         epicsdev.SPV(['STOP', 'RUN'], 'WD'),
         {SET: lambda v, _: scope.write(f'ACQuire:STATE {v}') if scope else None}],
        ['acquireSingle', 'Trigger single acquisition',
         epicsdev.SPV(['Idle', 'Acquire'], 'WD'),
         {SET: lambda v, _: acquire_single() if v == 'Acquire' else None}],
    ])
    
    # Channel 1-4 settings and waveforms
    for ch in range(1, 5):
        pvs.extend([
            [f'ch{ch}Scale', f'Channel {ch} vertical scale',
             epicsdev.SPV(1.0, 'W'), {U: 'V/div', LL: 0.001, LH: 10.0, SET: set_channel_scale}],
            [f'ch{ch}Offset', f'Channel {ch} vertical offset',
             epicsdev.SPV(0.0, 'W'), {U: 'V', LL: -10.0, LH: 10.0, SET: set_channel_offset}],
            [f'ch{ch}Coupling', f'Channel {ch} coupling mode',
             epicsdev.SPV(['DC', 'AC', 'GND'], 'WD'), {SET: set_channel_coupling}],
            [f'ch{ch}State', f'Channel {ch} display state',
             epicsdev.SPV(['OFF', 'ON'], 'WD'),
             {SET: lambda v, s: scope.write(f"CH{s.name[2]}:STATE {1 if v=='ON' else 0}") if scope else None}],
            [f'ch{ch}Waveform', f'Channel {ch} waveform data',
             epicsdev.SPV([0.0] * 1000), {U: 'V'}],
            [f'ch{ch}Mean', f'Channel {ch} waveform mean',
             epicsdev.SPV(0.0), {U: 'V'}],
            [f'ch{ch}Peak2Peak', f'Channel {ch} peak-to-peak amplitude',
             epicsdev.SPV(0.0), {U: 'V'}],
            [f'ch{ch}RMS', f'Channel {ch} RMS value',
             epicsdev.SPV(0.0), {U: 'V'}],
        ])
    
    # Measurement parameters
    pvs.extend([
        ['frequency', 'Measured frequency',
         epicsdev.SPV(0.0), {U: 'Hz'}],
        ['period', 'Measured period',
         epicsdev.SPV(0.0), {U: 's'}],
    ])
    
    # Update controls
    pvs.extend([
        ['updateRate', 'Waveform update rate',
         epicsdev.SPV(1.0, 'W'), {U: 'Hz', LL: 0.1, LH: 100.0}],
        ['enableUpdates', 'Enable automatic waveform updates',
         epicsdev.SPV(['Disabled', 'Enabled'], 'WD'), {}],
    ])
    
    return pvs


def update_waveforms():
    """Update waveform data for all enabled channels."""
    if not scope or not scope.connected:
        return
    
    enable_updates = str(epicsdev.pvv('enableUpdates'))
    if enable_updates != 'Enabled':
        return
    
    # Update waveforms for each channel
    for ch in range(1, 5):
        try:
            # Check if channel is enabled
            ch_state = str(epicsdev.pvv(f'ch{ch}State'))
            if ch_state == 'ON':
                waveform = scope.get_waveform(ch)
                if len(waveform) > 0:
                    # Publish waveform
                    epicsdev.publish(f'ch{ch}Waveform', waveform)
                    
                    # Calculate and publish statistics
                    mean_val = np.mean(waveform)
                    p2p_val = np.max(waveform) - np.min(waveform)
                    rms_val = np.sqrt(np.mean(waveform**2))
                    
                    epicsdev.publish(f'ch{ch}Mean', mean_val)
                    epicsdev.publish(f'ch{ch}Peak2Peak', p2p_val)
                    epicsdev.publish(f'ch{ch}RMS', rms_val)
        except Exception as e:
            epicsdev.printw(f'Failed to update CH{ch}: {e}')


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='EPICS PVAccess server for Tektronix MSO oscilloscopes')
    parser.add_argument('-a', '--address', 
                       help='Oscilloscope VISA address (e.g., TCPIP::192.168.1.100::INSTR)',
                       default=None)
    parser.add_argument('-p', '--prefix', 
                       help='PV name prefix',
                       default='TEK:MSO:')
    parser.add_argument('-v', '--verbose',
                       help='Verbosity level (0-3)',
                       type=int, default=0)
    parser.add_argument('-s', '--simulate',
                       help='Run in simulation mode without hardware',
                       action='store_true')
    parser.add_argument('-l', '--list-dir',
                       help='Directory to save PV list',
                       default='/tmp/pvlist/')
    
    args = parser.parse_args()
    
    # Check arguments
    if not args.simulate and not args.address:
        print("ERROR: --address required for hardware mode, or use --simulate for simulation")
        sys.exit(1)
    
    # Initialize oscilloscope
    global scope
    try:
        scope = TektronixMSO(args.address, simulate=args.simulate)
        if not scope.connected:
            epicsdev.printe("Failed to connect to oscilloscope")
            sys.exit(1)
    except Exception as e:
        epicsdev.printe(f"Failed to initialize oscilloscope: {e}")
        sys.exit(1)
    
    # Initialize EPICS server
    pvs = epicsdev.init_epicsdev(args.prefix, myPVDefs(), 
                                  verbose=args.verbose,
                                  listDir=args.list_dir)
    
    # Start PVAccess server
    from p4p.server import Server
    server = Server(providers=[{k: v for k, v in pvs.items()}])
    
    epicsdev.printi("Server is running. Press Ctrl+C to exit.")
    
    # Main loop
    last_update_time = time.time()
    try:
        while True:
            # Check server state
            if epicsdev.serverState() == 'Exit':
                break
            
            # Update waveforms at specified rate
            current_time = time.time()
            update_rate = epicsdev.pvv('updateRate')
            if update_rate > 0:
                update_interval = 1.0 / update_rate
                if current_time - last_update_time >= update_interval:
                    update_waveforms()
                    last_update_time = current_time
            
            # Sleep and update cycle PVs
            epicsdev.sleep()
            
    except KeyboardInterrupt:
        epicsdev.printi("Interrupted by user")
    finally:
        if scope and scope.instrument:
            scope.instrument.close()
        epicsdev.printi("Server stopped")


if __name__ == "__main__":
    main()
