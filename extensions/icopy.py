from IPython.core.magic import register_line_cell_magic


def load_ipython_extension(ipython):
    print("Loaded extension icopy")

    def import_pyperclip():
        try:
            import pyperclip
        except ImportError:
            answer = input("Package 'pyperclip' is not installed; pip install it? y/n: ").strip()
            if answer.lower() == "n":
                print("icopy cannot proceed without 'pyperclip'")
                return
            import os

            os.system("pip install pyperclip")
            import pyperclip
        return pyperclip

    @register_line_cell_magic("icopy")
    def icopy(line: str, cell: str = None):
        """
        Copies current line or cell to clipboard using pyperclip.
        Dedents the text before copying.

        Usage:
            %icopy <line>

            %%icopy
            <cell>
        """
        import textwrap

        line = line.strip()
        cell = cell.strip() if cell else None
        if cell:
            if line:
                print("line: ", repr(line), "\ncell: ", repr(cell))
                raise NotImplementedError("don't know how to handle both line and cell?")
            dedented = textwrap.dedent(cell).strip()
        else:
            if not line:
                print("Nothing to copy")
                return
            dedented = textwrap.dedent(line).strip()
        pyperclip = import_pyperclip()
        if not pyperclip:
            return
        pyperclip.copy(dedented)
