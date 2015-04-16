## Project description ##
Pym's is a pure python disassembly library. It is merely a port of [udis86](http://udis86.sourceforge.net/) to python. At the moment it is a one shot project. But I'll do a some support.

## New ##
Beta 3 Released
  * Some bugs corrected
To be continued on beta ??
  * AT&T syntax support.

## Try it online ##
You can try the web base version of Pym's desassembler online [here](http://pyms86.appspot.com/). Upload your file and obtain its disassembled code.

## Quick example ##
```
>>> import pymsasid as pyms
>>> prog = pyms.Pymsasid(hook = pyms.PEFileHook, source = './xcopy.exe')
>>> inst = prog.disassemble (prog.pc); print inst
call 0x100291cL 
>>> print inst.operator
call
>>> print inst.operand
[0x100291cL]
>>> branch = inst.branch(); map (hex, branch)
['0x1002912L', '0x100291cL']
>>> inst = prog.disassemble (branch[1]); print inst
mov edi edi 
>>> branch = inst.branch()
>>> while (len(branch) == 1) :
...   s = '[' + hex (prog.pc) + '] '
...   inst = prog.disassemble (branch[0])
...   print (s + str (inst))
...   branch = inst.branch()
... 
[0x100291cL] push rbp 
[0x100291eL] mov ebp esp 
[0x100291fL] sub esp 0x10 
[0x1002921L] mov rax [0x1009000] 
[0x1002924L] and [bp-0x8] 0x0 
[0x1002929L] and [bp-0x4] 0x0 
[0x100292dL] push rdi 
[0x1002931L] mov rdi 0xbb40e64eL 
[0x1002932L] cmp eax edi 
[0x1002937L] jnz 0x10057a6L 
>>> map (hex, branch)
['0x100293fL', '0x10057a6L']
>>> exit ()

```