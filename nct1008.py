#!/usr/bin/env python
#
#
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

class NCT1008:

    # constants for nct1008
    nct_1008_regs = {
        0x00:'Local Temp (R)',
        0x01:'Ext Temp High Byte (R)',
        0x02:'Status (R)',
        0x03:'Config (R)',
        0x04:'Rate (R)',
        0x05:'Local High Limit (R)',
        0x06:'Local Low Limit (R)',
        0x07:'Ext High Limit High Byte (R)',
        0x08:'Ext Low Limit High Byte(R)',
        0x09:'Config (W)',
        0x0A:'Rate (W)',
        0x0B:'Local High Limit (W)',
        0x0C:'Local Low Limit (W)',
        0x0D:'Ext High Limit High Byte (W)',
        0x0E:'Ext Low Limit High Byte(W)',
        0x0F:'One Shot (W)',
        0x10:'Ext Temp Low Byte (R)',
        0x11:'Ext Temp Offset High Byte',
        0x12:'Ext Temp Offset Low Byte',
        0x13:'Ext Temp Offset High Limit Low Byte',
        0x14:'Ext Temp Offset Low Limit Low Byte',
        0x19:'Ext THERM limit',
        0x20:'Local THERM limit',
        0x21:'THERM hysteresis',
        0x22:'Consecutive Alert',
        0xFE:'MFG ID (R)',
    }

    in_reg_transaction = False
    temp_register = None
    temp_range = 'normal'
    in_extended_read = False
    extended_low_byte = None
    regname = None

    def print_regname(self, regname):
        print "nct1008: %s:" % regname.ljust(29),

    def print_data(self, data):
        print "0x%0.2x :" % data,

    def dump_config_data(self, data):
        self.print_regname(self.regname)
        self.print_data(data)
        if data & 0x80:
            print "[ALERT Enabled]",
        else:
            print "[Alert Disabled]",
        if data & 0x40:
            print "[Standby]",
        else:
            print "[Run]",
        if data & 0x20:
            print "[THERM2]",
        else:
            print "[ALERT]",
        if data & 0x04:
            print "[Extended Range]",
            self.temp_range = 'extended'
        else:
            print "[Normal Range]",
            self.temp_range = 'normal'
        print
        return

    def dump_rate_data(self, data):
        self.print_regname(self.regname)
        self.print_data(data)
        if data == 0x00:
            print "16 S",
        elif data == 0x01:
            print "8 S",
        elif data == 0x02:
            print "4 S",
        elif data == 0x03:
            print "2 S",
        elif data == 0x04:
            print "1 S",
        elif data == 0x05:
            print "500 mS",
        elif data == 0x06:
            print "250 mS",
        elif data == 0x07:
            print "125 mS",
        elif data == 0x08:
            print "62.5 mS",
        elif data == 0x09:
            print "31.25 mS",
        elif data == 0x0A:
            print "15.5 mS",
        else:
            print "Reserved value",
        print
        return

    def dump_simple_temp(self, data):
        self.print_regname(self.regname)
        self.print_data(data)
        # TODO FIXME
        #if self.temp_range == 'extended':
        #    data = data + 64
        print "%d Degrees C" % data
        return
    
    def dump_generic_info(self, data):
        self.print_regname(self.regname)
        self.print_data(data)
        print
        return

    def dump_offset_value(self, extended_low_byte, data):
        # TODO fix this
        #print "%s: 0x%x" % (self.regname, data)
        if self.regname == 'Ext Temp Offset High Byte':
            self.print_regname('Ext Temp Offset')
        else:
            self.print_regname(self.regname)
        print "%0.2x:%0.2x" % (data, extended_low_byte)
        return
    
    # Offset registers - same format as temp
    def dump_extended_temp(self, extended_low_byte, data):
        self.print_regname(self.regname)
        self.print_data(data)
        # TODO fix this

        if self.temp_range == 'extended':
            #print "offsetting [FIXME]",
            #data = data - 64
            # This behavior does not seem to match the data sheet
            temp = float(data)
            temp = temp + ((extended_low_byte >> 6) * 0.25)
        print "%f C" % temp
        return
    
    def start_extended_read(self, deltatime, rw, data):
        self.in_extended_read = True
        self.extended_low_byte = data
        #print "     Begin Extended Read: %s" %  self.regname
        return
    
    def finish_extended_read(self, deltatime, rw, data):
        if not self.in_extended_read:
            print "Second half called while not in extended read"
        else:
            # self.temp_register contains the register which ended this extended read
            if (self.temp_register == 0x01): # ext temp
                #print "ext temp"
                self.dump_extended_temp(self.extended_low_byte, data)
            elif (self.temp_register == 0x11): # Ext Temp Offset
                #print "ext temp offset"
                self.dump_offset_value(self.extended_low_byte, data)
            elif (self.temp_register == 0x07): # Ext Temp High Limit
                #print "Ext Temp High Limit"
                self.dump_extended_temp(self.extended_low_byte, data)
            elif (self.temp_register == 0x08): # Ext Temp Low Limit
                #print "Ext Temp Low Limit"
                self.dump_extended_temp(self.extended_low_byte, data)
            else:
                print "Confused. temp_register is %s" % self.temp_register
                self.in_extended_read = False
        return
    
    def finish_register_access(self, deltatime, rw, data):
        #print "finish_register_access ENTER"
        if (self.temp_register == 0x04) or (self.temp_register == 0x0A): # Rate
            self.dump_rate_data(data)
        elif self.temp_register == 0x09: # 'Config (W)'
            self.dump_config_data(data)
        elif ((self.temp_register == 0x05) or (self.temp_register == 0x06) # local high limit, local low limit (read)
            or (self.temp_register == 0x00) # local temp (read)
            or (self.temp_register == 0x19) or (self.temp_register == 0x20) # ext THERM limit, local THERM limit(read/write)
            or (self.temp_register == 0x0B) or (self.temp_register == 0x0C)): # Local high limit, local low limit (write)
                #print "single"
                self.dump_simple_temp(data)
        # High Byte Registers which are WRITE
        elif ((self.temp_register == 0x0D) or (self.temp_register == 0x0E)): # ext high limit high byte (write), ext low limit high byte (write)
            #print "high byte single display"
            self.dump_generic_info(data)
        elif (self.temp_register == 0x11): # Ext Temp Offset High Byte (rw)
            if rw is 'Write':
                #print "A"
                self.dump_generic_info(data)
            else:
                #print "B"
                self.finish_extended_read(deltatime, rw, data)

        # Low byte registers which can be part of extended sets
        elif ((self.temp_register == 0x10) or (self.temp_register == 0x12) # ext temp low byte (r), Ext Temp Offset Low Byte (rw)
              or (self.temp_register == 0x13) or (self.temp_register == 0x14)): # Ext Temp Offset High Limit Low Byte (rw), Ext Temp Offset Low Limit Low Byte (rw)
              self.start_extended_read(deltatime, rw, data)
        # High Byte registers which can be part of extended sets for READ
        elif ((self.temp_register == 0x07) or (self.temp_register == 0x08) # Ext High Limit High Byte, Ext Low Limit High Byte (read)
              or (self.temp_register == 0x01)): # ext temp high byte (read)
                  #print "Z"
                  self.finish_extended_read(deltatime, rw, data)

        # Misc remaining registers
        elif ((self.temp_register == 0x02) or (self.temp_register == 0x02) # Status, config
            or (self.temp_register == 0x0F) or (self.temp_register == 0x21) # One Shot, THERM hysterysis
            or (self.temp_register == 0x22) or (self.temp_register == 0xFE)): # Consecutive Alert, Mfg ID
                self.dump_generic_info(data)
        else:
            print "finish_register_access: WTF?"

        self.in_reg_transaction = False
        return
    
    def process_transaction(self, deltatime, rw, data):
        #print "process_transaction ENTER, data = 0x%x" % data

        if self.in_reg_transaction:
            self.finish_register_access(deltatime, rw, data)
        elif data in self.nct_1008_regs:
            # This is the first half of a register access
            self.regname = self.nct_1008_regs[data]
            self.in_reg_transaction = True
            #print "%s:" % self.regname,
            self.temp_register = data
        else:
            print "nct1008: Unknown register address %d, skipping" % data
    
        #print "Temp Sensor, delta = %f %s %s (%s)" % (deltatime, rw, data, regname)


