#!/usr/bin/python3

import sys, re
from depytg._internals import shadow as fix_name

"""
Document
This object represents a general file (as opposed to photos, voice messages and audio files).

Field	Type	Description
file_id	String	Unique file identifier
thumb	PhotoSize	Optional. Document thumbnail as defined by sender
file_name	String	Optional. Original filename as defined by sender
mime_type	String	Optional. MIME type of the file as defined by sender
file_size	Integer	Optional. File size
"""

objname_re = re.compile(r"^(\w+)$", re.MULTILINE)
docstring_re = re.compile(r"\w+\n(.+)\n\n")
field_re = re.compile(r"^(?P<name>[\w_]+)\t+(?P<type>[\w ]+)\t+(?P<desc>.+)$", re.MULTILINE)

type_map = {
    "String": "str",
    "Integer": "int",
    "Float": "float",
    "Float number": "float",
    "Boolean": "bool",
    "True": "bool",
    "False": "bool"
}

fix_name

def fix_type(t):
    if t in type_map:
        return type_map[t]
    if " " in t:
        return "'{}'".format(t)
    return t

def gen_docstring(docstr, fields):
    docstr = '"""\n' + docstr
    for name, type, desc in fields:
        docstr += "\n"
        docstr += ":param {}: ({}) {}".format(fix_name(name), fix_type(type), desc)
    return docstr + '\n"""'

def indent(string):
    return "\n".join(["    " + i for i in string.splitlines()])

def gen_init(fields):
    args = "self, "
    args += "{}: {}, ".format(fix_name(fields[0][0]), fix_type(fields[0][1]))
    for name, type, desc in fields[1:]:
        s = "\n             {}: {}".format(fix_name(name), fix_type(type))
        if desc.startswith("Optional"):
            s += " = None"
        s += ", "
        args += s
    args = args[:-2]

    decl = "def __init__({}):".format(args)

    body = "super().__init__()\n\n"

    for name, _, _ in fields:
        body += "self.{0} = {0}\n".format(fix_name(name))

    return decl + "\n" + indent(body)


def gen_object(string):
    objname = objname_re.findall(string)[0]
    docstring = docstring_re.findall(string)[0]
    fields = field_re.findall(string)

    i = 0
    while i < len(fields):
        if fields[i][0] == "Field":
            break
        i += 1

    fields = fields[i+1:]

    obj = "class {}(TelegramObjectBase):\n".format(objname)
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