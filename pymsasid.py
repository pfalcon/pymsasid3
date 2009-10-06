#-----------------------------------------------------------------------------
# pymasid
#
# author: matthieu.kaczmarek@mines-nancy.org
# Mainly rewrited from udis86 -- Vivek Mohan <vivek@sig9.com>
# -----------------------------------------------------------------------------

from input import *
from decode import *
from syn_intel import *
from syn_att import *

VENDOR_INTEL = 0
VENDOR_AMD   = 1


class Pymsasid:

  def __init__ (self, 
                mode = None, 
                source = '', 
                syntax = intel_syntax,
                vendor = VENDOR_INTEL,
                Hook = Buffer_hook):
      self.error = 0
      self.vendor = self.set_vendor(vendor)
      self.input = Input (Hook, source) 
      self.entry_point = self.pc = long(self.input.hook.entry_point)
      if mode == None :
        self.dis_mode = self.input.hook.dis_mode
      else :
        self.dis_mode = mode
      self.syntax = syntax

  def disassemble(self, add):
    try:
      self.seek (add)
      return decode(self)
    except:
      return Inst()
      
  def set_vendor(self, vendor):
    if vendor == VENDOR_INTEL:
      self.vendor = vendor
    else:
      u.vendor = VENDOR_AMD
      
  def seek (self, add):
    self.input.hook.seek (add)
    self.pc = add
