#!/usr/bin/python3

from gen_object import *

field_re = re.compile(r"^(?P<name>[\w_]+)\t+(?P<type>[\w ]+)\t+(?P<required>\w+)\t+(?P<desc>.+)$", re.MULTILINE)


def gen_docstring(docstr, fields):
    docstr = '"""\n' + docstr
    for name, type, required, desc in fields:
        docstr += "\n"
        docstr += ":param {}: ({}) {}{}".format(fix_name(name), fix_type(type), "Optional. " if required != "Yes" else "", desc)
    return docstr + '\n"""'

def gen_init(fields):
    args = "self, "
    args += "{}: {}, ".format(fix_name(fields[0][0]), fix_type(fields[0][1]))
    for name, type, required, desc in fields[1:]:
        s = "\n             {}: {}".format(fix_name(name), fix_type(type))
        if required != "Yes":
            s += " = None"
        s += ", "
        args += s
    args = args[:-2]

    decl = "def __init__({}):".format(args)

    body = "super().__init__()\n\n"

    for name, _, _, _ in fields:
        body += "self.{0} = {0}\n".format(fix_name(name))

    return decl + "\n" + indent(body)


def gen_object(string):
    objname = objname_re.findall(string)[0]
    docstring = docstring_re.findall(string)[0]
    fields = field_re.findall(string)

    i = 0
    while i < len(fields):
        if fields[i][0] == "Parameters":
            break
        i += 1

    fields = fields[i+1:]

    obj = "class {}(TelegramMethodBase):\n".format(objname)
    obj += indent(gen_docstring(docstring, fields))
    obj += "\n\n"
    obj += indent(gen_init(fields))

    return obj

def main():
    print()
    print()
    print(gen_object(sys.stdin.read()))
    print()

if __name__ == "__main__":
    main()