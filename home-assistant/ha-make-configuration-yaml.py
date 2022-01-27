#!/usr/bin/env python3

import csv
import sys

def get_column(heading, key):
    try:
        col = heading.index(key)
        return col
    except ValueError:
        print("Can't find '%s' column in table" % key)
        sys.exit(1)

def get_scale_unit(scaled_unit):
    # take the numerical part
    number = ''.join(c for c in scaled_unit if c in '0123456789.')
    unit = ''.join(c for c in scaled_unit if c not in '0123456789. ')
    return (float(number), unit)

inputfile = '../input-register-readonly.tsv'
outputfile = 'configuration.yaml'

with open(inputfile) as infile:
    reader = csv.reader(infile, delimiter='\t')
    data = [row for row in reader]
    title = data[0][:]
    heading = data[1][:]
    table = data[2:][:]


include_col = get_column(heading, "Home Assistant include")
addr_col = get_column(heading, "Address")
unit_col = get_column(heading, "Units")
desc_col = get_column(heading, "Description")

# PyYAML doesn't support comments, so do this by hand
header = """
modbus:
  - name: ashp
    type: serial
    baudrate: 19200
    bytesize: 8
    method: rtu
    parity: N
    port: /dev/ttyUSB0
    stopbits: 2
#  - name: "ashp"
#    type: tcp
#    host: 192.168.99.99
#    port: 502
    sensors:"""

outfile = open(outputfile, "w") 
outfile.write(header)

for row in table:
    if row[include_col] != "":
        addr = int(row[addr_col])
        desc = row[desc_col]
        scaled_units = row[unit_col]
        (scale, unit) = get_scale_unit(scaled_units)
        name = "ASHP "+desc.rstrip()
        yaml = """
      - name: "%s"
        slave: 1
        address: %d
        input_type: input
        unit_of_measurement: %s
        scale: %f
        state_class: measurement"""
        outfile.write(yaml % (name, addr, unit, scale))
        
outfile.close()
