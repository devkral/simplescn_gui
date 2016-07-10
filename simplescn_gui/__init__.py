#! /usr/bin/env python3

import os
import sys
import logging

sharedir = os.path.dirname(os.path.realpath(__file__))

from simplescn.tools import loglevel_converter


own_help = """
# help:
  * help: help in markdown format
  * help-md, help-markdown: help in html format (parsed markdown)
"""


# for config
def parsepath(inp):
    ret = os.path.expanduser(os.path.expandvars(inp))
    if ret[-1] in ["/", "\\"]:
        ret = ret[:-1]
    if sys.platform.startswith('win32'):
        ret = ret.replace("/", "\\")
    return ret

# default_args, overwrite_args are modified
def scnparse_args(arg_list, _funchelp, default_args):
    new_arglist = {}
    for key, val in default_args.items():
        new_arglist[key] = val
    if len(arg_list) > 0:
        tparam = ()
        for elem in arg_list: #strip filename from arg list
            elem = elem.strip("-")
            if elem in ["help", "h"]:
                print(own_help)
                print(_funchelp())
                sys.exit(0)
            elif elem in ["help-md", "help-markdown"]:
                try:
                    import markdown
                    print(markdown.markdown(own_help+_funchelp().replace("<", "&lt;").replace(">", "&gt;").replace("[", "&#91;").replace("]", "&#93;")))
                    sys.exit(0)
                except ImportError:
                    print("markdown help not available", file=sys.stderr)
                    sys.exit(1)
            else:
                tparam = elem.split("=", 1)
                if len(tparam) == 1:
                    tparam = elem.split(":")
                if len(tparam) == 1:
                    tparam = (tparam[0], "True")
                # autoconvert name to loglevel
                if tparam[0] == "loglevel":
                    tparam[1] = str(loglevel_converter(tparam[1]))
                    logging.root.setLevel(int(tparam[1]))
                if tparam[0] in default_args:
                    new_arglist[tparam[0]] = default_args[tparam[0]].copy()
                    new_arglist[tparam[0]][0] = tparam[1]
    return new_arglist
