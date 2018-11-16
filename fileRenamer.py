#!/usr/bin/env python3

import getopt
import os
import re
import sys

def usage():
    print("Usage:\n"
          "-h, --help\tPrint help info\n"
          "-d, --dir\tDirectory\tDefault: .\n"
          "-r, --regex\tFilename regex\tDefault: .*\n"
          "-o, --orig\tOriginal substring\tMandatory\n"
          "-s, --sub\tSubstitute substring\tDefault: empty str\n")

def getOpts():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:r:o:s:",
                ["help", "dir=", "regex=", "orig=", "sub="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    directory = "."
    regex = ".*"
    orig = sub = ""
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-d", "--dir"):
            directory = arg
        elif opt in ("-r", "--regex"):
            regex = arg
        elif opt in ("-o", "--orig"):
            orig = arg
        elif opt in ("-s", "--sub"):
            sub = arg
        else:
            assert False, "unhandled option"
    if orig == "": 
        usage()
        sys.exit(2)
    return directory, regex, orig, sub

def listFiles(directory, regex):
    files = []
    allFiles = os.listdir(directory)
    prog = re.compile(regex)
    for filename in allFiles:
        if prog.match(filename) and filename not in sys.argv[0]:
            files.append(directory + "/" + filename)
    return files

def main():
    directory, regex, orig, sub = getOpts()
    files = listFiles(directory, regex)
    for filePath in files:
        os.rename(filePath, filePath.replace(orig, sub))
    print("Done")

if __name__ == "__main__":
    main()
