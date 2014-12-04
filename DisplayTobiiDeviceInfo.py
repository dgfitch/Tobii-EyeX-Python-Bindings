#!/usr/bin/env python
import os
from tobii import *


tobii = TobiiPythonInterface()
info = tobii.info
                                          
print("Device URL: %s" % tobii.url.value)
print("Device info status: %s" % tobii.error_code.value)
print("Serial number: %r" % info.serial_number)
print("Model: %r" % info.model)
print("Generation: %r" % info.generation)
print("Firmware_version: %r" % info.firmware_version)


