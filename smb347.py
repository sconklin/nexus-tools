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

class SMB347:

    # constants for smb349
    smb347_regs = {
    0x00:'CHARGE',
    0x01:'CHRG_CRNTS',
    0x02:'VRS_FUNC',
    0x03:'FLOAT_VLTG',
    0x04:'CHRG_CTRL',
    0x05:'STAT_TIME_CTRL',
    0x06:'PIN_CTRL',
    0x07:'THERM_CTRL',
    0x08:'SYSOK_USB3',
    0x09:'CTRL_REG',
    0x0A:'OTG_TLIM_REG',
    0x0B:'HRD_SFT_TEMP',
    0x0C:'FAULT_INTR',
    0x0D:'STS_INTR_1',
    0x0E:'I2C_ADDR',
    0x10:'IN_CLTG_DET',
    0x11:'STS_INTR_2',
    # Command registers
    0x30:'CMD_REG',
    0x31:'CMD_REG_B',
    0x33:'CMD_REG_C',
    # Interrupt Status registers
    0x35:'INTR_STS_A',
    0x36:'INTR_STS_B',
    0x37:'INTR_STS_C',
    0x38:'INTR_STS_D',
    0x39:'INTR_STS_E',
    0x3A:'INTR_STS_F',
    # Status registers
    0x3B:'STS_REG_A',
    0x3C:'STS_REG_B',
    0x3D:'STS_REG_C',
    0x3E:'STS_REG_D',
    0x3F:'STS_REG_E',
}

#'ENABLE_WRITE	1
#'DISABLE_WRITE	0
#ENABLE_WRT_ACCESS	0x80
#'ENABLE_APSD		0x04
#'HC_MODE		0x01
#'USB_5_9_CUR		0x02
#'PIN_CTRL		0x10
#'THERM_CTRL		0x10
#'BATTERY_MISSING		0x10
#'CHARGING		0x06
#'DEDICATED_CHARGER	0x02
#'CHRG_DOWNSTRM_PORT	0x04
#'ENABLE_CHARGE		0x02
#'ENABLE_CHARGER		1
#'DISABLE_CHARGER		0
#'USBIN		0x80
#'APSD_OK		0x08
#'APSD_RESULT		0x07
#'APSD_CDP		0x01
#'APSD_DCP		0x02
#'APSD_OTHER		0x03
#'APSD_SDP		0x04
#'USB_30		0x20

# ================================================

    in_reg_transaction = False
    temp_register = None
    regname = None

    def dump(self, data, labels):
        """ Print list of bit masks and their values in data byte.
            If bitmask in dictionary labels, substitute labels[bitmask] for bitmask,
            and display enable status.
            Label INOK uses a special value display."""
        mask = 0x80
        while mask > 0:
            bitval = bool(data & mask)
            label = labels.get(mask)
            if not label:
                print '[%#4.2x = %d]' % (mask, bitval),
            else:
                if label == 'INOK':
                    values = ['not Active High', 'Active High    ']
                else:
                    values = ['Disabled', 'Enabled ']
                print '[%s %s]' % (label, values[bitval]),
            mask >>= 1
        print
        return

    def dump_generic(self, data):
        self.dump(data, {})

    def dump_usb3(self, data):
        self.dump(data, {0x01: 'INOK'})

    def dump_command(self, data):
        self.dump(data, {0x80: 'WRT Access', 0x10: 'OTG', 0x02: 'Charge'})

    def finish_register_access(self, deltatime, rw, data):
        if rw == "Read":
            rwtext = "(R)"
        else:
            rwtext = "(W)"
        print "smb347 : %s %s, data = 0x%0.2x" % (self.regname.ljust(12), rwtext,data),
        if self.temp_register == 0x30: # CMD_REG
            self.dump_command(data)
        elif self.temp_register == 0x08: # SYSOK_USB3
            self.dump_usb3(data)
        else:
            print

        self.in_reg_transaction = False
        return
    
    def process_transaction(self, deltatime, rw, data):
        if self.in_reg_transaction:
            self.finish_register_access(deltatime, rw, data)
        elif data in self.smb347_regs:
            # This is the first half of a register access
            self.regname = self.smb347_regs[data]
            self.in_reg_transaction = True
            #print "%s:" % self.regname,
            self.temp_register = data
        else:
            print "smb347: Unknown register address %d, skipping" % data
