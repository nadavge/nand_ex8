def label_asm(name, function=None):
	"""The assembly implementation of a label"""
	return 'l_{name}'.format(name=name)
	
def label(name, function=None):
	"""Insert a label to the code from the given function"""
	label_name = label_asm(name, function)
	return '({label})\n'.format(label=label_name)

def goto(name, function=None):
	"""Go to a label in the code from the given function"""
	label_name = label_asm(name, function)
	return '''@{label}
0;JMP\n'''.format(label=label_name)

def if_goto(name, function=None):
	"""Go to a label like @goto based on a condition
	pops the first element from the stack, if non-zero, jump"""
	label_name = label_asm(name, function)
	return '''@SP
AM = M-1; // Pop top element, stored in M
D = M; // Hold it in D
@{label}
D;JNE // jump in case of non-zero\n'''.format(label=label_name)
