import os
import sys
import collections

'''
ClapPy : Command line argument parser for Python
Author: Gregory Schare
Version: 0.1
'''

class ParserError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return self.message
        else:
            return ''

class Parser:
    def __init__(self, prog=sys.argv[0], version=None, description=None):
        self.options = {}
        self.operands = []

        self.prog = prog
        self.version = version
        self.description = description

    def add_argument(self, *flags, usage=None, default=False):

        flags = [flag for flag in flags if flag]
        error_message = f"{' '.join(flags)}, usage={usage}, default={default}"

        if not flags:
            raise ParserError(f"No flags provided for argument:\n\t" + error_message)

        if any([flag[0]=="-" for flag in flags]) and not all([flag[0]=="-" for flag in flags]):
            raise ParserError(f"Flags for optional arguments must begin with - or --:\n\t" + error_message)

        if any([flag[:2]!="--" and flag[0]=="-" and len(flag)>2 for flag in flags]):
            raise ParserError(f"Shorthand flags must be a single letter:\n\t" + error_message)

        # no -- or - implies operand (mandatory argument)
        if not any([flag[0]=="-" for flag in flags]):
            self.operands.append({
                "value" : default,
                "flags" : flags,
                "help" : str(usage)
            })

        # inclusion of - or -- in flags implies optional argument
        else:
            longhand = [flag for flag in flags if "--" in flag[:2]]
            shorthand = [flag for flag in flags if flag not in longhand]
            if longhand:
                name = longhand[0][2:].replace("-", "_") # name of argument is the first longform without initial --
            else:
                name = shorthand[0][1:] # otherwise, name of argument is first shorthand without initial -
            self.options[name] = {
                "value" : default,
                "flags" : flags,
                "help" : str(usage)
            }

    def help(self):
        message = "\n"

        # usage example
        message += "Usage:\n"
        usage = []
        usage.append(self.prog)
        if self.options:
            usage.append("[options]")
        if self.operands:
            for op in self.operands:
                usage.append(op["flags"][0])
        message += " ".join(usage)

        # program desciption
        if self.description:
            message += "\n\n"
            message += self.description

        # positional arguments
        if self.operands:
            col_width = max(len(" ".join(arg["flags"])) for arg in self.operands) + 4 # padding
            message += "\n\n"
            message += "Positional arguments:"
            for op in self.operands:
                message += "\n\t" + " ".join(op["flags"]).ljust(col_width) + op["help"]

        # argument descriptions
        message += "\n\nOptional arguments:\n"

        indent = 4
        percentage_of_screen_to_use = 0.75
        terminal_width = int(os.get_terminal_size(0)[0] * percentage_of_screen_to_use)
        description_indent = indent
        description_width = terminal_width - indent - description_indent

        descriptions = [
            "-h --help",
            " "*description_indent + "Print this help message and exit.\n",
            "-v --version",
            " "*description_indent + "Print program version and exit.\n"
        ]

        for op in self.options.values():
            help_lines = [op["help"][i:i+description_width] for i in range(0, len(op["help"]), description_width)]
            descriptions.append(" ".join(op["flags"]))
            for i, line in enumerate(help_lines):
                if i+1==len(help_lines):
                    line += "\n"
                descriptions.append(" "*description_indent + line)

        for row in descriptions:
            message += " "*indent + row + "\n"

        return message
    
    def parse_args(self, args):
        usage = self.help() # generate the help message

        operands = []
        options = {k:v["value"] for k,v in self.options.items()}

        args = collections.deque(args)
        while args:
            arg = args.popleft()

            if not arg:
                continue

            # print this message and exit
            if arg in ("-h", "--help"):
                print(usage, file=sys.stdout)
                sys.exit(0)

            # print version and exit
            if arg in ("-v", "--version"):
                print(self.version, file=sys.stdout)
                sys.exit(0)

            # check for single longhand flags
            if arg[:2] == "--":
                for name, op in self.options.items():
                    if arg in op["flags"]:
                        options[name] = True
                        break
                else:
                    raise ParserError("Unrecognized optional argument. See usage:\n" + usage)
                
            # check for grouped shorthand flags
            elif arg[0] == "-":
                for subarg in arg[1:]:
                    for name, op in self.options.items():
                        if "-" + subarg in op["flags"]:
                            options[name] = True
                            break
                    else:
                        raise ParserError("Unrecognized optional argument. See usage:\n" + usage)

            # must be positional argument, so add to operands
            else:
                operands.append(arg)
                if len(operands) > len(self.operands):
                    raise ParserError("Too many positional arguments. See usage:\n" + usage)

        return operands, Map(options)


class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'})
    Source:
    https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    """
    def __init__(self, dictionary):
        super(Map, self).__init__(dictionary)
        try:
            for k, v in dictionary.items():
                self[k] = v
        except ValueError:
            raise ValueError(f"Expected dict or dict-ike object, given {type(dictionary)}")

    def __getattr__(self, attr):
        return self.get(attr)

if __name__ == "__main__":
    parser = Parser()
    parser.add_argument("-d", "--dry-run")
    parser.add_argument("-s", "--silent", usage="Quiet mode. Do not print progress to console.")
    parser.add_argument("folios", usage="Specify which folios to load.")
    operands, options = parser.parse_args(["-d", "-d", "--dry-run", "-s", "[005v, 005r]", "-s"])
    print(operands)
    print(options)
    print(options.silent)