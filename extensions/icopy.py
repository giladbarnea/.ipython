print('icopy')
from IPython.core.magic import register_line_cell_magic

def load_ipython_extension(ipython):
    @register_line_cell_magic("icopy")
    def icopy(line: str, cell: str=None):
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
                print(f'Copied str with {lines_len} newlines: {lines[0]}, ..., {lines[-1]}')
            else:
                print(f'Copied str with {lines_len} newlines: {", ".join(lines)}')
        else:
            if not line:
                return
            tocopy = line.strip()
        tocopy = tocopy.replace('"', r'\"')
        import os
        import sys
        if sys.platform == 'darwin':
            return os.system(f'echo -n "{tocopy}" | pbcopy')
        else:
            return os.system(f'echo -n "{tocopy}" | xclip -selection clipboard')

