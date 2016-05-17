segment_symbols = {'local'   : 'LCL', 
                   'this'    : 'THIS',
                   'that'    : 'THAT',
                   'argument': 'ARG'}
segment_constants = {'pointer' : '3', 
                     'temp'    : '5'}


def push(segment, i, filename):
	"""Push the value in segment:i to the stack"""
	
	command = ''
	
	if segment in segment_symbols or segment in segment_constants:
		if segment in segment_symbols:
			command += '@' + segment_symbols[segment] + '\n'
			command += 'D = M;\n'
		else:
			command += '@' + segment_constants[segment] + '\n'
			command += 'D = A;\n'

		command += '@' + i + '\n'
		command += 'A = D+A;\n'
		command += 'D = M; // D is the value in *(BASE+<i>)\n'
		
	elif segment == 'constant':
		command += '@' + i + '\n'
		command += 'D = A;\n'
		
	elif segment == 'static':
		command += '@s_' + filename + '.' + i + '\n'
		command += 'D = M;\n'
		
	command += '''@SP
		A = M; // Point to where the stack is
		M = D; // Put *(BASE+<i>) in stack
		@SP
		M = M+1; // Increase SP\n'''
	
	return command


def pop(segment, i, filename):
	"""Pop the value from the stack to segment:i"""

	command = ''
	
	if segment in segment_symbols or segment in segment_constants:
		if segment in segment_symbols:
			command += '@' + segment_symbols[segment] + '\n'
			command += 'D = M;\n'
		else:
			command += '@' + segment_constants[segment] + '\n'
			command += 'D = A;\n'
		
		command += '@' + i + '\n'
		command += 'D = D+A; // D is the target address\n'
		
	elif segment == 'static':
		command += '@s_' + filename + '.' + i + '\n'
		command += 'D = A;\n'
	
	command += '''@R13
		M = D; //Hold target address at R13
		// What to pop
		@SP
		AM = M-1; // Point to where the stack top element is, decrease SP
		D = M; // Take value of top element
		// Restore the target address
		@R13
		A = M; // Point to target address
		M = D; // Store pop result in target\n'''
	
	return command
