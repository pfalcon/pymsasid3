## Pymsasid3 ##

Pymsasid3 is a pure Python disassembly library. It's a maintenance-style
development of the original Pymsasid library, which was a port of
[udis86](http://udis86.sourceforge.net/) to Python.

Pymsasid3 is compatible with Python3 and should be compatible with Python2.7.
Various instruction decoding issues were fixed comparing to the original.

Trivia: "msasid" is "disasm" reversed.

## Quick example ##

(Copied from the original README, not up to date.)

```
>>> import pymsasid as pyms
>>> prog = pyms.Pymsasid(hook=pyms.PEFileHook, source='./xcopy.exe')
>>> inst = prog.disassemble(prog.pc); print(inst)
call 0x100291c
>>> print inst.operator
call
>>> print inst.operand
[0x100291c]
>>> branch = inst.branch(); map(hex, branch)
['0x1002912', '0x100291c']
>>> inst = prog.disassemble(branch[1]); print(inst)
mov edi edi
>>> branch = inst.branch()
>>> while len(branch) == 1:
...   s = '[' + hex(prog.pc) + '] '
...   inst = prog.disassemble(branch[0])
...   print (s + str(inst))
...   branch = inst.branch()
... 
[0x100291c] push rbp
[0x100291e] mov ebp, esp
[0x100291f] sub esp, 0x10
[0x1002921] mov rax, [0x1009000]
[0x1002924] and [bp-0x8], 0x0
[0x1002929] and [bp-0x4], 0x0
[0x100292d] push rdi
[0x1002931] mov rdi, 0xbb40e64e
[0x1002932] cmp eax, edi
[0x1002937] jnz 0x10057a6
>>> map(hex, branch)
['0x100293f', '0x10057a6']
```
