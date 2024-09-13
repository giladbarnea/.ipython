import os
import pickle
from pathlib import Path

from IPython.core.magic import register_line_magic


def load_ipython_extension(ipython):
    print("Loaded extension ipickle")

    @register_line_magic("ipickle")
    def magic(line: str):
        """%ipickle <expression> [-o <output>]

        `expression` can be a Python expression or a variable, in which case it will be pickled; or a pickle file, in which case it will be unpickled.
        `output` can be a file or a variable name.
        If `output` is specified, the result will be assigned to the variable or written to the file.
        """
        import pickle

        line = line.strip()
        if not line:
            return
        expression = ipython.var_expand(line).strip()
        print(f"\x1b[2mexpression: {expression!r} | line: {line!r}\x1b[0m")
        if not expression:
            return
        arguments: list = expression.split()
        arguments = [os.path.expanduser(arg) for arg in arguments]  # Just in case
        if len(arguments) == 1:
            return process_expression(arguments[0], ipython=ipython)
        if len(arguments) != 3:
            raise ValueError(f"too many arguments: {arguments!r}. Expecting either 1 or 3 arguments.")

        output_argument_index = next(i for i, arg in enumerate(arguments) if arg == "-o")
        output_argument = arguments[output_argument_index + 1]
        arguments.pop(output_argument_index)
        arguments.pop(output_argument_index)  # Twice to remove both -o and the output argument.
        return process_expression(arguments[0], output_argument, ipython=ipython)


def process_expression(expression, output=None, *, ipython):
    print(f"\x1b[2mexpression: {expression!r} | output: {output!r}\x1b[0m")
    if is_variable_in_namespace(expression, ipython=ipython):
        return pickle_and_output_variable(expression, output, ipython=ipython)
    if is_pickle_file(expression):
        return unpickle_and_output(expression, output, ipython=ipython)
    return pickle_and_output(expression, output, ipython=ipython)


def is_variable_in_namespace(var_name, *, ipython):
    """Check if a variable with the given name exists in the namespace."""
    return var_name in ipython.user_ns


def is_pickle_file(file_path) -> bool:
    """Check if a file with the given name is a pickle file."""
    if not os.path.isfile(file_path):
        return False
    try:
        with open(file_path, "rb") as f:
            pickle.load(f)
        return True
    except Exception:
        return False


def pickle_and_output_variable(var_name, output=None, *, ipython):
    """Pickle a variable and output it to a file or a variable."""
    obj = ipython.user_ns[var_name]
    if output is None:
        return pickle.dumps(obj)
    elif os.path.isfile(output) or Path(output).parent.is_dir():
        with open(output, "wb") as f:
            pickle.dump(obj, f)
    else:
        ipython.user_ns[var_name] = pickle.dumps(obj)


def pickle_and_output(expression, output=None, *, ipython):
    """Evaluate an expression, pickle the result and output it to a file or a variable."""
    obj = eval(expression, globals(), ipython.user_ns)
    if output is None:
        return pickle.dumps(obj)
    elif os.path.isfile(output) or Path(output).parent.is_dir():
        with open(output, "wb") as f:
            pickle.dump(obj, f)
    else:
        ipython.user_ns[output] = pickle.dumps(obj)


def unpickle_and_output(file_name, output=None, *, ipython):
    """Unpickle a file and output the result to a variable."""
    with open(file_name, "rb") as f:
        obj = pickle.load(f)
    if output is None:
        return obj
    else:
        ipython.user_ns[output] = obj
