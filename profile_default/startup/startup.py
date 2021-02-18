try:
	import os
	with open(os.environ['PYTHONPREBREAK']) as pythonprebreak:
		exec(compile(pythonprebreak.read(), os.environ['PREBREAK'], mode='exec'))
		# __lines = ipdb_prebreak.readlines()
		# __i = __lines.index(next(line for line in __lines if line.startswith('import')))
		# __j = __lines.index(next(line for line in __lines if line.startswith('builtins.')))
		# exec(''.join(__lines[__i:__j]))
except Exception as e:
	print('failed running $PYTHONPREBREAK:', e.__class__.__qualname__, *e.args)
