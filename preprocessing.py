from os import scandir
from pathlib import Path
import re
import sys

def expandDefine(define, lines):
    definition = define.split()[1]
    val = " ".join(define.split()[2:])
    m = re.match(r"(?P<function>\w+)\s?\((?P<args>(?P<arg>\w+(,\s?)?)+)\)", definition)
    if m!= None:
        define = m['function']
        values = m['args'].split(',')
        func = val
        lines = expandDefineFunction(define, values, func, lines)
    else:
        lines = expandDefineVariable(definition, val, lines)
    return lines

def expandDefineVariable(define, value, lines):
    newArr = []
    for line in lines:
        line = re.sub(define, value, line)
        newArr.append(line)
    return newArr


def expandDefineFunction(define, values, func, lines):
    newArr = []
    for line in lines:
        newline = ""
        for part in line.split():
            m = re.match(r"(?P<function>\w+)\s?\((?P<args>(?P<arg>\w+(,\s?)?)+)\)(.*)", part)
            val_dict = {}
            if m != None:
                ends = False
                if(part[-1] == ";"):
                    ends=True
                dic = m.groupdict()
                complete = m.group()
                if (m["function"] == define):
                    args = m['args'].split(',')
                    for i in range(len(args)):
                        val_dict[values[i]] = args[i].strip()
                pieces = re.search("\((.*?)\)", part)
                #replace function with define
                piece = pieces.group(0)
                for val in val_dict:
                    func = re.sub(val, val_dict[val], func)
                part = part.replace(complete, func)
                if ends:
                    part = part + ";"
            newline = newline + " " + part
        newArr.append(newline + "\n")
    return newArr

def expandInclude(include):
    lines = []
    my_file = Path(include)

    if my_file.is_file():
        file = open(include, 'r')
        for line in file:
            lines.append(line)
    else:
        lines = ['#include "' + include + '"' + "\n"]
    return lines

def removeSpaces():
    pass

def preproc_include(lines):
    included_lines = {}
    for i in range(len(lines)):
        if(lines[i].startswith("#include")):
            inc = re.search("\"(.*?)\"", lines[i])
            if inc != None:
                inc = inc.group(0)[ 1:-1]
                included_lines[i] = expandInclude(inc)
            else:
                #TODO - preprocess <> includes
                inc = re.search("<(.*?)>", lines[i])
                if inc != None:
                    inc = inc.group(0)[ 1:-1]
                    included_lines[i] = expandInclude(inc)

    newLines = []
    for i in range (len(lines)):
        if(i in included_lines):
            newLines.extend(included_lines[i])
        else:
            newLines.append(lines[i])
    return newLines

def preproc_define(lines):
    for i in range(len(lines)):
        if(lines[i].startswith("#define")):
            lines = expandDefine(lines[i], lines)
    return lines

def preproc_remove(lines):
    lines = remove_comments(lines)
    lines = remove_spaces(lines)
    return lines

def remove_spaces(lines):
    newLines = []
    for line in lines:
        if line != "\n":
            line=line.strip() + "\n"
            if(line[:-1].endswith("{")):
                line = line[:-1] #remove \n
            if (line[:-1] == "}"):
                newLines[-1] = newLines[-1][:-1]
            if line != "\n":
                newLines.append(line)
    return newLines

def remove_comments(lines):
    auxLines = []
    for line in lines:
        if "//" in line:
            pieces = line.split("//")
            if(len(pieces) > 1):
                line = pieces[0]
            else:
                line = ""
        auxLines.append(line)

    started = False
    finalLines = []
    for line in auxLines:
        line, started = remove_block_comments(line, started)
        finalLines.append(line)
    return finalLines

def remove_block_comments(line, started):
    if "/*" in line:
        started = True
        pieces = line.split("/*")
        if(len(pieces) > 1):
            line = pieces[0]
        else:
            line = ""
    if started:
        if "*/" in line:
            pieces = line.split("*/")
            if(len(pieces) > 1):
                line = pieces[1]
            else:
                line = ""
            started = False
        else:
            line = ""
    return line, started

def preprocces(lines):
    fileLines = preproc_include(lines)
    fileLines = preproc_define(fileLines)
    fileLines = preproc_remove(fileLines)
    return fileLines

def write_to_file(fileName, lines):
    newFile = open("preproc" + fileName, 'w')
    for line in lines:
        if not line.startswith("#define"):
            newFile.write(line)
    newFile.close()

def main():
    if(len(sys.argv) == 1):
        print("No File Input")
        return

    fileName = sys.argv[1]
    cFile = open(fileName, 'r')
    lines = []
    for line in cFile:
        lines.append(line)
    lines = preprocces(lines)
    write_to_file(fileName, lines)

if __name__ == "__main__":
    main()
