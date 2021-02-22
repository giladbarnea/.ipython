try:
	import os
	
	prebreak_path = os.getenv('PYTHONPREBREAK')
	with open(prebreak_path) as prebreak_file:
		exec(compile(prebreak_file.read(), prebreak_path, mode='exec'))
		# __lines = ipdb_prebreak.readlines()
		# __i = __lines.index(next(line for line in __lines if line.startswith('import')))
		# __j = __lines.index(next(line for line in __lines if line.startswith('builtins.')))
		# exec(''.join(__lines[__i:__j]))
except Exception as e:
	print('[WARN][startup.py] failed running $PYTHONPREBREAK:', e.__class__.__qualname__, *e.args)
	
	

