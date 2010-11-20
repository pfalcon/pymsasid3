# Copyright (c) 2009-2010, matthieu.kaczmarek@mines-nancy.org
# Rewritten from udis86 -- Vivek Mohan <vivek@sig9.com>
# All rights reserved.

from input import *
from inst import Inst
import decode as dec
import syn_intel as intel

from operand import VENDOR_INTEL, VENDOR_AMD

class Pymsasid:
    def __init__(self, mode=None, source='',syntax=intel.intel_syntax,
                 vendor=VENDOR_INTEL, hook=BufferHook):
        self.error = 0
        self.vendor = self.set_vendor(vendor)
        self.input = Input(hook, source)
        self.entry_point = self.pc = long(self.input.hook.entry_point)
        self.syntax = syntax

        if mode is None:
            self.dis_mode = self.input.hook.dis_mode
        else:
            self.dis_mode = mode


    def disassemble(self, add):
        try:
            self.seek(add)
            return self.decode()
        except Exception:
            return Inst(self.input)


    def set_vendor(self, vendor):
        if vendor in [VENDOR_INTEL, VENDOR_AMD]:
            self.vendor = vendor
        else:
            raise Exception('Unknown vendor: %s' % str(vendor))


    def seek(self, add):
        self.input.hook.seek(add)
        self.pc = add


    def decode(self):
        return dec.decode(self)
