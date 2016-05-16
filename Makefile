all:
	chmod +x VMtranslator

tar: VMtranslator VMtranslator.py vm_memory.py vm_arithmetic.py README Makefile
	tar cf project7.tar $^