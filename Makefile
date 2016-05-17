all:
	chmod +x VMtranslator

tar: VMtranslator VMtranslator.py vm_memory.py vm_arithmetic.py vm_flow.py README Makefile
	tar cf project8.tar $^