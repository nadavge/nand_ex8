import os
import sys
import vm_arithmetic, vm_memory

VM_COMMENT_INITIAL = '//'

def parse(line):
	"""Parse a vm line
	@return the parsed line as a list of the keywords/arguments"""

	# Remove comments
	try:
		comment_index = line.index(VM_COMMENT_INITIAL)
		line = line[:comment_index]
	except:
		pass
	
	split_line = line.split()

	return split_line

def translate(parsed_line, filename):
	"""Translate a vm parsed line to hack assembly
	@return hack assembly code corresponding to the line as a string"""
	
	# The command is of the structure [INSTRUCTION, ARG1*, ARG2*]
	instruction = parsed_line[0]
	arg1 = parsed_line[1] if len(parsed_line) >= 2 else None
	arg2 = parsed_line[2] if len(parsed_line) >= 3 else None
	
	# Memory commands
	if instruction == 'push':
		return vm_memory.push(arg1, arg2, filename)
	elif instruction == 'pop':
		return vm_memory.pop(arg1, arg2, filename)
	# Arithmetic commands
	elif instruction == 'neg':
		return vm_arithmetic.neg()
	elif instruction == 'not':
		return vm_arithmetic.not_()
	elif instruction == 'add':
		return vm_arithmetic.add()
	elif instruction == 'sub':
		return vm_arithmetic.sub()
	elif instruction == 'and':
		return vm_arithmetic.and_()
	elif instruction == 'or':
		return vm_arithmetic.or_()
	elif instruction in ['eq', 'gt', 'lt']:
		return vm_arithmetic.compare(instruction)
	# Program flow commands
	elif instruction == 'label':
		pass # TODO handle label
	elif instruction == 'goto':
		pass # TODO handle goto
	elif instruction == 'if-goto':
		pass # TODO handle if-goto
	elif instruction == 'call':
		pass # TODO handle call
	elif instruction == 'return':
		pass # TODO handle return
	elif instruction == 'function':
		pass # TODO handle function, also save last function
	
	print("Unknown command: {}".format(parsed_line))
	sys.exit(1)

def process(file, filename):
	"""Manage the translation process
	@return a generator for the the translation of commands"""
	
	for line in file:
		parsed_line = parse(line)
		if not parsed_line:
			continue

		yield translate(parsed_line, filename)
		

def translate_file(file_path, output=None):
	"""Translate a file by filepath, save the result
	@file_path the path to the input file
	@output A supplied output file.
	        If None write the result to a file matching the input file's name"""
		
	with open(file_path, 'r') as file:
		file_name = os.path.basename(file_path)
		file_path_no_ext, _ = os.path.splitext(file_path)
		file_name_no_ext, _ = os.path.splitext(file_name)

		result = process(file, file_name_no_ext)

		if output is None:
			ofile_path = file_path_no_ext+'.asm'
			with open(ofile_path, 'w') as ofile:
				for command in result:
					ofile.write(command)
		else:
			for command in result:
				output.write(command)


def translate_dir(dir_path):
	"""Translate a directory, save the result to a hack assembly file in the directory"""
	dir_name = os.path.basename(os.path.normpath(dir_path))
	ofilename = os.path.join(dir_path, dir_name+'.asm')
	with open(ofilename, 'w') as ofile:
		for file in os.listdir(dir_path):
			file_path = os.path.join(dir_path, file)
			_, file_ext = os.path.splitext(file_path)
			# Choose only vm files
			if os.path.isfile(file_path) and file_ext.lower()=='.vm':
				translate_file(file_path, ofile)


def main():
	"""The main program, loading the file/files and calling the translator"""
	if len(sys.argv) < 2:
		print("Missing file parameter... Failure")
		sys.exit(1)

	input_path = sys.argv[1]

	if os.path.isdir(input_path):
		translate_dir(input_path)
	elif os.path.isfile(input_path):
		translate_file(input_path)
	else:
		print("Invalid argument supplied!")
		sys.exit(1)


if __name__=="__main__":
	main()
