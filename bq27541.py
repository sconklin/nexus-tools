#!/usr/bin/env python
#
#

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


