#!/usr/bin/env python3
"""Example script demonstrating Tektronix MSO device support usage.

This example shows how to:
1. Connect to the oscilloscope (or use simulation mode)
2. Configure channels and timebase
3. Set up trigger
4. Enable waveform acquisition
5. Read waveform data and measurements
"""

import sys
import time
import argparse

try:
    from p4p.client.thread import Context
except ImportError:
    print("Error: p4p not installed. Install with: pip install epicsdev")
    sys.exit(1)


def wait_for_pv(ctxt, pvname, timeout=5.0):
    """Wait for PV to be available."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            ctxt.get(pvname, timeout=1.0)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def main():
    parser = argparse.ArgumentParser(description='Tektronix MSO example client')
    parser.add_argument('-p', '--prefix', default='TEK:MSO:',
                       help='PV prefix (default: TEK:MSO:)')
    args = parser.parse_args()
    
    prefix = args.prefix
    
    # Create PVAccess context
    ctxt = Context('pva')
    
    print(f"Connecting to oscilloscope at prefix: {prefix}")
    
    # Wait for server to be available
    if not wait_for_pv(ctxt, f'{prefix}host'):
        print("ERROR: Server not found. Make sure tektronix_mso is running.")
        sys.exit(1)
    
    # Get server information
    host = ctxt.get(f'{prefix}host')
    version = ctxt.get(f'{prefix}version')
    print(f"Connected to: {host}")
    print(f"Version: {version}")
    print()
    
    # Configure Channel 1
    print("Configuring Channel 1...")
    ctxt.put(f'{prefix}ch1State', 'ON')
    ctxt.put(f'{prefix}ch1Scale', 1.0)  # 1 V/div
    ctxt.put(f'{prefix}ch1Offset', 0.0)
    ctxt.put(f'{prefix}ch1Coupling', 'DC')
    print("  State: ON")
    print("  Scale: 1.0 V/div")
    print("  Offset: 0.0 V")
    print("  Coupling: DC")
    print()
    
    # Configure timebase
    print("Configuring Timebase...")
    ctxt.put(f'{prefix}horizontalScale', 0.001)  # 1 ms/div
    ctxt.put(f'{prefix}recordLength', 1000)
    print("  Horizontal scale: 1 ms/div")
    print("  Record length: 1000 points")
    print()
    
    # Configure trigger
    print("Configuring Trigger...")
    ctxt.put(f'{prefix}triggerSource', 'CH1')
    ctxt.put(f'{prefix}triggerLevel', 0.5)  # 0.5 V
    print("  Source: CH1")
    print("  Level: 0.5 V")
    print()
    
    # Set acquisition mode
    print("Setting Acquisition Mode...")
    ctxt.put(f'{prefix}acquireMode', 'SAMple')
    ctxt.put(f'{prefix}acquireState', 'RUN')
    print("  Mode: Sample")
    print("  State: RUN")
    print()
    
    # Enable automatic waveform updates
    print("Enabling waveform updates...")
    ctxt.put(f'{prefix}updateRate', 2.0)  # 2 Hz
    ctxt.put(f'{prefix}enableUpdates', 'Enabled')
    print("  Update rate: 2 Hz")
    print()
    
    # Monitor waveform and measurements
    print("Monitoring Channel 1 (press Ctrl+C to stop)...")
    print("-" * 70)
    
    try:
        while True:
            # Get measurements
            mean = ctxt.get(f'{prefix}ch1Mean')
            p2p = ctxt.get(f'{prefix}ch1Peak2Peak')
            rms = ctxt.get(f'{prefix}ch1RMS')
            
            # Get waveform (just show length, not all data)
            waveform = ctxt.get(f'{prefix}ch1Waveform')
            
            print(f"CH1: Mean={mean:.4f}V  P-P={p2p:.4f}V  RMS={rms:.4f}V  "
                  f"Points={len(waveform)}", end='\r')
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n" + "-" * 70)
        print("Stopped by user")
    
    # Cleanup: stop updates
    print("\nDisabling updates...")
    ctxt.put(f'{prefix}enableUpdates', 'Disabled')
    ctxt.put(f'{prefix}acquireState', 'STOP')
    
    print("Done!")
    ctxt.close()


if __name__ == "__main__":
    main()
