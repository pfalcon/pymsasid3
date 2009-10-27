 # =============================================================================
 # input.py
 #
 # author : matthieu.kaczmarek@mines-nancy.fr 
 # Mainly rewrited from udis86 -- Vivek Mohan <vivek@sig9.com>
 # =============================================================================

from types import *
CACHE_SIZE = 64

class Hook_class :
  dis_mode = 32
  def __init__ (self, source, base_address):
    pass
  def hook (self):
    pass
  def seek (self, add) :
    pass
  def symbols (self) :
    return {}

# =============================================================================
# buff_hook - Hook for buffered inputs.
# =============================================================================
class Buffer_hook (Hook_class) :
  def __init__ (self, source, base_address):
    self.source = source
    self.pos = 0
    self.set_source (source)
    self.entry_point = self.base_address = base_address

  def set_source (self, source):
    self.source = source
    self.pos = 0

  def hook (self):
    if self.pos > 0 and self.pos < len(self.source):
      ret = self.source[self.pos]
      self.pos += 1
      #print (hex(self.pos) + " " + hex(ord(ret)))
      return ord(ret)
    else :
      print ("end of input " + self.pos + " " + self.base_address)
    
  def seek (self, add):
    pos = add - self.base_address
    if pos >= 0 and pos <= len (self.source):
      self.pos = pos
    else :
      print ("seek out of bounds " + add)   

class PEString_hook (Buffer_hook):
  def __init__ (self, source, base_address):
    import pefile
    self.pe = pefile.PE(data = source)
    self.source = self.pe.get_memory_mapped_image()
    self.base_address = self.pe.OPTIONAL_HEADER.ImageBase
    self.entry_point = (self.base_address 
                        + self.pe.OPTIONAL_HEADER.AddressOfEntryPoint)
    self.pos = 0
    self.seek (self.base_address + self.pe.OPTIONAL_HEADER.AddressOfEntryPoint)
    if self.pe.PE_TYPE == pefile.OPTIONAL_HEADER_MAGIC_PE:
      self.dis_mode = 32
    elif self.pe.PE_TYPE == pefile.OPTIONAL_HEADER_MAGIC_PE_PLUS:
      self.dis_mode = 64

  def seek (self, add):
    pos = add - self.base_address
    if pos >= 0 and pos <= len (self.source):
      self.pos = pos
    else :
      print ("seek out of bounds " + add)   

  def symbols (self):
    ret = {}
    for entry in self.pe.DIRECTORY_ENTRY_IMPORT:
      for imp in entry.imports:
        if imp.name :
          ret[imp.address] = imp.name
#        print (hex(imp.address) + ":" + imp.name)
    return  ret
    for exp in self.pe.DIRECTORY_ENTRY_EXPORT.symbols:
      key = self.pe.OPTIONAL_HEADER.ImageBase + exp.address
      ret[key] = exp.name # exp.ordinal    
    return ret
      
class PEFile_hook (PEString_hook):
  def __init__ (self, source, base_address):
    import pefile
    self.pe = pefile.PE(name = source)
    self.source = self.pe.get_memory_mapped_image()
    self.pos = self.base_address = base_address
    self.base_address = self.pe.OPTIONAL_HEADER.ImageBase
    self.entry_point = (self.base_address 
                        + self.pe.OPTIONAL_HEADER.AddressOfEntryPoint)
    self.seek (self.base_address + self.pe.OPTIONAL_HEADER.AddressOfEntryPoint)

# =============================================================================
# hexstring_hook - Hook for hex string inputs.
# =============================================================================
class Hexstring_hook (Hook_class):
  def __init__ (self, source, base_address):
    self.set_source (source)
    self.entry_point = self.base_address = base_address

  def set_source (self, source):
    self.source = source.split (' ')
    self.pos = 0

  def hook (self):
    ret = -1
    if self.pos < len(self.source):
      ret = int (self.source[self.pos], 16)
      self.pos += 1
    return ret

  def seek (self, add):
    pos = add - self.base_address
    if pos >= 0 and pos <= len (self.source):
      self.pos = pos
    else :
      print ("seek out of bounds " + add)   

# =============================================================================
# file_hook - Hook for FILE inputs.
# =============================================================================
class File_hook (Hook_class) :
  def __init__ (self, source, base_address):
    self.set_source (source)
    self.entry_point = self.base_address = base_address
  
  def set_source (self, source):
    self.source = source;

  def hook(self):
    s = self.source.read(1)
    if s == '' :
      return -1
    return s[0]

  def seek (self, add):
    pos = add - self.base_address
    if pos >= 0 :
      source.seek (pos)
    else :
      print ("seek out of bounds " + add)   

class Input :
 # =============================================================================
 # __init__() - Initializes the input system. 
 # =============================================================================
  def __init__ (self, Hook, source, base_address = 0) :
    self.hook = Hook (source, base_address)
    self.symbols = self.hook.symbols()
    self.start ()

  def seek(self, add):
    self.hook.seek (add)

  def start (self) :
    self.ctr = -1
    self.fill = -1
    self.error = 0
    self.buffer = []

  def current (self) :
    if self.ctr >= 0:
      return self.buffer[self.ctr]
    else :
      return -1

  def next (self):
    if self.ctr < self.fill :
      self.ctr += 1
      return self.current ()
    c = self.hook.hook ()
    if c != -1 :
      self.ctr += 1
      self.fill += 1
      self.buffer.append (c)
    else :
      self.error = 1
    return c

 # =============================================================================
 # back() - Move back a single byte in the stream.
 # =============================================================================
  def back(self):
    if self.ctr >= 0:
      self.ctr -= 1

 # =============================================================================
 # peek() - Peek into the next byte in source. 
 # =============================================================================
  def peek(self): 
    r = self.next()
    # Don't backup if there was an error  return r
    if not self.error :
      self.back()  
    return long(r)

#=============================================================================
#  read(N) - read uint of N bits from source.
#=============================================================================
  def read (self, n):
    if n < 8 :
      print ("minimal size of addressable memory is 8 bits (" + n +")")
    elif n == 8 :
      return self.next ()
    else :
      n /= 2
      a = self.read (n)
      b = self.read (n)
      return a | (b << n)
