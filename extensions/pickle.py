from IPython.core.magic import register_line_magic
def load_ipython_extension(ipython):
    @register_line_magic("pickle")
    def magic(line: str):
        if not line:
            raise ValueError("Nothing specified")
        obj = ipython.var_expand(line[5:])
        if line.startswith("load"):
            from pickle import load
            return load(obj)
        elif line.startswith("dump"):
            from pickle import dump
            return dump(obj)
        else:
            raise ValueError("Unknown command (must be 'load' or 'dump')")