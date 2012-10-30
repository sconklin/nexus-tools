#!/usr/bin/env python

# Copyright (C) Canonical, Inc 2012

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#import time
import sys
import fileinput

from nct1008 import NCT1008
from smb347 import SMB347
from bq27541 import BQ27541
from max77663 import MAX77663

i2caddrs = {
    0x1c:'rt5640', # codec
    0x36:'unknown 1',
    0x3c:'max77663', # pmic
    0x4c:'nct1008', # temp sensor
    0x55:'bq27541', # battery gas guage
    0x56:'at24', #eeprom
    0x68:'dummy', # dummy regulator ?!
    0x6a:'smb347', # battery charger IC
    0x0e:'notinkernel1',
    0x1e:'notinkernel2',
}

# Attempt to detect related transactions because they are close to each other
RELATED_DELTA = .0005
   
#skiplist = ['rt5640', 'max77663']
skiplist = ['rt5640','unknown 1','bq27541','max77663','at24','dummy','notinkernel1','notinkernel2', 'nct1008']
#allskiplist = ['rt5640','unknown 1','bq27541','smb347','max77663','at24','dummy','notinkernel1','notinkernel2', 'nct1008']
#skiplist = ['rt5640','unknown 1','bq27541','smb347','max77663','at24','dummy', 'nct1008']
#skiplist = ['rt5640','unknown 1','bq27541','smb347','at24','dummy','notinkernel1','notinkernel2', 'nct1008']
#skiplist = ['rt5640','unknown 1','max77663','at24','dummy','notinkernel1','notinkernel2']

if len(sys.argv) != 2:
    print "Please specify a csv file name"
    sys.exit(-1)

nct = NCT1008()
smb = SMB347()
bq = BQ27541()
max = MAX77663()

lasttime = None;
deltatime = 0;
#3.15e-05,,8,c,Write,ACK

# some state variables
in_charger_status = False

for line in fileinput.input(sys.argv[1]):
    # There are 6 parts
    # Time [s],Packet ID,Address,Data,Read/Write,ACK/NAK
    parts = line.strip().split(',')
    timestring = parts[0]
    if timestring.startswith("Time"):
        #print "Skipping First"
        continue
    packetno = parts[1]
    try:
        addr = int(parts[2].strip("'"),0)
    except:
        print "part0 = ", parts[0]
        print "part1 = ", parts[1]
        print "part2 = ", parts[2]
        print "part3 = ", parts[3]
        print "part4 = ", parts[4]
        print "part5 = ", parts[5]

    data = int(parts[3],0)
    rw = parts[4]
    acknak = parts[5]


    timestamp = float(timestring)
    if lasttime is not None:
        deltatime = timestamp - lasttime
    lasttime = timestamp

    # shift the address, throwing away the R/W bit
    i2caddr = addr >> 1
    if i2caddr not in i2caddrs:
        if i2caddr not in unknowns:
            #print "Unknown I2C address %x" % i2caddr
            unknowns.append(i2caddr)
        continue

    devname = i2caddrs[i2caddr]
    if devname in skiplist:
        continue

#    0x3c:'max77663', # pmic
#    0x4c:'nct1008', # temp sensor
#    0x55:'bq27541', # battery gas guage
#    0x56:'at24', #eeprom
#    0x68:'dummy', # dummy regulator ?!
#    0x6a:'smb347', # battery charger IC

    if deltatime > RELATED_DELTA:
        print "======================================"
    if devname is 'bq27541':
        bq.process_transaction(deltatime, rw, data)
    elif devname is 'smb347':
        smb.process_transaction(deltatime, rw, data)
    #elif devname is 'notinkernel1':
    #    print line
    #    print "devname =", devname
    #    print "i2caddr = 0x%0.2x " % i2caddr
    elif devname is 'nct1008':
        nct.process_transaction(deltatime, rw, data)
    elif devname is 'max77663':
        max.process_transaction(deltatime, rw, data)
    else: # unknown device
        print "%f device = %s (%s) %x [%s]" % (timestamp, devname, rw, data, acknak)
