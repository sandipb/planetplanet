#!/usr/bin/env python

# I am not expecting the config to be too unreasonably big to not fit in memory.
# I am more concerned with it not corrupting the existing config.
# So I will construct the desired output in memory, and write it at once, after taking a backup

import os
import sys
import io
import configparser

def sort_config(filename: str) -> bytes:
    fd = io.StringIO()
    oconfig = configparser.RawConfigParser()
    oconfig.read(filename)

    if oconfig._defaults:
        fd.write(f"[{configparser.DEFAULTSECT}]\n")
        for (key, value) in oconfig._defaults.items():
            fd.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
        fd.write("\n")

    result = {}
    for section in sorted(oconfig._sections):
        if section == 'Planet':
            fd.write("[%s]\n" % section)
        for (key, value) in oconfig._sections[section].items():
            if key != "__name__":
                if section == 'Planet':
                    fd.write("%s = %s\n" %
                        (key, str(value).replace('\n', '\n\t')))
                else:
                    # Keep the blog names without double quotes for sane sorting on them 
                    result[value.replace('"', '')] = section
        if section == 'Planet':
            fd.write("\n")
    
    for key, value in sorted(result.items()):
        fd.write("[%s]\n" % value)
        name = key
        # Quote the blog name if it has single quotes
        if "'" in key:
            name = '"%s"' % key
        fd.write("name = %s\n" % name)
        fd.write("\n")
    return fd.getvalue().encode()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'config.ini'
    
    if not os.path.exists(filename):
        print("Config file", filename, "does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(filename, "rb") as fd:
        original = fd.read()
    
    output = sort_config(filename)

    if original != output:
        os.rename(filename, filename + ".bak")

        with open(filename, 'wb') as fd:
            fd.write(output)
    else:
        print("No changes needed")
        


