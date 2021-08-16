# DO NOT uncomment; c.exec_PYTHONSTARTUP is True, and it's set to PYTHONDEBUGFILE
# try:
	# import os
	# 
	# debug_path = os.getenv('PYTHONDEBUGFILE')
	# with open(debug_path) as debug_file:
		# exec(compile(debug_file.read(), debug_path, mode='exec'))
		# # __lines = ipdb_debug.readlines()
		# # __i = __lines.index(next(line for line in __lines if line.startswith('import')))
		# # __j = __lines.index(next(line for line in __lines if line.startswith('builtins.')))
		# # exec(''.join(__lines[__i:__j]))
# except Exception as e:
	# print('[WARN][startup.py] failed running $PYTHONDEBUGFILE:', e.__class__.__qualname__, *e.args)
	# 
	# 
# 
