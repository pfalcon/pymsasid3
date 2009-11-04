from operand import *
from syn_intel import *
from syn_att import *

class itab_entry:
    def __init__(self, 
                 operator = None, 
                 op1 = O_NONE, op2 = O_NONE, op3 = O_NONE, 
                 pfx = 0):
        self.operator = operator
        self.operand = [op1, op2, op3]
        self.prefix = pfx

ie_invalid = itab_entry('invalid', O_NONE, O_NONE, O_NONE, P_none)
ie_pause = itab_entry('pause', O_NONE, O_NONE,    O_NONE, P_none)
ie_nop = itab_entry('nop', O_NONE, O_NONE, O_NONE, P_none)

class Prefix:
    def __init__(self):
        self.rex = 0
        self.seg = ''
        self.opr = 0
        self.adr = 0
        self.lock = 0
        self.rep = 0
        self.repe = 0
        self.repne = 0
        self.insn = 0
        
    def clear(self):
        self.seg     = ''
        self.opr     = 0
        self.adr     = 0
        self.lock    = 0
        self.repne = 0
        self.rep     = 0
        self.repe    = 0
        self.rex     = 0
        self.insn    = 0

class Ptr:
    def __init__(self, off = 0, seg = 0):
        self.off = off
        self.seg = seg

class Operand:
    def __init__(self):
        self.seg = None
        self.type = None
        self.size = 0
        self.lval = 0
        self.base = None
        self.index = None
        self.offset = 0
        self.scale = 0
        self.cast = 0
        self.pc = 0
        self.value = None
        self.ref = None

    def clear(self):
        self.__init__()
        
    def compute_sign(self, lval):
        if(lval < 0):
            return '-' + hex(-self.lval)
        elif self.value != '':
            return '+' + hex(self.lval)
        else:
            return hex(self.lval)
        
    # MASSIVE WTF?!?
    def compute_value(self):
        if self.type == 'OP_REG':
            self.value = self.base
        elif self.type == 'OP_MEM':
            self.value = ''
            if self.seg:
                self.value = self.seg + ':'
            if self.base:
                self.value += self.base
            if self.index:
                if self.value != '':
                    self.value += '+'
                self.value += self.index
            if self.scale != 0:
                self.value += hex(self.scale)
            if self.offset in [8, 16, 32, 64]:
                self.value += self.compute_sign(self.lval)
        elif self.type == 'OP_IMM':
            self.value = self.compute_sign(self.lval)
        elif self.type == 'OP_JIMM':
            self.value = self.compute_sign(self.pc + self.lval)
        elif self.type == 'OP_PTR':
            # used to be:(clearly broken)
            #self.value = long(self.lval.seg << 4) + self.lval.off
            raise NotImplementedError('should do something about OP_PTR. Really.')
        else:
            raise Exception('should not reach this point in Operand.compute_value()')


    def __str__(self):
        value = ''
        if self.cast:
            ret = {
                8: 'byte ',
                16: 'word ',
                32: 'dword ',
                64: 'qword ',
                84: 'tword '
            }
            value = ret[self.size]
        if not type(self.value) == str:
            value += hex(self.value)
        else:
            value += self.value
        if self.type == 'OP_MEM':
            return '[' + value + ']'
        return value
    
    def __repr__(self):
        return self.__str__()

class Inst:
    def __init__(self, add = 0, mode = 16, syntax = intel_syntax):
        self.dis_mode = mode
        self.size = 0
        self.add = add
        self.pc = 0
        self.syntax = syntax
        self.my_syntax = None
        self.itab_entry = ie_invalid
        self.operator = 'invalid'
        self.operand = [] 
        self.pfx = Prefix()
        self.opr_mode = 0 
        self.adr_mode = 0 
        self.branch_dist = None 
        
    def clear(self):
        self.pfx.clear()
        self.itab_entry = ie_invalid
        self.operator = self.itab_entry.operator
        for op in self.operand:
            op.clear()
 
    def __str__(self):
        if(self.my_syntax == None):
            self.my_syntax = self.syntax(self) # wtf ?
        return self.my_syntax

    def __repr__(self):
        return str(self)

    def set_pc(self, pc):
        self.pc = pc
        for op in self.operand:
            op.pc = pc
            
    def compute_values(self):
        for op in self.operand:
            op.compute_value()

    def branch(self):
        if(self.operator in operator_list_invalid 
               or self.operator in operator_list_ret 
               or self.operator in operator_list_hlt):
            return []
        elif self.operator in operator_list_jmp:
            return [self.target_add()]
        elif(self.operator in operator_list_call 
                or self.operator in operator_list_jcc):
            return [self.next_add(), self.target_add()]
        return [self.next_add()]

    def next_add(self):
        return long(self.pc)
        
    def target_add(self):
        if(self.operand[0].type == 'OP_JIMM' 
                or self.operand[0].type == 'OP_IMM'):
            ret = self.add + self.size + self.operand[0].lval
        elif self.operand[0].type == 'OP_PTR':
            ret = ((self.operand[0].lval.seg << 4) 
                   + self.operand[0].lval.off)
        elif self.operand[0].type == 'OP_MEM':
            ret = self.operand[0].value
        else:
            ret = str(self.operand[0])
        if(type(ret) == str):
            return ret
        return long(ret)

    def flow_label(self):
        if self.operator in operator_list_invalid:
            return 'invd'
        elif self.operator in operator_list_call:
            return 'call'
        elif self.operator in operator_list_jmp:
            return 'jmp'
        elif self.operator in operator_list_jcc:
            return 'jcc'
        elif self.operator in operator_list_ret:
            return 'ret'
        elif self.operator in operator_list_hlt:
            return 'hlt'
        else:
            return 'seq'
        
         

operator_list_invalid = [ 'invalid']

operator_list_call = ['syscall', 
                      'call', 
                      'vmcall', 
                      'vmmcall']

operator_list_ret = ['sysret',
                     'iretw',
                     'iretd',
                     'iretq',
                     'ret',
                     'retf']

operator_list_jmp = ['jmp']

operator_list_jcc = ['jo',
                     'jno',
                     'jb',
                     'jae',
                     'jz',
                     'jnz',
                     'jbe',
                     'ja',
                     'js',
                     'jns',
                     'jp',
                     'jnp',
                     'jl',
                     'jge',
                     'jle',
                     'jg',
                     'jcxz',
                     'jecxz',
                     'jrcxz',
                     'loopnz',
                     'loope',
                     'loop']

operator_list_hlt = ['hlt']
