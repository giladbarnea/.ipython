from IPython.core.magic import register_line_cell_magic



def load_ipython_extension(ipython):
    @register_line_cell_magic("copy")
    def linecellmagic(line, cell=None):
        if cell:
            if line:
                print(f'line: ', line, '\ncell: ', cell)
                raise NotImplementedError("don't know how to handle both line and cell?")
            lines = [line.strip() for line in cell.splitlines() if line.strip()]
            tocopy = "\n".join(lines)
            lines_len = len(lines)
            # TODO:
            #  1) keep indentation
            #  2) keep quotes
            if lines_len > 3:
                print(f'copied str with {lines_len} newlines: {lines[0]}, ..., {lines[-1]}')
            else:
                print(f'copied str with {lines_len} newlines: {", ".join(lines)}')
        else:
            if not line:
                return
            tocopy = line.strip()
        tocopy = tocopy.replace('"', r'\"')
        import subprocess as sp
        sp.check_call(f'echo -n "{tocopy}" | xclip -selection clipboard',shell=True)
    
    # print('\x1b[2mmagic loaded: %copy\x1b[0m')
