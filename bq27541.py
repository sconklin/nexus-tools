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

class BQ27541:

# constants
# All registers return 16 bits??
    bq27541_regs = {
        0x00:'MANUFACTURER_DATA',
        #REG_STATE_OF_HEALTH, 0
        0x06:'TEMPERATURE',
        0x08:'VOLTAGE',
        0x14:'CURRENT',
        0x16:'TIME_TO_EMPTY',
        0x18:'TIME_TO_FULL',
        0x0A:'STATUS',
        0x2C:'CAPACITY',
        #REG_SERIAL_NUMBER,
        #REG_MAX
    }


# ================================================

    in_reg_transaction = 0
    temp_register = None
    first_byte = None
    regname = None

    def dump_16(self, data1, data2):
        print "0x%0.2x%0.2x" % (data1, data2)
        return

    def continue_register_access(self, deltatime, rw, data):
        if self.in_reg_transaction == 1:
            # first byte
            self.first_byte = data
            self.in_reg_transaction = 2
        else:
            # finish it
            print "bq27541 : %s" % (self.regname.ljust(16)),
            self.dump_16(self.first_byte, data)

            self.in_reg_transaction = 0
        return
    
    def process_transaction(self, deltatime, rw, data):
        if self.in_reg_transaction:
            self.continue_register_access(deltatime, rw, data)
        elif data in self.bq27541_regs:
            # This is the first half of a register access
            self.regname = self.bq27541_regs[data]
            self.in_reg_transaction = 1
            #print "%s:" % self.regname,
            self.temp_register = data
        else:
            print "bq27541: Unknown register address %d, skipping" % data


