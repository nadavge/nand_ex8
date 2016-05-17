def label_asm(name, function=None):
	"""The assembly implementation of a label"""
	if function is None:
		return 'l_{name}'.format(name=name)
	return 'l_{function}${name}'.format(name=name, function=function)


def func_label_asm(name):
	"""The assembly implementation of a function label"""
	return 'f_{name}'.format(name=name)


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


rid = 0 # Return id - a counter for temp return labels for function calls

def call(func, argc):
	"""Call a function with a number of arguments using the stack
	@func the name of the function called to
	@argc the number of arguments called with"""
	global rid
	func_label = func_label_asm(func)
	arg_dist = int(argc) + 5 # The distance between SP and the arguments
	
	def _repush_label(name):
		'''Push a label, assuming SP is currently pointing to the top element'''
		return '''@{label}
			D = M;
			@SP
			AM = M+1;
			M = D;\n'''.format(label=name)

	# Push the return address to the stack
	command = '''@h_return.{rid} // ** Push return address
		D = A; // Hold the return address at D
		@SP
		A = M;
		M = D;\n'''
	# Push the pointers to the stack
	command += ''.join(_repush_label(lbl) for lbl in ['LCL', 'ARG', 'THIS', 'THAT'])
	# _repush_label assumes the SP points to the top element and leaves it this way
	# so we advance the SP to fix this
	command += '''@SP // Fix SP
		MD = M+1; // Calculate ARG and LCL
		@LCL
		M = D; // LCL now points to locals start, where SP is
		@{arg_dist}
		D = D-A;
		@ARG
		M = D; // ARG now points to first argument
		@{func_label}
		0; JMP // Go to function!
		(h_return.{rid})\n'''

	command = command.format(rid=rid, arg_dist=arg_dist, func_label=func_label)
	rid += 1

	return command


def function(func, locals):
	"""Declare a function with a given number of local variables"""
	func_label = func_label_asm(func)
	locals_c = int(locals)
	
	command = '({func_label})\n'.format(func_label=func_label)
	
	if locals_c == 0:
		return command
	
	# At least one local argument exists
	command += '''@SP
		A = M;
		M = 0;
		@SP
		AM = M+1;\n'''
	# For every other local argument, repeat this piece
	command += '''M=0;
		@SP
		AM = M+1;\n'''*(locals_c - 1)

	return command


def return_():
	"""Return from a function, retrieving the previous stack frame"""

	# Save return address in R13
	command = '''@LCL
		D = M;
		@5
		A = D-A; // Point to ret addr
		D = M; // Get ret addr
		@R13 // R13 = ret addr
		M = D;\n'''

	# Move the return value to where ARG is and restore stack frame
	command += '''@SP
		AM = M-1;
		D = M; // Pop top-most element
		@ARG
		A = M;
		M = D; // *(ARG) = return value
		D = A; // D = ARG
		@SP
		M = D+1; // SP points to ARG+1\n'''

	# Restore THAT, THIS, ARG and LCL (order important!)
	command += ''.join(
		'''@LCL
		D = M;
		@{offset}
		A = D-A;
		D = M;
		@{pointer}
		M = D;\n'''.format(offset=off, pointer=poi)
		for off, poi in enumerate(['THAT', 'THIS', 'ARG', 'LCL'], start=1)
	)
	
	# Jump to return address
	command += '''@R13
		A = M;
		0; JMP\n'''
	
	return command


def bootstrap():
	"""Set up the bootstrap code, write it into the file"""

	return '''@256
		D = A;
		@SP
		M = D;\n''' + call('Sys.init', '0')
