#!/usr/bin/env python3
import minimalmodbus
import serial
import time
import csv
import sys

# number of registers in each data table (table 2 doesn't exist)
number_registers = [125, 125, 0, 125, 125]


def get_column(heading, key):
    try:
        col = heading.index(key)
        return col
    except ValueError:
        print("Can't find '%s' column in table" % key)
        sys.exit(1)

definition_files = ['../coil-rw.tsv', '../discrete-inputs-readonly.tsv', '../holding-register-readwrite.tsv', '../input-register-readonly.tsv']
definition_labels = ['Coil    (output, fn=%d)', 'Discrete (input, fn=%d)',  'Holding    (i/o, fn=%d)', 'Input     (input, fn=%d)']

def read_definitions(table_number):
    inputfile = definition_files[table_number]
    table = {}
    with open(inputfile) as infile:
        reader = csv.reader(infile, delimiter='\t')
        data = [row for row in reader]
        title = data[0][:]
        table['heading'] = data[1][:]
        table['data'] = data[2:][:]
#        print(table['heading'])
#        print(table['data'])
        table['address_col'] = get_column(table['heading'], "Address")
        table['description_col'] = get_column(table['heading'], "Description")
#    print(table['data'])
    return table


def get_definition(defns, table, address):
    table = table-1
    addr_colidx = defns[table]['address_col']
#    print(addr_colidx)
    data = defns[table]['data']
    defn = ''
    for row in data:
        if row[addr_colidx] == str(address):
            defn = row[defns[table]['description_col']]
            break
#    print(defn)
#    row = defns[table]['data'][:][.index(str(address))
#    defn = defns[table]['description']
    return defn




def read_tables(instrument):
    data_tables = {}
    data_tables[1] = instrument.read_bits(registeraddress=1, number_of_bits=125, functioncode=1)
    data_tables[2] = instrument.read_bits(registeraddress=1, number_of_bits=125, functioncode=2)
    for table in [3, 4]:
        data = [-99]*number_registers[table]
        for reg in range(0,number_registers[table]):
           data[reg] = instrument.read_register(reg, functioncode=table, signed=True)
        data_tables[table] = data
    return data_tables


def diff_tables(defns, a, b):
    akeys = a.keys()
    avalues = a.values()
    bvalues = b.values()
    for key in akeys:
        for reg in range(1,len(avalues)):
            if a[key][reg] != b[key][reg]:
                defn = get_definition(defns, key, reg)
                table_label = definition_labels[key-1] % (key)
                print("%s, key %d: %d -> %d : %s" % (table_label, reg, a[key][reg], b[key][reg], defn) )
    return



defns = {}
for defn in [0, 1, 2, 3]:
    defns[defn] = read_definitions(defn)

#print("%d:%d %s" % (2, 4, get_definitions(defns, 2, 4)))


instrument = minimalmodbus.Instrument('/dev/ttyUSB0', slaveaddress=1, mode='rtu')  # port name, slave address (in decimal)
instrument.serial.baudrate = 19200         # Baud
instrument.serial.bytesize = 8
instrument.serial.parity   = serial.PARITY_NONE
instrument.serial.stopbits = 2
instrument.serial.timeout  = 0.05          # seconds

instrument.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
instrument.clear_buffers_before_each_transaction = True






a = read_tables(instrument)
while True:
    b = read_tables(instrument)
    diff_tables(defns, a, b)
    a=b
    print("")

