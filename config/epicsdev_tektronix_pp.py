"""Pypet definition for Tektronix MSO scope"""
import epicsScope_pp as module

def PyPage(**_):
    return  module.PyPage(instance='tektronix0:', title='Tektronix MSO',
        channels=4)
