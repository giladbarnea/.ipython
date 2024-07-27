import json
import os
from pathlib import Path

from IPython.core.magic import register_line_magic

try:
    from rich.traceback import install

    install(show_locals=True)
except ModuleNotFoundError:
    pass


def load_ipython_extension(ipython):
    print("Loaded extension ijson")

    @register_line_magic("ijson")
    def magic(line: str):
        """%ijson <expression> [-o <output>]

        `expression` can be:
        1. a Python expression or a variable, in which case it will be json.load'ed if it's a json string, or json.dump'ed if it's not;
        2. a json file, in which case it will be json.load'ed.

        `output` can be a file or a variable name.
        If `output` is specified, the result will be assigned to the variable or written to the file.
        """
        import json

        line = line.strip()
        if not line:
            return
        expression = ipython.var_expand(line).strip()
        print(f"\x1b[2m  expression:\n{expression}\n  line:\n{line}\x1b[0m")
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
        return json_and_output_variable(expression, output, ipython=ipython)
    if is_json_file(expression):
        return json_load_and_output(expression, output, ipython=ipython)
    return json_and_output(expression, output, ipython=ipython)


def is_variable_in_namespace(var_name, *, ipython):
    """Check if a variable with the given name exists in the namespace."""
    return var_name in ipython.user_ns


def is_json_file(file_path) -> bool:
    """Check if a file with the given name is json loadable."""
    if not os.path.isfile(file_path):
        return False
    try:
        with open(file_path, "r") as f:
            json.load(f)
        return True
    except Exception:
        return False


def is_json_loadable(string) -> bool:
    """Check if a string is json loadable."""
    try:
        json.loads(string)
        return True
    except Exception:
        return False


def json_and_output_variable(var_name, output=None, *, ipython):
    """json.dump a variable and output it to a file or a variable.
    If the variable is json loadable, json.load it and output it."""
    obj = ipython.user_ns[var_name]
    json_loadable: bool = is_json_loadable(obj)
    if output is None:
        if json_loadable:
            return json.loads(obj)
        return json.dumps(obj, indent=4)
    elif os.path.isfile(output) or Path(output).parent.is_dir():
        with open(output, "w") as f:
            if json_loadable:
                json.dump(json.loads(obj), f, indent=4)  # For indent
            else:
                json.dump(obj, f, indent=4)
    else:
        ipython.user_ns[var_name] = json.loads(obj) if json_loadable else json.dumps(obj, indent=4)


def json_and_output(expression, output=None, *, ipython):
    """Evaluate an expression, json.dump the result and output it to a file or a variable.
    If the expression is json loadable, json.load it and output it."""
    obj = eval(expression, globals(), ipython.user_ns)
    json_loadable: bool = is_json_loadable(obj)
    if output is None:
        if json_loadable:
            return json.loads(obj)
        return json.dumps(obj, indent=4)
    elif os.path.isfile(output) or Path(output).parent.is_dir():
        with open(output, "w") as f:
            if json_loadable:
                json.dump(json.loads(obj), f, indent=4)  # For indent
            else:
                json.dump(obj, f, indent=4)
    else:
        ipython.user_ns[output] = json.loads(obj) if json_loadable else json.dumps(obj, indent=4)


def json_load_and_output(file_name, output=None, *, ipython):
    """json.load a file and output the result to a variable."""
    with open(file_name, "r") as f:
        obj = json.load(f)
    if output is None:
        return obj
    else:
        ipython.user_ns[output] = obj
