from IPython.core.magic import register_line_cell_magic

try:
    from rich.traceback import install

    install(show_locals=True)
except ModuleNotFoundError:
    pass


def load_ipython_extension(ipython):
    print("Loaded extension copy")

    @register_line_cell_magic("copy")
    def copy(line: str, cell: str = None):
        """Copies current line or cell to clipboard.

        Usage:
            %copy <line>

            %%copy
            <cell>
        """
        import os
        import sys

        line = line.strip()
        cell = cell.strip() if cell else None
        if cell:
            if line:
                print(f"line: ", repr(line), "\ncell: ", repr(cell))
                raise NotImplementedError("don't know how to handle both line and cell?")
            lines = [line.strip() for line in cell.splitlines() if line]
            tocopy = "\n".join(lines)
            lines_len = len(lines)
            # TODO:
            #  1) keep indentation
            #  2) keep quotes
            if lines_len > 3:
                print(f"\x1b[2mCopying str with {lines_len} newlines: {lines[0]}, ..., {lines[-1]}\x1b[0m")
            else:
                print(f'\x1b[2mCopying str with {lines_len} newlines: {", ".join(lines)}\x1b[0m')
        else:
            if not line:
                return
            tocopy = line
        tocopy = tocopy.replace('"', r"\"")
        if sys.platform == "darwin":
            command = f'echo -n "{tocopy}" | pbcopy'
        else:
            command = f'echo -n "{tocopy}" | xclip -selection clipboard'
        print(f"\x1b[2mRunning command: {command!r}\x1b[0m")
        return os.system(command)
