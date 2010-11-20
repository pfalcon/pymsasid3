# Copyright (c) 2009-2010, matthieu.kaczmarek@mines-nancy.org
# Rewritten from udis86 -- Vivek Mohan <vivek@sig9.com>
# All rights reserved.

from operand import P_OSO, P_ASO, P_IMPADDR
from common import DecodeException

def intel_operand_cast(op):
    """Returns operand casts."""

    ret = {
        8 :     'byte ',
        16 :    'word ',
        32 :    'dword ',
        64 :    'qword ',
        84 :    'tword ',
    }

    if op.size in ret:
        return ret[op.size]
    else:
        raise KeyError('Unknown operand size: %s' % str(op.size))


def intel_operand_syntax(op):
    """Generates assembly output for operands."""

    ret = list()

    if op.type is None:
        return ''

    if op.type == 'OP_REG':
        return op.base

    if op.cast is 1:
        ret.append(intel_operand_cast(op))

    if op.type == 'OP_MEM':
        op_f = False
        ret.append('[')

        if op.seg:
            ret.extend([op.seg, ':'])

        if op.base is not None:
            ret.append(op.base)
            op_f = True

        if op.index is not None:
            if op_f:
                ret.append('+')

            ret.append(op.index)
            op_f = True

        if op.scale:
            ret.append(str(op.scale))

        if op.offset in [8, 16, 32, 64]:
            if (op.lval < 0):
                ret.extend(['-', hex(-op.lval)])
            else:
                if op_f:
                    if op.lval is 0.0:
                        op.lval = 0
                    ret.extend(['+', hex(op.lval)])
                else:
                    ret.append(hex(op.lval))

        ret.append(']')

    elif op.type == 'OP_IMM':
        ret.append(hex(op.lval))

    elif op.type == 'OP_JIMM':
        ret.append(hex(op.pc + op.lval))

    elif op.type == 'OP_PTR':
        ret.extend(['word ', hex(op.lval.seg), ':', hex(op.lval.off)])

    return ''.join(ret)


def intel_syntax(self):
    """Translates to intel syntax."""

    ret = list()

    # check if P_OSO prefix is used
    if not P_OSO(self.itab_entry.prefix) and self.pfx.opr:
        if self.dis_mode is 16:
            ret.append('o32 ')
        elif self.dis_mode in [32, 64]:
            ret.append('o16 ')

    # check if P_ASO prefix was used
    if not P_ASO(self.itab_entry.prefix) and self.pfx.adr:
        if self.dis_mode is 16:
            ret.append('a32 ')
        elif self.dis_mode is 32:
            ret.append('a16 ')
        elif self.dis_mode is 64:
            ret.append('a32 ')

    if self.pfx.lock:
        ret.append('lock ')

    if self.pfx.rep:
        ret.append('rep ')

    if self.pfx.repne:
        ret.append('repne ')

    if P_IMPADDR(self.itab_entry.prefix) and self.pfx.seg:
        ret.append(self.pfx.seg)

    # print the instruction operator
    ret.append(self.operator.ljust(8, ' '))

    if self.branch_dist:
        ret.extend([self.branch_dist, ' '])

    # print the operands
    operands = list()
    for op in self.operand:
        operands.append(intel_operand_syntax(op))

    ret.append(', '.join(operands))

    return ''.join(ret)
