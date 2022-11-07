from IPython.core.magic import register_line_magic


def load_ipython_extension(ipython):

    @register_line_magic("rg")
    def rg(path: str = "/"):
        import os
        return os.system(f"rg -uu 'Loading extensions from .* is deprecated' --type=py --no-messages --files-with-matches {path!r}")

    @register_line_magic("rgsed")
    def rgsed(path: str = "/"):
        import os
        return os.system(f"rg -uu 'Loading extensions from .* is deprecated' --type=py --no-messages --files-with-matches {path!r} | map gsed -i -E "'/if mod\.__file__\.startswith\(self\.ipython_extension_dir\)/,/dir\=compress_user/d'" '{}'")

